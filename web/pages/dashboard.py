"""
Página principal: Dashboard com KPIs e alertas
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.analysis import (
    RainfallAnalyzer,
    TemperatureAnalyzer,
    HumidityAnalyzer,
    WindAnalyzer,
    SolarAnalyzer
)
from src.utils.formatters import Formatters


def create_kpi_card(title, value, icon, delta=None, delta_color="normal"):
    """Cria um card de KPI."""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 3rem;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.metric(label=title, value=value, delta=delta, delta_color=delta_color)


def show_main_kpis(df_daily):
    """Exibe os principais KPIs."""
    st.markdown("## 📊 Indicadores Principais")
    
    # Últimos dados disponíveis
    last_day = df_daily.iloc[-1]
    
    # KPIs em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp = last_day.get('temperatura_media', 0)
        temp_formatted = Formatters.format_temperature(temp)
        st.metric(
            label="🌡️ Temperatura Média",
            value=temp_formatted,
            delta=None
        )
    
    with col2:
        umid = last_day.get('umidade_media', 0)
        umid_formatted = Formatters.format_percentage(umid)
        st.metric(
            label="💧 Umidade Média",
            value=umid_formatted,
            delta=None
        )
    
    with col3:
        # Chuva acumulada últimos 7 dias
        last_7_days = df_daily.tail(7)
        chuva_col = None
        for col in ['chuva_acumulada', 'chuva_total', 'chuva_dia', 'precipitacao']:
            if col in last_7_days.columns:
                chuva_col = col
                break
        
        if chuva_col:
            chuva_7d = last_7_days[chuva_col].sum()
            chuva_formatted = Formatters.format_rainfall(chuva_7d)
        else:
            chuva_formatted = "N/A"
        
        st.metric(
            label="🌧️ Chuva 7 dias",
            value=chuva_formatted,
            delta=None
        )
    
    with col4:
        # Dias sem chuva
        rain_analyzer = RainfallAnalyzer(df_daily)
        dry_spells = rain_analyzer.calculate_dry_spells()
        
        if dry_spells and len(dry_spells) > 0:
            # Verificar se o último período seco ainda está ativo
            last_spell = dry_spells[-1]
            if 'fim' in last_spell and last_spell['fim'] == df_daily['data'].iloc[-1]:
                dias_sem_chuva = last_spell['duracao']
            else:
                dias_sem_chuva = 0
        else:
            dias_sem_chuva = 0
        
        st.metric(
            label="🏜️ Dias sem Chuva",
            value=str(dias_sem_chuva),
            delta=None
        )


def show_trend_charts(df_daily):
    """Exibe gráficos de tendência."""
    st.markdown("## 📈 Tendências Recentes (Últimos 30 dias)")
    
    # Últimos 30 dias
    df_recent = df_daily.tail(30).copy()
    
    # Criar tabs para diferentes variáveis
    tab1, tab2, tab3 = st.tabs(["🌡️ Temperatura", "💧 Umidade", "🌧️ Chuva"])
    
    with tab1:
        fig = go.Figure()
        
        if 'temperatura_max' in df_recent.columns:
            fig.add_trace(go.Scatter(
                x=df_recent['data'],
                y=df_recent['temperatura_max'],
                name='Máxima',
                line=dict(color='red', width=2)
            ))
        
        if 'temperatura_media' in df_recent.columns:
            fig.add_trace(go.Scatter(
                x=df_recent['data'],
                y=df_recent['temperatura_media'],
                name='Média',
                line=dict(color='orange', width=2)
            ))
        
        if 'temperatura_min' in df_recent.columns:
            fig.add_trace(go.Scatter(
                x=df_recent['data'],
                y=df_recent['temperatura_min'],
                name='Mínima',
                line=dict(color='blue', width=2)
            ))
        
        fig.update_layout(
            title="Evolução da Temperatura",
            xaxis_title="Data",
            yaxis_title="Temperatura (°C)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = go.Figure()
        
        if 'umidade_max' in df_recent.columns:
            fig.add_trace(go.Scatter(
                x=df_recent['data'],
                y=df_recent['umidade_max'],
                name='Máxima',
                line=dict(color='darkblue', width=2)
            ))
        
        if 'umidade_media' in df_recent.columns:
            fig.add_trace(go.Scatter(
                x=df_recent['data'],
                y=df_recent['umidade_media'],
                name='Média',
                line=dict(color='blue', width=2)
            ))
        
        if 'umidade_min' in df_recent.columns:
            fig.add_trace(go.Scatter(
                x=df_recent['data'],
                y=df_recent['umidade_min'],
                name='Mínima',
                line=dict(color='lightblue', width=2)
            ))
        
        fig.update_layout(
            title="Evolução da Umidade",
            xaxis_title="Data",
            yaxis_title="Umidade (%)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Encontrar coluna de chuva
        chuva_col = None
        for col in ['chuva_acumulada', 'chuva_total', 'chuva_dia', 'precipitacao']:
            if col in df_recent.columns:
                chuva_col = col
                break
        
        if chuva_col:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_recent['data'],
                y=df_recent[chuva_col],
                name='Precipitação',
                marker_color='steelblue'
            ))
            
            fig.update_layout(
                title="Precipitação Diária",
                xaxis_title="Data",
                yaxis_title="Chuva (mm)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Dados de precipitação não disponíveis")


def show_agricultural_alerts(df_daily):
    """Exibe alertas agrícolas."""
    st.markdown("## 🚨 Alertas Agrícolas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Alerta de irrigação
        rain_analyzer = RainfallAnalyzer(df_daily)
        irrigation = rain_analyzer.calculate_irrigation_need()
        
        if irrigation and irrigation.get('necessita_irrigacao'):
            st.markdown("""
            <div class="alert-warning">
                <h4>💧 Alerta de Irrigação</h4>
                <p><strong>Necessidade:</strong> {}</p>
                <p><strong>Dias sem chuva significativa:</strong> {}</p>
                <p><strong>Recomendação:</strong> {}</p>
            </div>
            """.format(
                irrigation.get('nivel_necessidade', 'N/A'),
                irrigation.get('dias_sem_chuva', 'N/A'),
                irrigation.get('recomendacao', 'N/A')
            ), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <h4>✅ Irrigação</h4>
                <p>Umidade do solo adequada. Não há necessidade de irrigação no momento.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Alerta de aplicação de defensivos
        wind_analyzer = WindAnalyzer(df_daily)
        application = wind_analyzer.calculate_application_suitability()
        
        if application:
            status = application.get('status', 'N/A')
            dias_ideais_semana = application.get('dias_ideais_ultima_semana', 0)
            
            if status == 'FAVORÁVEL':
                alert_class = "alert-success"
                icon = "✅"
            elif status == 'MODERADO':
                alert_class = "alert-warning"
                icon = "⚠️"
            else:
                alert_class = "alert-danger"
                icon = "❌"
            
            st.markdown(f"""
            <div class="{alert_class}">
                <h4>{icon} Aplicação de Defensivos</h4>
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Dias ideais (última semana):</strong> {dias_ideais_semana}</p>
                <p><strong>Porcentagem ideal:</strong> {application.get('porcentagem_ideal', 0):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Alerta de conforto térmico para gado
    st.markdown("### 🐄 Conforto Térmico para Gado")
    
    temp_analyzer = TemperatureAnalyzer(df_daily)
    
    # Últimos 7 dias
    df_recent = df_daily.tail(7)
    
    dias_desconfortaveis = 0
    for _, row in df_recent.iterrows():
        if 'temperatura_max' in row and row['temperatura_max'] > 27:
            dias_desconfortaveis += 1
    
    if dias_desconfortaveis >= 5:
        st.markdown("""
        <div class="alert-danger">
            <h4>🔥 Alerta: Estresse Térmico</h4>
            <p>Temperaturas elevadas nos últimos dias podem causar estresse térmico no gado.</p>
            <p><strong>Recomendações:</strong></p>
            <ul>
                <li>Garantir acesso à água fresca e sombra</li>
                <li>Evitar manejo intensivo nas horas mais quentes</li>
                <li>Monitorar sinais de estresse térmico</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    elif dias_desconfortaveis > 0:
        st.markdown("""
        <div class="alert-warning">
            <h4>⚠️ Atenção: Temperaturas Elevadas</h4>
            <p>Alguns dias com temperaturas acima do ideal para conforto do gado.</p>
            <p><strong>Recomendação:</strong> Manter atenção aos animais e garantir acesso à água e sombra.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            <h4>✅ Conforto Térmico Adequado</h4>
            <p>Temperaturas dentro da faixa de conforto para o gado.</p>
        </div>
        """, unsafe_allow_html=True)


def show(df_raw, df_daily, df_monthly):
    """Função principal da página de dashboard."""
    
    # Cabeçalho
    st.markdown('<p class="main-header">🌦️ Dashboard Meteorológico</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Estação Weathercloud Galinhada - Ribeirão Claro, PR</p>', unsafe_allow_html=True)
    
    # KPIs principais
    show_main_kpis(df_daily)
    
    st.markdown("---")
    
    # Gráficos de tendência
    show_trend_charts(df_daily)
    
    st.markdown("---")
    
    # Alertas agrícolas
    show_agricultural_alerts(df_daily)
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>💡 <strong>Dica:</strong> Use a barra lateral para navegar entre as diferentes seções do sistema.</p>
        <p style='font-size: 0.9rem;'>Dados atualizados em: {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y às %H:%M')), unsafe_allow_html=True)
