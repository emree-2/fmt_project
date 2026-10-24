"""Recette fonctionnelle v4. Outil de développement facultatif, jamais requis par le CRM."""
import asyncio, json, base64, io
from PIL import Image
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=await b.new_context(viewport={'width':1440,'height':1100});page=await context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto('http://127.0.0.1:8765/index.html');await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();await context.set_offline(True)
  assert await page.evaluate('state.schemaVersion')==4
  assert not await page.get_by_text('Performance par commercial',exact=True).count()
  assert await page.locator('#nav button').count()==5 and await page.locator('#adminnav button').count()==2
  bottom=await page.locator('#adminnav').bounding_box();assert bottom['y']>700,bottom
  # Professional / personal toggles, validation and leading-zero SIRET.
  await page.evaluate('editClient()');assert await page.locator('[name=siret]').is_disabled();assert await page.locator('[name=company]').is_visible()
  await page.locator('[name=type]').select_option('Professionnel');await page.locator('[name=lastName]').fill('Test Global');await page.locator('[name=firstName]').fill('Élodie');await page.locator('[name=company]').fill('Atelier exemple');await page.locator('[name=siret]').fill('123')
  await page.get_by_role('button',name='Enregistrer',exact=True).click();assert '14 chiffres' in await page.locator('#toast').inner_text()
  await page.locator('[name=siret]').fill('001 234 567 89012');await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.clients.length===1')
  cid=await page.evaluate('state.clients[0].id');assert await page.evaluate('state.clients[0].siret')=='00123456789012'
  created=await page.evaluate('state.clients[0].createdAt');await page.evaluate('clientDetail(state.clients[0].id)');assert '001 234 567 89012' in await page.locator('#dialogbody').inner_text();await page.evaluate('closeDialog()')
  # Product dates and automatic numeric reference across the entire catalog.
  await page.evaluate("go('products');editProduct()")
  assert await page.locator('[name=ref]').input_value()==await page.evaluate('proposeProductReference()')
  await page.locator('[name=name]').fill('Échantillon Test Global');await page.locator('[name=unit]').fill('Pièce');await page.locator('[name=price]').fill('25');await page.locator('[name=url]').fill('www.example.invalid/produit')
  await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.products.length===3284')
  pid=await page.evaluate('state.products.at(-1).id');pc=await page.evaluate('state.products.at(-1).createdAt');assert pc and pc==await page.evaluate('state.products.at(-1).updatedAt');assert await page.evaluate('state.products.at(-1).url')=='https://www.example.invalid/produit'
  await page.evaluate(f"editProduct('{pid}')");await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_timeout(100);assert await page.evaluate('state.products.at(-1).updatedAt')==pc
  await page.evaluate(f"editProduct('{pid}')");await page.locator('[name=price]').fill('40');await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.products.at(-1).price===40');assert await page.evaluate('state.products.at(-1).createdAt')==pc;assert await page.evaluate('state.products.at(-1).updatedAt')!=pc
  await page.evaluate("productDetail('P-5')");assert 'Import historique' in await page.locator('#dialogbody').inner_text();await page.evaluate('closeDialog()')
  # A disabled high numeric reference counts; alphabetic references do not.
  assert await page.evaluate("proposeProductReference([{ref:'2',active:true},{ref:'010',active:false},{ref:'ABC-999'}])")=='11'
  await page.evaluate('editProduct()');await page.locator('[name=ref]').fill('1');await page.locator('[name=name]').fill('Doublon');await page.locator('[name=unit]').fill('Pièce');await page.get_by_role('button',name='Enregistrer',exact=True).click();assert 'Référence libre' in await page.locator('#toast').inner_text();assert await page.evaluate('state.products.length')==3284;await page.evaluate('closeDialog()')
  # Header sorting: natural refs, numeric prices, all results before pagination, keyboard access.
  ids=await page.evaluate('state.products.map(p=>p.id)')
  await page.locator('#list th').get_by_role('button',name='Référence',exact=False).click();assert (await page.locator('#list tbody tr td').first.inner_text()).startswith('1')
  await page.locator('#list th').get_by_role('button',name='Référence',exact=False).click();assert await page.evaluate('filtered()[0].ref')==await page.evaluate('proposeProductReference().replace(/.*/,String(BigInt(proposeProductReference())-1n))')
  await page.get_by_role('button',name='→',exact=True).click();assert await page.evaluate('page')==1;assert await page.locator('#list th[aria-sort=descending]').count()==1
  await page.locator('#list th').get_by_role('button',name='Prix HT',exact=False).focus();await page.keyboard.press('Enter');assert await page.evaluate('filtered().every((p,i,a)=>!i||p.price===null||a[i-1].price===null||a[i-1].price<=p.price)')
  assert await page.evaluate('document.activeElement.dataset.sortKey')=='price'
  assert ids==await page.evaluate('state.products.map(p=>p.id)')
  assert not await page.locator('#list th').get_by_role('button',name='Actions',exact=False).count()
  # Two handles, both directions and no crossing; state survives other filters/pagination.
  await page.locator('#toggle-filters').click();await page.locator('#price-lower').focus();await page.keyboard.press('ArrowRight');assert float(await page.locator('[data-filter-key=minPrice]').input_value())==float(await page.locator('#price-lower').input_value());await page.locator('[data-filter-key=minPrice]').fill('20');await page.locator('[data-filter-key=maxPrice]').fill('100');assert float(await page.locator('#price-lower').input_value())==20
  await page.locator('#price-upper').fill('80');await page.locator('#price-upper').dispatch_event('input');assert await page.locator('[data-filter-key=maxPrice]').input_value()=='80'
  await page.locator('[data-filter-key=minPrice]').fill('200');assert await page.locator('[data-filter-key=minPrice]').input_value()=='80'
  await page.locator('[data-filter-key=minPrice]').fill('20');await page.locator('[data-filter-key=name]').fill('travertin beige');assert await page.evaluate('productFilters.minPrice')=='20';assert await page.get_by_text('Nom du produit',exact=True).count()==1
  await page.evaluate("resetSearchFilters('products')")
  # Related fixtures to verify every universal-search category and typed amount/date/status sorting.
  await page.evaluate('''async()=>{await commit(s=>{const clientId=s.clients[0].id,p=s.products[0];s.opportunities.push({id:'OP-TEST',clientId,title:'Dossier Test Global',owner:'',amount:200,stage:'Qualification',notes:'',followUp:'2026-11-01',createdAt:now(),updatedAt:now()});for(let i=0;i<2;i++){s.quotes.push({id:'Q-TEST-'+i,clientId,kind:'quote',number:'DEV-TEST-'+i,date:i?'2026-02-01':'2026-01-01',status:i?'Accepté':'Envoyé',owner:'',channel:'Physique',createdAt:now(),updatedAt:now()});s.sales.push({id:'S-TEST-'+i,clientId,kind:'sale',number:'FAC-TEST-'+i,date:i?'2026-02-01':'2026-01-01',status:'Validée',owner:'',channel:'Physique',payment:'À payer',delivery:'À livrer',createdAt:now(),updatedAt:now()});for(const [collection,prefix] of [['quoteLines','Q'],['saleLines','S']])s[collection].push({id:prefix+'-LINE-'+i,documentId:prefix+'-TEST-'+i,productId:p.id,ref:p.ref,name:p.name,unit:p.unit,quantity:1,price:i?1000:66,vat:20});}})}''')
  await page.locator('#global').fill('test global');await page.locator('#global-results').wait_for();assert await page.locator('#global-results section').count()==5
  await page.locator('#global').press('ArrowDown');assert await page.locator('#global').get_attribute('aria-activedescendant')=='global-item-0';await page.locator('#global').press('Enter');assert await page.locator('#dialog').is_visible();assert 'Test Global' in await page.locator('#dialogbody').inner_text();await page.evaluate('closeDialog()')
  for term,heading in [('echantillon','Fiche produit'),('Dossier Test','Modifier l’opportunité'),('DEV-TEST-1','DEV-TEST-1'),('FAC-TEST-1','FAC-TEST-1')]:
   await page.locator('#global').fill(term);await page.locator('#global').press('ArrowDown');await page.locator('#global').press('Enter');assert heading in await page.locator('#dialogtitle').inner_text();await page.evaluate('closeDialog()')
  await page.locator('#global').fill('travertin');initial=await page.locator('.global-item').count();await page.get_by_role('button',name='Voir davantage',exact=False).first.click();assert await page.locator('.global-item').count()>initial
  await page.locator('#global').press('Escape');assert await page.locator('#global-results').is_hidden();await page.locator('#global').fill('travertin');await page.locator('#crumb').click();assert await page.locator('#global-results').is_hidden()
  for route in ['quotes','sales']:
   await page.evaluate(f"go('{route}')");await page.locator('#list th').get_by_role('button',name='Total HT',exact=False).click();assert '66,00' in await page.locator('#list tbody tr').first.inner_text();await page.locator('#list th').get_by_role('button',name='Total HT',exact=False).click();assert '1\u202f000,00' in await page.locator('#list tbody tr').first.inner_text() or '1\xa0000,00' in await page.locator('#list tbody tr').first.inner_text()
  await page.evaluate("go('pipeline');kanban=false;pipelinePage()");assert await page.locator('table[data-table=opportunities] th button').count()==5
  await page.evaluate("go('analytics')");assert not await page.get_by_text('Performance par commercial',exact=True).count();await page.locator('table[data-table=top-products] th button').first.click()
  # JSON import preview: add + update, no deletes, immutable ID/date and preserved relationships.
  await page.evaluate("go('clients')");number=await page.evaluate('state.clients[0].number')
  payload={'format':'fmt-clients','version':1,'clients':[{'id':cid,'number':number,'city':'Avignon','postalCode':'08400','createdAt':'1990-01-01T00:00:00Z'},{'lastName':'Nouveau importé','firstName':'Jean','type':'Professionnel','siret':'00000000000001','postalCode':'01000','notes':'Première ligne;\n"Deuxième"'}]}
  await page.locator('#client-import').set_input_files({'name':'clients.json','mimeType':'application/json','buffer':json.dumps(payload).encode()});assert '1 ajout(s)' in await page.locator('#dialogbody').inner_text();assert await page.evaluate('state.clients.length')==1
  await page.get_by_role('button',name='Confirmer l’import',exact=True).click();await page.wait_for_function('state.clients.length===2');assert await page.evaluate('state.clients[0].id')==cid;assert await page.evaluate('state.clients[0].createdAt')==created;assert await page.evaluate('state.quotes[0].clientId')==cid;assert await page.evaluate('state.opportunities[0].clientId')==cid
  assert await page.evaluate('state.clients[0].postalCode')=='08400'
  await page.evaluate("window.captured=[];download=(text,name,type)=>captured.push({text,name,type});exportClients('all');csvExport('all')")
  exports=await page.evaluate('captured');assert json.loads(exports[0]['text'])['clients'][0]['siret']=='00123456789012';assert 'siret' in exports[1]['text']
  assert await page.evaluate('parseClientCSV(captured[1].text)[1].notes')=='Première ligne;\n"Deuxième"'
  # CSV with stable readable number, leading zeros, and no other columns overwrites only specified fields.
  csv='number;city;postalCode\r\n'+number+';Orange;00100\r\n'
  await page.locator('#client-import').set_input_files({'name':'clients.csv','mimeType':'text/csv','buffer':csv.encode()});await page.get_by_role('button',name='Confirmer l’import',exact=True).click();await page.wait_for_function("state.clients[0].city==='Orange'");assert await page.evaluate('state.clients[0].postalCode')=='00100';assert await page.evaluate('state.clients[0].siret')=='00123456789012'
  # Invalid or duplicated IDs block the whole import before persistence.
  bad={'format':'fmt-clients','version':1,'clients':[{'id':cid,'number':number,'city':'Jamais sauvegardée'},{'id':cid,'number':number,'siret':'123'}]}
  await page.locator('#client-import').set_input_files({'name':'invalid.json','mimeType':'application/json','buffer':json.dumps(bad).encode()});assert await page.get_by_role('button',name='Confirmer l’import',exact=True).is_disabled();assert await page.evaluate('state.clients[0].city')=='Orange';await page.get_by_role('button',name='Annuler',exact=True).click()
  assert await page.evaluate('''()=>{const n='CLI-'+String(state.clientSequence+1).padStart(6,'0');return planClientImport(state,[{lastName:'Premier'},{number:n,lastName:'Collision implicite'}]).errors.length>0}''')
  assert await page.evaluate('''()=>{const s=structuredClone(state),p=s.products.at(-1),before=p.updatedAt,created=p.createdAt;mergeCatalog(s,{format:'fmt-catalog',version:3,products:[{...p,createdAt:'1990-01-01T00:00:00Z'}]});return s.products.at(-1).createdAt===created&&s.products.at(-1).updatedAt===before}''')
  # Personal client fields stay visible, greyed and empty after save.
  await page.evaluate(f"editClient('{cid}')");await page.locator('[name=type]').select_option('Particulier');assert await page.locator('[name=siret]').is_visible() and await page.locator('[name=siret]').is_disabled();assert await page.locator('[name=company]').is_disabled();await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function("state.clients[0].type==='Particulier'");assert await page.evaluate('state.clients[0].siret')=='' and await page.evaluate('state.clients[0].company')==''
  # Migration from v3 preserves historical product dates that exist and leaves unknowns blank.
  assert await page.evaluate("""()=>{let s=structuredClone(state);s.schemaVersion=3;delete s.clients[0].siret;delete s.products[0].createdAt;delete s.products[0].updatedAt;const m=validateImport(s);return m.schemaVersion===4&&m.clients[0].id===s.clients[0].id&&m.products[0].createdAt===''&&m.products[0].updatedAt===''&&m.clients[0].siret===''}""")
  # Optional image integration/export is tested with a synthetic fixture, not presented as the official logo.
  buf=io.BytesIO();Image.new('RGB',(16,10),'white').save(buf,format='PNG')
  await page.evaluate("go('settings')");await page.get_by_label('Choisir le logo officiel').set_input_files({'name':'fixture.png','mimeType':'image/png','buffer':buf.getvalue()});await page.wait_for_function('!!state.settings.logoDataURI');assert await page.locator('#brand img').get_attribute('src')==await page.evaluate('state.settings.logoDataURI')
  await page.evaluate('exportHTMLWithLogo()');html=await page.evaluate('captured.at(-1).text');assert 'id="embedded-logo"' in html and base64.b64encode(buf.getvalue()).decode() in html
  isolated=await b.new_context();await isolated.route('http://single-file.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));one=await isolated.new_page();one.on('pageerror',lambda e:errors.append(str(e)));await one.goto('http://single-file.test/index.html');await one.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await one.locator('#brand img').evaluate('(i)=>i.naturalWidth')==16;assert await one.evaluate('state.clients.length')==0;await isolated.close()
  # Reload and full backup validation; inspect current responsive UI.
  await context.set_offline(False);await page.reload();await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await page.evaluate('state.clients[0].postalCode')=='00100';assert await page.evaluate('state.products.at(-1).createdAt')==pc;assert await page.evaluate('validateImport(state).schemaVersion')==4
  await page.evaluate("go('products');productPanelOpen=true;productsPage()");await page.screenshot(path='/tmp/fm84-v4-desktop.png');await page.set_viewport_size({'width':768,'height':1024});await page.screenshot(path='/tmp/fm84-v4-tablet.png')
  assert not errors,errors
  print('PASS v4 : dates produit, référence proposée/conflit, SIRET, imports JSON/CSV et aperçu bloquant, liens préservés, tris typés avant pagination, slider synchronisé, recherche universelle et clavier, menu bas, KPI commercial retiré, migration et persistance, HTML autonome avec image embarquée de recette.')
  await b.close()
asyncio.run(main())
