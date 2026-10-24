"""Parcours navigateur réels. Prérequis de développement : Python, playwright, Chromium."""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
 async with async_playwright() as p:
  browser = await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page = await browser.new_page(viewport={"width":1440,"height":1000})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto('http://127.0.0.1:8765/index.html')
  await page.get_by_role('heading',name='Votre activité, en un regard.').wait_for()
  assert await page.evaluate('state.products.length')==3283
  assert await page.evaluate('state.sales.length')==0
  await page.get_by_role('button',name='+ Nouveau client').click()
  await page.locator('[name=lastName]').fill('Martin')
  await page.locator('[name=firstName]').fill('Alice')
  await page.locator('[name=phone]').fill('0612345678')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function('state.clients.length===1')
  await page.evaluate("go('products')")
  await page.locator('input[aria-label=Rechercher]').fill('531')
  assert await page.get_by_text('Référence dupliquée',exact=True).count()>=2
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
  qid=await page.evaluate('state.quotes[0].id')
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
  assert await page.evaluate('selectedSales().length')==1
  await page.evaluate("editProduct('P-5')")
  await page.locator('[name=price]').fill('99')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function("state.products.find(p=>p.id==='P-5').price===99")
  assert await page.evaluate('totals(lines(state.sales[0])).ht')==66
  await page.evaluate("go('dashboard')")
  assert '66,00' in await page.locator('.kpi').first.inner_text()
  await page.reload()
  await page.get_by_role('heading',name='Votre activité, en un regard.').wait_for()
  assert await page.evaluate('state.clients[0].phone')=='0612345678'
  assert await page.evaluate('state.sales.length')==1
  assert await page.evaluate('validateImport(structuredClone(state)).schemaVersion')==1
  rejected=await page.evaluate("""()=>{let s=structuredClone(state);s.saleLines[0].clientId='missing';s.saleLines[0].documentId='missing';try{validateImport(s);return false}catch{return true}}""")
  assert rejected
  await page.evaluate("editOpportunity(null,state.clients[0].id)")
  await page.locator('[name=title]').fill('Projet terrasse')
  await page.get_by_role('button',name='Enregistrer',exact=True).click()
  await page.wait_for_function('state.opportunities.length===1')
  for v in ['clients','products','pipeline','quotes','sales','analytics','settings','dashboard']:
   await page.evaluate(f"go('{v}')")
   assert await page.locator('#content h1').count()==1
  await page.screenshot(path='/tmp/fmt-dashboard.png',full_page=True)
  await page.set_viewport_size({'width':768,'height':1024})
  await page.screenshot(path='/tmp/fmt-tablet.png',full_page=True)
  assert not errors,errors
  print('PASS: catalogue complet, anomalie bloquante, client, téléphone, devis multiligne, calculs HT/TVA/TTC, relance, conversion unique, exclusion brouillon, validation facture, prix historique, IndexedDB après rechargement, sauvegarde valide, import incohérent refusé, opportunité, 8 écrans sans erreur JavaScript.')
  await browser.close()

asyncio.run(main())
