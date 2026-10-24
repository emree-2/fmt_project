"""Recette actuelle V6. Les scénarios des cycles précédents sont adaptés au nouveau modèle."""
import asyncio
from iteration6_test import main as daily
from iteration5_test import main as workflow
from migration5_test import main as migration
from iteration4_test import main as administration
from filters_test import main as filters
async def main():
 for name,run in [('Saisie, relances et migration V5',daily),('Cycle commercial et paiements',workflow),('Migrations V1–V4',migration),('Administration et imports',administration),('Filtres et performance',filters)]:
  print('Recette : '+name,flush=True)
  await run()
if __name__=='__main__':asyncio.run(main())
