"""V8 : audit des modules, responsive, composants partagés et état V7 inchangé."""
import asyncio,json,subprocess,re
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=await browser.new_context(viewport={'width':1440,'height':1000},locale='fr-FR',timezone_id='Europe/Paris');page=await context.new_page();page.set_default_timeout(10000);errors=[];page.on('pageerror',lambda e:errors.append(e.stack));page.on('dialog',lambda d:d.accept())
  # Real V7 database -> V8 UI: every persisted value must remain identical.
  oldhtml=subprocess.check_output(['git','show','15d3ae1:index.html'],cwd=Path(__file__).resolve().parents[1]).decode();await context.route('http://127.0.0.1:8765/v7.html',lambda r:r.fulfill(status=200,content_type='text/html',body=oldhtml));await page.goto('http://127.0.0.1:8765/v7.html');await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();await page.evaluate('async()=>{await commit(s=>populateDemo(s))}');baseline=await page.evaluate('JSON.parse(JSON.stringify(state))')
  core=await page.evaluate("()=>Object.fromEntries(['commit','persist','migrate','validateImport','trackBusinessChanges','generateInactivityReminders','paymentSummary','paymentProposal','confirmOpportunity','issueQuote','issueInvoice','setQuoteStatus','paymentForm','scheduleOpportunityReminder','setReminderStatus','populateDemo','restore','totals'].map(n=>[n,eval(n).toString()]))")
  await page.goto('http://127.0.0.1:8765/index.html');await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await page.evaluate('JSON.parse(JSON.stringify(state))')==baseline
  assert await page.evaluate("names=>Object.fromEntries(names.map(n=>[n,eval(n).toString()]))",list(core))==core
  await context.set_offline(True)
  # Six modules and main dialogs at desktop, laptop, tablet and phone widths.
  for width,height in [(1920,1080),(1366,900),(768,1024),(390,844)]:
   await page.set_viewport_size({'width':width,'height':height})
   for view in ['analytics','clients','pipeline','sales','products','settings']:
    await page.evaluate(f"closeDialog();go('{view}')")
    assert await page.locator('#content h1').is_visible()
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),(width,view,await page.evaluate('document.documentElement.scrollWidth'))
    if width in (1366,390):await page.screenshot(path=f'/tmp/fm84-v8-{width}-{view}.png')
   for kind,expr in [('client','clientDetail(state.clients[0].id)'),('dossier','opportunityDetail(state.opportunities[3].id)'),('billing','billingDetail(state.sales[0].id)')]:
    await page.evaluate(expr);assert await page.locator('#dialog').is_visible();box=await page.locator('#dialog').bounding_box();assert box['width']<=width and box['height']<=height,(width,kind,box)
    assert await page.locator('#dialog .dialoghead button').get_attribute('aria-label')=='Fermer'
    assert await page.locator('#dialog .dialoghead').evaluate("e=>getComputedStyle(e).position")=='sticky'
    if width in (1366,390):await page.screenshot(path=f'/tmp/fm84-v8-{width}-{kind}.png')
    await page.get_by_role('button',name='Fermer',exact=True).click()
  await page.set_viewport_size({'width':1440,'height':1000})
  assert await page.evaluate('JSON.parse(JSON.stringify(state))')==baseline
  # Common badges, readable tables and right-aligned amounts in all relevant views.
  await page.evaluate("go('pipeline');kanban=false;pipelinePage()")
  assert await page.locator('table[data-table=opportunities] [data-stage]').count()>0
  assert float(await page.locator('table[data-table=opportunities]').evaluate('e=>getComputedStyle(e).fontSize.replace("px","")'))>=13
  assert await page.locator('table[data-table=opportunities] td.numeric').first.evaluate('e=>getComputedStyle(e).textAlign')=='right'
  await page.get_by_role('button',name='Vue Kanban',exact=True).click();assert await page.locator('.column[data-stage]').count()==7;assert await page.locator('.opp .next-action.overdue').count()>0
  stage=await page.evaluate('state.opportunities[3].stage');badge=await page.evaluate('stageBadge(state.opportunities[3].stage)');await page.evaluate('opportunityDetail(state.opportunities[3].id)');assert await page.locator('.dossier-head [data-stage]').evaluate('e=>e.outerHTML')==badge
  await page.get_by_role('button',name='Relances & échanges',exact=True).first.click();assert await page.locator('#project-journal').is_visible()
  await page.get_by_role('button',name='Projet',exact=True).click();assert await page.locator('#project-info').evaluate('e=>e.open')
  await page.evaluate("closeDialog();go('sales')");assert await page.locator('table[data-table=billing] [data-payment]').count()>0
  await page.evaluate('billingDetail(state.sales[0].id)');assert await page.locator('.billing-kpis .kpi').count()==3;assert await page.locator('.deposit-note').count()==1
  # Settings navigation keeps original forms and handlers. Keyboard tab navigation works.
  await page.evaluate("closeDialog();go('settings')")
  assert await page.locator('.settings-panel:visible').count()==1;assert await page.locator('#settings-panel-general').is_visible()
  await page.get_by_role('tab',name='Général',exact=True).focus();await page.keyboard.press('ArrowRight');assert await page.get_by_role('tab',name='Commercial',exact=True).get_attribute('aria-selected')=='true';assert await page.locator('#automatic-form').is_visible()
  await page.get_by_role('tab',name='Documents',exact=True).click();assert await page.locator('#company-form').is_visible();await page.get_by_role('tab',name='Catalogue',exact=True).click();assert await page.locator('#unit-form').is_visible();await page.get_by_role('tab',name='Données & administration',exact=True).click();assert await page.locator('#restore').is_visible();assert await page.locator('.danger-zone').get_by_role('button',name='Réinitialiser les données',exact=True).is_visible()
  # Read-only browsing never rewrites the database or document snapshots.
  assert await page.evaluate('JSON.parse(JSON.stringify(state))')==baseline
  # Main list pagination: sizes, filters and sort remain functional without changing records.
  await page.evaluate("go('products')");assert await page.locator('table[data-table=products] tbody tr').count()==40
  await page.get_by_label('Lignes par page',exact=True).select_option('20');assert await page.locator('table[data-table=products] tbody tr').count()==20
  await page.locator('table[data-table=products]').locator('button[data-sort-key=price]').click();active=await page.evaluate('JSON.stringify(tableSorts.products)');await page.get_by_role('button',name='→',exact=True).click();assert await page.evaluate('JSON.stringify(tableSorts.products)')==active
  await page.get_by_label('Lignes par page',exact=True).select_option('100');assert await page.locator('table[data-table=products] tbody tr').count()==100;assert await page.evaluate('page')==0
  assert await page.locator('#advanced-filters #facet-category').count()==1 and await page.locator('#advanced-filters #facet-color').count()==1
  await page.evaluate("go('clients')");assert await page.locator('#advanced-filters [data-fkey=type]').count()==1;assert await page.locator('#advanced-filters #facet-cities').count()==1
  await page.evaluate("toggleCommonFilters('clients',true)");await page.locator('#advanced-filters [data-fkey=type] input[value=Professionnel]').check();assert await page.evaluate("filtered().every(c=>c.type==='Professionnel')");await page.get_by_role('button',name='Réinitialiser les filtres',exact=True).click()
  # Universal keyboard behavior and status badges in suggestions/full results.
  await page.locator('#global').fill('démonstration');await page.locator('#global').press('Enter');assert await page.evaluate('view')=='search';assert await page.locator('table[data-table=search-opportunities] [data-stage]').count()>0
  await page.locator('#global').fill('CLI-000001');await page.locator('#global').press('ArrowDown');await page.locator('#global').press('Enter');assert await page.locator('#dialogtitle').inner_text()=='Fiche client'
  # Notifications are also visible inside the modal. Portable HTML cannot leak the new notice content.
  await page.evaluate("toast('NOTICE_PRIVATE_SENTINEL')");assert await page.locator('#dialog-feedback').inner_text()=='NOTICE_PRIVATE_SENTINEL'
  await page.evaluate("state.settings.logoDataURI='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+cVZkAAAAASUVORK5CYII=';window.exported=[];download=(text,name,type)=>exported.push({text,name,type});exportHTMLWithLogo()")
  exported=await page.evaluate('exported[0].text');assert 'NOTICE_PRIVATE_SENTINEL' not in exported and baseline['clients'][0]['id'] not in exported
  # Chart values stay exact; keyboard focus reveals the same accessible value as hover.
  await page.evaluate("delete state.settings.logoDataURI;closeDialog();go('analytics')")
  for kind in ['cash','confirmed','invoices']:
   values=await page.evaluate("kind=>{const t=document.createElement('template');t.innerHTML=monthlyGraph(kind);return [...t.content.querySelectorAll('.bar')].map(e=>Number(e.dataset.value))}",kind)
   assert len(values)==12
   expected=await page.evaluate("""kind=>Array.from({length:12},(_,i)=>{const d=new Date();d.setDate(1);d.setMonth(d.getMonth()-11+i);const key=dayKey(d.toISOString()).slice(0,7);return kind==='cash'?state.payments.filter(p=>!p.voided&&p.date.startsWith(key)).reduce((n,p)=>n+p.amount,0):kind==='confirmed'?state.confirmedSales.filter(c=>c.confirmedAt.startsWith(key)).length:state.sales.filter(b=>b.status==='Validée'&&b.invoiceDate?.startsWith(key)).reduce((n,b)=>n+totals(lines(b)).ht,0)})""",kind)
   assert values==expected
  await page.locator('.bar').first.focus();assert await page.locator('.bar').first.locator('.bar-value').is_visible();assert await page.locator('.bar').first.get_attribute('aria-label')
  # Contrast spot-check for all commercial/payment status tokens (normal text AA threshold).
  contrasts=await page.evaluate(r"""()=>{const fixture=document.createElement('div');fixture.hidden=true;fixture.innerHTML=stages.map(stageBadge).join('')+['unpaid','deposit','paid','review'].map(key=>paymentBadge({key,label:key})).join('');document.body.append(fixture);const lum=c=>{const a=c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});return .2126*a[0]+.7152*a[1]+.0722*a[2]};const result=[...fixture.querySelectorAll('.badge')].map(b=>{const st=getComputedStyle(b),fg=lum(st.color),bg=lum(st.backgroundColor);return {label:b.textContent,ratio:(Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05)}});fixture.remove();return result}""")
  assert all(c['ratio']>=4.5 for c in contrasts),contrasts
  # Persist/reload still gives byte-identical business data; no schema migration for this UI iteration.
  await context.set_offline(False);await page.reload();await page.get_by_role('heading',name='Analyses & KPI',exact=True).wait_for();assert await page.evaluate('JSON.parse(JSON.stringify(state))')==baseline
  assert not errors,errors
  print('PASS V8 : six modules et trois fiches à 1920/1366/768/390 px sans débordement global, statuts communs, tableaux/alignements, pagination 20/40/100, filtres rapides, navigation paramètres/clavier, recherche universelle, retours modaux, HTML privé, graphiques accessibles aux valeurs inchangées, état V7 complet inchangé et persistant, hors ligne.')
  await browser.close()
if __name__=='__main__':asyncio.run(main())
