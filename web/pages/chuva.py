"""
Página de Análise Histórica de Chuva
Dados integrados: Sr. Luiz (1995-2025) + Estação Weathercloud (2025)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent.parent
DADOS_PATH = BASE_DIR / "Dados" / "precipitacao_integrada_1995_2025.csv"
STATS_PATH = BASE_DIR / "Dados" / "estatisticas_chuva.json"


@st.cache_data
def carregar_dados():
    """Carrega dados integrados de precipitação."""
    df = pd.read_csv(DADOS_PATH, parse_dates=['data'])
    
    # Carregar estatísticas
    with open(STATS_PATH, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    return df, stats


def grafico_distribuicao_principal(df):
    """Gráfico principal: heatmap de precipitação (ano x mês)."""
    
    # Criar pivot table: anos nas linhas, meses nas colunas
    df_pivot = df.pivot_table(
        values='precipitacao_mm',
        index='ano',
        columns='mes',
        aggfunc='sum'
    )
    
    # Nomes dos meses
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=meses_nomes,
        y=df_pivot.index,
        colorscale=[
            [0.0, '#ffffcc'],   # Amarelo claro (seco - pouca chuva)
            [0.25, '#a1dab4'],  # Verde claro
            [0.5, '#41b6c4'],   # Azul ciano
            [0.75, '#2c7fb8'],  # Azul médio
            [1.0, '#253494']    # Azul escuro (muito chuvoso)
        ],
        colorbar=dict(
            title="Precipitação<br>(mm)",
            thickness=20,
            len=0.7,
            x=1.02,
            tickvals=[0, 150, 300, 450, 600],
            ticktext=['0', '150', '300', '450', '600+']
        ),
        hovertemplate='<b>%{y} - %{x}</b><br>Precipitação: %{z:.1f}mm<extra></extra>',
        text=df_pivot.values,
        texttemplate='%{z:.0f}',
        textfont={"size": 8, "color": "rgba(0,0,0,0.6)"},
        showscale=True
    ))
    
    fig.update_layout(
        title={
            'text': '🌧️ Mapa de Calor da Precipitação (1995-2025)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title='Mês',
        yaxis_title='Ano',
        height=700,
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(side='top'),
        yaxis=dict(autorange='reversed')  # Anos mais recentes no topo
    )
    
    return fig


def grafico_barras_temporal(df):
    """Gráfico de barras coloridas por intensidade ao longo do tempo."""
    
    df_plot = df.copy()
    
    fig = go.Figure()
    
    # Barras coloridas
    fig.add_trace(go.Bar(
        x=df_plot['data'],
        y=df_plot['precipitacao_mm'],
        marker=dict(
            color=df_plot['precipitacao_mm'],
            colorscale=[
                [0.0, '#ecf0f1'],   # Cinza claro (0-100mm)
                [0.33, '#3498db'],  # Azul (100-200mm)
                [0.66, '#f39c12'],  # Laranja (200-300mm)
                [1.0, '#e74c3c']    # Vermelho (>300mm)
            ],
            showscale=True,
            colorbar=dict(
                title="mm",
                thickness=15,
                len=0.7,
                x=1.02
            )
        ),
        hovertemplate='<b>%{x|%b/%Y}</b><br>Precipitação: %{y:.1f}mm<extra></extra>',
        name='Precipitação'
    ))
    
    # Linha de média móvel
    df_plot['media_movel'] = df_plot['precipitacao_mm'].rolling(window=12, center=True).mean()
    fig.add_trace(go.Scatter(
        x=df_plot['data'],
        y=df_plot['media_movel'],
        mode='lines',
        name='Tendência (12 meses)',
        line=dict(color='#2c3e50', width=3),
        hovertemplate='<b>Média móvel</b><br>%{y:.1f}mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '📊 Série Temporal Completa - Precipitação Mensal',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Período',
        yaxis_title='Precipitação (mm)',
        hovermode='x unified',
        template='plotly_white',
        height=450,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def grafico_anual_barras(df):
    """Gráfico de barras: total anual de precipitação."""
    
    df_anual = df.groupby('ano')['precipitacao_mm'].sum().reset_index()
    df_anual.columns = ['ano', 'total']
    
    # Média geral
    media_geral = df_anual['total'].mean()
    
    # Cores baseadas em acima/abaixo da média
    cores = ['#e74c3c' if x > media_geral else '#3498db' for x in df_anual['total']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_anual['ano'],
        y=df_anual['total'],
        marker=dict(color=cores),
        hovertemplate='<b>%{x}</b><br>Total: %{y:.0f}mm<extra></extra>',
        name='Precipitação Anual'
    ))
    
    # Linha de média
    fig.add_hline(
        y=media_geral, 
        line_dash="dash", 
        line_color="#2c3e50", 
        line_width=2,
        annotation_text=f"Média: {media_geral:.0f}mm",
        annotation_position="right"
    )
    
    fig.update_layout(
        title={
            'text': '📈 Precipitação Total por Ano',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis_title='Ano',
        yaxis_title='Precipitação Total (mm)',
        template='plotly_white',
        height=450,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)', dtick=2)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def grafico_comparacao_estacoes(df):
    """Gráfico: comparação entre as 4 estações do ano."""
    
    # Definir estações
    def get_estacao(mes):
        if mes in [12, 1, 2]:
            return 'Verão'
        elif mes in [3, 4, 5]:
            return 'Outono'
        elif mes in [6, 7, 8]:
            return 'Inverno'
        else:
            return 'Primavera'
    
    df['estacao'] = df['mes'].apply(get_estacao)
    
    # Agregar por estação
    df_estacoes = df.groupby('estacao')['precipitacao_mm'].sum().reset_index()
    ordem = ['Verão', 'Outono', 'Inverno', 'Primavera']
    df_estacoes['estacao'] = pd.Categorical(df_estacoes['estacao'], categories=ordem, ordered=True)
    df_estacoes = df_estacoes.sort_values('estacao')
    
    # Cores por estação
    cores = {'Verão': '#e74c3c', 'Outono': '#f39c12', 'Inverno': '#3498db', 'Primavera': '#2ecc71'}
    df_estacoes['cor'] = df_estacoes['estacao'].map(cores)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_estacoes['estacao'],
        y=df_estacoes['precipitacao_mm'],
        marker=dict(color=df_estacoes['cor']),
        text=df_estacoes['precipitacao_mm'].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}mm',
        hovertemplate='<b>%{x}</b><br>Total: %{y:.0f}mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': '🌦️ Qual Estação do Ano Chove Mais?', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis_title='Estação do Ano',
        yaxis_title='Precipitação Total (mm) - 31 anos',
        template='plotly_white',
        height=450,
        showlegend=False
    )
    
    return fig


def grafico_top_meses(df):
    """Gráfico: Top 10 meses mais chuvosos da história."""
    
    df_sorted = df.nlargest(10, 'precipitacao_mm').copy()
    df_sorted['label'] = df_sorted['data'].dt.strftime('%b/%Y')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_sorted['label'],
        y=df_sorted['precipitacao_mm'],
        marker=dict(
            color=df_sorted['precipitacao_mm'],
            colorscale='Blues',
            showscale=False
        ),
        text=df_sorted['precipitacao_mm'].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}mm',
        hovertemplate='<b>%{x}</b><br>%{y:.0f}mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': '🏆 Top 10 Meses Mais Chuvosos', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis_title='Mês/Ano',
        yaxis_title='Precipitação (mm)',
        template='plotly_white',
        height=450,
        showlegend=False
    )
    
    return fig


def grafico_media_mensal_simples(df):
    """Gráfico: média de chuva em cada mês do ano (simplificado)."""
    
    df_mensal = df.groupby('mes')['precipitacao_mm'].mean().reset_index()
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    df_mensal['mes_nome'] = df_mensal['mes'].map(dict(enumerate(meses, 1)))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_mensal['mes_nome'],
        y=df_mensal['precipitacao_mm'],
        mode='lines+markers',
        line=dict(color='#3498db', width=4),
        marker=dict(size=12, color='#2c3e50'),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)',
        hovertemplate='<b>%{x}</b><br>Média: %{y:.1f}mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': '📅 Qual Mês Costuma Chover Mais?', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis_title='Mês',
        yaxis_title='Média de Precipitação (mm)',
        template='plotly_white',
        height=450,
        showlegend=False
    )
    
    return fig


def grafico_anos_extremos(df):
    """Gráfico: comparação dos anos mais e menos chuvosos."""
    
    df_anual = df.groupby('ano')['precipitacao_mm'].sum().reset_index()
    df_anual.columns = ['ano', 'total']
    
    # Top 5 mais chuvosos e menos chuvosos
    top5_mais = df_anual.nlargest(5, 'total').copy()
    top5_menos = df_anual.nsmallest(5, 'total').copy()
    
    top5_mais['tipo'] = 'Mais Chuvosos'
    top5_menos['tipo'] = 'Menos Chuvosos'
    
    df_extremos = pd.concat([top5_mais, top5_menos])
    
    fig = go.Figure()
    
    # Mais chuvosos
    fig.add_trace(go.Bar(
        name='Mais Chuvosos',
        x=top5_mais['ano'].astype(str),
        y=top5_mais['total'],
        marker_color='#3498db',
        text=top5_mais['total'].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}mm'
    ))
    
    # Menos chuvosos
    fig.add_trace(go.Bar(
        name='Menos Chuvosos',
        x=top5_menos['ano'].astype(str),
        y=top5_menos['total'],
        marker_color='#f39c12',
        text=top5_menos['total'].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}mm'
    ))
    
    fig.update_layout(
        title={'text': '⚖️ Anos Extremos: Mais e Menos Chuvosos', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis_title='Ano',
        yaxis_title='Precipitação Total (mm)',
        template='plotly_white',
        height=450,
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    
    return fig


def grafico_decadas_simples(df):
    """Gráfico: quanto choveu em cada década (simplificado)."""
    
    df['decada'] = (df['ano'] // 10) * 10
    df_decadas = df.groupby('decada')['precipitacao_mm'].sum().reset_index()
    df_decadas['decada_label'] = df_decadas['decada'].astype(str) + 's'
    
    # Calcular média por década
    df_decadas['media'] = df_decadas['precipitacao_mm'] / 10  # Aproximado
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_decadas['decada_label'],
        y=df_decadas['precipitacao_mm'],
        marker=dict(
            color=df_decadas['precipitacao_mm'],
            colorscale='Viridis',
            showscale=False
        ),
        text=df_decadas['precipitacao_mm'].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}mm',
        hovertemplate='<b>%{x}</b><br>Total: %{y:.0f}mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': '📊 Como Mudou a Chuva nas Últimas Décadas?', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18}},
        xaxis_title='Década',
        yaxis_title='Precipitação Total (mm)',
        template='plotly_white',
        height=450,
        showlegend=False
    )
    
    return fig


def cards_curiosidades(stats):
    """Cards com métricas importantes dos dados históricos."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Card 1: Total Acumulado
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white;'>
            <h3 style='margin:0; font-size: 16px;'>💧 Total Acumulado</h3>
            <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{:.1f} m</p>
            <p style='font-size: 14px; margin:0; opacity: 0.9;'>31 anos de dados</p>
        </div>
        """.format(stats['total_acumulado'] / 1000), unsafe_allow_html=True)
    
    # Card 2: Mês mais chuvoso
    with col2:
        mes_info = stats['mes_mais_chuvoso']
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white;'>
            <h3 style='margin:0; font-size: 16px;'>🌧️ Mês Mais Chuvoso</h3>
            <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{:.0f} mm</p>
            <p style='font-size: 14px; margin:0; opacity: 0.9;'>{}/{}</p>
        </div>
        """.format(mes_info['valor'], mes_info['mes'], mes_info['ano']), unsafe_allow_html=True)
    
    # Card 3: Ano mais chuvoso
    with col3:
        ano_info = stats['ano_mais_chuvoso']
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 20px; border-radius: 10px; color: white;'>
            <h3 style='margin:0; font-size: 16px;'>📅 Ano Mais Chuvoso</h3>
            <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{:.0f} mm</p>
            <p style='font-size: 14px; margin:0; opacity: 0.9;'>Ano {}</p>
        </div>
        """.format(ano_info['total'], ano_info['ano']), unsafe_allow_html=True)
    
    # Card 4: Maior período seco
    with col4:
        duracao = stats['maior_seca']['duracao_meses']
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 20px; border-radius: 10px; color: white;'>
            <h3 style='margin:0; font-size: 16px;'>🌵 Maior Período Seco</h3>
            <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{} meses</p>
            <p style='font-size: 14px; margin:0; opacity: 0.9;'>Consecutivos <10mm</p>
        </div>
        """.format(duracao), unsafe_allow_html=True)


def cards_comparacoes(stats, df):
    """Cards com comparações e curiosidades interessantes sobre os dados."""
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 Curiosidades sobre os Dados")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Calcular dados necessários
    media_janeiro = df[df['mes_nome'] == 'Jan']['precipitacao_mm'].mean()
    media_julho = df[df['mes_nome'] == 'Jul']['precipitacao_mm'].mean()
    vezes_mais = media_janeiro / media_julho
    
    col1, col2 = st.columns(2)
    
    # Card 1: Comparação com Deserto do Atacama
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                    padding: 35px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    text-align: center;'>
            <p style='color: #ecf0f1; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;'>
                🏜️ Ribeirão Claro recebe em <strong>1 ano</strong> o que o Deserto do Atacama 
                (lugar mais seco do mundo) recebe em
            </p>
            <p style='color: #f39c12; font-size: 56px; font-weight: 900; margin: 0; line-height: 1;'>
                100 anos
            </p>
            <p style='color: #bdc3c7; font-size: 13px; margin: 15px 0 0 0;'>
                Atacama: ~15mm/ano
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Card 2: Volume em campo de futebol
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                    padding: 35px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    text-align: center;'>
            <p style='color: #ecf0f1; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;'>
                ⚽ Se os <strong>50,5 metros</strong> de chuva caíssem sobre um campo de futebol oficial, 
                teríamos
            </p>
            <p style='color: #3498db; font-size: 56px; font-weight: 900; margin: 0; line-height: 1;'>
                360 milhões
            </p>
            <p style='color: #bdc3c7; font-size: 13px; margin: 15px 0 0 0;'>
                de litros (144 piscinas olímpicas)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    # Card 3: Intensidade recorde
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #833ab4 0%, #fd1d1d 100%); 
                    padding: 35px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    text-align: center;'>
            <p style='color: #ecf0f1; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;'>
                ⚡ O mês mais chuvoso (<strong>Janeiro/2005</strong>) registrou mais que 
                a precipitação anual de Lisboa
            </p>
            <p style='color: #fff; font-size: 56px; font-weight: 900; margin: 0; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                600mm
            </p>
            <p style='color: #f8f9fa; font-size: 13px; margin: 15px 0 0 0;'>
                em 1 mês (Lisboa: 774mm/ano)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Card 4: Padrão sazonal
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 35px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    text-align: center;'>
            <p style='color: #1a1a1a; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0; font-weight: 500;'>
                🌦️ <strong>Janeiro</strong> (verão) chove muito mais que <strong>Julho</strong> (inverno). 
                O verão concentra 38% da chuva anual
            </p>
            <p style='color: #0d5943; font-size: 56px; font-weight: 900; margin: 0; line-height: 1;'>
                {vezes_mais:.1f}x
            </p>
            <p style='color: #1a4d3a; font-size: 13px; margin: 15px 0 0 0; font-weight: 600;'>
                Jan: {media_janeiro:.0f}mm • Jul: {media_julho:.0f}mm
            </p>
        </div>
        """, unsafe_allow_html=True)


def grafico_sazonalidade(df):
    """Gráfico de padrão sazonal."""
    
    # Calcular média por mês do ano
    df_mensal = df.groupby('mes')['precipitacao_mm'].agg(['mean', 'std']).reset_index()
    df_mensal['mes_nome'] = df_mensal['mes'].map({
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_mensal['mes_nome'],
        y=df_mensal['mean'],
        error_y=dict(type='data', array=df_mensal['std'], visible=True),
        marker_color='#3498db',
        name='Média Mensal'
    ))
    
    fig.update_layout(
        title='Padrão Sazonal de Precipitação',
        xaxis_title='Mês',
        yaxis_title='Precipitação Média (mm)',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def grafico_decadas(df):
    """Análise por décadas."""
    
    df['decada'] = (df['ano'] // 10) * 10
    df_decadas = df.groupby('decada')['precipitacao_mm'].agg(['sum', 'mean', 'count']).reset_index()
    df_decadas['decada_label'] = df_decadas['decada'].astype(str) + 's'
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Total por Década', 'Média Mensal por Década')
    )
    
    # Total por década
    fig.add_trace(
        go.Bar(
            x=df_decadas['decada_label'],
            y=df_decadas['sum'],
            marker_color='#2ecc71',
            name='Total'
        ),
        row=1, col=1
    )
    
    # Média por década
    fig.add_trace(
        go.Bar(
            x=df_decadas['decada_label'],
            y=df_decadas['mean'],
            marker_color='#e74c3c',
            name='Média'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text='Análise por Década',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    fig.update_yaxes(title_text='Precipitação Total (mm)', row=1, col=1)
    fig.update_yaxes(title_text='Precipitação Média (mm)', row=1, col=2)
    
    return fig


def grafico_tendencia(df):
    """Gráfico de tendência anual."""
    
    df_anual = df.groupby('ano')['precipitacao_mm'].sum().reset_index()
    
    # Calcular tendência linear
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(df_anual['ano'], df_anual['precipitacao_mm'])
    df_anual['tendencia'] = slope * df_anual['ano'] + intercept
    
    fig = go.Figure()
    
    # Barras anuais
    fig.add_trace(go.Bar(
        x=df_anual['ano'],
        y=df_anual['precipitacao_mm'],
        marker_color='#3498db',
        name='Precipitação Anual',
        opacity=0.7
    ))
    
    # Linha de tendência
    fig.add_trace(go.Scatter(
        x=df_anual['ano'],
        y=df_anual['tendencia'],
        mode='lines',
        line=dict(color='#e74c3c', width=3),
        name=f'Tendência (R²={r_value**2:.3f})'
    ))
    
    fig.update_layout(
        title='Tendência Anual de Precipitação',
        xaxis_title='Ano',
        yaxis_title='Precipitação Total (mm)',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig


def show():
    """Função principal da página."""
    
    st.title("🌧️ Análise Histórica de Chuvas")
    st.markdown("### Ribeirão Claro - PR (1995-2025)")
    st.markdown("---")
    
    # Carregar dados
    df, stats = carregar_dados()
    
    # Adicionar colunas auxiliares
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    df['mes_nome'] = df['data'].dt.strftime('%b')
    
    # Introdução
    st.markdown("""
    Esta página apresenta uma análise detalhada de **31 anos de dados de precipitação** 
    em Ribeirão Claro, Paraná. 
    
    Graças à dedicação do **Sr. Luiz**, que com paciência e compromisso registrou 
    manualmente cada dia de chuva durante mais de três décadas, temos hoje esse 
    valioso arquivo histórico (1995-2025). Seu trabalho meticuloso nos permite 
    compreender os padrões climáticos da nossa região.
    """, unsafe_allow_html=True)
    
    # Cards de curiosidades
    cards_curiosidades(stats)
    
    # Cards de comparações
    cards_comparacoes(stats, df)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráfico principal: Heatmap
    st.markdown("## 📊 Visualizações dos Dados")
    fig_heat = grafico_distribuicao_principal(df)
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("---")
    
    # Gráficos alternativos em abas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Série Temporal", 
        "📈 Totais Anuais", 
        "🌦️ Estações do Ano",
        "🏆 Top 10 Meses",
        "📅 Média Mensal",
        "⚖️ Anos Extremos",
        "📊 Décadas"
    ])
    
    with tab1:
        st.markdown("### Evolução Mensal Completa")
        fig_barras = grafico_barras_temporal(df)
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with tab2:
        st.markdown("### Precipitação Total por Ano")
        fig_anual = grafico_anual_barras(df)
        st.plotly_chart(fig_anual, use_container_width=True)
    
    with tab3:
        st.markdown("### Comparação entre Estações do Ano")
        fig_estacoes = grafico_comparacao_estacoes(df)
        st.plotly_chart(fig_estacoes, use_container_width=True)
    
    with tab4:
        st.markdown("### Os 10 Meses Mais Chuvosos da História")
        fig_top = grafico_top_meses(df)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with tab5:
        st.markdown("### Média de Chuva por Mês do Ano")
        fig_media = grafico_media_mensal_simples(df)
        st.plotly_chart(fig_media, use_container_width=True)
    
    with tab6:
        st.markdown("### Comparação dos Anos Extremos")
        fig_extremos = grafico_anos_extremos(df)
        st.plotly_chart(fig_extremos, use_container_width=True)
    
    with tab7:
        st.markdown("### Evolução ao Longo das Décadas")
        fig_decadas_simp = grafico_decadas_simples(df)
        st.plotly_chart(fig_decadas_simp, use_container_width=True)
    
    st.markdown("---")
    
    # Segunda linha: Sazonalidade e Décadas
    col1, col2 = st.columns(2)
    
    with col1:
        fig_saz = grafico_sazonalidade(df)
        st.plotly_chart(fig_saz, use_container_width=True)
    
    with col2:
        fig_dec = grafico_decadas(df)
        st.plotly_chart(fig_dec, use_container_width=True)
    
    st.markdown("---")
    
    # Gráfico de tendência
    fig_tend = grafico_tendencia(df)
    st.plotly_chart(fig_tend, use_container_width=True)
    
    # Rodapé com informações
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; font-size: 14px;'>
        <p><strong>Fontes de Dados:</strong></p>
        <p>📊 Pluviômetro Sr. Luiz Fonteque (1995-2025) • 🌐 Estação Weathercloud Galinhada (2025)</p>
        <p style='margin-top: 10px; font-size: 12px;'>Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)
