# echantillon

Module Python de tirage d'échantillons (systématique à probabilités égales ou PPT, stratifié).

```python
%pip install git+https://github.com/riozakies/echantillon.git
import echantillon as ech
```

## Interface web

`index.html` est une page qui permet de tirer un échantillon sans installer Python :
charger une base de sondage (Excel ou CSV), choisir la méthode et les colonnes,
puis enregistrer l'échantillon en Excel, CSV ou PDF.
Voir le [manuel d'utilisation](MANUEL.md).

Le module est exécuté dans le navigateur avec [Pyodide](https://pyodide.org) :
les données ne quittent pas l'ordinateur de l'utilisateur.

### Mise en ligne avec GitHub Pages

1. Dépôt GitHub → **Settings** → **Pages**.
2. *Source* : **Deploy from a branch** ; branche `main`, dossier `/ (root)` ; **Save**.
3. Après une à deux minutes, la page est disponible à
   `https://riozakies.github.io/echantillon/`.

La page charge `echantillon.py` depuis le même dépôt : toute modification du module
est donc prise en compte automatiquement par l'interface.

### Tester en local

```bash
python -m http.server 8000
# puis ouvrir http://localhost:8000
```
