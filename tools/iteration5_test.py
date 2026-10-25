"""V5 : cycle dossier → devis → vente → facturation → règlements, sans réseau."""
import asyncio,json,io,re
from pathlib import Path
from pypdf import PdfReader
from playwright.async_api import async_playwright,Error
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=await b.new_context(viewport={'width':1440,'height':1080});pg=await ctx.new_page();errors=[]
  pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('dialog',lambda d:d.accept())
  await pg.goto('http://127.0.0.1:8765/index.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();await ctx.set_offline(True)
  assert await pg.evaluate('state.schemaVersion')==7
  assert await pg.evaluate("canonicalUnit('PIECE')")=='Pièce'
  assert await pg.evaluate("canonicalUnit('constructor')")=='constructor'
  assert await pg.locator('#nav button').count()==4 and await pg.locator('#adminnav button').count()==2
  assert not await pg.locator('#nav').get_by_text('Devis & relances',exact=True).count()
  assert await pg.evaluate('state.settings.traceability')==False
  # Client and genuine editable issuer parameters (fictional in this isolated test only).
  await pg.evaluate("go('clients');editClient()")
  for key,value in {'lastName':'Martin','firstName':'Élodie','street':'12 rue Fictive','postalCode':'01000','city':'Ville de test','email':'client@example.invalid'}.items():await pg.locator(f'[name={key}]').fill(value)
  await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.clients.length===1');cid=await pg.evaluate('state.clients[0].id')
  assert not await pg.locator('#list th').get_by_text('Création',exact=True).count()
  assert await pg.locator('.badge.personal').count()==1
  await pg.locator('#toggle-filters').click();assert await pg.locator('#advanced-filters fieldset').count()==1
  assert not await pg.locator('[data-filter-key=address]').count()
  await pg.locator('[data-filter-key=dateFrom]').fill('2020-01-01');await pg.locator('[data-filter-key=dateTo]').fill('2030-12-31');await pg.locator('[data-filter-key=dateType]').select_option('updatedAt');assert await pg.locator('[data-filter-key=dateFrom]').input_value()=='2020-01-01'
  await pg.evaluate("go('settings')")
  for key,value in {'legalName':'Entreprise de recette fictive','street':'1 rue de Recette','postalCode':'01000','city':'Ville fictive','siret':'00000000000000','email':'test@example.invalid','terms':'Conditions de recette.','legalMentions':'Mentions de test, sans valeur commerciale.'}.items():await pg.locator(f'#company-form [name={key}]').fill(value)
  await pg.get_by_role('button',name='Enregistrer l’émetteur',exact=True).click();await pg.wait_for_function("state.settings.company.legalName==='Entreprise de recette fictive'")
  await pg.locator('#trace-toggle').check();await pg.wait_for_function('state.settings.traceability===true');await pg.evaluate("go('clients')");assert await pg.locator('#list th').get_by_text('Création',exact=False).count()==1
  # Two independent dossiers for one client, with a complete multline proposal.
  await pg.evaluate(f"editOpportunity(null,'{cid}')")
  await pg.locator('[name=title]').fill('Terrasse travertin beige');await pg.locator('[name=description]').fill('Projet de test à deux produits.');await pg.locator('[name=stage]').select_option('Devis à préparer')
  for ref,qty,price in [('1','10','100'),('2','20','50')]:
   await pg.get_by_role('button',name='+ Ajouter une ligne produit',exact=True).click();n=await pg.evaluate('draftLines.length');await pg.locator(f'#line-product-{n-1}').fill(ref);await pg.locator(f'#line-product-{n-1}').press('Enter');await pg.locator(f'[aria-label="Quantité ligne {n}"]').fill(qty);await pg.locator(f'[aria-label="PU HT ligne {n}"]').fill(price)
  assert await pg.evaluate('totals(draftLines).ttc')==2400
  await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.opportunities.length===1');oid=await pg.evaluate('state.opportunities[0].id');assert await pg.locator('#dialogtitle').inner_text()=='Dossier commercial'
  await pg.evaluate(f"editOpportunity(null,'{cid}')");await pg.locator('[name=title]').fill('Second projet');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.opportunities.length===2');assert await pg.evaluate('state.opportunities.every(o=>o.clientId===state.clients[0].id)')
  await pg.evaluate(f"opportunityDetail('{oid}')")
  # Quote generation from dossier, no resaisie. Draft then explicit emission.
  await pg.get_by_role('button',name='Générer un devis',exact=True).click();assert await pg.evaluate('draftLines.length')==2
  await pg.get_by_role('button',name='Enregistrer et prévisualiser',exact=True).click();await pg.wait_for_function('state.quotes.length===1');qid=await pg.evaluate('state.quotes[0].id')
  assert await pg.evaluate('state.quotes[0].opportunityId')==oid
  await pg.get_by_role('button',name='Émettre et marquer envoyé',exact=True).click();await pg.wait_for_function("state.quotes[0].status==='Envoyé'")
  assert await pg.evaluate('state.reminders.filter(r=>!r.cancelled&&!r.done).length')==1
  original=await pg.evaluate('JSON.stringify(state.quotes[0].contentSnapshot)')
  await pg.evaluate("editProduct('P-5')");assert await pg.locator('select[name=unit]').input_value()=='m²';await pg.locator('[name=price]').fill('99');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.products[0].price===99')
  assert await pg.evaluate('JSON.stringify(state.quotes[0].contentSnapshot)')==original
  await pg.evaluate(f"quoteDetail('{qid}')");await pg.get_by_role('button',name='Nouvelle version',exact=True).click();await pg.locator('[name=conditions]').fill('Nouvelle version — même montant, conditions ajustées.');await pg.get_by_role('button',name='Enregistrer et prévisualiser',exact=True).click();await pg.wait_for_function('state.quotes.length===2');qid2=await pg.evaluate('state.quotes[1].id')
  await pg.get_by_role('button',name='Émettre et marquer envoyé',exact=True).click();await pg.wait_for_function("state.quotes[1].status==='Envoyé'");assert await pg.evaluate('state.quotes[0].supersededBy')==qid2;assert await pg.evaluate('JSON.stringify(state.quotes[0].contentSnapshot)')==original
  await pg.get_by_role('button',name='Marquer accepté',exact=True).click();await pg.wait_for_function("state.quotes[1].status==='Accepté'")
  assert await pg.evaluate('state.sales.length')==0
  await pg.get_by_role('button',name='+ Programmer une relance',exact=True).click();await pg.locator('[name=note]').fill('Confirmer la livraison');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("state.reminders.some(r=>r.note==='Confirmer la livraison')")
  await pg.get_by_role('button',name='Confirmer la vente',exact=True).click();await pg.get_by_role('button',name='Confirmer la vente et préparer la facturation',exact=True).click();await pg.wait_for_function('state.confirmedSales.length===1')
  assert await pg.evaluate('state.sales.length')==1
  bid=await pg.evaluate('state.sales[0].id');assert await pg.evaluate('totals(lines(state.sales[0])).ttc')==2400
  assert await pg.evaluate('state.sales[0].number')=='';assert await pg.evaluate("state.sales[0].status")=='Brouillon'
  await pg.evaluate(f"confirmOpportunity('{oid}')");assert await pg.evaluate('state.sales.length')==1
  # Confirmed sale, invoice and actual cash are distinct counters.
  assert await pg.evaluate('selectedSales().length')==0
  await pg.get_by_role('button',name='Préparer / générer une facture',exact=True).click();await pg.get_by_role('button',name='Valider et émettre la facture',exact=True).click();await pg.wait_for_function("state.sales[0].status==='Validée'")
  number=await pg.evaluate('state.sales[0].number');invoice_snapshot=await pg.evaluate('JSON.stringify(state.sales[0].contentSnapshot)');assert number.startswith('FAC-')
  await pg.evaluate(f"billingDetail('{bid}')")
  await pg.get_by_role('button',name='+ Enregistrer un règlement',exact=True).click();assert await pg.locator('[name=amount]').input_value()=='1200';await pg.locator('[name=date]').fill('2026-01-15');await pg.evaluate("()=>{const f=document.querySelector('#editform');f.requestSubmit();f.requestSubmit()}");await pg.wait_for_function('state.payments.length===1');assert await pg.evaluate('paymentSummary(state.sales[0]).paid')==1200;assert await pg.evaluate('paymentSummary(state.sales[0]).remaining')==1200
  await pg.get_by_role('button',name='+ Enregistrer un règlement',exact=True).click();await pg.locator('[name=amount]').fill('1300');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("document.getElementById('toast').textContent.includes('dépasse')");assert await pg.evaluate('state.payments.length')==1
  await pg.locator('[name=amount]').fill('1200');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.payments.length===2');assert await pg.evaluate('paymentSummary(state.sales[0]).key')=='paid'
  paymentid=await pg.evaluate('state.payments[0].id');await pg.evaluate(f"paymentForm('{bid}','deposit','{paymentid}')");await pg.locator('[name=amount]').fill('1000');await pg.locator('[name=reason]').fill('Correction du relevé bancaire');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.payments.length===3');assert await pg.evaluate('state.payments[0].voided')==True;assert await pg.evaluate('paymentSummary(state.sales[0]).remaining')==200;assert await pg.evaluate('paymentSummary(state.sales[0]).key')=='deposit'
  await pg.get_by_role('button',name='+ Enregistrer un règlement',exact=True).click();assert await pg.locator('[name=amount]').input_value()=='200';await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.payments.length===4');assert await pg.evaluate('paymentSummary(state.sales[0]).paid')==2400
  # Controlled cancellation/reissue retains old snapshot and reserves the old number.
  await pg.evaluate(f"invoicePreview('{bid}')");await pg.get_by_role('button',name='Annuler cette émission',exact=True).click();await pg.locator('[name=reason]').fill('Correction explicite des mentions');await pg.get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("state.sales[0].status==='Annulée'")
  await pg.get_by_role('button',name='Préparer une nouvelle édition',exact=True).click();await pg.wait_for_function("state.sales[0].status==='Brouillon'");assert await pg.evaluate('state.sales[0].invoiceHistory[0].number')==number
  await pg.get_by_role('button',name='Valider et émettre la facture',exact=True).click();await pg.wait_for_function("state.sales[0].status==='Validée'");assert await pg.evaluate('state.sales[0].number')!=number;assert await pg.evaluate('JSON.stringify(state.sales[0].invoiceHistory[0].snapshot)')==invoice_snapshot
  assert await pg.evaluate('state.confirmedSales.length')==1 and await pg.evaluate('selectedSales().length')==1
  await pg.evaluate("closeDialog();period='all';go('analytics')")
  assert await pg.locator('.kpi').filter(has=pg.get_by_text('Ventes confirmées',exact=True)).locator('strong').inner_text()=='1'
  assert await pg.locator('.kpi').filter(has=pg.get_by_text('Taux d’acceptation des devis',exact=True)).locator('strong').inner_text()=='100 %'
  assert await pg.evaluate('round(state.payments.filter(p=>!p.voided).reduce((n,p)=>n+p.amount,0))')==2400
  assert await pg.evaluate('''()=>{let s=structuredClone(state);s.payments.find(p=>!p.voided).date='2026-02-31';try{validateImport(s);return false}catch{return true}}''' )
  assert await pg.evaluate('''()=>{let s=structuredClone(state);s.confirmedSales.push({...s.confirmedSales[0],id:'DUP-CF'});try{validateImport(s);return false}catch{return true}}''' )
  await pg.evaluate(f"invoicePreview('{bid}')")
  # Native print is requested; print CSS contains only the frozen document.
  await pg.evaluate('()=>{window.printCalls=0;window.print=()=>{window.printCalls++}}')
  await pg.get_by_role('button',name='Imprimer / enregistrer en PDF',exact=True).click();assert await pg.evaluate('printCalls')==1,errors
  await pg.emulate_media(media='print');assert await pg.locator('#print-root').is_visible();assert await pg.locator('main').is_hidden();assert await pg.locator('aside').is_hidden()
  pdf=await pg.pdf(format='A4',print_background=True);assert pdf.startswith(b'%PDF');Path('/tmp/fm84-v5-print-test.pdf').write_bytes(pdf)
  await pg.evaluate("()=>{const d=structuredClone(state.sales[0].contentSnapshot);d.lines=Array.from({length:90},(_,i)=>({...d.lines[i%2],name:'Produit de test long '+i}));d.totals=totals(d.lines);document.querySelector('#print-root').innerHTML=documentMarkup(d)}")
  longpdf=await pg.pdf(format='A4',print_background=True);reader=PdfReader(io.BytesIO(longpdf));assert len(reader.pages)>=2;assert 'Référence' in reader.pages[1].extract_text();assert all('Suivi commercial & ventes' not in p.extract_text() for p in reader.pages);Path('/tmp/fm84-v5-multipage-test.pdf').write_bytes(longpdf)
  await pg.emulate_media(media='screen')
  await pg.evaluate('closeDialog()')
  # Enter with no selection opens the full results page; selected Enter opens the record.
  await pg.locator('#global').fill('travertin beige');await pg.locator('#global').press('Enter');assert await pg.evaluate('view')=='search';assert await pg.locator('#search-sections section').count()==5;assert await pg.locator('table[data-table=search-products] tbody tr').count()==30
  await pg.locator('#search-sections section').filter(has=pg.get_by_role('heading',name='Produits —',exact=False)).get_by_role('button',name='→',exact=True).click();assert await pg.evaluate('searchPages.products')==1
  await pg.get_by_role('button',name=re.compile(r'^Clients \(')).click();assert await pg.locator('#search-sections section').count()==1
  await pg.locator('#global').fill('CLI-000001');await pg.locator('#global').press('ArrowDown');await pg.locator('#global').press('Enter');assert await pg.locator('#dialogtitle').inner_text()=='Fiche client';await pg.evaluate('closeDialog()')
  # Units are configurable and do not rewrite existing document snapshots.
  await pg.evaluate("go('settings')");await pg.locator('#unit-form [name=unit]').fill('Boîte');await pg.locator('#unit-form button').click();await pg.wait_for_function("state.settings.allowedUnits.includes('Boîte')");await pg.evaluate('editProduct()');assert await pg.locator('select[name=unit] option[value="Boîte"]').count()==1;await pg.evaluate('closeDialog()')
  # Integrated quote/invoice filters and CSV exports remain available.
  await pg.evaluate("closeDialog();go('pipeline');commercialTab='devis';pipelinePage();window.csvs=[];download=(text,name,type)=>{csvs.push({text,name,type})}")
  await pg.locator('[aria-label="Statut du devis"]').select_option('Accepté');assert await pg.locator('table[data-table=quotes] tbody tr').count()==1
  await pg.get_by_role('button',name='Exporter les résultats CSV',exact=True).click();assert await pg.evaluate('csvs.at(-1).text.includes(state.quotes[1].number)')
  await pg.evaluate("go('sales')");await pg.locator('[data-status-kind=payments] summary').click();await pg.locator('[data-status-index="2"]').check();await pg.get_by_role('button',name='Exporter les résultats CSV',exact=True).click();assert '2400' in await pg.evaluate('csvs.at(-1).text')
  await pg.evaluate("go('settings')")
  # Model validation, demo lifecycle, backup restoration and reload.
  assert await pg.evaluate('validateImport(state).schemaVersion')==7
  real_sales=await pg.evaluate('state.sales.length');await pg.get_by_role('button',name='Générer des données de démonstration',exact=True).click();await pg.wait_for_function('state.clients.length===41');assert await pg.evaluate('state.opportunities.filter(o=>o.isDemo).length')==50
  assert await pg.evaluate('state.confirmedSales.filter(c=>c.isDemo).length')>0;assert await pg.evaluate('state.payments.filter(p=>p.isDemo).length')>0;assert await pg.evaluate('validateImport(state).schemaVersion')==7
  await pg.evaluate("go('pipeline');commercialTab='dossiers';kanban=false;pipelinePage()");assert await pg.locator('table[data-table=opportunities] tbody tr').count()==40;await pg.get_by_role('button',name='→',exact=True).click();assert await pg.evaluate('page')==1;await pg.evaluate("go('settings')")
  await pg.get_by_role('button',name='Supprimer les données de démonstration',exact=True).click();await pg.wait_for_function('state.clients.length===1');assert await pg.evaluate('state.sales.length')==real_sales;assert await pg.evaluate('state.payments.length')==4
  await pg.evaluate('window.exports=[];download=(text,name,type)=>exports.push({text,name,type})');await pg.get_by_role('button',name='Exporter JSON',exact=True).click();backup=await pg.evaluate('exports.at(-1).text');await pg.locator('#restore').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':backup.encode()});await pg.wait_for_function("document.getElementById('toast').textContent==='Sauvegarde restaurée.'")
  await ctx.set_offline(False);await pg.reload();await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await pg.evaluate('paymentSummary(state.sales[0]).paid')==2400
  await pg.evaluate("go('settings')");await pg.locator('#trace-toggle').uncheck();await pg.wait_for_function('!state.settings.traceability');await pg.evaluate("go('pipeline');kanban=false;pipelinePage()");await pg.screenshot(path='/tmp/fm84-v5-commercial.png',full_page=True);await pg.set_viewport_size({'width':768,'height':1024});await pg.screenshot(path='/tmp/fm84-v5-tablet.png',full_page=True);await pg.set_viewport_size({'width':1440,'height':1080});await pg.evaluate(f"billingDetail('{bid}')");await pg.screenshot(path='/tmp/fm84-v5-billing.png',full_page=True)
  assert not errors,errors
  print('PASS V5 : dossier multiligne, devis versionnés/figés, relances, confirmation unique, facture émise séparément, acompte 1 200 + solde, dépassement refusé, correction tracée, réémission, impression A4 PDF de recette, recherche complète/clavier, trace, unités, démo et sauvegarde/persistance.')
  await b.close()
if __name__=='__main__':asyncio.run(main())
