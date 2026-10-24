"""Recette complémentaire v5 : filtres combinés, dates, URL, migration, performance."""
import asyncio, json, time
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=await browser.new_context(viewport={'width':1440,'height':1050})
  page=await context.new_page();errors=[];requests=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('request',lambda r:requests.append(r.url))
  await page.goto('http://127.0.0.1:8765/index.html')
  await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  await context.set_offline(True)
  # Seed synthetic edge cases with stable identities and controlled historical dates.
  await page.evaluate('''async()=>{await commit(s=>{s.settings.traceability=true;for(let i=0;i<5;i++)s.clients.push({id:'test-'+i,number:nextClientNumber(s),firstName:'Élodie',lastName:'Test '+i,type:i<3?'Professionnel':'Particulier',company:i<3?'Atelier exemple':'',phone:'06 00 XX XX '+i,email:'test'+i+'@example.invalid',street:i<3?'12 rue de la République':'3 chemin du Test',postalCode:i===1?'84001':i<3?'84000':'01000',city:i<3?'Avignon':i===3?'Orange':'Bourg-en-Bresse',legacyAddress:'',origin:'Physique',notes:'',siret:'',createdAt:'2026-01-0'+(i+1)+'T10:00:00Z',updatedAt:i===4?'':'2026-02-0'+(5-i)+'T11:30:00Z'});})}''')
  await page.evaluate("go('clients')")
  await page.locator('#main-search').fill('elodie')
  assert await page.locator('#list tbody tr').count()==5
  await page.locator('#toggle-filters').click()
  await page.locator('[data-filter-key=type]').select_option('Professionnel')
  await page.locator('#facet-cities summary').click()
  await page.locator('#facet-cities input[type=search]').fill('avig')
  await page.locator('#facet-cities input[type=checkbox]').check()
  await page.locator('[data-filter-key=postalCode]').fill('84')
  assert await page.locator('#list tbody tr').count()==3
  assert '3 client' in await page.locator('#result-count').inner_text()
  assert not await page.locator('[data-filter-key=address]').count()
  await page.locator('[data-filter-key=dateFrom]').fill('2026-01-02')
  await page.locator('[data-filter-key=dateTo]').fill('2026-01-03')
  assert await page.locator('#list tbody tr').count()==2
  await page.locator('#list').get_by_role('button',name='Création',exact=False).click()
  assert 'Test 1' in await page.locator('#list tbody tr').first.inner_text()
  await page.locator('#list').get_by_role('button',name='Dernière modification',exact=False).click()
  assert 'Test 2' in await page.locator('#list tbody tr').first.inner_text()
  await page.locator('[data-filter-key=dateType]').select_option('updatedAt')
  assert await page.locator('[data-filter-key=dateFrom]').input_value()=='2026-01-02'
  await page.locator('[data-filter-key=dateFrom]').fill('2026-02-03')
  await page.locator('[data-filter-key=dateTo]').fill('2026-02-03')
  assert await page.locator('#list tbody tr').count()==1
  await page.locator('[data-filter-key=dateType]').select_option('createdAt')
  await page.locator('[data-filter-key=dateFrom]').fill('2026-01-02')
  await page.locator('[data-filter-key=dateTo]').fill('2026-01-03')
  await page.get_by_role('button',name='Retirer Date de début : 2026-01-02',exact=True).click()
  assert await page.locator('#list tbody tr').count()==3
  await page.get_by_role('button',name='Réinitialiser les filtres',exact=True).click()
  assert await page.locator('#list tbody tr').count()==5
  await page.locator('#list').get_by_role('button',name='Dernière modification',exact=False).click()
  assert 'Test 0' in await page.locator('#list tbody tr').first.inner_text()
  assert '—' in await page.locator('#list tbody tr').last.inner_text()
  # Multiple cities, dynamic values and postal-prefix semantics.
  await page.locator('#facet-cities summary').click()
  await page.locator('#facet-cities input[type=search]').fill('')
  await page.locator('#facet-cities input[value=Avignon]').check()
  await page.locator('#facet-cities input[value=Orange]').check()
  assert await page.locator('#list tbody tr').count()==4
  await page.evaluate("resetSearchFilters('clients');editClient('test-0')")
  old=await page.evaluate("client('test-0').updatedAt")
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_timeout(100)
  assert await page.evaluate("client('test-0').updatedAt")==old  # saving without changes
  await page.evaluate("editClient('test-0')")
  await page.locator('[name=city]').fill('Nouvelle ville')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function("client('test-0').city==='Nouvelle ville'")
  assert await page.evaluate("client('test-0').updatedAt")!=old
  assert await page.locator('#facet-cities input[value="Nouvelle ville"]').count()==1
  await page.evaluate("go('products')")
  await page.locator('#main-search').fill('TRAVERTIN BEIGE')
  assert await page.evaluate('filtered().length')>20
  assert await page.evaluate("filtered().every(p=>matches(p.name,'travertin beige'))")
  await page.locator('#toggle-filters').click()
  await page.locator('#facet-thickness summary').click()
  await page.locator('#facet-thickness input[type=search]').fill('1,2')
  await page.locator('#facet-thickness input[value="1,2 cm"]').check()
  await page.locator('#facet-color summary').click()
  await page.locator('#facet-color input[type=search]').fill('beige')
  await page.locator('#facet-color input[value="Beige Nuance"]').check()
  await page.locator('[data-filter-key=minPrice]').fill('20')
  await page.locator('[data-filter-key=maxPrice]').fill('40')
  assert await page.evaluate('filtered().length')>0
  assert await page.evaluate("filtered().every(p=>p.price>=20&&p.price<=40&&p.color==='Beige Nuance'&&p.thickness==='1,2 cm')")
  fmt=await page.evaluate('filtered()[0].format')
  await page.locator('#facet-format summary').click()
  await page.locator('#facet-format input[type=search]').fill(fmt)
  await page.locator('#facet-format').get_by_role('checkbox',name=fmt,exact=True).check()
  assert await page.evaluate('filtered().every(p=>p.format===productFilters.format[0])')
  await page.locator('#list').get_by_role('button',name='Prix HT',exact=False).click()
  await page.locator('#list').get_by_role('button',name='Prix HT',exact=False).click()
  assert await page.evaluate('filtered().every((p,i,a)=>!i||a[i-1].price>=p.price)')
  await page.locator('[data-filter-key=minPrice]').fill('99')
  assert await page.evaluate('Number(productFilters.minPrice)<=Number(productFilters.maxPrice)')
  await page.get_by_role('button',name='Réinitialiser les filtres',exact=True).click()
  assert await page.evaluate('filtered().length')==3283
  await page.locator('#main-search').fill('mosaique')
  assert await page.evaluate('filtered().length')>0
  assert await page.evaluate("filtered().every(p=>norm(p.name).includes('mosaique'))")
  await page.get_by_role('button',name='Réinitialiser les filtres',exact=True).click()
  # Public links are empty at migration, strictly HTTP(S), safely rendered and persisted.
  assert await page.evaluate("state.products.every(p=>p.url==='')")
  await page.evaluate("editProduct('P-5')")
  await page.locator('[name=url]').fill('javascript:alert(1)')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  assert 'lien web valide' in await page.locator('#toast').inner_text()
  await page.locator('[name=url]').fill('https://example.invalid/produit/travertin')
  await page.locator('[name=category]').fill('Pierres de test')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function("state.products[0].category==='Pierres de test'")
  await page.evaluate("productDetail('P-5')")
  link=page.get_by_role('link',name='Voir sur le site',exact=False)
  assert await link.get_attribute('target')=='_blank'
  assert await link.get_attribute('rel')=='noopener noreferrer'
  assert await link.get_attribute('href')=='https://example.invalid/produit/travertin'
  # Test opening in a new tab without actually contacting any external server.
  await context.route('https://example.invalid/**',lambda route:route.fulfill(status=200,content_type='text/html',body='Page produit de recette'))
  async with context.expect_page() as popup:
   await link.click()
  newpage=await popup.value;await newpage.wait_for_load_state();assert 'Page produit' in await newpage.locator('body').inner_text();await newpage.close()
  await page.evaluate('closeDialog()')
  # Current fields survive complete and catalog-only exports/imports. Legacy catalog leaves URL intact.
  await page.evaluate("window.captured=[];download=(text,name,type)=>captured.push({text,name,type});exportCatalog()")
  exported=await page.evaluate('JSON.parse(captured[0].text)')
  assert exported['version']==3 and exported['products'][0]['url'].startswith('https:')
  assert await page.evaluate("""()=>{const s=structuredClone(state),p={...s.products[0]};delete p.url;delete p.category;mergeCatalog(s,{format:'fmt-catalog',version:1,products:[p]});return s.products[0].url===state.products[0].url} """)
  assert await page.evaluate("""()=>{try{let s=structuredClone(state);s.products[0].url='data:text/html,x';validateImport(s);return false}catch{return true}}""")
  # Missing version-2 timestamps stay missing; all documents and stable IDs survive migration.
  assert await page.evaluate("""()=>{let s=structuredClone(state);s.schemaVersion=2;for(const p of s.products){delete p.url;delete p.category}delete s.clients[0].updatedAt;let m=validateImport(s);return m.schemaVersion===5&&m.clients[0].updatedAt===''&&m.products[0].url===''&&m.clients[0].id===s.clients[0].id} """)
  # Thousands of clients: use the same filtering and rendering path, check exact results and pagination.
  perf=await page.evaluate("""()=>{const original=state.clients;state.clients=Array.from({length:10000},(_,i)=>({...original[0],id:'PERF-'+i,number:'CLI-'+String(100000+i),lastName:'Client '+i,city:i%2?'Avignon':'Orange',postalCode:i%2?'84000':'84100'}));view='clients';query='client';clientFilters=blankClientFilters();clientFilters.type='Professionnel';clientFilters.cities=['Avignon'];clientFilters.postalCode='84';const start=performance.now();clientsPage();const elapsed=performance.now()-start,count=filtered().length;state.clients=original;clientFilters=blankClientFilters();query='';return {elapsed,count}} """)
  assert perf['count']==5000,perf
  print('10 000 clients, filtres + rendu paginé :',round(perf['elapsed']), 'ms ; 5 000 résultats exacts.')
  # Test persistence with reload, then capture all main responsive layouts.
  await context.set_offline(False);await page.reload()
  await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  assert await page.evaluate('state.products[0].url')=='https://example.invalid/produit/travertin'
  await page.evaluate("go('products');productPanelOpen=true;productsPage()")
  await page.screenshot(path='/tmp/fm84-catalogue-v3.png',full_page=True)
  await page.set_viewport_size({'width':768,'height':1024});await page.screenshot(path='/tmp/fm84-tablet-v3.png',full_page=True)
  assert not errors,errors
  assert all(u.startswith('http://127.0.0.1:8765/') or u.startswith('https://example.invalid/') or u.startswith('data:') for u in requests),requests
  print('PASS v5 filtres : filtres cumulés clients et produits, multi-villes, accents/multi-mots, dates/tri, sauvegarde sans changement, dates réellement modifiées, URL validées et nouvel onglet, export/import, migration v2, persistance. Zéro erreur JavaScript.')
  await browser.close()
if __name__=='__main__':asyncio.run(main())
