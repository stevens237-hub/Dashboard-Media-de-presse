"""
SPUTNIK NEWS AFRICA - DASHBOARD ANALYTIQUE
Dashboard interactif pour l'analyse comparative de corpus médiatiques
Auteur: Analyse de données - Macron/France vs Poutine/Russie
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

# ============================================
# CONFIGURATION ET CHARGEMENT DES DONNÉES
# ============================================

# Palette de couleurs cohérente
COLORS = {
    'primary': '#0ea5e9',
    'secondary': '#8b5cf6',
    'accent': '#f59e0b',
    'success': '#10b981',
    'danger': '#ef4444',
    'macron': '#ef4444',  # Rouge pour Macron/France
    'poutine': '#0ea5e9',  # Bleu pour Poutine/Russie
    'bg_primary': '#f8fafc',
    'bg_card': '#f8fafc',
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

def get_temporal_data(data, corpus_name):
    """Extraire les données temporelles"""
    records = []
    for year in data['data'].keys():
        for month in data['data'][year].keys():
            # Compter le nombre de jours (articles) dans ce mois
            days = data['data'][year][month]
            if isinstance(days, dict):
                n_articles = len(days)
            else:
                n_articles = len(days) if isinstance(days, list) else 0
            
            date = f"{year}-{month.zfill(2)}-01"
            records.append({
                'date': pd.to_datetime(date),
                'year': year,
                'month': month,
                'n_articles': n_articles,
                'corpus': corpus_name
            })
    return pd.DataFrame(records)

def get_top_entities(data, entity_type='kws', n=20):
    """Obtenir les top entités"""
    entities = data['metadata']['all'][entity_type]
    top_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)[:n]
    return pd.DataFrame(top_entities, columns=['entity', 'count'])

def calculate_kpis(data):
    """Calculer les KPIs"""
    kpis = {
        'total_kws': len(data['metadata']['all']['kws']),
        'total_loc': len(data['metadata']['all']['loc']),
        'total_org': len(data['metadata']['all']['org']),
        'total_per': len(data['metadata']['all']['per']),
        'top_kw': max(data['metadata']['all']['kws'].items(), key=lambda x: x[1]),
    }
    return kpis

# Préparer les données
df_temporal_macron = get_temporal_data(data_macron, 'Macron/France')
df_temporal_poutine = get_temporal_data(data_poutine, 'Poutine/Russie')
df_temporal = pd.concat([df_temporal_macron, df_temporal_poutine])

kpis_macron = calculate_kpis(data_macron)
kpis_poutine = calculate_kpis(data_poutine)

# ============================================
# INITIALISATION DE L'APPLICATION
# ============================================

app = dash.Dash(__name__, 
                suppress_callback_exceptions=True,
                assets_folder='assets',
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                external_stylesheets=['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'])

app.title = "Sputnik News Africa - Dashboard Analytique"

# ============================================
# LAYOUT DU DASHBOARD
# ============================================

app.layout = html.Div([
    # HEADER
    html.Div([
        html.H1("📊 Sputnik News Africa - Analyse Comparative"),
        html.P("Comparaison des corpus médiatiques : Macron/France vs Poutine/Russie (2024-2025)")
    ], className='dashboard-header'),
    
    # KPIs
    html.Div([
        # KPI 1: Total Articles
        html.Div([
            html.Div("Total Articles", className='kpi-label'),
            html.Div(f"{df_temporal['n_articles'].sum():,}", className='kpi-value'),
            html.Div("📈 Sur toute la période", className='kpi-trend'),
        ], className='kpi-card'),
        
        # KPI 2: Mots-clés uniques
        html.Div([
            html.Div("Mots-clés Uniques", className='kpi-label'),
            html.Div(f"{kpis_macron['total_kws'] + kpis_poutine['total_kws']:,}", className='kpi-value'),
            html.Div(f"Macron: {kpis_macron['total_kws']:,} | Poutine: {kpis_poutine['total_kws']:,}", className='kpi-trend'),
        ], className='kpi-card'),
        
        # KPI 3: Période couverte
        html.Div([
            html.Div("Période Analysée", className='kpi-label'),
            html.Div("19 mois", className='kpi-value'),
            html.Div("📅 Avril 2024 - Oct 2025", className='kpi-trend'),
        ], className='kpi-card'),
        
        # KPI 4: Entités nommées
        html.Div([
            html.Div("Entités Totales", className='kpi-label'),
            html.Div(f"{kpis_macron['total_loc'] + kpis_macron['total_org'] + kpis_macron['total_per'] + kpis_poutine['total_loc'] + kpis_poutine['total_org'] + kpis_poutine['total_per']:,}", className='kpi-value'),
            html.Div("🏛️ Lieux, Org., Personnes", className='kpi-trend'),
        ], className='kpi-card'),
    ], className='kpi-container'),
    
    # FILTRES
    html.Div([
        html.Div("Filtres de sélection", className='filters-title'),
        html.Div([
            # Filtre Corpus
            html.Div([
                html.Label("Sélectionner le corpus", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Dropdown(
                    id='corpus-filter',
                    options=[
                        {'label': '🔴 Macron/France', 'value': 'Macron/France'},
                        {'label': '🔵 Poutine/Russie', 'value': 'Poutine/Russie'},
                        {'label': '🟣 Les deux corpus', 'value': 'both'}
                    ],
                    value='both',
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
                        {'label': '🗓️ 3 derniers mois', 'value': 'last3'},
                    ],
                    value='all',
                    clearable=False
                ),
            ]),
            
            # Filtre Catégorie
            html.Div([
                html.Label("Catégorie d'entités", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Dropdown(
                    id='entity-filter',
                    options=[
                        {'label': '🔑 Mots-clés (keywords)', 'value': 'kws'},
                        {'label': '📍 Lieux (locations)', 'value': 'loc'},
                        {'label': '🏢 Organisations', 'value': 'org'},
                        {'label': '👤 Personnes', 'value': 'per'},
                    ],
                    value='kws',
                    clearable=False
                ),
            ]),
            
            # Top N
            html.Div([
                html.Label("Nombre d'éléments à afficher", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Slider(
                    id='top-n-slider',
                    min=5,
                    max=50,
                    step=5,
                    value=20,
                    marks={i: str(i) for i in range(5, 55, 5)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ]),
        ], className='filters-grid'),
    ], className='filters-container'),
    
    # VISUALIZATIONS GRID
    html.Div([
        # VIZ 1: Comparaison des protagonistes
        html.Div([
            html.Div("1️⃣ Comparaison des Protagonistes", className='viz-title'),
            dcc.Graph(id='viz-protagonists'),
        ], className='viz-card'),
        
        # VIZ 2: Évolution temporelle
        html.Div([
            html.Div("2️⃣ Évolution Temporelle des Publications", className='viz-title'),
            dcc.Graph(id='viz-temporal'),
        ], className='viz-card'),
        
        # VIZ 3: Top Keywords (Full width)
        html.Div([
            html.Div("3️⃣ Top Mots-clés par Corpus (Diverging)", className='viz-title'),
            dcc.Graph(id='viz-top-keywords'),
        ], className='viz-card viz-grid-full'),
        
        # VIZ 4: Cartographie géographique
        html.Div([
            html.Div("4️⃣ Distribution Géographique", className='viz-title'),
            dcc.Graph(id='viz-geography'),
        ], className='viz-card'),
        
        # VIZ 5: Distribution des entités
        html.Div([
            html.Div("5️⃣ Distribution des Entités Nommées", className='viz-title'),
            dcc.Graph(id='viz-entities-distribution'),
        ], className='viz-card'),
        
        # VIZ 6: Network Graph (Full width)
        html.Div([
            html.Div("6️⃣ Réseau de Co-occurrence (Top 30)", className='viz-title'),
            dcc.Graph(id='viz-network'),
        ], className='viz-card viz-grid-full'),
        
        # VIZ 7: Timeline personnalités
        html.Div([
            html.Div("7️⃣ Timeline des Personnalités Politiques", className='viz-title'),
            dcc.Graph(id='viz-timeline-people'),
        ], className='viz-card'),
        
        # VIZ 8: Heatmap thématique
        html.Div([
            html.Div("8️⃣ Heatmap Thématique Mensuelle", className='viz-title'),
            dcc.Graph(id='viz-heatmap'),
        ], className='viz-card'),
        
        # VIZ 9: Sunburst thématique
        html.Div([
            html.Div("9️⃣ Hiérarchie Thématique (Sunburst)", className='viz-title'),
            dcc.Graph(id='viz-sunburst'),
        ], className='viz-card'),
        
        # VIZ 10: Area chart évolution
        html.Div([
            html.Div("🔟 Évolution des Catégories d'Entités", className='viz-title'),
            dcc.Graph(id='viz-area-categories'),
        ], className='viz-card'),
    ], className='viz-grid', style={'marginBottom': '2rem'}),
    
], id='dashboard-container')

# ============================================
# CALLBACKS POUR L'INTERACTIVITÉ
# ============================================

@app.callback(
    [Output('viz-protagonists', 'figure'),
     Output('viz-temporal', 'figure'),
     Output('viz-top-keywords', 'figure'),
     Output('viz-geography', 'figure'),
     Output('viz-entities-distribution', 'figure'),
     Output('viz-network', 'figure'),
     Output('viz-timeline-people', 'figure'),
     Output('viz-heatmap', 'figure'),
     Output('viz-sunburst', 'figure'),
     Output('viz-area-categories', 'figure')],
    [Input('corpus-filter', 'value'),
     Input('period-filter', 'value'),
     Input('entity-filter', 'value'),
     Input('top-n-slider', 'value')]
)
def update_all_visualizations(corpus_selected, period, entity_type, top_n):
    """Callback principal pour mettre à jour toutes les visualisations"""
    
    # Filtrer les données selon les critères
    df_filtered = df_temporal.copy()
    
    # Filtre période
    if period == '2024':
        df_filtered = df_filtered[df_filtered['year'] == '2024']
    elif period == '2025':
        df_filtered = df_filtered[df_filtered['year'] == '2025']
    elif period == 'last6':
        cutoff = df_filtered['date'].max() - timedelta(days=180)
        df_filtered = df_filtered[df_filtered['date'] >= cutoff]
    elif period == 'last3':
        cutoff = df_filtered['date'].max() - timedelta(days=90)
        df_filtered = df_filtered[df_filtered['date'] >= cutoff]
    
    # Filtre corpus
    if corpus_selected != 'both':
        df_filtered = df_filtered[df_filtered['corpus'] == corpus_selected]
    
    # ========== VIZ 1: PROTAGONISTES ==========
    protagonists = ['macron', 'poutine', 'france', 'russie']
    protagonists_data = []
    
    for p in protagonists:
        count_m = data_macron['metadata']['all']['kws'].get(p, 0)
        count_p = data_poutine['metadata']['all']['kws'].get(p, 0)
        protagonists_data.append({'entity': p.capitalize(), 'Macron/France': count_m, 'Poutine/Russie': count_p})
    
    df_prot = pd.DataFrame(protagonists_data)
    
    fig_prot = go.Figure()
    fig_prot.add_trace(go.Bar(
        name='Macron/France',
        x=df_prot['entity'],
        y=df_prot['Macron/France'],
        marker_color=COLORS['macron'],
        text=df_prot['Macron/France'],
        textposition='outside'
    ))
    fig_prot.add_trace(go.Bar(
        name='Poutine/Russie',
        x=df_prot['entity'],
        y=df_prot['Poutine/Russie'],
        marker_color=COLORS['poutine'],
        text=df_prot['Poutine/Russie'],
        textposition='outside'
    ))
    
    fig_prot.update_layout(
        barmode='group',
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Protagoniste",
        yaxis_title="Nombre de mentions",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    # ========== VIZ 2: ÉVOLUTION TEMPORELLE ==========
    fig_temporal = px.line(
        df_filtered,
        x='date',
        y='n_articles',
        color='corpus',
        markers=True,
        color_discrete_map={'Macron/France': COLORS['macron'], 'Poutine/Russie': COLORS['poutine']}
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
    
    # ========== VIZ 3: TOP KEYWORDS DIVERGING ==========
    df_top_m = get_top_entities(data_macron, entity_type, top_n)
    df_top_p = get_top_entities(data_poutine, entity_type, top_n)
    
    # Créer un diverging bar chart
    fig_keywords = go.Figure()
    
    # Limiter aux top 15 pour la lisibilité
    top_display = 15
    df_top_m_display = df_top_m.head(top_display)
    df_top_p_display = df_top_p.head(top_display)
    
    fig_keywords.add_trace(go.Bar(
        name='Macron/France',
        y=df_top_m_display['entity'],
        x=-df_top_m_display['count'],  # Négatif pour diverger
        orientation='h',
        marker_color=COLORS['macron'],
        text=df_top_m_display['count'],
        textposition='outside'
    ))
    
    fig_keywords.add_trace(go.Bar(
        name='Poutine/Russie',
        y=df_top_p_display['entity'],
        x=df_top_p_display['count'],
        orientation='h',
        marker_color=COLORS['poutine'],
        text=df_top_p_display['count'],
        textposition='outside'
    ))
    
    fig_keywords.update_layout(
        barmode='overlay',
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Fréquence",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor=COLORS['text'])
    )
    
    # ========== VIZ 4: GÉOGRAPHIE ==========
    df_geo_m = get_top_entities(data_macron, 'loc', 15)
    df_geo_p = get_top_entities(data_poutine, 'loc', 15)
    df_geo_m['corpus'] = 'Macron/France'
    df_geo_p['corpus'] = 'Poutine/Russie'
    df_geo = pd.concat([df_geo_m, df_geo_p])
    
    fig_geo = px.bar(
        df_geo,
        x='count',
        y='entity',
        color='corpus',
        orientation='h',
        color_discrete_map={'Macron/France': COLORS['macron'], 'Poutine/Russie': COLORS['poutine']},
        barmode='group'
    )
    
    fig_geo.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Nombre de mentions",
        yaxis_title="Lieu",
        legend_title="Corpus",
        height=500
    )
    
    # ========== VIZ 5: DISTRIBUTION ENTITÉS ==========
    entities_data = [
        {'corpus': 'Macron/France', 'type': 'Lieux', 'count': kpis_macron['total_loc']},
        {'corpus': 'Macron/France', 'type': 'Organisations', 'count': kpis_macron['total_org']},
        {'corpus': 'Macron/France', 'type': 'Personnes', 'count': kpis_macron['total_per']},
        {'corpus': 'Poutine/Russie', 'type': 'Lieux', 'count': kpis_poutine['total_loc']},
        {'corpus': 'Poutine/Russie', 'type': 'Organisations', 'count': kpis_poutine['total_org']},
        {'corpus': 'Poutine/Russie', 'type': 'Personnes', 'count': kpis_poutine['total_per']},
    ]
    df_entities = pd.DataFrame(entities_data)
    
    fig_entities = px.bar(
        df_entities,
        x='corpus',
        y='count',
        color='type',
        barmode='group',
        color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    )
    
    fig_entities.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Corpus",
        yaxis_title="Nombre d'entités",
        legend_title="Type d'entité",
        height=400
    )
    
    # ========== VIZ 6: NETWORK GRAPH ==========
    # Créer un réseau simple avec les top 30 mots-clés
    top_kws_m = get_top_entities(data_macron, 'kws', 30)
    top_kws_p = get_top_entities(data_poutine, 'kws', 30)
    
    # Combiner
    all_kws = set(top_kws_m['entity'].tolist() + top_kws_p['entity'].tolist())
    
    # Créer un graphe simple basé sur la co-occurrence
    G = nx.Graph()
    for kw in all_kws:
        G.add_node(kw)
    
    # Ajouter des arêtes basées sur la présence commune dans les corpus
    common_kws = set(top_kws_m['entity'].tolist()).intersection(set(top_kws_p['entity'].tolist()))
    for kw in common_kws:
        for other_kw in common_kws:
            if kw != other_kw:
                G.add_edge(kw, other_kw)
    
    # Layout spring
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Créer les traces
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color=COLORS['text']),
        hoverinfo='none',
        mode='lines',
        opacity=0.3
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
            size=15,
            color=[],
            colorbar=dict(
                thickness=15,
                title='Connexions',
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
        node_trace['text'] += tuple([node[:15]])  # Limiter la longueur
        node_trace['marker']['color'] += tuple([len(list(G.neighbors(node)))])
    
    fig_network = go.Figure(data=[edge_trace, node_trace])
    
    fig_network.update_layout(
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
    
    # ========== VIZ 7: TIMELINE PERSONNALITÉS ==========
    # Récupérer les top personnes
    top_people = ['macron', 'poutine', 'trump', 'lecornu', 'biden']
    
    timeline_data = []
    for person in top_people:
        # Pour chaque mois, compter les mentions
        for _, row in df_filtered.iterrows():
            year = row['year']
            month = row['month']
            corpus = row['corpus']
            
            # Accéder aux données du corpus
            if corpus == 'Macron/France':
                data_source = data_macron
            else:
                data_source = data_poutine
            
            # Essayer de récupérer le count pour cette personne ce mois-ci
            try:
                month_data = data_source['metadata']['month'][year].get(month, {})
                per_data = month_data.get('per', {})
                count = per_data.get(person, 0)
            except:
                count = 0
            
            if count > 0:
                timeline_data.append({
                    'person': person.capitalize(),
                    'date': row['date'],
                    'count': count,
                    'corpus': corpus
                })
    
    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)
        
        fig_timeline = px.scatter(
            df_timeline,
            x='date',
            y='person',
            size='count',
            color='corpus',
            color_discrete_map={'Macron/France': COLORS['macron'], 'Poutine/Russie': COLORS['poutine']},
            hover_data=['count']
        )
        
        fig_timeline.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            xaxis_title="Date",
            yaxis_title="Personnalité",
            legend_title="Corpus",
            height=400
        )
    else:
        fig_timeline = go.Figure()
        fig_timeline.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=400,
            annotations=[dict(text="Données insuffisantes", x=0.5, y=0.5, showarrow=False, font=dict(size=20))]
        )
    
    # ========== VIZ 8: HEATMAP ==========
    # Créer une heatmap des top mots-clés par mois
    heatmap_kws = ['russie', 'ukraine', 'france', 'afrique', 'guerre', 'président']
    heatmap_data = []
    
    for kw in heatmap_kws:
        for year in ['2024', '2025']:
            for month in range(1, 13):
                month_str = str(month)
                try:
                    # Macron corpus
                    count_m = data_macron['metadata']['month'].get(year, {}).get(month_str, {}).get('kws', {}).get(kw, 0)
                    count_p = data_poutine['metadata']['month'].get(year, {}).get(month_str, {}).get('kws', {}).get(kw, 0)
                    total_count = count_m + count_p
                    
                    if total_count > 0:
                        heatmap_data.append({
                            'keyword': kw.capitalize(),
                            'date': f"{year}-{month_str.zfill(2)}",
                            'count': total_count
                        })
                except:
                    pass
    
    if heatmap_data:
        df_heatmap = pd.DataFrame(heatmap_data)
        df_heatmap_pivot = df_heatmap.pivot(index='keyword', columns='date', values='count').fillna(0)
        
        fig_heatmap = px.imshow(
            df_heatmap_pivot,
            aspect='auto',
            color_continuous_scale='Viridis',
            labels=dict(x="Mois", y="Mot-clé", color="Mentions")
        )
        
        fig_heatmap.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=400
        )
    else:
        fig_heatmap = go.Figure()
        fig_heatmap.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=400
        )
    
    # ========== VIZ 9: SUNBURST ==========
    # Créer une hiérarchie thématique
    sunburst_data = []
    
    themes = {
        'Politique': ['président', 'gouvernement', 'ministre', 'élection', 'politique'],
        'Géopolitique': ['russie', 'ukraine', 'france', 'guerre', 'otan'],
        'Afrique': ['afrique', 'mali', 'burkina', 'niger', 'sahel'],
        'Économie': ['économie', 'budget', 'finance', 'banque', 'monnaie']
    }
    
    for theme, keywords in themes.items():
        theme_total_m = sum([data_macron['metadata']['all']['kws'].get(kw, 0) for kw in keywords])
        theme_total_p = sum([data_poutine['metadata']['all']['kws'].get(kw, 0) for kw in keywords])
        
        # Ajouter le thème
        sunburst_data.append({
            'labels': theme,
            'parents': '',
            'values': theme_total_m + theme_total_p
        })
        
        # Ajouter les sous-catégories
        for kw in keywords:
            count = data_macron['metadata']['all']['kws'].get(kw, 0) + data_poutine['metadata']['all']['kws'].get(kw, 0)
            if count > 0:
                sunburst_data.append({
                    'labels': kw.capitalize(),
                    'parents': theme,
                    'values': count
                })
    
    df_sunburst = pd.DataFrame(sunburst_data)
    
    fig_sunburst = px.sunburst(
        df_sunburst,
        names='labels',
        parents='parents',
        values='values',
        color='values',
        color_continuous_scale='Viridis'
    )
    
    fig_sunburst.update_layout(
        template='plotly_white',
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        height=500
    )
    
    # ========== VIZ 10: AREA CHART CATÉGORIES ==========
    # Évolution des catégories d'entités par mois
    area_data = []
    
    for _, row in df_filtered.iterrows():
        year = row['year']
        month = row['month']
        corpus = row['corpus']
        
        if corpus == 'Macron/France':
            data_source = data_macron
        else:
            data_source = data_poutine
        
        try:
            month_data = data_source['metadata']['month'][year].get(month, {})
            n_loc = len(month_data.get('loc', {}))
            n_org = len(month_data.get('org', {}))
            n_per = len(month_data.get('per', {}))
            
            area_data.append({'date': row['date'], 'type': 'Lieux', 'count': n_loc})
            area_data.append({'date': row['date'], 'type': 'Organisations', 'count': n_org})
            area_data.append({'date': row['date'], 'type': 'Personnes', 'count': n_per})
        except:
            pass
    
    if area_data:
        df_area = pd.DataFrame(area_data)
        
        fig_area = px.area(
            df_area,
            x='date',
            y='count',
            color='type',
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent']]
        )
        
        fig_area.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            xaxis_title="Date",
            yaxis_title="Nombre d'entités uniques",
            legend_title="Type",
            hovermode='x unified',
            height=400
        )
    else:
        fig_area = go.Figure()
        fig_area.update_layout(
            template='plotly_white',
            paper_bgcolor=COLORS['bg_card'],
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            height=400
        )
    
    return (fig_prot, fig_temporal, fig_keywords, fig_geo, fig_entities, 
            fig_network, fig_timeline, fig_heatmap, fig_sunburst, fig_area)

# ============================================
# LANCEMENT DE L'APPLICATION
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)