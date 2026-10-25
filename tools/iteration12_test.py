"""V12: agency onboarding, old backups, column filters, and form hints."""
import base64
import json
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:8776/index.html'
SECRET = 'Phrase secrète longue 84 !'
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


def main():
 server = subprocess.Popen(['python', '-m', 'http.server', '8776', '--bind', '127.0.0.1', '--directory', str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
 try:
  with tempfile.TemporaryDirectory() as directory, sync_playwright() as playwright:
   browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
   context = browser.new_context(accept_downloads=True)
   page = context.new_page()
   errors = []
   requests = []
   page.on('pageerror', lambda error: errors.append(str(error)))
   page.on('request', lambda request: requests.append(request.url))
   page.goto(URL)
   page.locator('#welcome-form').wait_for()
   assert page.locator('#welcome-form input[name=installationName]').count() == 0
   assert page.locator('#welcome-form input[name=agencyName]').get_attribute('required') is not None
   assert page.locator('#welcome-form input[name=legalName]').count() == 1
   assert page.locator('#welcome-form textarea[name=terms]').count() == 1
   page.locator('#welcome-form input[name=agencyName]').fill('France Marbre Avignon')
   page.locator('#welcome-form input[name=legalName]').fill('Marbre Avignon SAS')
   page.locator('#welcome-form input[name=street]').fill('12 avenue de la République')
   page.locator('#welcome-form input[name=postalCode]').fill('84000')
   page.locator('#welcome-form input[name=city]').fill('Avignon')
   page.locator('#welcome-form input[name=siret]').fill('00000000000001')
   page.locator('#welcome-form details summary').click()
   page.locator('#welcome-form textarea[name=terms]').fill('Paiement à réception')
   page.locator('#welcome-logo').set_input_files({'name':'logo.png','mimeType':'image/png','buffer':PNG})
   page.locator('#welcome-logo-preview').wait_for(state='visible')
   page.locator('#welcome-form button[type=submit]').click()
   page.wait_for_function('installation && installation.agencyId')
   agency = page.evaluate('installation.agencyId')
   assert agency.startswith('AG-FRANCE-MARBRE-AVIGNON-')
   assert page.evaluate('installation.installationId===undefined && installation.installationName===undefined')
   assert page.evaluate('state.settings.company.displayName') == 'France Marbre Avignon'
   assert page.evaluate('state.settings.company.legalName') == 'Marbre Avignon SAS'
   assert page.evaluate('state.settings.company.siret') == '00000000000001'
   assert page.evaluate('state.settings.company.terms') == 'Paiement à réception'
   assert page.evaluate('state.settings.logoDataURI.startsWith("data:image/png;base64,")')
   assert page.locator('#brand img').get_attribute('alt') == 'France Marbre Avignon'
   assert page.title() == 'France Marbre Avignon — Espace commercial'
   page.evaluate("go('settings');openSettingsCategory('documents')")
   assert page.locator('#company-form input[name=legalName]').input_value() == 'Marbre Avignon SAS'
   assert page.locator('#company-form input[name=displayName]').input_value() == 'France Marbre Avignon'
   page.evaluate("openSettingsCategory('data')")
   assert page.locator('.logo-preview').count() >= 1
   assert page.locator('#my-agency input[readonly]').count() == 1
   assert page.locator('#my-agency input[readonly]').input_value() == agency
   page.locator('#agency-profile-form input[name=agencyName]').fill('Agence Avignon Centre')
   page.locator('#agency-profile-form button[type=submit]').click()
   assert page.evaluate('installation.agencyId') == agency
   assert page.evaluate('state.settings.company.displayName') == 'Agence Avignon Centre'
   assert page.locator('#brand img').get_attribute('alt') == 'Agence Avignon Centre'
   page.evaluate('async()=>{await commit(s=>populateDemo(s))}')
   snapshot = page.evaluate('JSON.stringify(state.quotes.find(q=>q.contentSnapshot).contentSnapshot)')
   page.evaluate("go('settings');openSettingsCategory('documents')")
   page.locator('#company-form input[name=displayName]').fill('Enseigne personnalisée')
   page.locator('#company-form button[type=submit]').click()
   assert page.evaluate('JSON.stringify(state.quotes.find(q=>q.contentSnapshot).contentSnapshot)') == snapshot
   assert page.evaluate('makeDocumentSnapshot("quote",state.quotes[0],lines(state.quotes[0])).issuer.displayName') == 'Enseigne personnalisée'

   page.evaluate("go('clients')")
   assert page.locator('#advanced-filters,#toggle-filters,.common-filter-panel,.filter-toggle').count() == 0
   assert page.locator('.searchbar .clear-filters').count() == 1
   assert page.locator('.searchbar .clear-filters').is_disabled()
   page.locator('[data-column-filter-table=clients][data-column-filter-key=name]').click()
   page.locator('#column-filter-menu input[type=search]').first.fill('AUCUN CLIENT')
   assert page.locator('#result-count').inner_text().startswith('0 ')
   assert not page.locator('.searchbar .clear-filters').is_disabled()
   page.locator('.searchbar .clear-filters').click()
   assert page.locator('#result-count').inner_text().startswith('40 ')
   page.locator('[data-column-filter-table=clients][data-column-filter-key=address]').click()
   assert page.locator('#column-filter-menu').get_by_text('Code postal (début)').count() > 0
   page.evaluate('closeColumnMenu()')
   page.get_by_role('button', name='+ Nouveau client').click()
   assert page.locator('#editform input[name=phone]').get_attribute('placeholder') == 'Ex. 06 12 34 56 78'
   assert 'Téléphone (texte)' not in page.locator('#editform').inner_text()
   page.locator('#editform input[name=lastName]').fill('Essai')
   page.locator('#editform input[name=phone]').fill('06 01 02 03 04')
   page.locator('#editform button[type=submit]').click()
   page.wait_for_function('state.clients.some(c=>c.lastName==="Essai")')
   assert page.evaluate('typeof state.clients.find(c=>c.lastName==="Essai").phone') == 'string'
   assert page.evaluate('state.clients.find(c=>c.lastName==="Essai").phone') == '06 01 02 03 04'

   page.evaluate("go('products')")
   assert page.locator('#advanced-filters,#toggle-filters,.common-filter-panel,.filter-toggle').count() == 0
   page.locator('[data-column-filter-table=products][data-column-filter-key=format]').click()
   assert page.locator('#column-filter-menu').get_by_text('Épaisseur').count() > 0
   assert page.locator('#column-filter-menu').get_by_text('Finition').count() > 0
   page.evaluate('closeColumnMenu()')
   page.locator('[data-column-filter-table=products][data-column-filter-key=price]').click()
   assert page.locator('#price-lower').count() == 1
   page.locator('#column-filter-menu input[type=number]').first.fill('100')
   assert not page.locator('.searchbar .clear-filters').is_disabled()
   page.evaluate("go('clients')")
   assert page.locator('.searchbar .clear-filters').is_disabled()
   page.evaluate("go('products')")
   assert page.evaluate('productFilters.minPrice') == '100'
   page.locator('.searchbar .clear-filters').click()
   assert page.evaluate('productFilters.minPrice') == ''
   page.get_by_role('button', name='+ Ajouter un produit').click()
   assert page.locator('#editform input[name=name]').get_attribute('placeholder') == 'Ex. Travertin Beige Nuancé 40 × 60 cm'
   assert page.locator('#editform input[name=ref]').input_value()
   page.evaluate('closeDialog()')
   page.evaluate("go('pipeline')")
   assert page.locator('#module-searchbar .clear-filters').count() == 1
   assert page.locator('.common-filter-panel,.filter-toggle').count() == 0
   page.evaluate("kanban=false;pipelinePage()")
   page.locator('[data-column-filter-table=opportunities][data-column-filter-key=title]').click()
   page.locator('#column-filter-menu input[type=search]').first.fill('AUCUN DOSSIER')
   assert page.locator('#opportunity-results .result-summary').inner_text() == '0 dossier(s)'
   page.locator('#module-searchbar .clear-filters').click()
   assert page.locator('#opportunity-results .result-summary').inner_text() == '50 dossier(s)'
   page.evaluate("kanban=true;pipelinePage()")
   assert page.locator('#module-searchbar .clear-filters').count() == 1
   for tab in ('Devis', 'Relances à effectuer'):
    page.locator('.tabs button').filter(has_text=tab).click()
    assert page.locator('#module-searchbar .clear-filters').count() == 1
    assert page.locator('.common-filter-panel,.filter-toggle').count() == 0
   page.evaluate("go('sales')")
   assert page.locator('#module-searchbar .clear-filters').count() == 1
   assert page.locator('.common-filter-panel,.filter-toggle').count() == 0
   page.locator('[data-column-filter-table=billing][data-column-filter-key=status]').click()
   page.locator('#column-filter-menu input[type=checkbox]').first.check()
   assert not page.locator('#module-searchbar .clear-filters').is_disabled()
   page.locator('#module-searchbar .clear-filters').click()
   assert page.evaluate('billingStatuses.length') == 0
   page.evaluate("fullSearchQuery='Exemple';go('search')")
   assert page.locator('#global-filter-area .clear-filters').count() == 1
   assert page.locator('.common-filter-panel,.filter-toggle').count() == 0
   page.evaluate("go('analytics')")
   assert page.locator('.toolbar .clear-filters').count() == 1
   assert page.locator('.common-filter-panel,.filter-toggle').count() == 0
   page.evaluate("go('settings');openSettingsCategory('data')")
   page.locator('#daily-backup-form input[name=passphrase]').fill(SECRET)
   context.set_offline(True)
   with page.expect_download() as download:
    page.locator('#daily-backup-form button').click()
   backup_path = Path(directory) / 'backup.json'
   download.value.save_as(backup_path)
   backup = json.loads(backup_path.read_text())
   assert backup['agencyId'] == agency and 'installationId' not in backup
   assert page.evaluate('async file=>validateAgencyBackup(file,await decryptAgencyBackup(file,"Phrase secrète longue 84 !")).manifest.agencyId', backup) == agency
   context.set_offline(False)
   with page.expect_download() as download:
    page.evaluate("exportModuleJSON('commercial')")
   module_path = Path(directory) / 'commercial.json'
   download.value.save_as(module_path)
   module = json.loads(module_path.read_text())
   assert module['agencyId'] == agency and 'installationId' not in module
   assert module['counts']['opportunities'] == 50
   with page.expect_download() as download:
    page.evaluate("exportClients('all')")
   clients_export = Path(directory) / 'clients.json'
   download.value.save_as(clients_export)
   assert 'installationId' not in json.loads(clients_export.read_text())
   with page.expect_download() as download:
    page.evaluate('exportCatalog()')
   catalog_export = Path(directory) / 'catalog.json'
   download.value.save_as(catalog_export)
   assert 'installationId' not in json.loads(catalog_export.read_text())

   # Recreate a V11 encrypted file with historical post metadata and verify V12 reads it.
   legacy = page.evaluate("""async secret=>{const manifest={...backupManifest(state),installationId:'POSTE-HISTORIQUE'},salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12)),header={format:'fmt-agency-backup',formatVersion:1,agencyId:manifest.agencyId,installationId:manifest.installationId,backupId:manifest.backupId,createdAt:manifest.createdAt,kdf:'PBKDF2-SHA256',iterations:600000,cipher:'AES-256-GCM',salt:b64(salt),iv:b64(iv)},key=await backupKey(secret,salt,600000),plain=utf8.encode(JSON.stringify({manifest,data:state})),ciphertext=b64(new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:utf8.encode(JSON.stringify(header))},key,plain)));return {...header,ciphertext}}""", SECRET)
   assert page.evaluate('async file=>validateAgencyBackup(file,await decryptAgencyBackup(file,"Phrase secrète longue 84 !")).manifest.installationId', legacy) == 'POSTE-HISTORIQUE'
   page.on('dialog', lambda dialog: dialog.accept(SECRET if dialog.type == 'prompt' else None))
   page.evaluate('async file=>restoreAgencyBackup(file)', legacy)
   assert page.evaluate('state.clients.some(c=>c.lastName==="Essai")')
   page.reload()
   page.wait_for_function('installation && installation.agencyId')
   assert page.evaluate('installation.agencyId') == agency
   assert page.locator('#welcome-form').count() == 0
   assert page.evaluate('installation.installationId===undefined')
   assert not errors, errors
   assert all(url.startswith('http://127.0.0.1:8776/') or url.startswith('data:') for url in requests), requests

   old_context = browser.new_context()
   old = old_context.new_page()
   old.goto(URL)
   old.locator('#welcome-form').wait_for()
   old.locator('#welcome-form input[name=agencyName]').fill('Agence temporaire')
   old.locator('#welcome-form button[type=submit]').click()
   old.wait_for_function('installation && installation.agencyId')
   old.evaluate('async()=>{await commit(s=>populateDemo(s))}')
   old.evaluate("""async()=>{const s=structuredClone(state);stampAgency(s,'AG01');s.settings.company.displayName='France Marbre 84';await idbPutMainAndInstallation(s,{mode:'agency',agencyId:'AG01',agencyNames:{AG01:'Agence historique'},installationId:'POSTE-EXISTANT',installationName:'Ancien poste',lastExportAt:'2026-01-01T10:00:00.000Z'})}""")
   old.reload()
   old.wait_for_function('installation && installation.agencyId')
   assert old.evaluate('installation.agencyId') == 'AG01'
   assert old.evaluate('installation.installationId===undefined && installation.installationName===undefined')
   assert old.evaluate('state.settings.company.displayName') == 'Agence historique'
   assert old.evaluate('state.clients.length') == 40
   assert old.evaluate('checkAgencyStamp(state,"AG01")===undefined')
   assert old.locator('#welcome-form').count() == 0
   old_context.close()
   browser.close()
  print('V12: configuration, identité, filtres, formulaires et sauvegardes OK')
 finally:
  server.terminate()
  server.wait(timeout=5)


if __name__ == '__main__':
 main()
