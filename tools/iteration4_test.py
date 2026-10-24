"""Régression administration, adaptée au modèle V5 (anciens parcours remplacés)."""
import asyncio,json,io,base64
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright,Error
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=await browser.new_context(viewport={'width':1440,'height':1000});page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
  await page.goto('http://127.0.0.1:8765/index.html');await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();await context.set_offline(True)
  assert await page.evaluate('state.products.length')==3283
  await page.evaluate("go('clients');editClient()")
  await page.locator('[name=lastName]').fill('Administration privée');await page.locator('[name=firstName]').fill('Alice');await page.locator('[name=type]').select_option('Professionnel');await page.locator('[name=company]').fill('Atelier fictif');await page.locator('[name=siret]').fill('00123456789012');await page.locator('[name=postalCode]').fill('01000');await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.clients.length===1')
  cid=await page.evaluate('state.clients[0].id');number=await page.evaluate('state.clients[0].number');creation=await page.evaluate('state.clients[0].createdAt')
  await page.evaluate(f"editOpportunity(null,'{cid}')");await page.locator('[name=title]').fill('Projet administratif');await page.get_by_role('button',name='+ Ajouter une ligne produit',exact=True).click();await page.locator('#line-product-0').fill('1');await page.locator('#line-product-0').press('Enter');await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.opportunities.length===1');oid=await page.evaluate('state.opportunities[0].id')
  await page.get_by_role('button',name='Générer un devis',exact=True).click();await page.get_by_role('button',name='Enregistrer et prévisualiser',exact=True).click();await page.wait_for_function('state.quotes.length===1');await page.evaluate("closeDialog();go('clients')")
  data={'format':'fmt-clients','version':1,'clients':[{'id':cid,'number':number,'city':'Avignon','postalCode':'08400','createdAt':'1990-01-01'},{'lastName':'Importé','type':'Professionnel','siret':'00000000000001','notes':'Ligne 1;\n"Ligne 2"'}]}
  await page.locator('#client-import').set_input_files({'name':'clients.json','mimeType':'application/json','buffer':json.dumps(data).encode()});assert await page.evaluate('state.clients.length')==1;await page.get_by_role('button',name='Confirmer l’import',exact=True).click();await page.wait_for_function('state.clients.length===2')
  assert await page.evaluate('state.clients[0].createdAt')==creation;assert await page.evaluate('state.quotes[0].clientId')==cid;assert await page.evaluate('state.opportunities[0].clientId')==cid
  await page.evaluate("window.captured=[];download=(text,name,type)=>{captured.push({text,name,type})};exportClients('all');csvExport('all')")
  exports=await page.evaluate('captured');assert json.loads(exports[0]['text'])['clients'][0]['siret']=='00123456789012';assert await page.evaluate('parseClientCSV(captured[1].text)[1].notes')=='Ligne 1;\n"Ligne 2"'
  csv='number;city;postalCode\r\n'+number+';Orange;00100\r\n';await page.locator('#client-import').set_input_files({'name':'clients.csv','mimeType':'text/csv','buffer':csv.encode()});await page.get_by_role('button',name='Confirmer l’import',exact=True).click();await page.wait_for_function("state.clients[0].city==='Orange'");assert await page.evaluate('state.clients[0].postalCode')=='00100'
  assert await page.evaluate('''()=>{const n='CLI-'+String(state.clientSequence+1).padStart(6,'0');return planClientImport(state,[{lastName:'Premier'},{number:n,lastName:'Collision'}]).errors.length>0}''')
  bad={'format':'fmt-clients','version':1,'clients':[{'id':cid,'number':number,'city':'Jamais appliqué'},{'id':cid,'number':number}]};await page.locator('#client-import').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad).encode()});assert await page.get_by_role('button',name='Confirmer l’import',exact=True).is_disabled();await page.get_by_role('button',name='Annuler',exact=True).click();assert await page.evaluate('state.clients[0].city')=='Orange'
  await page.evaluate(f"editClient('{cid}')");await page.locator('[name=type]').select_option('Particulier');assert await page.locator('[name=siret]').is_visible() and await page.locator('[name=siret]').is_disabled();await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function("state.clients[0].type==='Particulier'");assert await page.evaluate('state.clients[0].siret')==''
  await page.evaluate("go('products');editProduct()")
  proposed=await page.locator('[name=ref]').input_value();assert proposed==await page.evaluate('proposeProductReference()');await page.locator('[name=name]').fill('Produit administratif');await page.locator('select[name=unit]').select_option('Pièce');await page.locator('[name=price]').fill('10');await page.locator('[name=url]').fill('www.example.invalid/article');await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.products.length===3284')
  pid=await page.evaluate('state.products.at(-1).id');created=await page.evaluate('state.products.at(-1).createdAt');assert created==await page.evaluate('state.products.at(-1).updatedAt');assert await page.evaluate('state.products.at(-1).url')=='https://www.example.invalid/article'
  await page.evaluate(f"editProduct('{pid}')");await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_timeout(100);assert await page.evaluate('state.products.at(-1).updatedAt')==created
  await page.evaluate(f"editProduct('{pid}')");await page.locator('[name=price]').fill('20');await page.get_by_role('button',name='Enregistrer',exact=True).click();await page.wait_for_function('state.products.at(-1).price===20');assert await page.evaluate('state.products.at(-1).createdAt')==created
  assert await page.evaluate("proposeProductReference([{ref:'2'},{ref:'010',active:false},{ref:'ABC-999'}])")=='11'
  assert await page.evaluate('''()=>{const s=structuredClone(state),p=s.products.at(-1),before=p.updatedAt;mergeCatalog(s,{format:'fmt-catalog',version:3,products:[{...p,createdAt:'1990-01-01'}]});return s.products.at(-1).createdAt===p.createdAt&&s.products.at(-1).updatedAt===before}''')
  # Sorting is presentation only, before the 40-row page boundary.
  ids=await page.evaluate('state.products.map(p=>p.id)');await page.locator('#list th').get_by_role('button',name='Référence',exact=False).click();await page.locator('#list th').get_by_role('button',name='Référence',exact=False).click();assert await page.evaluate('filtered()[0].ref')==proposed;await page.get_by_role('button',name='→',exact=True).click();assert await page.evaluate('page')==1;assert ids==await page.evaluate('state.products.map(p=>p.id)')
  # Portable HTML clears any printed private content, not just the current screen.
  await page.evaluate("go('settings')");out=io.BytesIO();Image.new('RGB',(16,10),'white').save(out,format='PNG');await page.get_by_label('Choisir le logo officiel').set_input_files({'name':'fixture.png','mimeType':'image/png','buffer':out.getvalue()});await page.wait_for_function('!!state.settings.logoDataURI')
  await page.evaluate("document.querySelector('#print-root').innerHTML='CLIENT_PRIVATE_SENTINEL';document.querySelector('#dialogtitle').textContent='CLIENT_PRIVATE_SENTINEL';exportHTMLWithLogo()")
  html=await page.evaluate('captured.at(-1).text');assert 'CLIENT_PRIVATE_SENTINEL' not in html and 'Administration privée' not in html;assert base64.b64encode(out.getvalue()).decode() in html
  isolated=await browser.new_context();await isolated.route('http://single-file.test/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));one=await isolated.new_page();one.on('pageerror',lambda e:errors.append(str(e)));await one.goto('http://single-file.test/index.html');await one.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await one.evaluate('state.clients.length')==0;assert await one.locator('#brand img').evaluate('(i)=>i.naturalWidth')==16;await isolated.close()
  assert await page.evaluate('validateImport(state).schemaVersion')==6
  await context.set_offline(False);await page.reload();await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await page.evaluate('state.products.at(-1).createdAt')==created
  direct=await context.new_page()
  try:
   await direct.goto((Path(__file__).resolve().parents[1]/'index.html').as_uri(),timeout=10000);await direct.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for(timeout=10000);print('PASS file://')
  except Error as e:print('LIMITATION file:// :',str(e).splitlines()[0])
  assert not errors,errors
  print('PASS administration V5 : import/export JSON/CSV avec aperçu, SIRET, données et relations préservées, catalogue/date/référence, tri global, HTML autonome avec image de recette et sans données privées.')
  await browser.close()
if __name__=='__main__':asyncio.run(main())
