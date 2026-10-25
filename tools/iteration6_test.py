"""V6 : saisie, automatisation, journal, filtres, migration réelle V5 et hors ligne."""
import asyncio,json,subprocess
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  ctx=await b.new_context(viewport={'width':1500,'height':1100},timezone_id='Europe/Paris');pg=await ctx.new_page();pg.set_default_timeout(10000);errors=[]
  pg.on('pageerror',lambda e:errors.append(str(e)));pg.on('dialog',lambda d:d.accept())
  await pg.goto('http://127.0.0.1:8765/index.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();await ctx.set_offline(True)
  await pg.evaluate("go('clients');editClient()")
  await pg.locator('[name=lastName]').fill('Recette six');await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.clients.length===1')
  cid=await pg.evaluate('state.clients[0].id')
  # Empty project allowed; empty project cannot create a quote or sale.
  await pg.evaluate(f"editOpportunity(null,'{cid}')");await pg.locator('[name=title]').fill('Terrasse');await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.opportunities.length===1');oid=await pg.evaluate('state.opportunities[0].id')
  await pg.get_by_role('button',name='Générer un devis',exact=True).click();assert await pg.locator('#dialogtitle').inner_text()=='Dossier commercial';assert await pg.evaluate('state.quotes.length')==0
  # Shared editor, exact stable ID even for duplicated reference 531.
  await pg.evaluate(f"editOpportunity('{oid}')");await pg.get_by_role('button',name='+ Ajouter une ligne produit',exact=True).click()
  await pg.locator('#line-product-0').fill('531');assert await pg.locator('#line-options-0 [role=option]').count()>=2
  chosen=await pg.evaluate("state.products.find(p=>p.ref==='531'&&p.active&&p.price!==null).id")
  await pg.locator('#line-options-0 [role=option]').filter(has_text=chosen).click();assert await pg.evaluate('draftLines[0].productId')==chosen
  expected=await pg.evaluate('draftLines[0].price');assert float(await pg.get_by_label('PU HT ligne 1',exact=True).input_value())==expected
  assert await pg.locator('[data-line="0"] .line-unit').inner_text()==await pg.evaluate('draftLines[0].unit')
  await pg.get_by_label('Quantité ligne 1',exact=True).fill('2.5');await pg.get_by_label('PU HT ligne 1',exact=True).fill('100');await pg.get_by_label('TVA ligne 1',exact=True).fill('10')
  assert '250,00' in await pg.locator('[data-line="0"] .line-ht').inner_text();assert '275,00' in await pg.locator('[data-line="0"] .line-ttc').inner_text()
  assert '275,00' in await pg.locator('#doctotals .grand-total').inner_text()
  await pg.get_by_role('button',name='+ Ajouter une ligne produit',exact=True).click();await pg.locator('#line-product-1').fill('travertin beige');assert await pg.locator('#line-options-1 [role=option]').count()>0
  # Adding a line preserves unresolved search; save refuses it instead of silently losing it.
  await pg.get_by_role('button',name='+ Ajouter une ligne produit',exact=True).click();assert await pg.locator('#line-product-1').input_value()=='travertin beige'
  await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();assert await pg.locator('#dialogtitle').inner_text()=='Modifier le dossier';assert await pg.evaluate('oppLines(state.opportunities[0].id).length')==0
  await pg.locator('#line-product-1').fill('travertin beige');await pg.locator('#line-product-1').press('ArrowDown');await pg.locator('#line-product-1').press('Enter')
  await pg.get_by_label('Supprimer la ligne 3',exact=True).click();assert await pg.locator('#lineitems tr').count()==2
  await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.opportunityLines.length===2')
  saved=await pg.evaluate('JSON.stringify(oppLines(state.opportunities[0].id).map(({id,documentId,...l})=>l))')
  assert await pg.evaluate('state.products.find(p=>p.id===draftLines[0].productId).price')==expected
  await pg.evaluate(f"editOpportunity('{oid}')");assert await pg.locator('#lineitems tr').count()==2
  await pg.screenshot(path='/tmp/fm84-v6-editor.png',full_page=True)
  await pg.get_by_label('Supprimer la ligne 2',exact=True).click();assert '275,00' in await pg.locator('#doctotals .grand-total').inner_text()
  await pg.get_by_role('button',name='Annuler',exact=True).click();await pg.evaluate(f"editOpportunity('{oid}')");assert await pg.locator('#lineitems tr').count()==2
  await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("document.getElementById('dialogtitle').textContent==='Dossier commercial'");assert await pg.evaluate('JSON.stringify(oppLines(state.opportunities[0].id).map(({id,documentId,...l})=>l))')==saved
  await pg.get_by_role('button',name='Générer un devis',exact=True).click();assert await pg.locator('#dialog.editor-wide .entry-table').count()==1;await pg.get_by_role('button',name='Annuler',exact=True).click()
  # Search is capped and fast with thousands of catalog products.
  await pg.evaluate(f"editOpportunity('{oid}')");perf=await pg.evaluate("()=>{const t=performance.now();searchLineProducts(0,'travertin');return {ms:performance.now()-t,count:document.querySelectorAll('#line-options-0 [role=option]').length}}")
  assert perf['count']<=25 and perf['ms']<1500,perf;print('Recherche sur 3 283 produits :',round(perf['ms']),'ms, suggestions limitées à 25.')
  await pg.set_viewport_size({'width':700,'height':1000});assert await pg.locator('.editor-scroll').evaluate('e=>e.scrollWidth>e.clientWidth');await pg.screenshot(path='/tmp/fm84-v6-editor-small.png',full_page=True);await pg.set_viewport_size({'width':1500,'height':1100});await pg.evaluate('closeDialog()')
  # Backdate business activity explicitly in test DB. Other status/technical events cannot reset it.
  await pg.evaluate("async()=>{await commit(s=>{s.opportunities[0].lastBusinessActivityAt='2026-01-01T10:00:00Z';s.settings.autoReminders={enabled:true,days:10};});}")
  assert await pg.evaluate("state.reminders.filter(r=>r.reason==='inactivity').length")==1
  activity=await pg.evaluate('state.opportunities[0].lastBusinessActivityAt');rid=await pg.evaluate("state.reminders.find(r=>r.reason==='inactivity').id")
  await pg.evaluate('async()=>{await queueReminderCheck();await queueReminderCheck();await commit(s=>event(s,"opportunity",s.opportunities[0].id,"Événement technique sans activité"));}')
  assert await pg.evaluate('state.reminders.length')==1;assert await pg.evaluate('state.opportunities[0].lastBusinessActivityAt')==activity
  await pg.evaluate(f"opportunityDetail('{oid}')");assert await pg.locator('.technical-history').count()==0;assert await pg.locator('#journal .badge.automatic').count()==1;assert await pg.locator('#journal select.danger').count()==1
  before=await pg.evaluate('state.interactions.length');await pg.locator('select.reminder-status').select_option('done');await pg.wait_for_function('state.reminders[0].done')
  assert await pg.evaluate('state.interactions.length')==before;assert await pg.evaluate('state.reminders[0].completedAt')
  assert await pg.locator(f'[data-interaction-id="{rid}"] .badge.success').inner_text()=='Effectuée';assert 'à' in await pg.locator(f'[data-interaction-id="{rid}"] td').nth(3).inner_text();assert await pg.evaluate('state.opportunities[0].lastBusinessActivityAt')!=activity
  await pg.evaluate('queueReminderCheck()');assert await pg.evaluate('state.reminders.length')==1
  await pg.evaluate("async()=>{await commit(s=>{s.opportunities[0].lastBusinessActivityAt='2026-02-01T10:00:00Z';});}");assert await pg.evaluate('state.reminders.length')==2
  # Cancel does not produce an endless new alert in the same inactivity period.
  await pg.evaluate('cancelReminder(state.reminders[1].id)');await pg.evaluate('queueReminderCheck()');assert await pg.evaluate('state.reminders.length')==2
  await pg.evaluate("async()=>{await commit(s=>{s.settings.autoReminders.enabled=false;s.opportunities[0].lastBusinessActivityAt='2026-03-01T10:00:00Z';});}");assert await pg.evaluate('state.reminders.length')==2
  # Settings UI keeps independent quote delay. Explicit re-enable detects stale dossier.
  await pg.evaluate("closeDialog();go('settings');openSettingsCategory('data')");await pg.evaluate("openSettingsCategory('commercial')");await pg.locator('#automatic-form [name=enabled]').check();await pg.locator('#automatic-form [name=days]').fill('7');await pg.locator('#automatic-form button').click();await pg.wait_for_function('state.settings.autoReminders.days===7');assert await pg.evaluate('state.settings.reminderDays')==10;assert await pg.evaluate('state.reminders.length')==3
  # Timer queued during a form never closes it or discards typed fields.
  await pg.evaluate(f"editOpportunity('{oid}')");await pg.locator('[name=title]').fill('Saisie en cours');await pg.evaluate('queueReminderCheck()');assert await pg.locator('[name=title]').input_value()=='Saisie en cours';await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("state.opportunities[0].title==='Saisie en cours'");assert await pg.evaluate('state.opportunities[0].lastBusinessActivityAt')>'2026-03-01'
  # Manual reminder CRUD and actual completion date, quick exchange, one journal row each.
  await pg.get_by_role('button',name='+ Programmer une relance',exact=True).click();await pg.locator('[name=date]').fill('2026-01-02');await pg.locator('[name=note]').fill('Rappel convenu');await pg.locator('[name=notes]').fill('Choix des dimensions');await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("state.reminders.some(r=>r.note==='Rappel convenu')")
  mrid=await pg.evaluate("state.reminders.find(r=>r.note==='Rappel convenu').id");row=pg.locator(f'[data-interaction-id="{mrid}"]');assert await row.locator('.badge.manual').count()==1
  await row.get_by_role('button',name='Modifier',exact=True).click();await pg.locator('[name=note]').fill('Rappel modifié');await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function("state.reminders.some(r=>r.note==='Rappel modifié')")
  await pg.locator(f'[data-interaction-id="{mrid}"] select.reminder-status').select_option('done');await pg.wait_for_function("state.reminders.find(r=>r.id==='"+mrid+"').done")
  assert await pg.locator(f'[data-interaction-id="{mrid}"] td').nth(2).inner_text()!=await pg.locator(f'[data-interaction-id="{mrid}"] td').nth(3).inner_text()
  await pg.locator(f'[data-interaction-id="{mrid}"]').get_by_role('button',name='Voir le détail',exact=True).click();await pg.locator('[name=report]').fill('Client joint, dimensions validées');await pg.locator('#reminder-report button').click();await pg.wait_for_function("state.reminders.find(r=>r.id==='"+mrid+"').report.length>0")
  await pg.get_by_role('button',name='+ Enregistrer un échange',exact=True).click();assert await pg.locator('[name=occurredAt]').input_value();await pg.locator('[name=channel]').select_option('Téléphone');await pg.locator('[name=note]').fill('Client hésite entre deux pierres');await pg.locator('#editform').get_by_role('button',name='Enregistrer',exact=True).click();await pg.wait_for_function('state.interactions.length===1');assert await pg.locator('#journal .badge.quick').count()==2
  await pg.locator('[data-column-filter-table=journal][data-column-filter-key=type]').click();await pg.locator('#column-filter-menu input[value=quick]').check();assert await pg.locator('#journal-rows tbody tr').count()==1;await pg.locator('#column-filter-menu').get_by_role('button',name='Effacer cette colonne',exact=True).click()
  await pg.keyboard.press('Escape');await pg.locator('#journal').screenshot(path='/tmp/fm84-v6-journal.png')
  await pg.evaluate("closeDialog();go('pipeline');commercialTab='relances';pipelinePage()");assert await pg.locator('table[data-table=follow-ups] tbody tr').count()==1
  # Technical histories in every relevant module are absent or closed by default.
  await pg.evaluate('async()=>{await setTraceability(true)}');await pg.evaluate(f"opportunityDetail('{oid}')");assert not await pg.locator('.technical-history').evaluate('e=>e.open');await pg.locator('.technical-history summary').click();assert await pg.locator('.technical-log').is_visible();assert await pg.locator('#journal-rows').is_visible()
  await pg.evaluate(f"clientDetail('{cid}')");assert not await pg.locator('.technical-history').evaluate('e=>e.open');await pg.evaluate("productDetail('P-5')");assert not await pg.locator('.technical-history').evaluate('e=>e.open')
  # All excluded stages: no automatic reminders even with old activity; new business activity restarts delay.
  result=await pg.evaluate("""()=>{const s=structuredClone(state);s.reminders=[];for(const stage of ['Vente confirmée','Perdu / abandonné','À vérifier (historique)'])s.opportunities.push({...s.opportunities[0],id:'EX-'+stage,stage,lastBusinessActivityAt:'2025-01-01T10:00:00Z'});s.opportunities[0].lastBusinessActivityAt=now();return generateInactivityReminders(s)}""");assert result==0
  # Multiselection stays active across table/Kanban and combines with search; payments use same component.
  await pg.evaluate("closeDialog();go('settings');openSettingsCategory('data');generateDemo()");await pg.wait_for_function('state.clients.length===41')
  await pg.evaluate("go('pipeline');commercialTab='dossiers';kanban=false;pipelinePage()")
  await pg.locator('[data-column-filter-table=opportunities][data-column-filter-key=stage]').click();await pg.locator('#column-filter-menu input[value="Nouveau contact"]').check();await pg.locator('#column-filter-menu input[value="Besoin identifié"]').check();await pg.keyboard.press('Escape')
  count=await pg.evaluate('state.opportunities.filter(o=>commercialStages.includes(o.stage)).length');assert await pg.locator('table[data-table=opportunities] tbody tr').count()==count
  await pg.get_by_role('button',name='Vue Kanban',exact=True).click();assert await pg.locator('.kanban .column').count()==2;assert await pg.evaluate('commercialStages.length')==2
  await pg.get_by_role('button',name='Vue tableau',exact=True).click();await pg.get_by_label('Rechercher un dossier',exact=True).fill('Saisie');assert await pg.locator('table[data-table=opportunities] tbody tr').count()==1
  await pg.locator('[data-column-filter-table=opportunities][data-column-filter-key=stage]').click();await pg.get_by_role('button',name='Effacer cette colonne',exact=True).click();await pg.keyboard.press('Escape');assert await pg.evaluate('commercialStages.length')==0
  await pg.evaluate("go('sales')");await pg.locator('[data-column-filter-table=billing][data-column-filter-key=status]').click();await pg.locator('#column-filter-menu input[value=unpaid]').check();await pg.locator('#column-filter-menu input[value=deposit]').check()
  expected_count=await pg.evaluate("state.sales.filter(b=>['unpaid','deposit'].includes(paymentSummary(b).key)).length");assert await pg.locator('table[data-table=billing] tbody tr').count()==expected_count
  assert str(expected_count)+' résultat' in await pg.locator('#billing-results .pagination').inner_text()
  await pg.keyboard.press('Escape');await pg.locator('table[data-table=billing]').locator('button[data-sort-key=total]').click();assert await pg.locator('table[data-table=billing] tbody tr').count()==expected_count
  await pg.evaluate("go('products');productPanelOpen=true;productsPage()");assert await pg.locator('#facet-unit').count()==0;assert await pg.locator('table[data-table=products]').get_by_role('button',name='Unité',exact=False).count()==1
  assert await pg.evaluate('()=>{const s=structuredClone(state);applyDemoRemoval(s);validateImport(s);return !s.clients.some(c=>c.isDemo)}')
  assert await pg.evaluate('validateImport(state).schemaVersion')==7
  assert not errors,errors
  await ctx.set_offline(False);await pg.reload();await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await pg.evaluate('state.clients.length')==41
  await ctx.close()
  # Real V5 IndexedDB -> V6, duplicate completion grouped without deleting original records.
  old_html=subprocess.check_output(['git','show','add11f9:index.html'],cwd=Path(__file__).resolve().parents[1]).decode()
  ctx=await b.new_context();await ctx.route('http://127.0.0.1:8765/v5.html',lambda r:r.fulfill(status=200,content_type='text/html',body=old_html));pg=await ctx.new_page();pg.on('pageerror',lambda e:errors.append(str(e)))
  await pg.goto('http://127.0.0.1:8765/v5.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  await pg.evaluate("async()=>{await commit(s=>{populateDemo(s);const o=s.opportunities.find(isOpen);s.reminders.push({id:'MIG-R',clientId:o.clientId,opportunityId:o.id,date:'2026-01-01',note:'Rappel historique',done:true,cancelled:false,completedAt:'2026-01-02T12:00:00Z',createdAt:'2026-01-01T12:00:00Z'});s.interactions.push({id:'MIG-I',clientId:o.clientId,opportunityId:o.id,note:'Relance effectuée : Rappel historique',createdAt:'2026-01-02T12:00:00Z'});});}")
  old=await pg.evaluate('JSON.parse(JSON.stringify(state))');assert old['schemaVersion']==5
  await pg.goto('http://127.0.0.1:8765/index.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for()
  new=await pg.evaluate('JSON.parse(JSON.stringify(state))');assert new['schemaVersion']==7
  for k in ['clients','products','opportunities','opportunityLines','quotes','quoteLines','sales','saleLines','confirmedSales','payments','reminders','interactions','events']:
   assert [x['id'] for x in old[k]]==[x['id'] for x in new[k]],k
  assert [x.get('contentSnapshot') for x in old['quotes']]==[x.get('contentSnapshot') for x in new['quotes']]
  assert old['sales']==new['sales'] and old['payments']==new['payments'] and old['opportunityLines']==new['opportunityLines']
  assert next(i for i in new['interactions'] if i['id']=='MIG-I')['reminderId']=='MIG-R'
  oid=next(r for r in new['reminders'] if r['id']=='MIG-R')['opportunityId'];await pg.evaluate(f"opportunityDetail('{oid}')");assert await pg.locator('[data-interaction-id=MIG-R]').count()==1;assert await pg.locator('[data-interaction-id=MIG-I]').count()==0
  assert 'Rappel historique' in await pg.locator('[data-interaction-id=MIG-R]').inner_text()
  assert await pg.evaluate('validateImport(state).schemaVersion')==7
  # Restore JSON through actual file input and check business activity remains the backed-up value.
  await pg.evaluate("closeDialog();go('settings');openSettingsCategory('data')");pg.on('dialog',lambda d:d.accept());await pg.locator('#restore').set_input_files({'name':'v6.json','mimeType':'application/json','buffer':json.dumps(new).encode()});await pg.wait_for_function("document.getElementById('toast').textContent==='Sauvegarde restaurée.'")
  assert await pg.evaluate('state.opportunities[0].lastBusinessActivityAt')==new['opportunities'][0]['lastBusinessActivityAt']
  # Startup detects overdue work persisted without running a check; repeated reload preserves one alert.
  await pg.evaluate("async()=>{closeDialog();state.settings.autoReminders={enabled:true,days:10};for(const o of state.opportunities)o.lastBusinessActivityAt=now();state.opportunities.find(isOpen).lastBusinessActivityAt='2025-01-01T10:00:00Z';await persist(state)}")
  await pg.reload();await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await pg.evaluate("state.reminders.filter(r=>r.reason==='inactivity').length")==1
  alert=await pg.evaluate("state.reminders.find(r=>r.reason==='inactivity').id");await pg.reload();await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await pg.evaluate("state.reminders.filter(r=>r.reason==='inactivity').map(r=>r.id)")==[alert]
  assert not errors,errors
  print('PASS V6 : éditeur partagé, totaux immédiats, sélection stable/clavier, suppression/édition sans perte, mobile, relances automatiques persistées sans doublons, activité métier, désactivation, journal unique, CRUD manuel/échanges, traçabilité repliable, multisélection/tableau/Kanban/paiements, unités conservées, migration réelle V5 et restauration JSON hors ligne.')
  await ctx.close()
  # A real scheduled one-minute check, with virtual time rather than waiting a minute.
  ctx=await b.new_context(viewport={'width':1500,'height':1100});pg=await ctx.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));await pg.clock.install()
  await pg.goto('http://127.0.0.1:8765/index.html');await pg.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();await ctx.set_offline(True)
  await pg.evaluate('async()=>{await commit(s=>populateDemo(s));editOpportunity(state.opportunities.find(isOpen).id)}')
  await pg.locator('[name=title]').fill('Formulaire conservé pendant le contrôle périodique')
  await pg.evaluate("async()=>{for(const o of state.opportunities)o.lastBusinessActivityAt=now();state.opportunities.find(isOpen).lastBusinessActivityAt='2025-01-01T10:00:00Z';state.settings.autoReminders={enabled:true,days:10};await persist(state)}")
  assert await pg.evaluate("state.reminders.filter(r=>r.reason==='inactivity').length")==0
  await pg.clock.fast_forward(61000);await pg.evaluate('writeQueue')
  assert await pg.evaluate("state.reminders.filter(r=>r.reason==='inactivity').length")==1
  assert await pg.locator('[name=title]').input_value()=='Formulaire conservé pendant le contrôle périodique'
  assert not errors,errors;print('PASS contrôle périodique réel : horloge avancée de 61 secondes, alerte persistée, formulaire conservé, réseau coupé.')
  await b.close()
if __name__=='__main__':asyncio.run(main())
