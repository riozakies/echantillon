# Manuel d'utilisation

Ce manuel décrit l'utilisation de la page de tirage d'échantillon (`index.html`).

## 1. Ouvrir la page

Ouvrir l'adresse de la page dans Chrome, Firefox ou Edge.

Au premier chargement, le navigateur télécharge l'environnement de calcul
(environ 25 Mo). Le bouton **Lancer** affiche « Chargement » pendant ce temps.
Les ouvertures suivantes sont plus rapides.

Une connexion internet est nécessaire. Les données ne sont envoyées à aucun
serveur : tout le calcul se fait sur l'ordinateur de l'utilisateur.

## 2. Préparer la base de sondage

La base de sondage est un tableau avec une ligne par unité (ménage, zone de
dénombrement, établissement…) et une colonne par variable.

| Format | Remarques |
|---|---|
| Excel (.xlsx, .xls, .ods) | La première ligne de la feuille contient les noms de colonnes. |
| CSV (.csv, .txt) | Séparateur virgule, point-virgule ou tabulation, détecté automatiquement. Avec le point-virgule, la virgule décimale est acceptée. |

Points à vérifier avant le tirage :

- les noms de colonnes sont sur la première ligne, sans lignes de titre au-dessus ;
- la variable de taille (ménages, population…) est numérique et ne contient pas que des zéros ;
- la variable de stratification est renseignée pour chaque ligne. Les lignes sans valeur sont exclues du tirage stratifié, et un message l'indique.

## 3. Remplir le formulaire

### Base de sondage et feuille

Cliquer sur **Base de sondage** et choisir le fichier, ou le glisser sur le champ.
Pour un fichier Excel à plusieurs feuilles, choisir la feuille dans **Feuille**.
Les listes de colonnes se remplissent une fois le fichier lu.

### Type d'échantillonnage

| Type | Principe | Champs à remplir |
|---|---|---|
| Systématique à probabilités égales | Une unité toutes les N/n lignes, après un départ aléatoire. | Taille de l'échantillon |
| Systématique à probabilités inégales (PPT) | Probabilité de tirage proportionnelle à une variable de taille. Une unité dont la probabilité dépasse 1 est retenue d'office. | Taille de l'échantillon, Variable de taille |
| Stratifié | Tirage systématique indépendant dans chaque strate. | Taille de l'échantillon, Variable de stratification, Allocation entre strates |

Pour le tirage stratifié :

- **Allocation entre strates** :
  - *Proportionnelle aux effectifs* : chaque strate reçoit n × N<sub>h</sub> / N unités ;
  - *Effectif × somme d'une variable* : la part de la strate est proportionnelle à
    N<sub>h</sub> × (somme de la variable d'allocation dans la strate). Choisir alors la
    **Variable d'allocation**.
- **Probabilités inégales dans les strates** : activé, le tirage dans chaque strate est
  PPT selon la **Variable de taille** choisie ; désactivé, il est à probabilités égales.

Les tailles par strate sont arrondies par la méthode de Hamilton (plus forts restes),
de sorte que leur somme soit égale à n.

### Taille de l'échantillon

Nombre d'unités à tirer (n). Si n est supérieur ou égal au nombre d'unités, toutes
les unités sont retenues.

### Graine aléatoire

Nombre entier qui fixe le point de départ aléatoire. Avec la même base, les mêmes
paramètres et la même graine, on obtient toujours le même échantillon : noter la
graine utilisée pour pouvoir reproduire le tirage.

En tirage systématique, changer la graine ne fait que décaler le point de départ.
Les échantillons obtenus se ressemblent donc beaucoup : c'est normal.

### Trier la base par (facultatif)

En tirage systématique, l'ordre des lignes compte. Trier la base par une variable
géographique (région, département, arrondissement…) répartit l'échantillon sur
toutes ses modalités : c'est une stratification implicite.

### Nom et format du fichier de sortie

- **Nom du fichier de sortie** (facultatif) : sans extension. Par défaut,
  `echantillon_` suivi du nom de la base.
- **Format du fichier de sortie** : `.xlsx`, `.csv` ou `.pdf`.

## 4. Lancer le tirage

Cliquer sur **Lancer**. Le résultat s'affiche sous le formulaire :

- le nombre d'unités tirées, le nombre d'unités de la base, le taux de sondage et la somme des poids ;
- les messages éventuels (lignes exclues, tirage impossible…) ;
- pour un tirage stratifié, la répartition par strate (N<sub>h</sub> : unités dans la base, n<sub>h</sub> : unités tirées) ;
- la liste des unités tirées.

Le format ou le nom du fichier peuvent être changés après le tirage, sans le relancer.

## 5. Enregistrer l'échantillon

Cliquer sur le bouton de téléchargement, qui porte le nom du fichier.

| Format | Contenu |
|---|---|
| .xlsx | Feuille *Echantillon* ; feuille *Strates* pour un tirage stratifié. |
| .csv | Échantillon, séparateur point-virgule, virgule décimale, encodage UTF-8 (s'ouvre directement dans Excel). |
| .pdf | Paramètres du tirage, liste des unités tirées et répartition par strate. |

Colonnes ajoutées à l'échantillon :

| Colonne | Signification |
|---|---|
| `ligne_base` | Numéro de la ligne dans la base de sondage d'origine. |
| `proba_inclusion` | Probabilité d'inclusion de l'unité. |
| `poids_sondage` | Poids de sondage, égal à 1 / probabilité d'inclusion. |

## 6. Messages et problèmes fréquents

| Message ou symptôme | Cause et solution |
|---|---|
| Le bouton reste sur « Chargement » | Connexion lente ou site cdn.jsdelivr.net bloqué. Patienter, puis recharger la page (Ctrl+F5). |
| « Python n'a pas pu être chargé » | Le téléchargement a échoué. Vérifier la connexion, désactiver le bloqueur de publicité, recharger la page. |
| « Lecture impossible » | Fichier vide, protégé par mot de passe ou dans un format non pris en charge. |
| « Seulement 0 unités ont un poids > 0 » | La variable de taille ne contient que des zéros ou des valeurs non numériques. Choisir une autre variable. |
| « … ligne(s) sans valeur pour la strate … ont été exclues » | Certaines lignes n'ont pas de valeur de strate. Les compléter dans la base si elles doivent être tirées. |
| « Les strates sont nombreuses et ne permettent pas de repartir… » | L'allocation n'a pas pu être répartie. Augmenter n ou regrouper des strates. |
| Une strate a 0 unité tirée | Avec l'allocation proportionnelle, une petite strate peut recevoir 0 unité. Augmenter n ou regrouper les petites strates. |

## 7. Utilisation en Python

Les mêmes fonctions sont disponibles dans le module :

```python
%pip install git+https://github.com/riozakies/echantillon.git
import echantillon as ech

# Systématique à probabilités égales
select, ech_df = ech.select_sys(base, 50, random_state=42)

# Systématique PPT
select, ech_df = ech.select_sys(base, 50, poids="menages", random_state=42)

# Stratifié, allocation proportionnelle, PPT dans les strates
select, ech_df = ech.select_sys_complete(base, 50, "region", poids_u="menages",
                                         random_state=42, share=0)
```
