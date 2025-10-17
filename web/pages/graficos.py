"""
Página 2: Análise Gráfica Organizada
Sistema de visualização com navegação por categoria
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import timedelta
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


def filter_by_period(df, period_days):
    """Filtra dados pelo período."""
    if period_days == "all":
        return df
    max_date = df['data'].max()
    start_date = max_date - timedelta(days=int(period_days))
    return df[df['data'] >= start_date]


# ============================================================================
# GRÁFICOS DE PRECIPITAÇÃO
# ============================================================================

def grafico_precipitacao_diaria(df):
    """Gráfico de barras - Precipitação diária."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['data'],
        y=df['chuva_acumulada'],
        marker_color='#1f77b4',
        name='Precipitação'
    ))
    
    fig.update_layout(
        title='Precipitação Diária',
        xaxis_title='Data',
        yaxis_title='Precipitação (mm)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def grafico_precipitacao_acumulada(df):
    """Gráfico de linha - Precipitação acumulada no período."""
    df_copy = df.copy()
    df_copy['acumulado'] = df_copy['chuva_acumulada'].cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_copy['data'],
        y=df_copy['acumulado'],
        fill='tozeroy',
        line=dict(color='#2ca02c', width=2),
        name='Acumulado'
    ))
    
    fig.update_layout(
        title='Precipitação Acumulada no Período',
        xaxis_title='Data',
        yaxis_title='Chuva Acumulada (mm)',
        height=500,
        template='plotly_white'
    )
    
    return fig


def grafico_precipitacao_mensal(df):
    """Gráfico de barras - Total mensal."""
    if 'mes_nome' not in df.columns:
        return None
    
    df_mensal = df.groupby(['ano', 'mes', 'mes_nome'])['chuva_acumulada'].sum().reset_index()
    df_mensal['mes_ano'] = df_mensal['mes_nome'] + '/' + df_mensal['ano'].astype(str)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_mensal['mes_ano'],
        y=df_mensal['chuva_acumulada'],
        marker_color='#17becf',
        name='Total Mensal'
    ))
    
    fig.update_layout(
        title='Distribuição Mensal de Precipitação',
        xaxis_title='Mês',
        yaxis_title='Precipitação Total (mm)',
        height=500,
        template='plotly_white'
    )
    
    return fig


def grafico_precipitacao_intensidade(df):
    """Histograma - Distribuição de intensidades."""
    df_chuva = df[df['chuva_acumulada'] > 0]
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df_chuva['chuva_acumulada'],
        nbinsx=20,
        marker_color='#9467bd',
        name='Frequência'
    ))
    
    fig.update_layout(
        title='Distribuição de Intensidade de Chuva',
        xaxis_title='Precipitação (mm)',
        yaxis_title='Frequência (dias)',
        height=500,
        template='plotly_white'
    )
    
    return fig


def grafico_precipitacao_top10(df):
    """Gráfico de barras - Top 10 dias mais chuvosos."""
    top10 = df.nlargest(10, 'chuva_acumulada')[['data', 'chuva_acumulada']].copy()
    top10['data_str'] = top10['data'].dt.strftime('%d/%m/%Y')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top10['data_str'],
        y=top10['chuva_acumulada'],
        marker_color='#d62728',
        name='Precipitação'
    ))
    
    fig.update_layout(
        title='Top 10 Dias Mais Chuvosos',
        xaxis_title='Data',
        yaxis_title='Precipitação (mm)',
        height=500,
        template='plotly_white'
    )
    
    return fig


# ============================================================================
# GRÁFICOS DE TEMPERATURA
# ============================================================================

def grafico_temperatura_evolucao(df):
    """Gráfico de linhas - Evolução temporal."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_max'],
        name='Máxima', line=dict(color='#d62728', width=2),
        mode='lines'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_media'],
        name='Média', line=dict(color='#ff7f0e', width=2),
        mode='lines'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_min'],
        name='Mínima', line=dict(color='#1f77b4', width=2),
        mode='lines'
    ))
    
    fig.update_layout(
        title='Evolução da Temperatura',
        xaxis_title='Data',
        yaxis_title='Temperatura (°C)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def grafico_temperatura_amplitude(df):
    """Gráfico de área - Amplitude térmica."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_max'],
        fill=None, mode='lines',
        line=dict(color='rgba(214, 39, 40, 0.5)'),
        name='Máxima'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_min'],
        fill='tonexty', mode='lines',
        line=dict(color='rgba(31, 119, 180, 0.5)'),
        fillcolor='rgba(255, 127, 14, 0.2)',
        name='Mínima'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_media'],
        mode='lines', line=dict(color='#ff7f0e', width=3),
        name='Média'
    ))
    
    fig.update_layout(
        title='Amplitude Térmica Diária',
        xaxis_title='Data',
        yaxis_title='Temperatura (°C)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def grafico_temperatura_mensal(df):
    """Box plot - Distribuição mensal."""
    if 'mes_nome' not in df.columns:
        return None
    
    fig = go.Figure()
    
    for mes in df['mes_nome'].unique():
        df_mes = df[df['mes_nome'] == mes]
        fig.add_trace(go.Box(
            y=df_mes['temperatura_media'],
            name=mes,
            boxmean='sd'
        ))
    
    fig.update_layout(
        title='Distribuição de Temperatura por Mês',
        yaxis_title='Temperatura (°C)',
        height=500,
        template='plotly_white'
    )
    
    return fig


# ============================================================================
# GRÁFICOS DE UMIDADE
# ============================================================================

def grafico_umidade_evolucao(df):
    """Gráfico de linhas - Evolução da umidade."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['umidade_max'],
        name='Máxima', line=dict(color='#8c564b', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['umidade_media'],
        name='Média', line=dict(color='#e377c2', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['umidade_min'],
        name='Mínima', line=dict(color='#7f7f7f', width=2)
    ))
    
    fig.update_layout(
        title='Evolução da Umidade Relativa',
        xaxis_title='Data',
        yaxis_title='Umidade (%)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def grafico_umidade_mensal(df):
    """Box plot - Distribuição mensal de umidade."""
    if 'mes_nome' not in df.columns:
        return None
    
    fig = go.Figure()
    
    for mes in df['mes_nome'].unique():
        df_mes = df[df['mes_nome'] == mes]
        fig.add_trace(go.Box(
            y=df_mes['umidade_media'],
            name=mes
        ))
    
    fig.update_layout(
        title='Distribuição de Umidade por Mês',
        yaxis_title='Umidade (%)',
        height=500,
        template='plotly_white'
    )
    
    return fig


# ============================================================================
# GRÁFICOS DE VENTO
# ============================================================================

def grafico_vento_velocidade(df):
    """Gráfico de linhas - Velocidade do vento."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['vento_velocidade_max'],
        name='Vel. Máxima', line=dict(color='#9467bd', width=2)
    ))
    
    if 'vento_rajada_max' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['data'], y=df['vento_rajada_max'],
            name='Rajada', line=dict(color='#d62728', width=2, dash='dot')
        ))
    
    fig.update_layout(
        title='Velocidade do Vento',
        xaxis_title='Data',
        yaxis_title='Velocidade (m/s)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


# ============================================================================
# GRÁFICOS DE CORRELAÇÃO
# ============================================================================

def grafico_correlacao_temp_umidade(df):
    """Correlação Temperatura vs Umidade."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['temperatura_media'],
                  name='Temperatura', line=dict(color='#ff7f0e', width=2)),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['umidade_media'],
                  name='Umidade', line=dict(color='#e377c2', width=2, dash='dot')),
        secondary_y=True
    )
    
    corr = df['temperatura_media'].corr(df['umidade_media'])
    
    fig.update_layout(
        title=f'Temperatura vs Umidade (Correlação: {corr:.3f})',
        xaxis_title='Data',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Temperatura (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Umidade (%)", secondary_y=True)
    
    return fig


def grafico_correlacao_chuva_umidade(df):
    """Correlação Chuva vs Umidade."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=df['data'], y=df['chuva_acumulada'],
              name='Chuva', marker_color='#1f77b4'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['umidade_media'],
                  name='Umidade', line=dict(color='#e377c2', width=2)),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Precipitação vs Umidade',
        xaxis_title='Data',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Precipitação (mm)", secondary_y=False)
    fig.update_yaxes(title_text="Umidade (%)", secondary_y=True)
    
    return fig


def grafico_conforto_termico_aves(df):
    """Análise de Conforto Térmico para Galinhas (Zona de 18-24°C)."""
    fig = go.Figure()
    
    # Zona de conforto ideal (18-24°C)
    fig.add_hrect(y0=18, y1=24, fillcolor="lightgreen", opacity=0.2,
                  annotation_text="Zona de Conforto", annotation_position="top left")
    
    # Zona de estresse por calor (>28°C)
    fig.add_hrect(y0=28, y1=df['temperatura_max'].max()+2, fillcolor="red", opacity=0.1,
                  annotation_text="Estresse Térmico", annotation_position="top left")
    
    # Temperatura máxima
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_max'],
        name='Temp. Máxima', line=dict(color='#ff4444', width=2),
        fill='tonexty', fillcolor='rgba(255,68,68,0.1)'
    ))
    
    # Temperatura média
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_media'],
        name='Temp. Média', line=dict(color='#ff7f0e', width=2)
    ))
    
    # Temperatura mínima
    fig.add_trace(go.Scatter(
        x=df['data'], y=df['temperatura_min'],
        name='Temp. Mínima', line=dict(color='#2ca02c', width=2),
        fill='tonexty', fillcolor='rgba(44,160,44,0.1)'
    ))
    
    # Calcular dias fora da zona de conforto
    dias_estresse_calor = (df['temperatura_max'] > 28).sum()
    dias_estresse_frio = (df['temperatura_min'] < 18).sum()
    
    fig.update_layout(
        title=f'Conforto Térmico para Aves - Estresse: {dias_estresse_calor} dias calor, {dias_estresse_frio} dias frio',
        xaxis_title='Data',
        yaxis_title='Temperatura (°C)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def grafico_gestao_ventilacao(df):
    """Análise para Gestão de Inlets e Exaustores (Temp + Umidade + Vento)."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Temperatura e Umidade', 'Velocidade do Vento'),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )
    
    # Gráfico 1: Temperatura e Umidade
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['temperatura_max'],
                  name='Temp. Máxima', line=dict(color='#ff4444', width=2)),
        row=1, col=1, secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['umidade_media'],
                  name='Umidade Média', line=dict(color='#2ca02c', width=2, dash='dot')),
        row=1, col=1, secondary_y=True
    )
    
    # Zona crítica para ventilação (>26°C e >70% umidade)
    df_critico = df[(df['temperatura_max'] > 26) & (df['umidade_media'] > 70)]
    if len(df_critico) > 0:
        fig.add_trace(
            go.Scatter(x=df_critico['data'], y=df_critico['temperatura_max'],
                      mode='markers', name='Crítico (T>26°C + U>70%)',
                      marker=dict(color='red', size=10, symbol='x')),
            row=1, col=1, secondary_y=False
        )
    
    # Gráfico 2: Velocidade do Vento
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['vento_velocidade_media'],
                  name='Vento Médio', line=dict(color='#1f77b4', width=2)),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['vento_rajada_max'],
                  name='Rajada Máxima', line=dict(color='#ff7f0e', width=2, dash='dash')),
        row=2, col=1
    )
    
    dias_criticos = len(df_critico)
    
    fig.update_layout(
        title=f'Gestão de Ventilação - {dias_criticos} dias críticos identificados',
        height=700,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True
    )
    
    fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Umidade (%)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Velocidade (km/h)", row=2, col=1)
    fig.update_xaxes(title_text="Data", row=2, col=1)
    
    return fig


def grafico_umidade_cama(df):
    """Análise de Risco para Umidade da Cama (Chuva + Umidade Relativa)."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Precipitação
    fig.add_trace(
        go.Bar(x=df['data'], y=df['chuva_acumulada'],
              name='Precipitação', marker_color='#1f77b4', opacity=0.6),
        secondary_y=False
    )
    
    # Umidade relativa
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['umidade_media'],
                  name='Umidade Média', line=dict(color='#e377c2', width=2)),
        secondary_y=True
    )
    
    # Linha de alerta para umidade da cama (>70%)
    fig.add_hline(y=70, line_dash="dash", line_color="orange",
                  annotation_text="Limite Ideal Umidade (70%)",
                  annotation_position="right", secondary_y=True)
    
    # Identificar períodos de risco (chuva + umidade alta)
    df['risco_cama'] = ((df['chuva_acumulada'] > 5) & (df['umidade_media'] > 70)).astype(int)
    dias_risco = df['risco_cama'].sum()
    
    # Marcar dias de alto risco
    df_risco = df[df['risco_cama'] == 1]
    if len(df_risco) > 0:
        fig.add_trace(
            go.Scatter(x=df_risco['data'], y=df_risco['umidade_media'],
                      mode='markers', name='Alto Risco para Cama',
                      marker=dict(color='red', size=12, symbol='diamond')),
            secondary_y=True
        )
    
    fig.update_layout(
        title=f'Risco para Umidade da Cama - {dias_risco} dias de alto risco',
        xaxis_title='Data',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Precipitação (mm)", secondary_y=False)
    fig.update_yaxes(title_text="Umidade Relativa (%)", secondary_y=True)
    
    return fig


def grafico_estresse_termico_agricultura(df):
    """Índice de Estresse Térmico para Plantas (Temp + Umidade + Radiação)."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Temperatura e Umidade', 'Radiação Solar'),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )
    
    # Gráfico 1: Temperatura e Umidade
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['temperatura_max'],
                  name='Temp. Máxima', line=dict(color='#ff4444', width=2),
                  fill='tozeroy', fillcolor='rgba(255,68,68,0.1)'),
        row=1, col=1, secondary_y=False
    )
    
    # Zona crítica para plantas (>35°C)
    fig.add_hrect(y0=35, y1=df['temperatura_max'].max()+2,
                  fillcolor="red", opacity=0.1,
                  annotation_text="Estresse Térmico",
                  row=1, col=1, secondary_y=False)
    
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['umidade_media'],
                  name='Umidade Média', line=dict(color='#2ca02c', width=2, dash='dot')),
        row=1, col=1, secondary_y=True
    )
    
    # Gráfico 2: Radiação Solar
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['radiacao_solar_max'],
                  name='Radiação Solar Máx', line=dict(color='#ffa500', width=2),
                  fill='tozeroy', fillcolor='rgba(255,165,0,0.1)'),
        row=2, col=1
    )
    
    # Identificar dias de alto estresse (>32°C + umidade <40%)
    dias_estresse = ((df['temperatura_max'] > 32) & (df['umidade_media'] < 40)).sum()
    
    fig.update_layout(
        title=f'Estresse Térmico para Agricultura - {dias_estresse} dias críticos',
        height=700,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True
    )
    
    fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Umidade (%)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Radiação (W/m²)", row=2, col=1)
    fig.update_xaxes(title_text="Data", row=2, col=1)
    
    return fig


def grafico_deficit_hidrico(df):
    """Análise de Déficit Hídrico para Agricultura (Chuva + Evapotranspiração Estimada)."""
    # Estimar evapotranspiração simplificada (método Thornthwaite simplificado)
    # ETo aproximada = 0.46 * Tmedia + 8 (para latitudes tropicais)
    df['eto_estimada'] = 0.46 * df['temperatura_media'] + 8
    df['balanco_hidrico'] = df['chuva_acumulada'] - df['eto_estimada']
    df['deficit_acumulado'] = df['balanco_hidrico'].cumsum()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Balanço Hídrico Diário', 'Déficit Acumulado'),
        vertical_spacing=0.12
    )
    
    # Gráfico 1: Balanço diário
    colors = ['green' if x > 0 else 'red' for x in df['balanco_hidrico']]
    fig.add_trace(
        go.Bar(x=df['data'], y=df['balanco_hidrico'],
              name='Balanço Hídrico', marker_color=colors),
        row=1, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=1, col=1)
    
    # Gráfico 2: Déficit acumulado
    fig.add_trace(
        go.Scatter(x=df['data'], y=df['deficit_acumulado'],
                  name='Déficit Acumulado', line=dict(color='#d62728', width=3),
                  fill='tozeroy', fillcolor='rgba(214,39,40,0.1)'),
        row=2, col=1
    )
    
    # Linha de alerta (-50mm)
    fig.add_hline(y=-50, line_dash="dash", line_color="orange",
                  annotation_text="Alerta Déficit", row=2, col=1)
    
    dias_deficit = (df['balanco_hidrico'] < 0).sum()
    deficit_max = df['deficit_acumulado'].min()
    
    fig.update_layout(
        title=f'Déficit Hídrico Agrícola - {dias_deficit} dias com déficit (Mínimo: {deficit_max:.1f}mm)',
        height=700,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True
    )
    
    fig.update_yaxes(title_text="Balanço (mm)", row=1, col=1)
    fig.update_yaxes(title_text="Déficit Acumulado (mm)", row=2, col=1)
    fig.update_xaxes(title_text="Data", row=2, col=1)
    
    return fig


# ============================================================================
# CONFIGURAÇÃO DE GRÁFICOS DISPONÍVEIS
# ============================================================================

GRAFICOS_CONFIG = {
    "🌧️ Precipitação": {
        "Precipitação Diária": grafico_precipitacao_diaria,
        "Acumulado no Período": grafico_precipitacao_acumulada,
        "Distribuição Mensal": grafico_precipitacao_mensal,
        "Distribuição de Intensidade": grafico_precipitacao_intensidade,
        "Top 10 Dias Mais Chuvosos": grafico_precipitacao_top10
    },
    "🌡️ Temperatura": {
        "Evolução Temporal": grafico_temperatura_evolucao,
        "Amplitude Térmica": grafico_temperatura_amplitude,
        "Distribuição Mensal": grafico_temperatura_mensal
    },
    "💧 Umidade": {
        "Evolução Temporal": grafico_umidade_evolucao,
        "Distribuição Mensal": grafico_umidade_mensal
    },
    "💨 Vento": {
        "Velocidade e Rajadas": grafico_vento_velocidade
    },
    "🔗 Correlações": {
        "Temperatura vs Umidade": grafico_correlacao_temp_umidade,
        "Precipitação vs Umidade": grafico_correlacao_chuva_umidade
    },
    "🐔 Avicultura": {
        "Conforto Térmico das Aves": grafico_conforto_termico_aves,
        "Gestão de Ventilação (Inlets/Exaustores)": grafico_gestao_ventilacao,
        "Risco de Umidade na Cama": grafico_umidade_cama
    },
    "🌾 Agricultura": {
        "Estresse Térmico de Plantas": grafico_estresse_termico_agricultura,
        "Déficit Hídrico": grafico_deficit_hidrico
    }
}


def show_statistics(df, category):
    """Exibe estatísticas relevantes."""
    st.markdown("### 📊 Estatísticas do Período")
    
    if category == "🌧️ Precipitação":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total = df['chuva_acumulada'].sum()
            st.metric("💧 Total", f"{total:.1f} mm")
        with col2:
            dias_chuva = (df['chuva_acumulada'] > 0).sum()
            st.metric("📅 Dias com Chuva", f"{dias_chuva}")
        with col3:
            max_val = df['chuva_acumulada'].max()
            st.metric("🌧️ Máximo Diário", f"{max_val:.1f} mm")
        with col4:
            media = df[df['chuva_acumulada'] > 0]['chuva_acumulada'].mean()
            st.metric("📊 Média (dias c/ chuva)", f"{media:.1f} mm")
    
    elif category == "🌡️ Temperatura":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌡️ Temp. Média", f"{df['temperatura_media'].mean():.1f}°C")
        with col2:
            st.metric("🔥 Máxima Absoluta", f"{df['temperatura_max'].max():.1f}°C")
        with col3:
            st.metric("❄️ Mínima Absoluta", f"{df['temperatura_min'].min():.1f}°C")
        with col4:
            amplitude = df['temperatura_max'].max() - df['temperatura_min'].min()
            st.metric("📊 Amplitude Total", f"{amplitude:.1f}°C")
    
    elif category == "💧 Umidade":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💧 Umidade Média", f"{df['umidade_media'].mean():.1f}%")
        with col2:
            st.metric("📈 Máxima", f"{df['umidade_max'].max():.1f}%")
        with col3:
            st.metric("📉 Mínima", f"{df['umidade_min'].min():.1f}%")
    
    elif category == "💨 Vento":
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💨 Vel. Média", f"{df['vento_velocidade_media'].mean():.1f} km/h")
        with col2:
            if 'vento_rajada_max' in df.columns:
                st.metric("🌪️ Rajada Máxima", f"{df['vento_rajada_max'].max():.1f} km/h")
    
    elif category == "🐔 Avicultura":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            dias_conforto = ((df['temperatura_min'] >= 18) & (df['temperatura_max'] <= 24)).sum()
            st.metric("✅ Dias em Conforto", f"{dias_conforto}")
        with col2:
            dias_calor = (df['temperatura_max'] > 28).sum()
            st.metric("🔥 Dias c/ Estresse Calor", f"{dias_calor}", delta=None, delta_color="inverse")
        with col3:
            dias_criticos = ((df['temperatura_max'] > 26) & (df['umidade_media'] > 70)).sum()
            st.metric("⚠️ Dias Críticos Ventilação", f"{dias_criticos}")
        with col4:
            dias_risco_cama = ((df['chuva_acumulada'] > 5) & (df['umidade_media'] > 70)).sum()
            st.metric("💧 Dias Risco Cama", f"{dias_risco_cama}")
    
    elif category == "🌾 Agricultura":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_chuva = df['chuva_acumulada'].sum()
            st.metric("💧 Precipitação Total", f"{total_chuva:.1f} mm")
        with col2:
            dias_estresse = ((df['temperatura_max'] > 32) & (df['umidade_media'] < 40)).sum()
            st.metric("🌡️ Dias Estresse Térmico", f"{dias_estresse}")
        with col3:
            if 'radiacao_solar_max' in df.columns:
                rad_media = df['radiacao_solar_max'].mean()
                st.metric("☀️ Radiação Média", f"{rad_media:.0f} W/m²")
        with col4:
            dias_sem_chuva = (df['chuva_acumulada'] == 0).sum()
            st.metric("🌵 Dias Sem Chuva", f"{dias_sem_chuva}")


def show(df_raw, df_daily, df_monthly):
    """Exibe a página de gráficos."""
    
    # Inicializar valores padrão na sessão se não existirem
    if 'categoria' not in st.session_state:
        st.session_state.categoria = "🌧️ Precipitação"
    if 'tipo_grafico' not in st.session_state:
        st.session_state.tipo_grafico = list(GRAFICOS_CONFIG[st.session_state.categoria].keys())[0]
    if 'periodo' not in st.session_state:
        st.session_state.periodo = "30"
    
    # --- FILTRAR DADOS ---
    df_filtered = filter_by_period(df_daily, st.session_state.periodo)
    
    if df_filtered.empty:
        st.warning("⚠️ Nenhum dado disponível para o período selecionado.")
        return
    
    # --- GERAR E EXIBIR GRÁFICO (NO TOPO) ---
    funcao_grafico = GRAFICOS_CONFIG[st.session_state.categoria][st.session_state.tipo_grafico]
    
    try:
        fig = funcao_grafico(df_filtered)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Não foi possível gerar este gráfico com os dados disponíveis.")
    
    except Exception as e:
        st.error(f"❌ Erro ao gerar gráfico: {str(e)}")
        st.exception(e)
    
    st.markdown("---")
    
    # --- CONTROLES (ABAIXO DO GRÁFICO) ---
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Seletor de categoria
        categoria = st.selectbox(
            "📂 Categoria",
            list(GRAFICOS_CONFIG.keys()),
            index=list(GRAFICOS_CONFIG.keys()).index(st.session_state.categoria),
            key="select_categoria"
        )
        if categoria != st.session_state.categoria:
            st.session_state.categoria = categoria
            # Reset tipo de gráfico quando categoria muda
            st.session_state.tipo_grafico = list(GRAFICOS_CONFIG[categoria].keys())[0]
            st.rerun()
    
    with col2:
        # Seletor de tipo de gráfico (baseado na categoria)
        tipo_grafico = st.selectbox(
            "📈 Tipo de Gráfico",
            list(GRAFICOS_CONFIG[st.session_state.categoria].keys()),
            index=list(GRAFICOS_CONFIG[st.session_state.categoria].keys()).index(st.session_state.tipo_grafico) if st.session_state.tipo_grafico in GRAFICOS_CONFIG[st.session_state.categoria].keys() else 0,
            key="select_tipo"
        )
        if tipo_grafico != st.session_state.tipo_grafico:
            st.session_state.tipo_grafico = tipo_grafico
            st.rerun()
    
    with col3:
        # Seletor de período
        periodos = ["30", "60", "90", "all"]
        periodo = st.selectbox(
            "🗓️ Período",
            periodos,
            format_func=lambda x: f"{x} dias" if x != "all" else "Todos",
            index=periodos.index(st.session_state.periodo),
            key="select_periodo"
        )
        if periodo != st.session_state.periodo:
            st.session_state.periodo = periodo
            st.rerun()
    
    # --- INFO DO PERÍODO (COMPACTA) ---
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        st.metric("📅 Dias no Período", len(df_filtered))
    with col_i2:
        st.metric("📆 Data Inicial", df_filtered['data'].min().strftime('%d/%m/%Y'))
    with col_i3:
        st.metric("📆 Data Final", df_filtered['data'].max().strftime('%d/%m/%Y'))
    
    st.markdown("---")
    
    # --- ESTATÍSTICAS (NA PARTE INFERIOR) ---
    show_statistics(df_filtered, st.session_state.categoria)
