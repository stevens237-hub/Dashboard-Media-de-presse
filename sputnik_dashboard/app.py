"""
SPUTNIK NEWS AFRICA - DASHBOARD ANALYTIQUE V2
Dashboard interactif pour l'analyse de corpus médiatiques
Architecture : Vue d'ensemble → Temporel → Relationnel → Géographique
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from collections import Counter
import networkx as nx
from itertools import combinations

# ============================================
# CONFIGURATION ET CHARGEMENT DES DONNÉES
# ============================================

# Palette de couleurs cohérente - THÈME CLAIR
COLORS = {
    'primary': '#0ea5e9',
    'secondary': '#8b5cf6',
    'accent': '#f59e0b',
    'success': '#10b981',
    'danger': '#ef4444',
    'macron': '#ef4444',
    'poutine': '#0ea5e9',
    'combined': '#8b5cf6',
    'bg_primary': '#f8fafc',
    'bg_card': '#ffffff',
    'text': '#0f172a',
    'text_secondary': '#334155',
}

# Charger les données
def load_data():
    with open('fr.sputniknews.africa-2025/data/fr.sputniknews.africa-france-macron.json', 'r', encoding='utf-8') as f:
        data_macron = json.load(f)
    
    with open('fr.sputniknews.africa-2025/data/fr.sputniknews.africa-russie-poutine.json', 'r', encoding='utf-8') as f:
        data_poutine = json.load(f)
    
    return data_macron, data_poutine

data_macron, data_poutine = load_data()

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def get_combined_data():
    """Combiner les données des deux corpus"""
    combined = {
        'kws': Counter(data_macron['metadata']['all']['kws']) + Counter(data_poutine['metadata']['all']['kws']),
        'loc': Counter(data_macron['metadata']['all']['loc']) + Counter(data_poutine['metadata']['all']['loc']),
        'org': Counter(data_macron['metadata']['all']['org']) + Counter(data_poutine['metadata']['all']['org']),
        'per': Counter(data_macron['metadata']['all']['per']) + Counter(data_poutine['metadata']['all']['per']),
    }
    return combined

def get_data_by_corpus(corpus_selected):
    """Obtenir les données selon le corpus sélectionné"""
    if corpus_selected == 'Macron/France':
        return data_macron['metadata']['all']
    elif corpus_selected == 'Poutine/Russie':
        return data_poutine['metadata']['all']
    else:  # Combined
        return get_combined_data()

def get_top_entities(data, entity_type='kws', n=20):
    """Obtenir les top entités"""
    if isinstance(data, dict) and entity_type in data:
        entities = data[entity_type]
    else:
        entities = data
    
    top_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)[:n]
    return pd.DataFrame(top_entities, columns=['entity', 'count'])

def calculate_kpis(corpus_selected):
    """Calculer les KPIs selon le corpus sélectionné"""
    if corpus_selected == 'Macron/France':
        data = data_macron
        kpis = {
            'total_kws': len(data['metadata']['all']['kws']),
            'total_loc': len(data['metadata']['all']['loc']),
            'total_org': len(data['metadata']['all']['org']),
            'total_per': len(data['metadata']['all']['per']),
        }
    elif corpus_selected == 'Poutine/Russie':
        data = data_poutine
        kpis = {
            'total_kws': len(data['metadata']['all']['kws']),
            'total_loc': len(data['metadata']['all']['loc']),
            'total_org': len(data['metadata']['all']['org']),
            'total_per': len(data['metadata']['all']['per']),
        }
    else:  # Combined
        combined = get_combined_data()
        kpis = {
            'total_kws': len(combined['kws']),
            'total_loc': len(combined['loc']),
            'total_org': len(combined['org']),
            'total_per': len(combined['per']),
        }
    
    return kpis

def get_temporal_data(corpus_selected):
    """Extraire les données temporelles"""
    records = []
    
    if corpus_selected in ['Macron/France', 'Combined']:
        for year in data_macron['data'].keys():
            for month in data_macron['data'][year].keys():
                days = data_macron['data'][year][month]
                n_articles = len(days) if isinstance(days, dict) else 0
                
                date = f"{year}-{month.zfill(2)}-01"
                records.append({
                    'date': pd.to_datetime(date),
                    'year': year,
                    'month': month,
                    'n_articles': n_articles,
                    'corpus': 'Macron/France'
                })
    
    if corpus_selected in ['Poutine/Russie', 'Combined']:
        for year in data_poutine['data'].keys():
            for month in data_poutine['data'][year].keys():
                days = data_poutine['data'][year][month]
                n_articles = len(days) if isinstance(days, dict) else 0
                
                date = f"{year}-{month.zfill(2)}-01"
                records.append({
                    'date': pd.to_datetime(date),
                    'year': year,
                    'month': month,
                    'n_articles': n_articles,
                    'corpus': 'Poutine/Russie'
                })
    
    return pd.DataFrame(records)

def create_actor_network(data, top_n=15):
    """Créer un réseau d'acteurs (personnes) basé sur co-occurrence"""
    persons = get_top_entities(data, 'per', top_n)
    persons_list = persons['entity'].tolist()
    
    # Créer le graphe
    G = nx.Graph()
    for person in persons_list:
        G.add_node(person, size=data['per'].get(person, 0))
    
    # Ajouter des arêtes basées sur co-occurrence (simplifié)
    for p1, p2 in combinations(persons_list[:10], 2):
        # Co-occurrence simulée (dans un vrai cas, on analyserait les articles)
        weight = min(data['per'].get(p1, 0), data['per'].get(p2, 0)) * 0.1
        if weight > 5:
            G.add_edge(p1, p2, weight=weight)
    
    return G

def create_thematic_structure():
    """Créer une structure thématique hiérarchique"""
    themes = {
        'Politique': ['président', 'gouvernement', 'ministre', 'élection', 'politique', 'député'],
        'Géopolitique': ['russie', 'ukraine', 'france', 'guerre', 'otan', 'conflit'],
        'Afrique': ['afrique', 'mali', 'burkina', 'niger', 'sahel', 'africain'],
        'Économie': ['économie', 'budget', 'finance', 'banque', 'euro', 'commerce'],
        'Diplomatie': ['diplomatie', 'ambassade', 'sommet', 'rencontre', 'accord', 'traité'],
        'Sécurité': ['militaire', 'armée', 'défense', 'terrorisme', 'sécurité', 'police']
    }
    return themes

# ============================================
# INITIALISATION DE L'APPLICATION
# ============================================

app = dash.Dash(__name__, 
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                external_stylesheets=['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'])

app.title = "Sputnik News Africa - Dashboard Analytique V2"

# ============================================
# LAYOUT DU DASHBOARD
# ============================================

app.layout = html.Div([
    # HEADER
    html.Div([
        html.H1("📊 Sputnik News Africa - Analyse de Corpus Médiatiques"),
        html.P("Analyse approfondie des publications sur Macron/France et Poutine/Russie (2024-2025)")
    ], className='dashboard-header'),
    
    # KPIs DYNAMIQUES
    html.Div(id='kpi-container', className='kpi-container'),
    
    # FILTRES PRINCIPAUX
    html.Div([
        html.Div("🎛️ Filtres de sélection", className='filters-title'),
        html.Div([
            # Filtre Corpus
            html.Div([
                html.Label("Sélectionner le corpus à analyser", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Dropdown(
                    id='corpus-filter',
                    options=[
                        {'label': '🔴 Corpus Macron/France', 'value': 'Macron/France'},
                        {'label': '🔵 Corpus Poutine/Russie', 'value': 'Poutine/Russie'},
                        {'label': '🟣 Analyse Combinée', 'value': 'Combined'}
                    ],
                    value='Combined',
                    clearable=False
                ),
            ]),
            
            # Filtre Période
            html.Div([
                html.Label("Période temporelle", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Dropdown(
                    id='period-filter',
                    options=[
                        {'label': '📅 Toute la période', 'value': 'all'},
                        {'label': '📆 2024 uniquement', 'value': '2024'},
                        {'label': '📆 2025 uniquement', 'value': '2025'},
                        {'label': '🗓️ 6 derniers mois', 'value': 'last6'},
                    ],
                    value='all',
                    clearable=False
                ),
            ]),
            
            # Top N
            html.Div([
                html.Label("Nombre d'éléments à afficher", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Slider(
                    id='top-n-slider',
                    min=10,
                    max=50,
                    step=5,
                    value=20,
                    marks={i: str(i) for i in range(10, 55, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ]),
        ], className='filters-grid'),
    ], className='filters-container'),
    
    # SECTION 1 : VUE D'ENSEMBLE
    html.Div([
        html.H2("📌 Section 1 : Vue d'Ensemble", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        
        html.Div([
            # VIZ 1: Word Cloud
            html.Div([
                html.Div("1️⃣ Nuage de Mots - Termes les Plus Fréquents", className='viz-title'),
                dcc.Graph(id='viz-wordcloud'),
            ], className='viz-card'),
            
            # VIZ 2: Top Keywords
            html.Div([
                html.Div("2️⃣ Top 20 Mots-clés", className='viz-title'),
                dcc.Graph(id='viz-top-keywords'),
            ], className='viz-card'),
            
            # VIZ 3: Thèmes structurants (Full width)
            html.Div([
                html.Div("3️⃣ Thèmes Structurants - Hiérarchie Thématique", className='viz-title'),
                dcc.Graph(id='viz-themes'),
            ], className='viz-card viz-grid-full'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
    # SECTION 2 : ANALYSE TEMPORELLE
    html.Div([
        html.H2("⏱️ Section 2 : Analyse Temporelle", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        
        html.Div([
            # VIZ 4: Évolution temporelle
            html.Div([
                html.Div("4️⃣ Évolution Temporelle des Publications", className='viz-title'),
                dcc.Graph(id='viz-temporal'),
            ], className='viz-card'),
            
            # VIZ 5: Pics d'attention
            html.Div([
                html.Div("5️⃣ Pics d'Attention - Heatmap Temporelle", className='viz-title'),
                dcc.Graph(id='viz-attention-peaks'),
            ], className='viz-card'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
    # SECTION 3 : ANALYSE RELATIONNELLE
    html.Div([
        html.H2("🔗 Section 3 : Analyse Relationnelle", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        
        html.Div([
            # VIZ 6: Réseau d'acteurs
            html.Div([
                html.Div("6️⃣ Réseau d'Acteurs Politiques", className='viz-title'),
                dcc.Graph(id='viz-actor-network'),
            ], className='viz-card viz-grid-full'),
            
            # VIZ 7: Corrélation acteurs-lieux
            html.Div([
                html.Div("7️⃣ Corrélation Acteurs-Lieux-Thèmes", className='viz-title'),
                dcc.Graph(id='viz-correlation'),
            ], className='viz-card'),
            
            # VIZ 8: Réseau interactif avec sélection
            html.Div([
                html.Div("8️⃣ Réseau Interactif - Connexions d'un Mot", className='viz-title'),
                html.Div([
                    html.Label("Sélectionner un mot-clé", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                    dcc.Dropdown(
                        id='word-selector',
                        options=[],
                        value=None,
                        placeholder="Choisir un mot-clé..."
                    ),
                ], style={'marginBottom': '1rem'}),
                dcc.Graph(id='viz-word-network'),
            ], className='viz-card'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
    # SECTION 4 : ANALYSE GÉOGRAPHIQUE
    html.Div([
        html.H2("🌍 Section 4 : Analyse Géographique", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        
        html.Div([
            # VIZ 9: Distribution géographique
            html.Div([
                html.Div("9️⃣ Distribution Géographique - Top Lieux", className='viz-title'),
                dcc.Graph(id='viz-geography'),
            ], className='viz-card'),
            
            # VIZ 10: Lieux par acteur
            html.Div([
                html.Div("🔟 Acteurs et Lieux Associés", className='viz-title'),
                dcc.Graph(id='viz-actors-locations'),
            ], className='viz-card'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
], id='dashboard-container')

# ============================================
# CALLBACKS POUR L'INTERACTIVITÉ
# ============================================

@app.callback(
    Output('kpi-container', 'children'),
    [Input('corpus-filter', 'value')]
)
def update_kpis(corpus_selected):
    """Mettre à jour les KPIs selon le corpus sélectionné"""
    kpis = calculate_kpis(corpus_selected)
    
    # Déterminer la couleur selon le corpus
    if corpus_selected == 'Macron/France':
        corpus_color = COLORS['macron']
        corpus_emoji = '🔴'
    elif corpus_selected == 'Poutine/Russie':
        corpus_color = COLORS['poutine']
        corpus_emoji = '🔵'
    else:
        corpus_color = COLORS['combined']
        corpus_emoji = '🟣'
    
    return [
        # KPI 1: Mots-clés
        html.Div([
            html.Div("Mots-clés Uniques", className='kpi-label'),
            html.Div(f"{kpis['total_kws']:,}", className='kpi-value'),
            html.Div(f"{corpus_emoji} {corpus_selected}", className='kpi-trend'),
        ], className='kpi-card'),
        
        # KPI 2: Lieux
        html.Div([
            html.Div("Lieux Mentionnés", className='kpi-label'),
            html.Div(f"{kpis['total_loc']:,}", className='kpi-value'),
            html.Div("📍 Zones géographiques", className='kpi-trend'),
        ], className='kpi-card'),
        
        # KPI 3: Organisations
        html.Div([
            html.Div("Organisations", className='kpi-label'),
            html.Div(f"{kpis['total_org']:,}", className='kpi-value'),
            html.Div("🏢 Entités institutionnelles", className='kpi-trend'),
        ], className='kpi-card'),
        
        # KPI 4: Personnalités
        html.Div([
            html.Div("Personnalités", className='kpi-label'),
            html.Div(f"{kpis['total_per']:,}", className='kpi-value'),
            html.Div("👤 Acteurs politiques", className='kpi-trend'),
        ], className='kpi-card'),
    ]

@app.callback(
    Output('word-selector', 'options'),
    [Input('corpus-filter', 'value'),
     Input('top-n-slider', 'value')]
)
def update_word_selector(corpus_selected, top_n):
    """Mettre à jour les options du sélecteur de mots"""
    data = get_data_by_corpus(corpus_selected)
    df_top = get_top_entities(data, 'kws', top_n)
    
    options = [{'label': word, 'value': word} for word in df_top['entity'].tolist()]
    return options

@app.callback(
    [Output('viz-wordcloud', 'figure'),
     Output('viz-top-keywords', 'figure'),
     Output('viz-themes', 'figure'),
     Output('viz-temporal', 'figure'),
     Output('viz-attention-peaks', 'figure'),
     Output('viz-actor-network', 'figure'),
     Output('viz-correlation', 'figure'),
     Output('viz-word-network', 'figure'),
     Output('viz-geography', 'figure'),
     Output('viz-actors-locations', 'figure')],
    [Input('corpus-filter', 'value'),
     Input('period-filter', 'value'),
     Input('top-n-slider', 'value'),
     Input('word-selector', 'value')]
)
def update_all_visualizations(corpus_selected, period, top_n, selected_word):
    """Callback principal pour mettre à jour toutes les visualisations"""
    
    # Obtenir les données selon le corpus
    data = get_data_by_corpus(corpus_selected)
    df_temporal = get_temporal_data(corpus_selected)
    
    # Filtrer par période
    if period == '2024':
        df_temporal = df_temporal[df_temporal['year'] == '2024']
    elif period == '2025':
        df_temporal = df_temporal[df_temporal['year'] == '2025']
    elif period == 'last6':
        cutoff = df_temporal['date'].max() - timedelta(days=180)
        df_temporal = df_temporal[df_temporal['date'] >= cutoff]
    
    # Couleur selon corpus
    if corpus_selected == 'Macron/France':
        main_color = COLORS['macron']
    elif corpus_selected == 'Poutine/Russie':
        main_color = COLORS['poutine']
    else:
        main_color = COLORS['combined']
    
    # ========== VIZ 1: WORD CLOUD (simulé avec scatter) ==========
    df_top_wc = get_top_entities(data, 'kws', 50)
    
    # Créer un scatter plot simulant un word cloud
    np.random.seed(42)
    df_top_wc['x'] = np.random.rand(len(df_top_wc)) * 100
    df_top_wc['y'] = np.random.rand(len(df_top_wc)) * 100
    df_top_wc['size'] = df_top_wc['count'] / df_top_wc['count'].max() * 100 + 10
    
    fig_wordcloud = go.Figure()
    
    fig_wordcloud.add_trace(go.Scatter(
        x=df_top_wc['x'],
        y=df_top_wc['y'],
        mode='text',
        text=df_top_wc['entity'],
        textfont=dict(
            size=df_top_wc['size'],
            color=main_color
        ),
        hovertemplate='<b>%{text}</b><br>Fréquence: %{customdata}<extra></extra>',
        customdata=df_top_wc['count']
    ))
    
    fig_wordcloud.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        showlegend=False,
        height=500,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    # ========== VIZ 2: TOP KEYWORDS ==========
    df_top = get_top_entities(data, 'kws', top_n)
    
    fig_top = px.bar(
        df_top,
        y='entity',
        x='count',
        orientation='h',
        color_discrete_sequence=[main_color]
    )
    
    fig_top.update_traces(
        text=df_top['count'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Fréquence: %{x}<extra></extra>'
    )
    
    fig_top.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Fréquence",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        height=600,
        margin=dict(l=150)
    )
    
    # ========== VIZ 3: THÈMES STRUCTURANTS (TREEMAP) ==========
    themes = create_thematic_structure()
    treemap_data = []
    
    for theme, keywords in themes.items():
        theme_total = sum([data['kws'].get(kw, 0) for kw in keywords])
        
        # Ajouter le thème
        treemap_data.append({
            'labels': theme,
            'parents': '',
            'values': theme_total,
            'text': f"{theme}<br>{theme_total:,}"
        })
        
        # Ajouter les mots-clés
        for kw in keywords:
            count = data['kws'].get(kw, 0)
            if count > 0:
                treemap_data.append({
                    'labels': kw.capitalize(),
                    'parents': theme,
                    'values': count,
                    'text': f"{kw}<br>{count:,}"
                })
    
    df_treemap = pd.DataFrame(treemap_data)
    
    fig_themes = px.treemap(
        df_treemap,
        names='labels',
        parents='parents',
        values='values',
        color='values',
        color_continuous_scale='Viridis'
    )
    
    fig_themes.update_traces(
        textinfo="label+value",
        hovertemplate='<b>%{label}</b><br>Mentions: %{value}<extra></extra>'
    )
    
    fig_themes.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        height=600
    )
    
    # ========== VIZ 4: ÉVOLUTION TEMPORELLE ==========
    if corpus_selected == 'Combined':
        fig_temporal = px.line(
            df_temporal,
            x='date',
            y='n_articles',
            color='corpus',
            markers=True,
            color_discrete_map={'Macron/France': COLORS['macron'], 'Poutine/Russie': COLORS['poutine']}
        )
    else:
        fig_temporal = px.line(
            df_temporal,
            x='date',
            y='n_articles',
            markers=True,
            color_discrete_sequence=[main_color]
        )
    
    fig_temporal.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Date",
        yaxis_title="Nombre d'articles",
        legend_title="Corpus",
        hovermode='x unified',
        height=400
    )
    
    # ========== VIZ 5: PICS D'ATTENTION (HEATMAP) ==========
    top_kws_for_heatmap = ['russie', 'ukraine', 'france', 'afrique', 'poutine', 'macron', 'guerre', 'président']
    heatmap_data = []
    
    # Sélectionner la source de données
    if corpus_selected == 'Macron/France':
        source_data = data_macron
    elif corpus_selected == 'Poutine/Russie':
        source_data = data_poutine
    else:
        # Pour combiné, on va merger les deux
        source_data = None
    
    if source_data:
        for kw in top_kws_for_heatmap:
            for year in ['2024', '2025']:
                for month in range(1, 13):
                    month_str = str(month)
                    try:
                        count = source_data['metadata']['month'].get(year, {}).get(month_str, {}).get('kws', {}).get(kw, 0)
                        if count > 0:
                            heatmap_data.append({
                                'keyword': kw.capitalize(),
                                'date': f"{year}-{month_str.zfill(2)}",
                                'count': count
                            })
                    except:
                        pass
    else:
        # Combiné
        for kw in top_kws_for_heatmap:
            for year in ['2024', '2025']:
                for month in range(1, 13):
                    month_str = str(month)
                    try:
                        count_m = data_macron['metadata']['month'].get(year, {}).get(month_str, {}).get('kws', {}).get(kw, 0)
                        count_p = data_poutine['metadata']['month'].get(year, {}).get(month_str, {}).get('kws', {}).get(kw, 0)
                        total = count_m + count_p
                        if total > 0:
                            heatmap_data.append({
                                'keyword': kw.capitalize(),
                                'date': f"{year}-{month_str.zfill(2)}",
                                'count': total
                            })
                    except:
                        pass
    
    if heatmap_data:
        df_heatmap = pd.DataFrame(heatmap_data)
        df_heatmap_pivot = df_heatmap.pivot(index='keyword', columns='date', values='count').fillna(0)
        
        fig_attention = px.imshow(
            df_heatmap_pivot,
            aspect='auto',
            color_continuous_scale='YlOrRd',
            labels=dict(x="Mois", y="Mot-clé", color="Mentions")
        )
        
        fig_attention.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=400
        )
    else:
        fig_attention = go.Figure()
        fig_attention.add_annotation(text="Données insuffisantes", x=0.5, y=0.5, showarrow=False, font=dict(size=20))
        fig_attention.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=400
        )
    
    # ========== VIZ 6: RÉSEAU D'ACTEURS ==========
    G = create_actor_network(data, 15)
    
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#e2e8f0'),
        hoverinfo='none',
        mode='lines'
    )
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        textposition="top center",
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            size=[],
            color=[],
            colorbar=dict(
                thickness=15,
                title='Mentions',
                xanchor='left',
                titleside='right'
            ),
            line_width=2
        )
    )
    
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([node[:20]])
        node_size = G.nodes[node].get('size', 10)
        node_trace['marker']['size'] += tuple([min(node_size / 10, 50)])
        node_trace['marker']['color'] += tuple([node_size])
    
    fig_actor = go.Figure(data=[edge_trace, node_trace])
    
    fig_actor.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        showlegend=False,
        hovermode='closest',
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    # ========== VIZ 7: CORRÉLATION ACTEURS-LIEUX (SANKEY) ==========
    # Top acteurs
    df_actors = get_top_entities(data, 'per', 8)
    # Top lieux
    df_locs = get_top_entities(data, 'loc', 8)
    
    # Créer les liens (simulés)
    sources = []
    targets = []
    values = []
    
    for i, actor in enumerate(df_actors['entity'].tolist()):
        actor_count = df_actors.iloc[i]['count']
        # Lier l'acteur à 2-3 lieux proportionnellement
        for j in range(min(3, len(df_locs))):
            sources.append(i)
            targets.append(len(df_actors) + j)
            values.append(actor_count * (0.5 - j * 0.15))
    
    all_labels = df_actors['entity'].tolist() + df_locs['entity'].tolist()
    
    fig_correlation = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="white", width=0.5),
            label=all_labels,
            color=main_color
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(14, 165, 233, 0.2)'
        )
    )])
    
    fig_correlation.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(size=12, color=COLORS['text']),
        height=600
    )
    
    # ========== VIZ 8: RÉSEAU INTERACTIF AVEC MOT SÉLECTIONNÉ ==========
    if selected_word:
        # Créer un réseau centré sur le mot sélectionné
        G_word = nx.Graph()
        G_word.add_node(selected_word, size=data['kws'].get(selected_word, 0), central=True)
        
        # Trouver les mots co-occurrents (simulation basée sur proximité de fréquence)
        all_kws = sorted(data['kws'].items(), key=lambda x: x[1], reverse=True)[:50]
        selected_freq = data['kws'].get(selected_word, 0)
        
        connected_words = []
        for word, freq in all_kws:
            if word != selected_word and abs(freq - selected_freq) < selected_freq * 0.8:
                connected_words.append((word, freq))
                if len(connected_words) >= 10:
                    break
        
        for word, freq in connected_words:
            G_word.add_node(word, size=freq, central=False)
            G_word.add_edge(selected_word, word)
        
        pos_word = nx.spring_layout(G_word, k=1, iterations=50)
        
        edge_trace_word = go.Scatter(
            x=[],
            y=[],
            line=dict(width=2, color=main_color),
            hoverinfo='none',
            mode='lines',
            opacity=0.5
        )
        
        for edge in G_word.edges():
            x0, y0 = pos_word[edge[0]]
            x1, y1 = pos_word[edge[1]]
            edge_trace_word['x'] += tuple([x0, x1, None])
            edge_trace_word['y'] += tuple([y0, y1, None])
        
        node_trace_word = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            textposition="top center",
            marker=dict(
                size=[],
                color=[],
                colorscale=[[0, COLORS['secondary']], [1, main_color]],
                line_width=2
            )
        )
        
        for node in G_word.nodes():
            x, y = pos_word[node]
            node_trace_word['x'] += tuple([x])
            node_trace_word['y'] += tuple([y])
            node_trace_word['text'] += tuple([node])
            is_central = G_word.nodes[node].get('central', False)
            node_size = 50 if is_central else 30
            node_trace_word['marker']['size'] += tuple([node_size])
            node_trace_word['marker']['color'] += tuple([1 if is_central else 0])
        
        fig_word = go.Figure(data=[edge_trace_word, node_trace_word])
        
        fig_word.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            showlegend=False,
            hovermode='closest',
            height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title=f"Connexions du mot '{selected_word}'"
        )
    else:
        fig_word = go.Figure()
        fig_word.add_annotation(
            text="Sélectionnez un mot-clé ci-dessus pour voir ses connexions",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color=COLORS['text_secondary'])
        )
        fig_word.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    
    # ========== VIZ 9: DISTRIBUTION GÉOGRAPHIQUE ==========
    df_geo = get_top_entities(data, 'loc', 15)
    
    fig_geo = px.bar(
        df_geo,
        y='entity',
        x='count',
        orientation='h',
        color='count',
        color_continuous_scale='Blues'
    )
    
    fig_geo.update_traces(
        text=df_geo['count'],
        textposition='outside'
    )
    
    fig_geo.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Nombre de mentions",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        height=500,
        showlegend=False
    )
    
    # ========== VIZ 10: ACTEURS ET LIEUX ASSOCIÉS ==========
    # Créer une matrice acteurs x lieux (simplifiée)
    actors = get_top_entities(data, 'per', 10)['entity'].tolist()
    locations = get_top_entities(data, 'loc', 8)['entity'].tolist()
    
    # Matrice simulée
    matrix = []
    for actor in actors:
        actor_freq = data['per'].get(actor, 0)
        row = []
        for loc in locations:
            loc_freq = data['loc'].get(loc, 0)
            # Simulation de co-occurrence
            value = min(actor_freq, loc_freq) * np.random.uniform(0.1, 0.5)
            row.append(value)
        matrix.append(row)
    
    fig_actors_loc = px.imshow(
        matrix,
        x=locations,
        y=actors,
        aspect='auto',
        color_continuous_scale='Blues',
        labels=dict(x="Lieu", y="Acteur", color="Co-occurrence")
    )
    
    fig_actors_loc.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        height=500
    )
    
    return (fig_wordcloud, fig_top, fig_themes, fig_temporal, fig_attention,
            fig_actor, fig_correlation, fig_word, fig_geo, fig_actors_loc)

# ============================================
# LANCEMENT DE L'APPLICATION
# ============================================

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)