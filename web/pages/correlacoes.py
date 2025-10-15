"""
Página 4: Análise de Correlações
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

from src.analysis import CorrelationAnalyzer


def show_correlation_matrix(df_daily):
    """Exibe matriz de correlação interativa."""
    st.markdown("## 🔗 Matriz de Correlação")
    
    analyzer = CorrelationAnalyzer(df_daily)
    corr_matrix = analyzer.calculate_all_correlations()
    
    if corr_matrix.empty:
        st.warning("⚠️ Não foi possível calcular a matriz de correlação")
        return
    
    # Criar heatmap com plotly
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 8},
        colorbar=dict(title="Correlação")
    ))
    
    fig.update_layout(
        title="Matriz de Correlação entre Variáveis",
        xaxis_title="Variáveis",
        yaxis_title="Variáveis",
        height=800,
        width=800
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_strongest_correlations(df_daily):
    """Exibe as correlações mais fortes."""
    st.markdown("## 💪 Correlações Mais Fortes")
    
    analyzer = CorrelationAnalyzer(df_daily)
    strong_corr = analyzer.get_strongest_correlations(threshold=0.5)
    
    if not strong_corr:
        st.info("ℹ️ Nenhuma correlação forte (|r| > 0.5) encontrada")
        return
    
    # Criar DataFrame para exibição
    df_corr = pd.DataFrame(strong_corr, columns=['Variável 1', 'Variável 2', 'Correlação'])
    df_corr['Correlação'] = df_corr['Correlação'].round(3)
    df_corr['Intensidade'] = df_corr['Correlação'].abs()
    df_corr['Tipo'] = df_corr['Correlação'].apply(lambda x: 'Positiva' if x > 0 else 'Negativa')
    
    # Exibir top 15
    st.dataframe(
        df_corr[['Variável 1', 'Variável 2', 'Correlação', 'Tipo']].head(15),
        use_container_width=True
    )


def show_specific_correlations(df_daily):
    """Exibe análises específicas de correlação."""
    st.markdown("## 🔍 Análises Específicas")
    
    analyzer = CorrelationAnalyzer(df_daily)
    
    # Criar tabs para diferentes análises
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️💧 Temp × Umidade",
        "🌧️📊 Pressão × Chuva",
        "💨🌡️ Vento × Temp",
        "☀️🌡️ Solar × Temp"
    ])
    
    with tab1:
        st.markdown("### Correlação entre Temperatura e Umidade")
        
        temp_umid = analyzer.temperature_humidity_correlation()
        
        if temp_umid:
            for key, value in temp_umid.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Correlação", f"{value['correlacao']:.3f}")
                
                with col2:
                    st.metric("Significativo", "✅ Sim" if value['significativo'] else "❌ Não")
                
                with col3:
                    st.metric("Interpretação", value['interpretacao'])
                
                # Gráfico de dispersão
                if key == 'temp_media_umid_media':
                    if 'temperatura_media' in df_daily.columns and 'umidade_media' in df_daily.columns:
                        fig = px.scatter(
                            df_daily,
                            x='temperatura_media',
                            y='umidade_media',
                            title="Temperatura Média × Umidade Média",
                            labels={'temperatura_media': 'Temperatura (°C)', 'umidade_media': 'Umidade (%)'},
                            trendline='ols'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
        else:
            st.info("ℹ️ Dados insuficientes para análise")
    
    with tab2:
        st.markdown("### Correlação entre Pressão e Chuva")
        
        press_rain = analyzer.pressure_rain_correlation()
        
        if press_rain:
            for key, value in press_rain.items():
                if isinstance(value, dict) and 'correlacao' in value:
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Correlação", f"{value['correlacao']:.3f}")
                    
                    with col2:
                        st.metric("Significativo", "✅ Sim" if value['significativo'] else "❌ Não")
                    
                    with col3:
                        st.metric("Interpretação", value['interpretacao'])
                    
                    st.markdown("---")
                
                elif key == 'comparacao_pressao':
                    st.markdown("**Comparação de Pressão:**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Pressão com Chuva", f"{value.get('pressao_media_com_chuva', 0):.1f} hPa")
                    
                    with col2:
                        st.metric("Pressão sem Chuva", f"{value.get('pressao_media_sem_chuva', 0):.1f} hPa")
                    
                    with col3:
                        st.metric("Diferença", f"{value.get('diferenca', 0):.1f} hPa")
        else:
            st.info("ℹ️ Dados insuficientes para análise")
    
    with tab3:
        st.markdown("### Correlação entre Vento e Temperatura")
        
        wind_temp = analyzer.wind_temperature_correlation()
        
        if wind_temp:
            for key, value in wind_temp.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Correlação", f"{value['correlacao']:.3f}")
                
                with col2:
                    st.metric("Significativo", "✅ Sim" if value['significativo'] else "❌ Não")
                
                with col3:
                    st.metric("Interpretação", value['interpretacao'])
                
                # Gráfico de dispersão
                if 'velocidade_vento_media' in df_daily.columns and 'temperatura_media' in df_daily.columns:
                    fig = px.scatter(
                        df_daily,
                        x='velocidade_vento_media',
                        y='temperatura_media',
                        title="Velocidade do Vento × Temperatura",
                        labels={'velocidade_vento_media': 'Vento (km/h)', 'temperatura_media': 'Temperatura (°C)'},
                        trendline='ols'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Dados insuficientes para análise")
    
    with tab4:
        st.markdown("### Correlação entre Radiação Solar e Temperatura")
        
        solar_temp = analyzer.solar_temperature_correlation()
        
        if solar_temp:
            for key, value in solar_temp.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Correlação", f"{value['correlacao']:.3f}")
                
                with col2:
                    st.metric("Significativo", "✅ Sim" if value['significativo'] else "❌ Não")
                
                with col3:
                    st.metric("Interpretação", value['interpretacao'])
                
                # Gráfico de dispersão
                if 'radiacao_solar_total' in df_daily.columns and 'temperatura_max' in df_daily.columns:
                    fig = px.scatter(
                        df_daily,
                        x='radiacao_solar_total',
                        y='temperatura_max',
                        title="Radiação Solar × Temperatura Máxima",
                        labels={'radiacao_solar_total': 'Radiação (W/m²)', 'temperatura_max': 'Temperatura (°C)'},
                        trendline='ols'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Dados insuficientes para análise")


def show_interpretation_guide(df_daily):
    """Exibe guia de interpretação de correlações."""
    st.markdown("## 📖 Guia de Interpretação")
    
    st.markdown("""
    ### Como Interpretar Correlações
    
    A correlação mede a relação linear entre duas variáveis, variando de -1 a +1:
    
    #### Intensidade:
    - **0.0 - 0.3**: Fraca
    - **0.3 - 0.5**: Moderada
    - **0.5 - 0.7**: Forte
    - **0.7 - 1.0**: Muito forte
    
    #### Direção:
    - **Positiva (+)**: Quando uma variável aumenta, a outra também tende a aumentar
    - **Negativa (-)**: Quando uma variável aumenta, a outra tende a diminuir
    
    #### Significância Estatística:
    - **p-valor < 0.05**: A correlação é estatisticamente significativa
    - **p-valor ≥ 0.05**: A correlação pode ser resultado do acaso
    
    ### Exemplos Práticos:
    
    **Temperatura × Umidade (negativa forte)**
    - Quando a temperatura aumenta, a umidade relativa tende a diminuir
    - Importante para planejamento de irrigação
    
    **Radiação Solar × Temperatura (positiva forte)**
    - Mais radiação solar resulta em temperaturas mais altas
    - Útil para previsão de temperaturas máximas
    
    **Pressão × Chuva (negativa moderada)**
    - Quedas de pressão frequentemente precedem chuvas
    - Indicador útil para previsão de tempo
    """)


def show(df_daily):
    """Função principal da página de correlações."""
    
    # Cabeçalho
    st.markdown('<p class="main-header">🔗 Análise de Correlações</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Relações entre variáveis meteorológicas</p>', unsafe_allow_html=True)
    
    # Correlações mais fortes
    show_strongest_correlations(df_daily)
    
    st.markdown("---")
    
    # Análises específicas
    show_specific_correlations(df_daily)
    
    st.markdown("---")
    
    # Matriz de correlação
    show_correlation_matrix(df_daily)
    
    st.markdown("---")
    
    # Guia de interpretação
    show_interpretation_guide(df_daily)
