# Codes de sortie sous Blender 5.1.2

Trois temoins, lances avec `--background --factory-startup --python-exit-code 1`.
Ils fixent la convention utilisee par tous les tests F0 :
**0 = succes, 2 = echec metier annonce, 1 = panne technique**.

| script | attendu | code observe |
| --- | ---: | ---: |
| `pass.py` | 0 | **0** |
| `echec_metier.py` | 2 | **2** |
| `echec_technique.py` | 1 | **1** |

Commande exacte :

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python experiments/f0-exit-code/<script>.py
```
