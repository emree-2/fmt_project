"""Migration réelle d’un état V4, lecture des sauvegardes V1–V4, pas de paiement inventé."""
import asyncio,json,subprocess
from playwright.async_api import async_playwright
async def main():
 old_html=subprocess.check_output(['git','show','3f4bb1f:index.html'],cwd='/workspace/fmt_project').decode()
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=await b.new_context();await ctx.route('http://127.0.0.1:8765/legacy.html',lambda r:r.fulfill(status=200,content_type='text/html',body=old_html));pg=await ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('dialog',lambda d:d.accept())
  await pg.goto('http://127.0.0.1:8765/legacy.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  await pg.evaluate('''async()=>{await commit(s=>{s.clientSequence=1;s.clients.push({id:'C-LEGACY',number:'CLI-000001',firstName:'Jean',lastName:'Historique',type:'Particulier',company:'',siret:'',phone:'0600000000',email:'test@example.invalid',street:'12 rue Ancienne',postalCode:'01000',city:'Ville',legacyAddress:'',origin:'Physique',notes:'À conserver',createdAt:'2025-01-01T10:00:00Z',updatedAt:'2026-01-01T11:00:00Z'});s.opportunities.push({id:'OP-LEGACY',clientId:'C-LEGACY',title:'Ancien projet',stage:'Accepté',amount:120,owner:'',notes:'Historique',followUp:'',createdAt:'2025-01-02T10:00:00Z',updatedAt:'2026-01-02T10:00:00Z'});s.quotes.push({id:'Q-LEGACY',kind:'quote',number:'DEV-HIST-1',clientId:'C-LEGACY',date:'2026-01-05',status:'Accepté',owner:'',channel:'Physique',createdAt:'2026-01-05T10:00:00Z',updatedAt:'2026-01-06T10:00:00Z'});s.sales.push({id:'B-LEGACY',kind:'sale',number:'FAC-HIST-1',quoteId:'Q-LEGACY',clientId:'C-LEGACY',date:'2026-10-20',status:'Validée',payment:'Payée',delivery:'Livrée',owner:'',channel:'Physique',createdAt:'2026-10-20T10:00:00Z',updatedAt:'2026-10-20T10:00:00Z'});const l={productId:'P-5',ref:'1',name:s.products[0].name,unit:'m²',quantity:10,price:12,vat:20};s.quoteLines.push({...l,id:'QL-LEGACY',documentId:'Q-LEGACY'});s.saleLines.push({...l,id:'BL-LEGACY',documentId:'B-LEGACY'});s.reminders.push({id:'R-LEGACY',clientId:'C-LEGACY',documentId:'Q-LEGACY',date:'2026-10-21',note:'Ancienne relance',done:false,createdAt:'2026-10-20T10:00:00Z'});});}''')
  legacy=await pg.evaluate('JSON.parse(JSON.stringify(state))');assert legacy['schemaVersion']==4
  await pg.goto('http://127.0.0.1:8765/index.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await pg.evaluate('state.schemaVersion')==7
  assert await pg.evaluate('state.clients[0].id')=='C-LEGACY';assert await pg.evaluate('state.opportunities[0].id')=='OP-LEGACY';assert await pg.evaluate('state.quotes[0].id')=='Q-LEGACY';assert await pg.evaluate('state.sales[0].id')=='B-LEGACY';assert await pg.evaluate('state.quoteLines[0].id')=='QL-LEGACY'
  assert await pg.evaluate('state.opportunities[0].stage')=='À vérifier (historique)';assert await pg.evaluate('state.opportunities[0].legacyStage')=='Accepté'
  assert await pg.evaluate('state.sales[0].legacyPaymentUnverified')==True;assert await pg.evaluate('state.payments.length')==0;assert await pg.evaluate('state.confirmedSales.length')==0;assert await pg.evaluate('state.sales[0].invoiceDate')=='2026-10-20'
  assert await pg.evaluate('validateImport(state).schemaVersion')==7
  related=await pg.evaluate('state.quotes[0].opportunityId');assert related==await pg.evaluate('state.sales[0].opportunityId');assert related==await pg.evaluate('state.reminders[0].opportunityId')
  for version in [1,2,3,4]:
   fixture=json.loads(json.dumps(legacy));fixture['schemaVersion']=version
   if version==1:
    fixture.pop('clientSequence',None)
    for c in fixture['clients']:
     for k in ['number','street','postalCode','city','legacyAddress']:c.pop(k,None)
     c['address']='Adresse ancienne non décomposable';c['owner']='Ancien responsable'
   result=await pg.evaluate('''s=>{const m=validateImport(s);return {version:m.schemaVersion,client:m.clients[0].id,sale:m.sales[0].id,payments:m.payments.length,review:m.sales[0].legacyPaymentUnverified}}''',fixture)
   assert result=={'version':7,'client':'C-LEGACY','sale':'B-LEGACY','payments':0,'review':True},result
  # Reload must not recreate wrappers or IDs on every opening.
  opids=await pg.evaluate('state.opportunities.map(o=>o.id)');await pg.reload();await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await pg.evaluate('state.opportunities.map(o=>o.id)')==opids
  # Explicit review confirms the existing sale without duplicating its historical invoice.
  await pg.evaluate(f"confirmOpportunity('{related}')");await pg.get_by_role('button',name='Confirmer la vente et préparer la facturation',exact=True).click();await pg.wait_for_function('state.confirmedSales.length===1');assert await pg.evaluate('state.sales.length')==1;assert await pg.evaluate('state.sales[0].number')=='FAC-HIST-1'
  await pg.get_by_role('button',name='+ Enregistrer un règlement',exact=True).click();await pg.locator('[name=amount]').fill('100');await pg.locator('[name=date]').fill('2026-10-20');await pg.locator('[name=reviewed]').check();await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.payments.length===1');assert await pg.evaluate('paymentSummary(state.sales[0]).paid')==100;assert await pg.evaluate('paymentSummary(state.sales[0]).remaining')==44;assert not await pg.evaluate('state.sales[0].legacyPaymentUnverified')
  assert not errors,errors
  print('PASS migrations V1–V4 : identifiants/lignes/liens conservés, statuts ambigus signalés, aucun montant ni date de règlement inventé, wrappers stables au rechargement, confirmation explicite réutilisant la facturation existante, rapprochement de paiement contrôlé.')
  await b.close()
if __name__=='__main__':asyncio.run(main())
