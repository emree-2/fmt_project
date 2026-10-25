"""V11 regression: single agency, relational transfers, backups, and filter layout."""
import json
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:8768/index.html'
SECRET = 'Phrase secrète longue 84 !'


def main():
 server = subprocess.Popen(['python', '-m', 'http.server', '8768', '--bind', '127.0.0.1', '--directory', str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
 try:
  with tempfile.TemporaryDirectory() as directory, sync_playwright() as playwright:
   browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
   context = browser.new_context(accept_downloads=True)
   page = context.new_page()
   errors = []
   page.on('pageerror', lambda error: errors.append(str(error)))
   page.goto(URL)
   page.get_by_role('heading', name='Bienvenue dans votre espace France Marbre 84').wait_for()
   assert page.get_by_role('heading', name='Bienvenue dans votre espace France Marbre 84').count() == 1
   assert 'Direction' not in page.locator('body').inner_text()
   page.locator('#welcome-form input[name=agencyName]').fill('France Marbre 84 — Avignon')
   page.locator('#welcome-form input[name=city]').fill('Avignon')
   page.get_by_role('button', name='Configurer mon agence').click()
   page.wait_for_function('installation && /^AG-AVIGNON-[0-9A-F]{6}$/.test(installation.agencyId)')
   agency = page.evaluate('installation.agencyId')
   page.evaluate("go('settings');openSettingsCategory('data')")
   assert page.locator('#agency-profile-form input[readonly]').first.input_value() == agency
   page.locator('#agency-profile-form input[name=agencyName]').fill('France Marbre 84 — Centre')
   page.get_by_role('button', name='Enregistrer mon agence').click()
   assert page.evaluate('installation.agencyId') == agency
   page.evaluate('async()=>{await commit(s=>populateDemo(s))}')
   assert page.evaluate('checkAgencyStamp(state,installation.agencyId)===undefined')
   baseline = page.evaluate('Object.fromEntries(collections.map(k=>[k,state[k].length]))')

   for view in ('pipeline', 'sales'):
    page.evaluate('view=>go(view)', view)
    assert page.locator('details.management summary').inner_text() == 'Gestion des données ▾'
    assert page.locator('#module-searchbar .filter-toggle').count() == 1
    page.locator('#module-searchbar .filter-toggle').click()
    assert page.locator('#module-filter-area .common-filter-panel').is_visible()
    assert page.locator('#module-filter-area .common-filter-panel').count() == 1
    page.locator('#module-filter-area').get_by_role('button', name='Fermer').click()
    assert not page.locator('#module-filter-area .common-filter-panel').is_visible()
   page.evaluate("go('pipeline')")
   page.locator('#module-searchbar .filter-toggle').click()
   first_text_filter = page.locator('#module-filter-area .common-filter-panel input[type=search]').first
   first_text_filter.fill('AUCUN-DOSSIER-CORRESPONDANT')
   assert page.locator('#opportunity-results .result-summary').inner_text() == '0 dossier(s)'
   first_text_filter.fill('')
   assert page.locator('#opportunity-results .result-summary').inner_text() == '50 dossier(s)'
   for tab in ('devis', 'relances'):
    page.locator('.tabs button').filter(has_text={'devis':'Devis','relances':'Relances à effectuer'}[tab]).click()
    assert page.locator('#module-searchbar .filter-toggle').count() == 1
    assert page.locator('#module-filter-area .common-filter-panel').count() == 1
   page.evaluate("commercialTab='dossiers';kanban=true;pipelinePage()")
   assert page.locator('#module-searchbar .filter-toggle').count() == 1
   assert page.locator('.kanban').count() == 1

   page.evaluate("go('settings');openSettingsCategory('data')")
   page.locator('#daily-backup-form input[name=passphrase]').fill(SECRET)
   context.set_offline(True)
   with page.expect_download() as download:
    page.locator('#daily-backup-form button').click()
   backup_path = Path(directory) / 'backup.json'
   download.value.save_as(backup_path)
   backup = json.loads(backup_path.read_text())
   assert backup['agencyId'] == agency and backup['cipher'] == 'AES-256-GCM'
   assert 'clients' not in backup and 'agencyName' not in backup
   assert page.evaluate('async file=>validateAgencyBackup(file,await decryptAgencyBackup(file,"Phrase secrète longue 84 !")).manifest.agencyId', backup) == agency
   context.set_offline(False)

   exported = {}
   for scope in ('commercial', 'billing'):
    with page.expect_download() as download:
     page.evaluate('scope=>exportModuleJSON(scope)', scope)
    path = Path(directory) / f'{scope}.json'
    download.value.save_as(path)
    payload = json.loads(path.read_text())
    exported[scope] = payload
    assert payload['agencyId'] == agency and payload['agencyName'] == 'France Marbre 84 — Centre'
    assert payload['installationId'] and payload['createdAt']
    assert payload['counts']['opportunities'] >= payload['counts']['sales'] > 0
    assert payload['counts']['payments'] > 0
    assert page.evaluate('payload=>planModuleImport(state,payload).added.opportunities', payload) == 0
    assert page.evaluate('payload=>planModuleImport(state,payload).conflicts.length', payload) == 0
    foreign = {**payload, 'agencyId':'AG-OTHER-123456'}
    try:
     page.evaluate('payload=>validateModuleEnvelope(payload,payload.scope)', foreign)
    except Exception:
     pass
    else:
     raise AssertionError('Foreign agency module accepted')
   conflict = json.loads(json.dumps(exported['billing']))
   conflict['records']['sales'][0]['status'] = 'Autre statut'
   assert page.evaluate('payload=>planModuleImport(state,payload).conflicts.some(x=>x.collection==="sales")', conflict)
   assert page.evaluate('payload=>planModuleImport(state,payload).added.sales', conflict) == 0
   page.evaluate("go('sales')")
   page.locator('#billing-import').set_input_files(str(Path(directory) / 'billing.json'))
   assert 'Prévisualisation de l’import' in page.locator('#dialogtitle').inner_text()
   assert 'déjà présent' in page.locator('#dialogbody').inner_text()
   page.locator('#dialogbody').get_by_role('button', name='Annuler').click()
   broken = json.loads(json.dumps(exported['billing']))
   broken['records']['opportunities'].pop()
   broken['counts']['opportunities'] -= 1
   try:
    page.evaluate('payload=>{const empty=fresh();stampAgency(empty,installation.agencyId);return planModuleImport(empty,payload)}', broken)
   except Exception:
    pass
   else:
    raise AssertionError('Orphaned billing graph accepted')

   page.evaluate("commercialTab='dossiers';go('pipeline')")
   with page.expect_download() as download:
    page.evaluate("exportModuleCSV('commercial')")
   csv_path = Path(directory) / 'dossiers.csv'
   download.value.save_as(csv_path)
   assert all(field in csv_path.read_text(encoding='utf-8-sig').splitlines()[0] for field in ('agencyId', 'agencyName', 'dossier', 'client', 'projet', 'estimationHT'))
   page.evaluate("go('sales')")
   with page.expect_download() as download:
    page.evaluate("exportModuleCSV('billing')")
   csv_path = Path(directory) / 'facturation.csv'
   download.value.save_as(csv_path)
   assert all(field in csv_path.read_text(encoding='utf-8-sig').splitlines()[0] for field in ('agencyId', 'client', 'facture', 'TTC', 'encaisse', 'reste'))
   with page.expect_download() as download:
    page.evaluate("exportAgencyCSV('payments')")
   csv_path = Path(directory) / 'reglements.csv'
   download.value.save_as(csv_path)
   assert 'reglement' in csv_path.read_text(encoding='utf-8-sig').splitlines()[0]

   # A real import restores linked records without changing the agency identity.
   page.evaluate("async()=>{const empty=fresh();stampAgency(empty,installation.agencyId);await persist(empty);state=empty;render()}")
   page.evaluate('async payload=>{pendingModuleImport={payload,scope:"commercial"};await applyModuleImport()}', exported['commercial'])
   assert page.evaluate('state.opportunities.length') == baseline['opportunities']
   assert page.evaluate('state.sales.length') == baseline['sales']
   assert page.evaluate('state.payments.length') == baseline['payments']
   assert page.evaluate('checkAgencyStamp(state,installation.agencyId)===undefined')
   page.evaluate('async payload=>{pendingModuleImport={payload,scope:"commercial"};await applyModuleImport()}', exported['commercial'])
   assert page.evaluate('state.payments.length') == baseline['payments']

   # The full encrypted backup remains restorable after a module import.
   page.on('dialog', lambda dialog: dialog.accept(SECRET if dialog.type == 'prompt' else None))
   page.evaluate('async file=>restoreAgencyBackup(file)', backup)
   assert page.evaluate('state.clients.length') == baseline['clients']
   assert page.evaluate('state.payments.length') == baseline['payments']
   assert page.evaluate("""async file=>{const original=installation;installation={...installation,agencyId:'AG-OTHER-123456'};try{await restoreAgencyBackup(file);return false}catch(e){return e.message.includes('appartient')}finally{installation=original}}""", backup)

   page.reload()
   page.wait_for_function('installation && installation.agencyId')
   assert page.evaluate('installation.agencyId') == agency
   assert page.locator('#welcome-form').count() == 0
   assert page.evaluate('Object.fromEntries(collections.map(k=>[k,state[k].length]))') == baseline
   assert not errors, errors

   old_context = browser.new_context()
   old = old_context.new_page()
   old.goto(URL)
   old.get_by_role('heading', name='Bienvenue dans votre espace France Marbre 84').wait_for()
   old.wait_for_function('installation !== null')
   old.locator('#welcome-form input[name=agencyName]').fill('Agence temporaire')
   old.get_by_role('button', name='Configurer mon agence').click()
   old.wait_for_function('installation && installation.agencyId')
   old.evaluate('async()=>{await commit(s=>populateDemo(s))}')
   old.evaluate("""async()=>{const s=structuredClone(state);stampAgency(s,'AG01');const legacy={mode:'agency',agencyId:'AG01',agencyNames:{AG01:'France Marbre 84 — Ancienne agence'},installationId:'POSTE-EXISTANT',lastExportAt:'2026-01-01T10:00:00.000Z'};await idbPutMainAndInstallation(s,legacy)}""")
   old.reload()
   old.wait_for_function('installation && installation.agencyId')
   assert old.evaluate('installation.agencyId') == 'AG01'
   assert old.evaluate('installation.installationId') == 'POSTE-EXISTANT'
   assert old.evaluate('state.clients.length') == 40
   assert old.evaluate('checkAgencyStamp(state,"AG01")===undefined')
   assert old.locator('#welcome-form').count() == 0
   old_context.close()
   browser.close()
  print('V11: configuration, filtres, sauvegarde et transferts relationnels OK')
 finally:
  server.terminate()
  server.wait(timeout=5)


if __name__ == '__main__':
 main()
