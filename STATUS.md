STATUS: EN COURS — BOOTSTRAP, AUCUN TRAVAIL FACIAL COMMENCÉ

| | |
| --- | --- |
| **statut global** | **EN COURS** (bootstrap) |
| dernière étape terminée | inspection mesurée de l'asset source |
| étape suivante | audit de topologie de `Head (Animation) - Realistic` (chat 3) |
| branche active | `main` |
| commit de départ | ce commit de bootstrap |
| géométrie faciale | **inexistante** |
| shape keys | **aucune** |
| rig facial | **inexistant** |
| critères réussis / échoués | sans objet — aucun critère défini à ce stade |
| processus actifs | **aucun** |

## Ce qui existe

- l'inspection chiffrée de l'asset (`audit/inspection-asset-*.json`) ;
- les deux scripts d'inspection, reproductibles (`tests/`) ;
- le périmètre V1 (`docs/SCOPE_V1.md`) ;
- le bootstrap du chat 3 (`handoffs/BOOTSTRAP_CHAT_3_FACE.md`).

## Ce qui n'existe pas

Tout le reste : aucun `.blend`, aucun rig, aucune shape key, aucun rendu,
aucune vidéo, aucun test de validation.

## Blocages connus

1. **Dents et langue absentes de l'asset** — mesuré. Une bouche qui s'ouvre sur
   le vide se voit ; c'est un chantier à part entière.
2. **La densité autour de la bouche n'a pas pu être mesurée** — mon repère
   sagittal n'a pas convergé. Le chiffre manque, et je préfère l'écrire plutôt
   que d'en publier un douteux.
3. **Le multires n'est pas tranché** : cage ou maillage subdivisé.
