"""Recette de régression v4. Outil de développement facultatif ; index.html est autonome."""
import asyncio, json, tempfile
from pathlib import Path
from playwright.async_api import async_playwright, Error

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  context=await browser.new_context(viewport={'width':1440,'height':1000})
  page=await context.new_page();errors=[];requests=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('request',lambda r:requests.append(r.url))
  await page.goto('http://127.0.0.1:8765/index.html')
  await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  assert await page.evaluate('state.schemaVersion')==4
  assert await page.evaluate('state.products.length')==3283
  assert await page.locator('#nav button').count()==5
  assert await page.locator('#adminnav button').count()==2
  assert 'Tableau de bord' not in await page.locator('#nav').inner_text()
  assert await page.evaluate("modules[0][0]")=='analytics'
  await context.set_offline(True)  # All following interactions run with network disabled.
  await page.get_by_role('button',name='+ Nouveau client').click()
  assert await page.locator('[name=company]').is_disabled()
  await page.locator('[name=type]').select_option('Professionnel')
  assert await page.locator('[name=company]').is_enabled()
  await page.locator('[name=company]').fill('Société à effacer')
  await page.locator('[name=type]').select_option('Particulier')
  assert await page.locator('[name=company]').input_value()==''
  assert await page.locator('[name=owner]').count()==0
  await page.locator('[name=lastName]').fill('Martin')
  await page.locator('[name=firstName]').fill('Alice')
  await page.locator('[name=phone]').fill('0612345678')
  await page.locator('[name=street]').fill('12 rue de Test')
  await page.locator('[name=postalCode]').fill('01000')
  await page.locator('[name=city]').fill('Bourg-en-Bresse')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function('state.clients.length===1')
  cid=await page.evaluate('state.clients[0].id')
  assert await page.evaluate('state.clients[0].number')=='CLI-000001'
  assert await page.evaluate('state.clients[0].company')==''
  await page.evaluate("go('clients')")
  assert await page.get_by_role('button',name='Modifier',exact=True).count()==1
  await page.evaluate("setFilter('clients','cities',['Bourg-en-Bresse'])")
  assert await page.locator('#list tbody tr').count()==1
  await page.evaluate("setFilter('clients','postalCode','99999')")
  assert 'Aucun résultat' in await page.locator('#list').inner_text()
  await page.evaluate("setFilter('clients','postalCode','01000')")
  await page.locator('#main-search').fill('CLI-000001')
  assert 'Alice Martin' in await page.locator('#list').inner_text()
  # Cancel must not persist changes.
  await page.get_by_role('button',name='Modifier',exact=True).click()
  await page.locator('[name=lastName]').fill('Non enregistré')
  await page.get_by_role('button',name='Annuler',exact=True).click()
  assert await page.evaluate('state.clients[0].lastName')=='Martin'
  # Original commercial workflow remains operational.
  await page.evaluate("go('quotes')")
  await page.get_by_role('button',name='+ Nouveau devis').click()
  await page.locator('#productpick').fill('531')
  await page.get_by_role('button',name='Ajouter une ligne').click()
  assert await page.evaluate('draftLines.length')==0
  for ref,qty in [('1','2'),('2','3')]:
   await page.locator('#productpick').fill(ref)
   await page.get_by_role('button',name='Ajouter une ligne').click()
   n=await page.evaluate('draftLines.length')
   await page.locator(f'input[aria-label="Quantité ligne {n}"]').fill(qty)
  assert await page.evaluate('totals(draftLines).ht')==66
  assert await page.evaluate('totals(draftLines).ttc')==79.2
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function('state.quotes.length===1')
  await page.evaluate("changeDocument('quote',state.quotes[0].id,'Envoyé')")
  await page.wait_for_function("state.quotes[0].status==='Envoyé'")
  assert await page.evaluate('state.reminders.length')==1
  await page.evaluate("changeDocument('quote',state.quotes[0].id,'Accepté')")
  await page.wait_for_function("state.quotes[0].status==='Accepté'")
  await page.evaluate('convertQuote(state.quotes[0].id)')
  await page.wait_for_function('state.sales.length===1')
  await page.evaluate('convertQuote(state.quotes[0].id)')
  assert await page.evaluate('state.sales.length')==1
  assert await page.evaluate('selectedSales().length')==0
  await page.evaluate("changeDocument('sale',state.sales[0].id,'Validée')")
  await page.wait_for_function("state.sales[0].status==='Validée'")
  # Visible edit controls and historical price/name snapshots.
  await page.evaluate("go('products')")
  assert await page.get_by_role('button',name='Modifier',exact=True).count()==40
  await page.get_by_role('button',name='Modifier',exact=True).first.click()
  await page.locator('[name=price]').fill('99')
  await page.locator('[name=name]').fill('Produit corrigé')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function("state.products[0].price===99")
  assert await page.evaluate('totals(lines(state.sales[0])).ht')==66
  assert await page.evaluate('state.saleLines[0].name')!='Produit corrigé'
  await page.evaluate("editClient(state.clients[0].id)")
  await page.locator('[name=type]').select_option('Professionnel')
  await page.locator('[name=company]').fill('Atelier réel')
  await page.locator('[name=city]').fill('Nouvelle ville')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function("state.clients[0].company==='Atelier réel'")
  assert await page.evaluate('state.clients[0].id')==cid
  assert await page.evaluate('state.clients[0].number')=='CLI-000001'
  assert await page.evaluate('state.quotes[0].clientId')==cid
  assert await page.evaluate('state.sales[0].clientId')==cid
  # New documents must use the amended catalog, while old ones keep their snapshots.
  await page.evaluate("editDocument('quote',state.clients[0].id)")
  await page.locator('#productpick').fill('1')
  await page.get_by_role('button',name='Ajouter une ligne').click()
  assert await page.evaluate('draftLines[0].price')==99
  assert await page.evaluate('draftLines[0].name')=='Produit corrigé'
  await page.evaluate('closeDialog()')
  # Demo generate/replace/delete while retaining exact real records.
  await page.evaluate("go('settings')")
  page.on('dialog',lambda d:d.accept())
  await page.get_by_role('button',name='Générer des données de démonstration',exact=True).click()
  await page.wait_for_function('state.clients.length===41')
  assert await page.evaluate('state.products.length')==3283
  assert await page.evaluate('validateImport(state).schemaVersion')==4
  assert await page.evaluate("new Set(state.opportunities.filter(o=>o.isDemo).map(o=>o.stage)).size")==8
  assert await page.evaluate("new Set(state.sales.filter(o=>o.isDemo).map(o=>o.date.slice(0,7))).size")==6
  assert await page.evaluate("new Set(state.quotes.filter(o=>o.isDemo).map(o=>o.status)).size")==4
  demo_count=await page.evaluate('state.events.length')
  await page.get_by_role('button',name='Générer des données de démonstration',exact=True).click()
  await page.wait_for_function(f'state.events.length==={demo_count}')
  await page.wait_for_timeout(200)
  assert await page.evaluate('state.clients.length')==41
  assert await page.evaluate("new Set(state.clients.map(c=>c.number)).size")==41
  assert await page.evaluate("new Set(state.clients.filter(c=>c.isDemo).map(c=>c.demoBatch)).size")==1
  await page.get_by_role('button',name='Supprimer les données de démonstration',exact=True).click()
  await page.wait_for_function('state.clients.length===1')
  assert await page.evaluate('state.sales.length')==1
  assert await page.evaluate('state.quotes.length')==1
  assert await page.evaluate('state.clients[0].id')==cid
  # Demo data linked from a real interaction must survive removal.
  await page.get_by_role('button',name='Générer des données de démonstration',exact=True).click()
  await page.wait_for_function('state.clients.length===41')
  await page.evaluate("""async()=>{let c=state.clients.find(c=>c.isDemo);await commit(s=>s.interactions.push({id:uid(),clientId:c.id,note:'Échange réel à préserver',createdAt:now()}));} """)
  await page.get_by_role('button',name='Supprimer les données de démonstration',exact=True).click()
  await page.wait_for_function('state.clients.length===2')
  assert await page.evaluate("state.interactions.some(i=>i.note==='Échange réel à préserver')")
  assert await page.evaluate('validateImport(state).schemaVersion')==4
  # Catalog import merges with unchanged IDs, cannot remove products or alter history.
  await page.evaluate("""async()=>{let s={format:'fmt-catalog',version:1,products:[{...state.products[0],price:111,name:'Catalogue réimporté'}]};await commit(x=>mergeCatalog(x,s));} """)
  assert await page.evaluate('state.products[0].price')==111
  assert await page.evaluate('state.products.length')==3283
  assert await page.evaluate('totals(lines(state.sales.find(s=>!s.isDemo))).ht')==66
  assert await page.evaluate("""()=>{let s=structuredClone(state);try{mergeCatalog(s,{format:'fmt-catalog',version:1,products:[{...s.products[0],id:'new-id'}]});return false}catch{return true}}""")
  # Real export paths, captured as text rather than relying on managed download policies.
  await page.evaluate("window.savedDownload=download;window.captured=[];download=(text,name,type)=>captured.push({text,name,type});exportCatalog()")
  catalog=await page.evaluate('JSON.parse(captured[0].text)')
  assert len(catalog['products'])==3283 and catalog['products'][0]['price']==111
  await page.evaluate("go('clients');resetSearchFilters('clients');csvExport()")
  csv=await page.evaluate('captured.at(-1).text')
  assert 'postalCode' in csv and 'legacyAddress' in csv and 'owner' not in csv and 'CLI-000001' in csv
  # Full backup restoration through file input.
  await page.evaluate("go('settings')")
  await page.get_by_role('button',name='Exporter JSON',exact=True).click()
  backup=await page.evaluate('JSON.parse(captured.at(-1).text)')
  assert backup['schemaVersion']==4
  await page.locator('#restore').set_input_files({'name':'sauvegarde.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
  await page.wait_for_function("document.getElementById('toast').textContent==='Sauvegarde restaurée.'")
  # Restore a schema-1 backup: original technical IDs and references must remain.
  legacy=json.loads(json.dumps(backup));legacy['schemaVersion']=1;legacy.pop('clientSequence',None)
  for c in legacy['clients']:
   for k in ['number','street','postalCode','city','legacyAddress']:c.pop(k,None)
   c['address']='Adresse ancienne non décomposable';c['owner']='Ancien commercial'
  await page.locator('#restore').set_input_files({'name':'ancienne.json','mimeType':'application/json','buffer':json.dumps(legacy).encode()})
  await page.wait_for_function("state.clients[0].legacyAddress==='Adresse ancienne non décomposable'")
  assert await page.evaluate('state.clients[0].street')==''
  assert await page.evaluate('state.clients[0].postalCode')==''
  assert await page.evaluate('state.clients[0].id')==cid
  assert await page.evaluate("'owner' in state.clients[0]")==False
  assert await page.evaluate('state.sales[0].clientId')==cid
  # Reload while online (the tested interactions themselves required no network).
  await context.set_offline(False);await page.reload()
  await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  assert await page.evaluate('state.products[0].price')==111
  assert await page.evaluate('state.clients[0].legacyAddress')=='Adresse ancienne non décomposable'
  assert await page.evaluate('state.clients[0].phone')=='0612345678'
  await page.evaluate("editClient()")
  await page.locator('[name=lastName]').fill('Après restauration')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function('state.clients.length===3')
  assert await page.evaluate("new Set(state.clients.map(c=>c.number)).size")==3
  assert await page.evaluate('validateImport(state).schemaVersion')==4
  # Also exercise automatic startup migration, not only import migration.
  await page.evaluate('''async()=>{let old=structuredClone(state);old.schemaVersion=1;delete old.clientSequence;for(let c of old.clients){delete c.number;delete c.street;delete c.postalCode;delete c.city;delete c.legacyAddress;c.address='Ancienne adresse au démarrage';c.owner='Historique';}await persist(old);}''')
  await page.reload()
  await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  assert await page.evaluate('state.schemaVersion')==4
  assert await page.evaluate('state.clients[0].legacyAddress')=='Ancienne adresse au démarrage'
  assert await page.evaluate('state.sales[0].clientId')==cid
  for v in ['analytics','clients','products','pipeline','quotes','sales','settings']:
   await page.evaluate(f"go('{v}')")
   assert await page.locator('#content h1').count()==1
  assert not errors,errors
  assert all(u.startswith('http://127.0.0.1:8765/index.html') or u.startswith('data:') for u in requests),requests
  await page.evaluate("go('analytics')");await page.screenshot(path='/tmp/fmt-v2-desktop.png',full_page=True)
  await page.set_viewport_size({'width':768,'height':1024});await page.screenshot(path='/tmp/fmt-v2-tablet.png',full_page=True)
  # Test direct file mode separately; report managed policy denial without bypassing it.
  direct=await context.new_page()
  try:
   await direct.goto((Path(__file__).resolve().parents[1]/'index.html').as_uri(),timeout=10000)
   await direct.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for(timeout=10000)
   print('PASS ouverture directe file://')
  except Error as e:print('LIMITATION file:// dans ce navigateur géré :',str(e).splitlines()[0])
  print('PASS régression v4 : 11 scénarios métier, régression devis/vente, migration v1, démo protégée et remplaçable, catalogue export/import et persistance, fonctionnement hors réseau. Aucune erreur JavaScript.')
  await browser.close()

asyncio.run(main())
