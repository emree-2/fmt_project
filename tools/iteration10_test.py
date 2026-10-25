"""V10: local encrypted backups, four isolated agency snapshots, read-only direction."""
import json
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:8767/index.html'
SECRET = 'Phrase secrète longue 84 !'


def main():
 server = subprocess.Popen(['python', '-m', 'http.server', '8767', '--bind', '127.0.0.1', '--directory', str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
 try:
  with tempfile.TemporaryDirectory() as directory, sync_playwright() as playwright:
   browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
   files = []
   newer_file = None
   for index in range(1, 5):
    agency = f'AG0{index}'
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    failures = []
    requests = []
    page.on('pageerror', lambda error: failures.append(str(error)))
    page.on('request', lambda request: requests.append(request.url))
    page.goto(URL)
    page.locator('#dialogbody button').filter(has_text=agency).click()
    if index == 1:
     page.evaluate('async()=>{await commit(s=>populateDemo(s))}')
    else:
     page.evaluate("""async index=>{await commit(s=>{s.clientSequence=1;s.clients.push({id:'C-SAME',number:'CLI-000001',lastName:index===3?'<img src=x onerror=window.__xss=1>':'Client '+index,firstName:'Essai',type:'Particulier',company:'',siret:'',phone:'',email:'',street:'',postalCode:'',city:'',legacyAddress:'',origin:'',notes:'',createdAt:now(),updatedAt:now()})})}""", index)
    assert page.evaluate('state.clients.every(c=>c.agencyId===installation.agencyId)')
    assert page.evaluate('checkAgencyStamp(state,installation.agencyId)===undefined')
    assert page.evaluate('state.settings.agencyId') == agency
    page.evaluate("go('settings');openSettingsCategory('data')")
    page.locator('#daily-backup-form input[name=passphrase]').fill(SECRET)
    context.set_offline(True)
    with page.expect_download() as download:
     page.locator('#daily-backup-form button').click()
    path = Path(directory) / f'{agency}.backup.json'
    download.value.save_as(path)
    envelope = json.loads(path.read_text())
    assert envelope['agencyId'] == agency and 'clients' not in envelope and 'agencyName' not in envelope
    assert 'Client' not in path.read_text() and envelope['cipher'] == 'AES-256-GCM'
    payload = page.evaluate('async([file,secret])=>validateAgencyBackup(file,await decryptAgencyBackup(file,secret)).manifest', [envelope, SECRET])
    assert payload['counts']['clients'] == (40 if index == 1 else 1)
    for damaged, phrase in [(envelope, 'wrong phrase'), ({**envelope, 'ciphertext': envelope['ciphertext'][:-3] + 'AAA'}, SECRET)]:
     try:
      page.evaluate('async([file,secret])=>decryptAgencyBackup(file,secret)', [damaged, phrase])
     except Exception:
      pass
     else:
      raise AssertionError('Wrong phrase or tampered ciphertext accepted')
    if index == 1:
     page.on('dialog', lambda dialog: dialog.accept(SECRET if dialog.type == 'prompt' else None))
     page.evaluate('async file=>restoreAgencyBackup(file)', envelope)
     assert page.evaluate('state.clients.length') == 40
    if index == 2:
     page.evaluate("""async()=>{await commit(s=>{s.clientSequence=2;s.clients.push({id:'C-NEW',number:'CLI-000002',lastName:'Client nouveau',firstName:'Essai',type:'Particulier',company:'',siret:'',phone:'',email:'',street:'',postalCode:'',city:'',legacyAddress:'',origin:'',notes:'',createdAt:now(),updatedAt:now()})})}""")
     page.evaluate("go('settings');openSettingsCategory('data')")
     page.locator('#daily-backup-form input[name=passphrase]').fill(SECRET)
     with page.expect_download() as second_download:
      page.locator('#daily-backup-form button').click()
     newer_file = Path(directory) / 'AG02-new.backup.json'
     second_download.value.save_as(newer_file)
    assert not failures, failures
    assert all(url.startswith('http://127.0.0.1:8767/') or url.startswith('data:') for url in requests), requests
    files.append(path)
    context.close()

   direction_context = browser.new_context(accept_downloads=True)
   manager = direction_context.new_page()
   errors = []
   manager.on('pageerror', lambda error: errors.append(str(error)))
   manager.goto(URL)
   manager.locator('#dialogbody button').filter(has_text='Direction').click()
   manager.evaluate("go('settings');openSettingsCategory('data')")
   def accept_dialog(dialog):
    dialog.accept(SECRET if dialog.type == 'prompt' else None)
   manager.on('dialog', accept_dialog)
   direction_context.set_offline(True)
   for path in files:
    manager.locator('#consolidation-card input[type=file]').first.set_input_files(str(path))
    manager.wait_for_function('(id)=>!!directionSnapshots[id]', arg=path.name[:4])
   assert manager.evaluate('Object.keys(directionSnapshots).length') == 4
   assert manager.evaluate('state.clients.length') == 43
   assert manager.evaluate('state.clients.filter(c=>c.number==="CLI-000001").length') == 4
   assert manager.evaluate('new Set(state.clients.map(c=>c.id)).size===state.clients.length')
   assert manager.evaluate('state.products.length') < 4000  # Common seed is not repeated four times.
   before = manager.evaluate('JSON.stringify(directionSnapshots.AG02)')
   manager.locator('#consolidation-card input[type=file]').first.set_input_files(str(files[1]))
   assert manager.evaluate('JSON.stringify(directionSnapshots.AG02)') == before
   other_agencies = manager.evaluate('JSON.stringify([directionSnapshots.AG01,directionSnapshots.AG03,directionSnapshots.AG04])')
   manager.locator('#consolidation-card input[type=file]').first.set_input_files(str(newer_file))
   manager.wait_for_function('directionSnapshots.AG02.manifest.counts.clients===2')
   assert manager.evaluate('state.clients.length') == 44
   assert manager.evaluate('JSON.stringify([directionSnapshots.AG01,directionSnapshots.AG03,directionSnapshots.AG04])') == other_agencies
   newer_snapshot = manager.evaluate('JSON.stringify(directionSnapshots.AG02)')
   for check in [
    "async file=>{const p=await decryptAgencyBackup(file,'Phrase secrète longue 84 !');delete p.data.reminders;validateAgencyBackup(file,p)}",
    "async()=>{const p=structuredClone(directionSnapshots.AG02);p.manifest.installationId='unexpected-post';await reviewAgencyImport(p)}",
   ]:
    try:
     manager.evaluate(check, json.loads(files[1].read_text()) if 'file=>' in check else None)
    except Exception:
     pass
    else:
     raise AssertionError('Incomplete backup or unexpected reference post accepted')
   assert manager.evaluate('JSON.stringify(directionSnapshots.AG02)') == newer_snapshot
   manager.locator('#consolidation-card input[type=file]').first.set_input_files(str(files[1]))
   manager.wait_for_timeout(300)
   assert manager.evaluate('JSON.stringify(directionSnapshots.AG02)') == newer_snapshot
   manager.evaluate("selectAgencyView('AG03');go('clients')")
   assert manager.locator('#content img[src=x]').count() == 0
   assert manager.evaluate('window.__xss===undefined')
   assert manager.evaluate('state.clients.length') == 1
   assert manager.evaluate('state.clients[0].agencyId') == 'AG03'
   manager.evaluate("findGlobalResults('Client')")
   assert manager.evaluate("globalGroups.find(g=>g.kind==='clients').items.every(c=>c.agencyId==='AG03')")
   with manager.expect_download() as csv_download:
    manager.evaluate("csvExport('all')")
   csv_path = Path(directory) / 'clients.csv'
   csv_download.value.save_as(csv_path)
   assert csv_path.read_text(encoding='utf-8-sig').splitlines()[0].startswith('"agencyId";"agencyName";')
   assert 'AG03' in csv_path.read_text(encoding='utf-8-sig')
   manager.evaluate("selectAgencyView('all');go('clients');clientDetail(state.clients[0].id)")
   assert manager.get_by_role('button', name='Modifier les informations').is_disabled()
   assert 'Agence d’origine' in manager.locator('#dialogbody').inner_text()
   manager.evaluate('closeDialog();go("pipeline");opportunityDetail(state.opportunities[0].id)')
   assert manager.locator('#dialogtitle').inner_text() == 'Dossier commercial'
   manager.evaluate('closeDialog();go("sales");billingDetail(state.sales[0].id)')
   assert 'Facturation' in manager.locator('#dialogtitle').inner_text()
   assert manager.evaluate('async()=>await commit(s=>s.clients.pop())') is False
   manager.evaluate('closeDialog();go("analytics")')
   assert manager.locator('.direction-comparison').count() == 1
   assert manager.locator('.direction-comparison').inner_text().count('Agence') >= 4
   sold_count = manager.evaluate('state.confirmedSales.filter(c=>inPeriod(c.confirmedAt)).length')
   assert manager.locator('.direction-comparison .kpi').filter(has_text='Ventes confirmées').locator('strong').inner_text() == str(sold_count)
   unpaid = manager.evaluate('round(state.sales.reduce((n,b)=>n+paymentSummary(b).remaining,0))')
   assert manager.locator('.direction-comparison .kpi').filter(has_text='Reste à payer').locator('strong').inner_text() == manager.evaluate('n=>eur(n)', unpaid)
   direction_context.set_offline(False)
   manager.reload()
   manager.wait_for_function('Object.keys(directionSnapshots).length===4')
   assert manager.evaluate('state.clients.length') == 44
   assert not errors, errors

   # A V9 database stays unassigned until an operator chooses its agency.
   old = subprocess.check_output(['git', 'show', 'abd3588:index.html'], cwd=ROOT).decode()
   legacy_context = browser.new_context()
   legacy = legacy_context.new_page()
   legacy_context.route('http://127.0.0.1:8767/old.html', lambda route: route.fulfill(status=200, content_type='text/html', body=old))
   legacy.goto('http://127.0.0.1:8767/old.html')
   legacy.wait_for_function('state&&state.schemaVersion===7')
   legacy.evaluate('async()=>{await commit(s=>populateDemo(s))}')
   legacy.goto(URL)
   legacy.locator('#dialogtitle').get_by_text('Configuration de l’installation').wait_for()
   assert legacy.locator('#dialogtitle').inner_text() == 'Configuration de l’installation'
   assert legacy.evaluate('state.clients[0].agencyId===undefined')
   legacy.locator('#dialogbody button').filter(has_text='AG02').click()
   legacy.locator('#dialog').wait_for(state='hidden')
   assert legacy.evaluate('state.clients.every(c=>c.agencyId==="AG02")')
   legacy.reload()
   legacy.wait_for_function('installation&&installation.agencyId==="AG02"')
   assert legacy.evaluate('state.clients.length') == 40
   legacy_context.close()
   browser.close()
  print('V10: encrypted offline backups, 4 agencies, isolation, read-only, migration — OK')
 finally:
  server.terminate()
  server.wait(timeout=5)


if __name__ == '__main__':
 main()
