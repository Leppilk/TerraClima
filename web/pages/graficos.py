"""
Página 2: Gráficos Categorizados
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


def show_temperature_charts(df_daily):
    """Gráficos de temperatura."""
    st.markdown("### 🌡️ Análise de Temperatura")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolução temporal
        fig = go.Figure()
        
        if 'temperatura_max' in df_daily.columns:
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['temperatura_max'],
                name='Máxima',
                line=dict(color='red')
            ))
        
        if 'temperatura_media' in df_daily.columns:
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['temperatura_media'],
                name='Média',
                line=dict(color='orange')
            ))
        
        if 'temperatura_min' in df_daily.columns:
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['temperatura_min'],
                name='Mínima',
                line=dict(color='blue')
            ))
        
        fig.update_layout(
            title="Evolução da Temperatura",
            xaxis_title="Data",
            yaxis_title="Temperatura (°C)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição (boxplot)
        fig = go.Figure()
        
        for col, name in [('temperatura_max', 'Máxima'), ('temperatura_media', 'Média'), ('temperatura_min', 'Mínima')]:
            if col in df_daily.columns:
                fig.add_trace(go.Box(
                    y=df_daily[col],
                    name=name
                ))
        
        fig.update_layout(
            title="Distribuição de Temperatura",
            yaxis_title="Temperatura (°C)"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_humidity_charts(df_daily):
    """Gráficos de umidade."""
    st.markdown("### 💧 Análise de Umidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolução temporal
        fig = go.Figure()
        
        if 'umidade_max' in df_daily.columns:
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['umidade_max'],
                name='Máxima',
                line=dict(color='darkblue')
            ))
        
        if 'umidade_media' in df_daily.columns:
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['umidade_media'],
                name='Média',
                line=dict(color='blue')
            ))
        
        if 'umidade_min' in df_daily.columns:
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['umidade_min'],
                name='Mínima',
                line=dict(color='lightblue')
            ))
        
        fig.update_layout(
            title="Evolução da Umidade",
            xaxis_title="Data",
            yaxis_title="Umidade (%)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Histograma
        if 'umidade_media' in df_daily.columns:
            fig = px.histogram(
                df_daily,
                x='umidade_media',
                nbins=30,
                title="Distribuição da Umidade Média"
            )
            fig.update_layout(
                xaxis_title="Umidade (%)",
                yaxis_title="Frequência"
            )
            st.plotly_chart(fig, use_container_width=True)


def show_rain_charts(df_daily, df_monthly):
    """Gráficos de chuva."""
    st.markdown("### 🌧️ Análise de Precipitação")
    
    # Encontrar coluna de chuva
    chuva_col = None
    for col in ['chuva_total', 'chuva_dia', 'precipitacao']:
        if col in df_daily.columns:
            chuva_col = col
            break
    
    if not chuva_col:
        st.info("📊 Dados de precipitação não disponíveis")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chuva diária
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_daily['data'],
            y=df_daily[chuva_col],
            name='Precipitação',
            marker_color='steelblue'
        ))
        
        fig.update_layout(
            title="Precipitação Diária",
            xaxis_title="Data",
            yaxis_title="Chuva (mm)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Chuva acumulada
        df_daily_copy = df_daily.copy()
        df_daily_copy['chuva_acumulada'] = df_daily_copy[chuva_col].cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_daily_copy['data'],
            y=df_daily_copy['chuva_acumulada'],
            name='Acumulada',
            line=dict(color='darkblue', width=2),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title="Precipitação Acumulada",
            xaxis_title="Data",
            yaxis_title="Chuva Acumulada (mm)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Chuva mensal
    if df_monthly is not None and 'mes_nome' in df_monthly.columns:
        # Encontrar coluna de chuva mensal
        chuva_mensal_col = None
        for col in df_monthly.columns:
            if 'chuva' in col.lower() and ('sum' in col or 'total' in col):
                chuva_mensal_col = col
                break
        
        if chuva_mensal_col:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_monthly['mes_nome'],
                y=df_monthly[chuva_mensal_col],
                marker_color='teal'
            ))
            
            fig.update_layout(
                title="Precipitação Mensal",
                xaxis_title="Mês",
                yaxis_title="Chuva Total (mm)"
            )
            
            st.plotly_chart(fig, use_container_width=True)


def show_wind_charts(df_daily):
    """Gráficos de vento."""
    st.markdown("### 💨 Análise de Vento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Velocidade do vento
        if 'velocidade_vento_media' in df_daily.columns:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['velocidade_vento_media'],
                name='Velocidade Média',
                line=dict(color='green')
            ))
            
            if 'velocidade_vento_max' in df_daily.columns:
                fig.add_trace(go.Scatter(
                    x=df_daily['data'],
                    y=df_daily['velocidade_vento_max'],
                    name='Rajada Máxima',
                    line=dict(color='darkgreen', dash='dash')
                ))
            
            fig.update_layout(
                title="Velocidade do Vento",
                xaxis_title="Data",
                yaxis_title="Velocidade (km/h)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição da velocidade
        if 'velocidade_vento_media' in df_daily.columns:
            fig = px.histogram(
                df_daily,
                x='velocidade_vento_media',
                nbins=20,
                title="Distribuição da Velocidade do Vento"
            )
            fig.update_layout(
                xaxis_title="Velocidade (km/h)",
                yaxis_title="Frequência"
            )
            st.plotly_chart(fig, use_container_width=True)


def show_solar_charts(df_daily):
    """Gráficos de radiação solar."""
    st.markdown("### ☀️ Análise de Radiação Solar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Radiação solar
        if 'radiacao_solar_total' in df_daily.columns:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['radiacao_solar_total'],
                name='Radiação Total',
                line=dict(color='orange'),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title="Radiação Solar Diária",
                xaxis_title="Data",
                yaxis_title="Radiação (W/m²)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Índice UV
        if 'indice_uv' in df_daily.columns:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_daily['data'],
                y=df_daily['indice_uv'],
                name='Índice UV',
                mode='markers+lines',
                marker=dict(size=6, color=df_daily['indice_uv'], colorscale='Reds')
            ))
            
            fig.update_layout(
                title="Índice UV Diário",
                xaxis_title="Data",
                yaxis_title="Índice UV"
            )
            
            st.plotly_chart(fig, use_container_width=True)


def show_pressure_charts(df_daily):
    """Gráficos de pressão atmosférica."""
    st.markdown("### 🌐 Análise de Pressão Atmosférica")
    
    if 'pressao_atmosferica' not in df_daily.columns:
        st.info("📊 Dados de pressão atmosférica não disponíveis")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolução da pressão
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_daily['data'],
            y=df_daily['pressao_atmosferica'],
            name='Pressão',
            line=dict(color='purple')
        ))
        
        fig.update_layout(
            title="Pressão Atmosférica",
            xaxis_title="Data",
            yaxis_title="Pressão (hPa)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição
        fig = px.histogram(
            df_daily,
            x='pressao_atmosferica',
            nbins=30,
            title="Distribuição da Pressão Atmosférica"
        )
        fig.update_layout(
            xaxis_title="Pressão (hPa)",
            yaxis_title="Frequência"
        )
        st.plotly_chart(fig, use_container_width=True)


def show(df_daily, df_monthly):
    """Função principal da página de gráficos."""
    
    # Cabeçalho
    st.markdown('<p class="main-header">📈 Gráficos Meteorológicos</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Análises visuais detalhadas por categoria</p>', unsafe_allow_html=True)
    
    # Tabs para diferentes categorias
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌡️ Temperatura",
        "💧 Umidade",
        "🌧️ Chuva",
        "💨 Vento",
        "☀️ Solar",
        "🌐 Pressão"
    ])
    
    with tab1:
        show_temperature_charts(df_daily)
    
    with tab2:
        show_humidity_charts(df_daily)
    
    with tab3:
        show_rain_charts(df_daily, df_monthly)
    
    with tab4:
        show_wind_charts(df_daily)
    
    with tab5:
        show_solar_charts(df_daily)
    
    with tab6:
        show_pressure_charts(df_daily)
