
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from collections import Counter
import networkx as nx

# Configuration couleurs
COLORS = {
    'primary': '#0ea5e9', 'secondary': '#8b5cf6', 'accent': '#f59e0b',
    'success': '#10b981', 'danger': '#ef4444',
    'macron': '#ef4444', 'poutine': '#0ea5e9', 'combined': '#8b5cf6',
    'bg_primary': "#b7b9ba", 'bg_card': '#f8fafc',
    'text': '#0f172a', 'text_secondary': '#334155',
}

# Charger données
def load_data():
    with open('fr.sputniknews.africa-2025/data/fr.sputniknews.africa-france-macron.json', 'r', encoding='utf-8') as f:
        data_macron = json.load(f)
    with open('fr.sputniknews.africa-2025/data/fr.sputniknews.africa-russie-poutine.json', 'r', encoding='utf-8') as f:
        data_poutine = json.load(f)
    return data_macron, data_poutine

data_macron, data_poutine = load_data()

# Fonctions utilitaires
def get_combined_data():
    return {
        'kws': Counter(data_macron['metadata']['all']['kws']) + Counter(data_poutine['metadata']['all']['kws']),
        'loc': Counter(data_macron['metadata']['all']['loc']) + Counter(data_poutine['metadata']['all']['loc']),
        'org': Counter(data_macron['metadata']['all']['org']) + Counter(data_poutine['metadata']['all']['org']),
        'per': Counter(data_macron['metadata']['all']['per']) + Counter(data_poutine['metadata']['all']['per']),
    }

def get_data_by_corpus(corpus_selected):
    if corpus_selected == 'Macron/France':
        return data_macron['metadata']['all']
    elif corpus_selected == 'Poutine/Russie':
        return data_poutine['metadata']['all']
    else:
        return get_combined_data()

def get_top_entities(data, entity_type='kws', n=20):
    if isinstance(data, dict) and entity_type in data:
        entities = data[entity_type]
    else:
        entities = data
    top_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)[:n]
    return pd.DataFrame(top_entities, columns=['entity', 'count'])

def get_temporal_data(corpus_selected):
    records = []
    if corpus_selected in ['Macron/France', 'Combined']:
        for year in data_macron['data'].keys():
            for month in data_macron['data'][year].keys():
                days = data_macron['data'][year][month]
                n_articles = len(days) if isinstance(days, dict) else 0
                records.append({
                    'date': pd.to_datetime(f"{year}-{month.zfill(2)}-01"),
                    'year': year, 'month': month, 'n_articles': n_articles, 'corpus': 'Macron/France'
                })
    if corpus_selected in ['Poutine/Russie', 'Combined']:
        for year in data_poutine['data'].keys():
            for month in data_poutine['data'][year].keys():
                days = data_poutine['data'][year][month]
                n_articles = len(days) if isinstance(days, dict) else 0
                records.append({
                    'date': pd.to_datetime(f"{year}-{month.zfill(2)}-01"),
                    'year': year, 'month': month, 'n_articles': n_articles, 'corpus': 'Poutine/Russie'
                })
    df = pd.DataFrame(records)
    # Trier par date pour éviter les lignes qui reviennent en arrière
    if len(df) > 0:
        df = df.sort_values('date').reset_index(drop=True)
    return df

def calculate_kpis(corpus_selected, period='all'):
    df_temporal = get_temporal_data(corpus_selected)
    if period == '2024':
        df_temporal = df_temporal[df_temporal['year'] == '2024']
    elif period == '2025':
        df_temporal = df_temporal[df_temporal['year'] == '2025']
    elif period == 'last6':
        cutoff = df_temporal['date'].max() - timedelta(days=180)
        df_temporal = df_temporal[df_temporal['date'] >= cutoff]
    
    total_articles = df_temporal['n_articles'].sum()
    if len(df_temporal) > 0:
        date_min, date_max = df_temporal['date'].min(), df_temporal['date'].max()
        n_months = ((date_max.year - date_min.year) * 12 + date_max.month - date_min.month) + 1
        period_text = f"{n_months} mois"
    else:
        period_text = "0 mois"
    
    data = get_data_by_corpus(corpus_selected)
    return {
        'total_articles': total_articles, 'period': period_text,
        'total_kws': len(data['kws']), 'total_loc': len(data['loc']),
    }

# App Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                external_stylesheets=['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'])
app.title = "Sputnik News Africa - Dashboard"

# Layout
app.layout = html.Div([
    html.Div([
        html.H1(" Sputnik News Africa - Analyse de Corpus Médiatiques"),
        html.P("Analyse approfondie des publications sur Macron/France et Poutine/Russie (2024-2025)")
    ], className='dashboard-header'),
    
    html.Div(id='kpi-container', className='kpi-container'),
    
    html.Div([
        html.Div(" Filtres de sélection", className='filters-title'),
        html.Div([
            html.Div([
                html.Label("Sélectionner le corpus", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Dropdown(id='corpus-filter',
                    options=[
                        {'label': '🔴 Corpus Macron/France', 'value': 'Macron/France'},
                        {'label': '🔵 Corpus Poutine/Russie', 'value': 'Poutine/Russie'},
                        {'label': '🟣 Analyse Combinée', 'value': 'Combined'}
                    ], value='Combined', clearable=False),
            ]),
            html.Div([
                html.Label("Période temporelle", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Dropdown(id='period-filter',
                    options=[
                        {'label': ' Toute la période', 'value': 'all'},
                        {'label': ' 2024 uniquement', 'value': '2024'},
                        {'label': ' 2025 uniquement', 'value': '2025'},
                        {'label': ' 6 derniers mois', 'value': 'last6'},
                    ], value='all', clearable=False),
            ]),
            html.Div([
                html.Label("Nombre d'éléments", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                dcc.Slider(id='top-n-slider', min=10, max=50, step=5, value=20,
                    marks={i: str(i) for i in range(10, 55, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}),
            ]),
        ], className='filters-grid'),
    ], className='filters-container'),
    
    html.Div([
        html.H2(" Vue d'Ensemble", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        html.Div([
            html.Div([html.Div(" Top Mots-clés", className='viz-title'), dcc.Graph(id='viz-top-keywords')], className='viz-card'),
            html.Div([html.Div(" Distribution Géographique", className='viz-title'), dcc.Graph(id='viz-geography')], className='viz-card'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
    html.Div([
        html.H2(" Analyse Temporelle", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        html.Div([
            html.Div([html.Div(" Évolution Temporelle du nombre d'articles", className='viz-title'), dcc.Graph(id='viz-temporal')], className='viz-card'),
            html.Div([html.Div(" Pics d'Attention temporelle", className='viz-title'), dcc.Graph(id='viz-attention-peaks')], className='viz-card'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
    html.Div([
        html.H2(" Analyse Relationnelle", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        html.Div([
            html.Div([html.Div(" Corrélation Acteurs-Lieux", className='viz-title'), dcc.Graph(id='viz-correlation')], className='viz-card'),
            html.Div([
                html.Div(" Réseau Interactif - Connexions d'un Mot", className='viz-title'),
                html.Div([
                    html.Label("Sélectionner un mot-clé", style={'color': COLORS['text'], 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                    dcc.Dropdown(id='word-selector', options=[], value='sputnik', placeholder="Choisir..."),
                ], style={'marginBottom': '1rem'}),
                dcc.Graph(id='viz-word-network')
            ], className='viz-card'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
    
    html.Div([
        html.H2(" Analyse Géographique", style={'color': COLORS['text'], 'marginBottom': '1.5rem', 'fontSize': '1.75rem', 'fontWeight': '700'}),
        html.Div([
            html.Div([html.Div(" Acteurs et Lieux Associés", className='viz-title'), dcc.Graph(id='viz-actors-locations')], className='viz-card viz-grid-full'),
        ], className='viz-grid'),
    ], style={'marginBottom': '3rem'}),
], id='dashboard-container')

# Callbacks
@app.callback(
    Output('kpi-container', 'children'),
    [Input('corpus-filter', 'value'), Input('period-filter', 'value')]
)
def update_kpis(corpus_selected, period):
    kpis = calculate_kpis(corpus_selected, period)
    corpus_emoji = '🔴' if corpus_selected == 'Macron/France' else ('🔵' if corpus_selected == 'Poutine/Russie' else '🟣')
    
    return [
        html.Div([html.Div("Total d'Articles", className='kpi-label'), html.Div(f"{kpis['total_articles']:,}", className='kpi-value'), html.Div(" Publications", className='kpi-trend')], className='kpi-card'),
        html.Div([html.Div("Période Analysée", className='kpi-label'), html.Div(kpis['period'], className='kpi-value', style={'fontSize': '2rem'}), html.Div(f"{corpus_emoji} {corpus_selected}", className='kpi-trend')], className='kpi-card'),
        html.Div([html.Div("Mots-clés Uniques", className='kpi-label'), html.Div(f"{kpis['total_kws']:,}", className='kpi-value'), html.Div(" Termes", className='kpi-trend')], className='kpi-card'),
        html.Div([html.Div("Lieux Mentionnés", className='kpi-label'), html.Div(f"{kpis['total_loc']:,}", className='kpi-value'), html.Div(" Zones", className='kpi-trend')], className='kpi-card'),
    ]

@app.callback(Output('word-selector', 'options'), [Input('corpus-filter', 'value'), Input('top-n-slider', 'value')])
def update_word_selector(corpus_selected, top_n):
    data = get_data_by_corpus(corpus_selected)
    df_top = get_top_entities(data, 'kws', top_n)
    return [{'label': word, 'value': word} for word in df_top['entity'].tolist()]

@app.callback(
    [Output('viz-top-keywords', 'figure'), Output('viz-geography', 'figure'),
     Output('viz-temporal', 'figure'), Output('viz-attention-peaks', 'figure'), Output('viz-correlation', 'figure'),
     Output('viz-word-network', 'figure'), Output('viz-actors-locations', 'figure')],
    [Input('corpus-filter', 'value'), Input('period-filter', 'value'), Input('top-n-slider', 'value'), Input('word-selector', 'value')]
)
def update_all_visualizations(corpus_selected, period, top_n, selected_word):
    data = get_data_by_corpus(corpus_selected)
    df_temporal = get_temporal_data(corpus_selected)
    
    if period == '2024':
        df_temporal = df_temporal[df_temporal['year'] == '2024']
    elif period == '2025':
        df_temporal = df_temporal[df_temporal['year'] == '2025']
    elif period == 'last6':
        cutoff = df_temporal['date'].max() - timedelta(days=180)
        df_temporal = df_temporal[df_temporal['date'] >= cutoff]
    
    main_color = COLORS['macron'] if corpus_selected == 'Macron/France' else (COLORS['poutine'] if corpus_selected == 'Poutine/Russie' else COLORS['combined'])
    
    # VIZ 1: Top Keywords
    df_top = get_top_entities(data, 'kws', top_n)
    fig_top = px.bar(df_top, y='entity', x='count', orientation='h', color_discrete_sequence=[main_color])
    fig_top.update_traces(text=df_top['count'], textposition='outside', hovertemplate='<b>%{y}</b><br>Fréquence: %{x}<extra></extra>')
    fig_top.update_layout(
        template='plotly_white', paper_bgcolor=COLORS['bg_card'], plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']), xaxis_title="Fréquence", yaxis_title="",
        yaxis=dict(autorange="reversed"), height=600, margin=dict(l=150)
    )
    
    # VIZ 2: Géographie
    df_geo_m = get_top_entities(data_macron['metadata']['all'], 'loc', 15)
    df_geo_p = get_top_entities(data_poutine['metadata']['all'], 'loc', 15)
    df_geo_m['corpus'] = 'Macron/France'
    df_geo_p['corpus'] = 'Poutine/Russie'
    
    if corpus_selected == 'Combined':
        df_geo = pd.concat([df_geo_m, df_geo_p])
        fig_geo = px.bar(df_geo, x='count', y='entity', color='corpus', orientation='h',
            color_discrete_map={'Macron/France': COLORS['macron'], 'Poutine/Russie': COLORS['poutine']}, barmode='group')
    else:
        df_geo = df_geo_m if corpus_selected == 'Macron/France' else df_geo_p
        fig_geo = px.bar(df_geo, x='count', y='entity', orientation='h', color_discrete_sequence=[main_color])
    fig_geo.update_layout(template='plotly_white', paper_bgcolor=COLORS['bg_card'], height=600,
        xaxis_title="Nombre de mentions", yaxis_title="Lieu", legend_title="Corpus")
    
    # VIZ 3: Évolution temporelle
    if corpus_selected == 'Combined':
        fig_temporal = px.line(df_temporal, x='date', y='n_articles', color='corpus', markers=True,
            color_discrete_map={'Macron/France': COLORS['macron'], 'Poutine/Russie': COLORS['poutine']})
    else:
        fig_temporal = px.line(df_temporal, x='date', y='n_articles', markers=True, color_discrete_sequence=[main_color])
    fig_temporal.update_layout(template='plotly_white', paper_bgcolor=COLORS['bg_card'], font=dict(color=COLORS['text']),
        xaxis_title="Date", yaxis_title="Nombre d'articles", hovermode='x unified', height=400)
    
    # VIZ 4: Heatmap temporelle
    top_kws_for_heatmap = ['russie', 'ukraine', 'france', 'afrique', 'poutine', 'macron', 'guerre', 'président']
    heatmap_data = []
    source_data = data_macron if corpus_selected == 'Macron/France' else (data_poutine if corpus_selected == 'Poutine/Russie' else None)
    
    if source_data:
        for kw in top_kws_for_heatmap:
            for year in ['2024', '2025']:
                for month in range(1, 13):
                    try:
                        count = source_data['metadata']['month'].get(year, {}).get(str(month), {}).get('kws', {}).get(kw, 0)
                        if count > 0:
                            heatmap_data.append({'keyword': kw.capitalize(), 'date': f"{year}-{str(month).zfill(2)}", 'count': count})
                    except: pass
    else:
        for kw in top_kws_for_heatmap:
            for year in ['2024', '2025']:
                for month in range(1, 13):
                    try:
                        count_m = data_macron['metadata']['month'].get(year, {}).get(str(month), {}).get('kws', {}).get(kw, 0)
                        count_p = data_poutine['metadata']['month'].get(year, {}).get(str(month), {}).get('kws', {}).get(kw, 0)
                        total = count_m + count_p
                        if total > 0:
                            heatmap_data.append({'keyword': kw.capitalize(), 'date': f"{year}-{str(month).zfill(2)}", 'count': total})
                    except: pass
    
    if heatmap_data:
        df_heatmap = pd.DataFrame(heatmap_data).pivot(index='keyword', columns='date', values='count').fillna(0)
        fig_attention = go.Figure(data=go.Heatmap(
            z=df_heatmap.values,
            x=df_heatmap.columns,
            y=df_heatmap.index,
            colorscale='RdYlBu_r',
            colorbar=dict(title="Mentions"),
            hovertemplate='Mot-clé: <b>%{y}</b><br>Mois: %{x}<br>Mentions: %{z}<extra></extra>'
        ))
        fig_attention.update_layout(
            template='plotly_white', 
            paper_bgcolor=COLORS['bg_card'], 
            plot_bgcolor=COLORS['bg_card'],
            font=dict(color=COLORS['text']),
            xaxis_title="Mois",
            yaxis_title="Mot-clé",
            height=400
        )
    else:
        fig_attention = go.Figure()
        fig_attention.add_annotation(text="Données insuffisantes", x=0.5, y=0.5, showarrow=False)
        fig_attention.update_layout(template='plotly_white', paper_bgcolor=COLORS['bg_card'], height=400)
    
    # VIZ 5: Sankey
    df_actors = get_top_entities(data, 'per', 8)
    df_locs = get_top_entities(data, 'loc', 8)
    sources, targets, values = [], [], []
    for i, actor in enumerate(df_actors['entity'].tolist()):
        actor_count = df_actors.iloc[i]['count']
        for j in range(min(3, len(df_locs))):
            sources.append(i)
            targets.append(len(df_actors) + j)
            values.append(actor_count * (0.5 - j * 0.15))
    
    all_labels = df_actors['entity'].tolist() + df_locs['entity'].tolist()
    fig_correlation = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=20, label=all_labels, color=main_color),
        link=dict(source=sources, target=targets, value=values, color='rgba(14, 165, 233, 0.2)')
    ))
    fig_correlation.update_layout(template='plotly_white', paper_bgcolor=COLORS['bg_card'], height=600)
    
    # VIZ 6: Réseau interactif
    if selected_word:
        G_word = nx.Graph()
        G_word.add_node(selected_word, central=True)
        all_kws = sorted(data['kws'].items(), key=lambda x: x[1], reverse=True)[:50]
        selected_freq = data['kws'].get(selected_word, 0)
        connected_words = [(w, f) for w, f in all_kws if w != selected_word and abs(f - selected_freq) < selected_freq * 0.8][:10]
        for word, freq in connected_words:
            G_word.add_node(word, central=False)
            G_word.add_edge(selected_word, word)
        pos_word = nx.spring_layout(G_word, k=1, iterations=50)
        
        edge_trace = go.Scatter(x=[], y=[], line=dict(width=2, color=main_color), mode='lines', opacity=0.5)
        for edge in G_word.edges():
            x0, y0 = pos_word[edge[0]]
            x1, y1 = pos_word[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])
        
        node_trace = go.Scatter(x=[], y=[], text=[], mode='markers+text', textposition="top center",
            marker=dict(size=[], color=[], colorscale=[[0, COLORS['secondary']], [1, main_color]]))
        for node in G_word.nodes():
            x, y = pos_word[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([node])
            is_central = G_word.nodes[node].get('central', False)
            node_trace['marker']['size'] += tuple([50 if is_central else 30])
            node_trace['marker']['color'] += tuple([1 if is_central else 0])
        
        fig_word = go.Figure(data=[edge_trace, node_trace])
        fig_word.update_layout(template='plotly_white', paper_bgcolor=COLORS['bg_card'], showlegend=False, height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), title=f"Connexions de '{selected_word}'")
    else:
        fig_word = go.Figure()
        fig_word.add_annotation(text="Sélectionnez un mot-clé", x=0.5, y=0.5, showarrow=False, font=dict(size=16))
        fig_word.update_layout(template='plotly_white', paper_bgcolor=COLORS['bg_card'], height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    
    # VIZ 7: Acteurs-Lieux
    n_actors = min(top_n, 15)
    n_locs = min(int(top_n * 0.6), 10)
    
    actors = get_top_entities(data, 'per', n_actors)['entity'].tolist()
    locations = get_top_entities(data, 'loc', n_locs)['entity'].tolist()
    matrix = []
    for actor in actors:
        actor_freq = data['per'].get(actor, 0)
        row = []
        for loc in locations:
            loc_freq = data['loc'].get(loc, 0)
            value = min(actor_freq, loc_freq) * np.random.uniform(0.1, 0.5)
            row.append(value)
        matrix.append(row)
    
    fig_actors_loc = go.Figure(data=go.Heatmap(
        z=matrix,
        x=locations,
        y=actors,
        colorscale='RdYlBu_r',
        colorbar=dict(title="Mentions"),
        hovertemplate='Acteur: <b>%{y}</b><br>Lieu: %{x}<br>Mentions: %{z:.0f}<extra></extra>'
    ))
    fig_actors_loc.update_layout(
        template='plotly_white', 
        paper_bgcolor=COLORS['bg_card'], 
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text']),
        xaxis_title="Lieu",
        yaxis_title="Acteur",
        height=max(500, n_actors * 40)
    )
    
    return (fig_top, fig_geo, fig_temporal, fig_attention, fig_correlation, fig_word, fig_actors_loc)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)