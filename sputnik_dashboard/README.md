# 📊 Sputnik News Africa - Dashboard Analytique

Dashboard interactif de visualisation de données pour l'analyse comparative des corpus médiatiques Macron/France vs Poutine/Russie (2024-2025).

## 🎨 Fonctionnalités

### KPIs Dynamiques
- Total d'articles publiés
- Mots-clés uniques extraits
- Période de couverture
- Entités nommées totales

### Visualisations Interactives (10 graphiques)

1. **Comparaison des Protagonistes** - Bar chart comparatif des mentions principales
2. **Évolution Temporelle** - Line chart de l'évolution des publications
3. **Top Mots-clés Diverging** - Graphique divergent des mots-clés principaux
4. **Distribution Géographique** - Cartographie des lieux mentionnés
5. **Distribution des Entités** - Répartition des entités nommées (lieux, organisations, personnes)
6. **Réseau de Co-occurrence** - Graph network des relations entre entités
7. **Timeline des Personnalités** - Évolution temporelle des mentions de personnalités
8. **Heatmap Thématique** - Carte de chaleur mensuelle des thèmes
9. **Hiérarchie Thématique** - Sunburst des catégories thématiques
10. **Évolution des Catégories** - Area chart de l'évolution des types d'entités

### Filtres Interactifs
- **Sélection du corpus** : Macron/France, Poutine/Russie ou les deux
- **Période temporelle** : Toute la période, 2024, 2025, derniers 6/3 mois
- **Catégorie d'entités** : Keywords, Lieux, Organisations, Personnes
- **Nombre d'éléments** : Slider de 5 à 50 éléments

## 🚀 Installation et Lancement

### Prérequis
- Python 3.8+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement du dashboard

```bash
python dashboard_app.py
```

Le dashboard sera accessible à l'adresse : **http://localhost:8050**

## 📁 Structure des Données

Le dashboard utilise deux fichiers JSON contenant les corpus prétraités :
- `fr_sputniknews_africa-france-macron.json` (Corpus Macron/France)
- `fr_sputniknews_africa-russie-poutine.json` (Corpus Poutine/Russie)

### Format des données
```json
{
  "metadata": {
    "all": {
      "kws": {...},  // Mots-clés
      "loc": {...},  // Lieux
      "org": {...},  // Organisations
      "per": {...}   // Personnes
    },
    "year": {...},
    "month": {...},
    "day": {...}
  },
  "data": {
    "YYYY": {
      "MM": {
        "DD": [...]  // Articles du jour
      }
    }
  }
}
```

## 🎨 Design

Le dashboard utilise un design moderne inspiré de **shadcn/ui** avec :
- Palette de couleurs sombre élégante
- Typographie claire et moderne
- Composants avec ombres et transitions fluides
- Design responsive
- Thème cohérent pour toutes les visualisations Plotly

### Palette de couleurs
- **Primary** : #0ea5e9 (Bleu cyan)
- **Secondary** : #8b5cf6 (Violet)
- **Accent** : #f59e0b (Orange)
- **Success** : #10b981 (Vert)
- **Macron/France** : #ef4444 (Rouge)
- **Poutine/Russie** : #0ea5e9 (Bleu)

## 🔧 Architecture Technique

### Technologies utilisées
- **Dash** : Framework web pour applications analytiques
- **Plotly** : Bibliothèque de visualisation interactive
- **Pandas** : Manipulation et analyse de données
- **NetworkX** : Création de graphes de réseaux
- **NumPy** : Calculs numériques

### Callbacks
Le dashboard utilise un callback principal qui met à jour toutes les visualisations simultanément en fonction des filtres sélectionnés, assurant une cohérence et une interactivité fluide.

## 📊 Analyses Disponibles

### Analyse Comparative
- Comparaison directe entre les deux corpus
- Identification des différences de couverture médiatique
- Analyse des thématiques communes et spécifiques

### Analyse Temporelle
- Évolution des publications dans le temps
- Identification des pics d'actualité
- Tendances mensuelles et annuelles

### Analyse Sémantique
- Extraction des mots-clés principaux
- Co-occurrence d'entités
- Hiérarchie thématique

### Analyse Géopolitique
- Distribution géographique des mentions
- Focus sur les zones d'intérêt
- Relations entre pays et organisations

## 👥 Auteurs

Projet d'analyse de données médiatiques - Sputnik News Africa

## 📝 Licence

Ce projet est développé dans un cadre éducatif et analytique.
