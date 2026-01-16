# 🎯 GUIDE D'UTILISATION - Dashboard Sputnik News Africa

## 📋 Table des Matières
1. [Installation Rapide](#installation-rapide)
2. [Utilisation du Dashboard](#utilisation-du-dashboard)
3. [Comprendre les Visualisations](#comprendre-les-visualisations)
4. [Filtres et Interactivité](#filtres-et-interactivité)
5. [Interprétation des Résultats](#interprétation-des-résultats)
6. [Dépannage](#dépannage)

---

## 🚀 Installation Rapide

### Étape 1 : Prérequis
```bash
# Vérifier la version de Python (3.8+ requis)
python3 --version
```

### Étape 2 : Installation des dépendances
```bash
cd sputnik_dashboard
pip install -r requirements.txt
```

### Étape 3 : Lancement
```bash
# Option 1 : Avec le script de lancement (recommandé)
python3 launch.py

# Option 2 : Directement
python3 dashboard_app.py
```

### Étape 4 : Accéder au dashboard
Ouvrez votre navigateur et allez à : **http://localhost:8050**

---

## 🎨 Utilisation du Dashboard

### Interface Principale

Le dashboard est divisé en plusieurs sections :

#### 1️⃣ **Header** (Haut de page)
- Titre du dashboard
- Description courte du projet

#### 2️⃣ **KPIs** (Indicateurs clés)
- **Total Articles** : Nombre total d'articles analysés
- **Mots-clés Uniques** : Nombre de mots-clés différents extraits
- **Période Analysée** : Durée de la couverture médiatique
- **Entités Totales** : Nombre d'entités nommées (lieux, organisations, personnes)

#### 3️⃣ **Section Filtres**
- **Sélection du corpus** : Choisir entre Macron/France, Poutine/Russie ou les deux
- **Période temporelle** : Filtrer par période (toute la période, 2024, 2025, etc.)
- **Catégorie d'entités** : Choisir le type d'entités à analyser
- **Nombre d'éléments** : Ajuster le nombre d'éléments affichés (5-50)

#### 4️⃣ **Visualisations** (10 graphiques interactifs)
Chaque visualisation est interactive :
- **Hover** : Survoler pour voir les détails
- **Zoom** : Cliquer-glisser pour zoomer
- **Pan** : Maintenir Shift + cliquer-glisser pour se déplacer
- **Réinitialiser** : Double-clic pour réinitialiser la vue

---

## 📊 Comprendre les Visualisations

### 1️⃣ Comparaison des Protagonistes
**Type** : Bar Chart Groupé  
**Objectif** : Comparer les mentions des 4 protagonistes principaux (Macron, Poutine, France, Russie) entre les deux corpus

**Interprétation** :
- Les barres rouges = Corpus Macron/France
- Les barres bleues = Corpus Poutine/Russie
- Plus la barre est haute, plus l'entité est mentionnée

**Exemple d'analyse** :
- Si "Poutine" a une barre bleue très haute : Le corpus Poutine/Russie se concentre sur lui
- Si "Macron" a une barre rouge similaire à la bleue : Macron est mentionné dans les deux corpus

---

### 2️⃣ Évolution Temporelle des Publications
**Type** : Line Chart  
**Objectif** : Voir l'évolution du nombre d'articles publiés mois par mois

**Interprétation** :
- **Pics** : Moments d'actualité intense (événements majeurs)
- **Creux** : Périodes plus calmes
- **Tendance** : Augmentation ou diminution de la couverture

**Exemple d'analyse** :
- Un pic en février 2024 peut indiquer un événement important (guerre, sommet, etc.)
- Une tendance à la hausse montre un intérêt croissant

---

### 3️⃣ Top Mots-clés (Diverging Bar Chart)
**Type** : Diverging Horizontal Bar Chart  
**Objectif** : Comparer visuellement les mots-clés les plus fréquents de chaque corpus

**Interprétation** :
- **Côté gauche (rouge)** : Top mots-clés du corpus Macron/France
- **Côté droit (bleu)** : Top mots-clés du corpus Poutine/Russie
- **Mots au centre** : Peu de différence entre les corpus
- **Mots éloignés** : Spécifiques à un corpus

**Exemple d'analyse** :
- "Ukraine" très à droite → Très présent dans le corpus Poutine
- "Afrique" équilibré → Présent dans les deux corpus

---

### 4️⃣ Distribution Géographique
**Type** : Horizontal Bar Chart Groupé  
**Objectif** : Identifier les zones géographiques les plus mentionnées

**Interprétation** :
- Compare les 15 lieux les plus mentionnés dans chaque corpus
- Identifie les zones d'intérêt géopolitique

**Exemple d'analyse** :
- "Mali" très présent → Focus sur le Sahel
- "Ukraine" dominant → Contexte de la guerre

---

### 5️⃣ Distribution des Entités Nommées
**Type** : Grouped Bar Chart  
**Objectif** : Comparer le nombre d'entités uniques (lieux, organisations, personnes) entre les corpus

**Interprétation** :
- Plus de personnes = Focus sur les personnalités
- Plus d'organisations = Analyse institutionnelle
- Plus de lieux = Couverture géographique large

---

### 6️⃣ Réseau de Co-occurrence
**Type** : Network Graph  
**Objectif** : Visualiser les relations entre les mots-clés les plus fréquents

**Interprétation** :
- **Nœuds (cercles)** : Mots-clés
- **Liens (lignes)** : Co-occurrence (apparaissent ensemble)
- **Couleur** : Nombre de connexions
- **Clusters** : Groupes thématiques

**Exemple d'analyse** :
- Cluster "guerre-ukraine-russie" = Thème militaire
- Cluster "france-macron-afrique" = Politique africaine

---

### 7️⃣ Timeline des Personnalités Politiques
**Type** : Scatter Plot avec taille variable  
**Objectif** : Voir l'évolution des mentions de personnalités politiques dans le temps

**Interprétation** :
- **Taille des bulles** : Fréquence des mentions
- **Position temporelle** : Quand la personnalité est mentionnée
- **Couleur** : Corpus (rouge = Macron, bleu = Poutine)

---

### 8️⃣ Heatmap Thématique Mensuelle
**Type** : Heatmap  
**Objectif** : Visualiser l'intensité des thèmes par mois

**Interprétation** :
- **Couleur claire** : Peu de mentions
- **Couleur foncée** : Beaucoup de mentions
- **Patterns** : Saisonnalité ou événements récurrents

---

### 9️⃣ Hiérarchie Thématique (Sunburst)
**Type** : Sunburst Chart  
**Objectif** : Visualiser la hiérarchie des thèmes et sous-thèmes

**Interprétation** :
- **Centre** : Thèmes principaux
- **Anneaux extérieurs** : Sous-thèmes
- **Taille des segments** : Importance du thème

**Navigation** :
- Cliquer sur un segment pour zoomer
- Cliquer au centre pour dézoomer

---

### 🔟 Évolution des Catégories d'Entités
**Type** : Stacked Area Chart  
**Objectif** : Voir l'évolution des différents types d'entités dans le temps

**Interprétation** :
- **Hauteur totale** : Diversité des entités
- **Proportions** : Quel type d'entité domine
- **Tendances** : Évolution de la couverture

---

## 🎛️ Filtres et Interactivité

### Comment utiliser les filtres ?

#### 1. **Sélectionner le Corpus**
```
🔴 Macron/France → Affiche uniquement les données du corpus Macron
🔵 Poutine/Russie → Affiche uniquement les données du corpus Poutine
🟣 Les deux corpus → Compare les deux (recommandé)
```

#### 2. **Choisir la Période**
```
📅 Toute la période → Avril 2024 - Octobre 2025 (19 mois)
📆 2024 uniquement → Données de 2024
📆 2025 uniquement → Données de 2025
🗓️ 6 derniers mois → Focus sur la période récente
🗓️ 3 derniers mois → Analyse des actualités très récentes
```

#### 3. **Catégorie d'Entités**
```
🔑 Mots-clés → Termes lemmatisés (forme de base)
📍 Lieux → Pays, villes, régions mentionnés
🏢 Organisations → Institutions, entreprises, partis
👤 Personnes → Personnalités citées
```

#### 4. **Nombre d'Éléments (Slider)**
```
5  → Affiche le Top 5 (vue très synthétique)
20 → Affiche le Top 20 (valeur par défaut, bon équilibre)
50 → Affiche le Top 50 (vue détaillée)
```

### Synchronisation Automatique

**Important** : Tous les graphiques se mettent à jour automatiquement lorsque vous changez un filtre. Il n'y a pas besoin de cliquer sur un bouton "Appliquer".

---

## 🧠 Interprétation des Résultats

### Questions d'Analyse

#### 1. **Quels sont les biais de chaque corpus ?**
→ Comparer les top mots-clés et les protagonistes mentionnés

#### 2. **Y a-t-il des événements marquants ?**
→ Regarder les pics dans l'évolution temporelle

#### 3. **Quelles zones géographiques sont prioritaires ?**
→ Analyser la distribution géographique

#### 4. **Qui sont les acteurs clés ?**
→ Examiner la timeline des personnalités

#### 5. **Quels thèmes dominent ?**
→ Explorer la hiérarchie thématique (Sunburst)

### Cas d'Usage Pratiques

#### Analyse Politique
1. Sélectionner "Les deux corpus"
2. Période "Toute la période"
3. Observer les différences dans la visualisation des protagonistes
4. Analyser la timeline des personnalités pour voir qui domine le discours

#### Analyse Géopolitique
1. Choisir "Lieux" dans la catégorie d'entités
2. Observer la distribution géographique
3. Identifier les zones de tension (Ukraine, Sahel, etc.)

#### Analyse Temporelle
1. Filtrer par période (ex: 2024)
2. Observer l'évolution temporelle
3. Corréler les pics avec des événements connus

---

## 🔧 Dépannage

### Le dashboard ne se lance pas
```bash
# Vérifier que les dépendances sont installées
pip install -r requirements.txt --break-system-packages

# Vérifier les ports utilisés
netstat -tuln | grep 8050

# Si le port est occupé, utiliser un autre port
python3 dashboard_app.py  # puis modifier le port dans le code
```

### Les graphiques ne s'affichent pas
1. Vérifier la console du navigateur (F12)
2. Rafraîchir la page (Ctrl+R)
3. Vider le cache (Ctrl+Shift+R)

### Les filtres ne fonctionnent pas
1. Vérifier que JavaScript est activé
2. Tester avec un autre navigateur (Chrome, Firefox recommandés)

### Données manquantes
```bash
# Vérifier que les fichiers JSON sont présents
ls -lh /mnt/project/*.json
ls -lh /mnt/user-data/uploads/*.json
```

---

## 💡 Conseils Pro

1. **Performance** : Pour de meilleures performances, commencez avec "Top 20" puis ajustez
2. **Comparaison** : Toujours utiliser "Les deux corpus" pour des analyses comparatives
3. **Export** : Utilisez la barre d'outils Plotly (icône caméra) pour exporter les graphiques
4. **Zoom** : Double-cliquez pour réinitialiser le zoom sur un graphique
5. **Fullscreen** : La plupart des navigateurs permettent F11 pour le mode plein écran

---

## 📞 Support

Pour toute question ou problème :
1. Vérifiez d'abord la section Dépannage
2. Consultez le README.md pour les détails techniques
3. Vérifiez les logs dans le terminal où le dashboard est lancé

---

## ✨ Fonctionnalités Avancées

### Export de Graphiques
Survolez un graphique et cliquez sur l'icône 📷 pour exporter en PNG

### Isolation de Séries
Dans les graphiques avec légende, cliquez sur un élément de la légende pour l'isoler

### Sélection Multiple
Double-cliquez sur un élément de légende pour isoler, simple-clic pour ajouter/retirer

---

**Bon analyse ! 📊✨**
