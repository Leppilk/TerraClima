"""
Página 3: Estatísticas e Recordes
"""

import streamlit as st
import pandas as pd
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


def show_general_statistics(df_daily):
    """Exibe estatísticas gerais."""
    st.markdown("## 📊 Estatísticas Descritivas")
    
    # Temperatura
    st.markdown("### 🌡️ Temperatura")
    temp_analyzer = TemperatureAnalyzer(df_daily)
    temp_stats = temp_analyzer.calculate_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Temperatura Máxima**")
        if 'temp_max' in temp_stats:
            st.metric("Absoluta", f"{temp_stats['temp_max']['absoluta']:.1f}°C")
            st.metric("Média", f"{temp_stats['temp_max']['media']:.1f}°C")
            st.metric("Desvio Padrão", f"{temp_stats['temp_max']['desvio_padrao']:.1f}°C")
    
    with col2:
        st.markdown("**Temperatura Média**")
        if 'temp_media' in temp_stats:
            st.metric("Geral", f"{temp_stats['temp_media']['geral']:.1f}°C")
            st.metric("Mediana", f"{temp_stats['temp_media']['mediana']:.1f}°C")
            st.metric("Desvio Padrão", f"{temp_stats['temp_media']['desvio_padrao']:.1f}°C")
    
    with col3:
        st.markdown("**Temperatura Mínima**")
        if 'temp_min' in temp_stats:
            st.metric("Absoluta", f"{temp_stats['temp_min']['absoluta']:.1f}°C")
            st.metric("Média", f"{temp_stats['temp_min']['media']:.1f}°C")
            st.metric("Desvio Padrão", f"{temp_stats['temp_min']['desvio_padrao']:.1f}°C")
    
    st.markdown("---")
    
    # Umidade
    st.markdown("### 💧 Umidade")
    humidity_analyzer = HumidityAnalyzer(df_daily)
    humidity_stats = humidity_analyzer.calculate_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Umidade Máxima**")
        if 'umidade_max' in humidity_stats:
            st.metric("Absoluta", f"{humidity_stats['umidade_max']['absoluta']:.0f}%")
            st.metric("Média", f"{humidity_stats['umidade_max']['media']:.1f}%")
    
    with col2:
        st.markdown("**Umidade Média**")
        if 'umidade_media' in humidity_stats:
            st.metric("Geral", f"{humidity_stats['umidade_media']['geral']:.1f}%")
            st.metric("Mediana", f"{humidity_stats['umidade_media']['mediana']:.1f}%")
    
    with col3:
        st.markdown("**Umidade Mínima**")
        if 'umidade_min' in humidity_stats:
            st.metric("Absoluta", f"{humidity_stats['umidade_min']['absoluta']:.0f}%")
            st.metric("Média", f"{humidity_stats['umidade_min']['media']:.1f}%")
    
    st.markdown("---")
    
    # Chuva
    st.markdown("### 🌧️ Precipitação")
    rain_analyzer = RainfallAnalyzer(df_daily)
    rain_stats = rain_analyzer.calculate_statistics()
    
    if rain_stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total no Período", f"{rain_stats.get('total', 0):.1f} mm")
        
        with col2:
            st.metric("Média Diária", f"{rain_stats.get('media_diaria', 0):.2f} mm")
        
        with col3:
            st.metric("Máxima em 24h", f"{rain_stats.get('maxima_diaria', 0):.1f} mm")
        
        with col4:
            st.metric("Dias com Chuva", f"{rain_stats.get('dias_com_chuva', 0)}")


def show_records(df_daily):
    """Exibe recordes históricos."""
    st.markdown("## 🏆 Recordes do Período")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 Recordes de Calor")
        
        if 'temperatura_max' in df_daily.columns:
            max_temp_idx = df_daily['temperatura_max'].idxmax()
            max_temp_row = df_daily.loc[max_temp_idx]
            
            st.markdown(f"""
            **Dia Mais Quente:**
            - 📅 Data: {max_temp_row['data'].strftime('%d/%m/%Y')}
            - 🌡️ Temperatura Máxima: {max_temp_row['temperatura_max']:.1f}°C
            """)
        
        st.markdown("---")
        
        st.markdown("### ❄️ Recordes de Frio")
        
        if 'temperatura_min' in df_daily.columns:
            min_temp_idx = df_daily['temperatura_min'].idxmin()
            min_temp_row = df_daily.loc[min_temp_idx]
            
            st.markdown(f"""
            **Dia Mais Frio:**
            - 📅 Data: {min_temp_row['data'].strftime('%d/%m/%Y')}
            - 🌡️ Temperatura Mínima: {min_temp_row['temperatura_min']:.1f}°C
            """)
    
    with col2:
        st.markdown("### 🌧️ Recordes de Chuva")
        
        # Encontrar coluna de chuva
        chuva_col = None
        for col in ['chuva_total', 'chuva_dia', 'precipitacao']:
            if col in df_daily.columns:
                chuva_col = col
                break
        
        if chuva_col:
            max_rain_idx = df_daily[chuva_col].idxmax()
            max_rain_row = df_daily.loc[max_rain_idx]
            
            st.markdown(f"""
            **Dia Mais Chuvoso:**
            - 📅 Data: {max_rain_row['data'].strftime('%d/%m/%Y')}
            - 🌧️ Precipitação: {max_rain_row[chuva_col]:.1f} mm
            """)
        
        st.markdown("---")
        
        st.markdown("### 💨 Recordes de Vento")
        
        if 'velocidade_vento_max' in df_daily.columns:
            max_wind_idx = df_daily['velocidade_vento_max'].idxmax()
            max_wind_row = df_daily.loc[max_wind_idx]
            
            st.markdown(f"""
            **Rajada Mais Forte:**
            - 📅 Data: {max_wind_row['data'].strftime('%d/%m/%Y')}
            - 💨 Velocidade: {max_wind_row['velocidade_vento_max']:.1f} km/h
            """)


def show_agricultural_indices(df_daily):
    """Exibe índices agrícolas."""
    st.markdown("## 🌾 Índices Agrícolas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💧 Análise de Irrigação")
        
        rain_analyzer = RainfallAnalyzer(df_daily)
        irrigation = rain_analyzer.calculate_irrigation_need()
        
        if irrigation:
            st.markdown(f"""
            **Status Atual:**
            - Necessita irrigação: {'✅ Sim' if irrigation.get('necessita_irrigacao') else '❌ Não'}
            - Nível de necessidade: {irrigation.get('nivel_necessidade', 'N/A')}
            - Dias sem chuva: {irrigation.get('dias_sem_chuva', 0)}
            
            **Recomendação:**
            {irrigation.get('recomendacao', 'N/A')}
            """)
        
        st.markdown("---")
        
        st.markdown("### 💧 Impacto da Umidade")
        
        humidity_analyzer = HumidityAnalyzer(df_daily)
        humidity_impact = humidity_analyzer.calculate_agricultural_impact()
        
        if humidity_impact:
            st.markdown(f"""
            **Análise de Umidade:**
            - Dias com umidade ideal: {humidity_impact.get('dias_umidade_ideal', 0)}
            - Dias com umidade baixa: {humidity_impact.get('dias_umidade_baixa', 0)}
            - Dias com umidade excessiva: {humidity_impact.get('dias_umidade_excessiva', 0)}
            - Porcentagem ideal: {humidity_impact.get('porcentagem_ideal', 0):.1f}%
            - Status: **{humidity_impact.get('status', 'N/A')}**
            """)
    
    with col2:
        st.markdown("### 🚜 Adequação para Aplicação")
        
        wind_analyzer = WindAnalyzer(df_daily)
        application = wind_analyzer.calculate_application_suitability()
        
        if application:
            st.markdown(f"""
            **Análise de Vento:**
            - Dias ideais para aplicação: {application.get('dias_ideais_aplicacao', 0)}
            - Dias muito calmos: {application.get('dias_muito_calmo', 0)}
            - Dias muito ventosos: {application.get('dias_muito_ventoso', 0)}
            - Porcentagem ideal: {application.get('porcentagem_ideal', 0):.1f}%
            - Status: **{application.get('status', 'N/A')}**
            """)
        
        st.markdown("---")
        
        st.markdown("### ☀️ Potencial Solar")
        
        solar_analyzer = SolarAnalyzer(df_daily)
        solar_energy = solar_analyzer.calculate_solar_energy_potential()
        
        if solar_energy:
            st.markdown(f"""
            **Análise de Radiação Solar:**
            - Radiação média diária: {solar_energy.get('radiacao_media_diaria', 0):.0f} W/m²
            - Energia estimada (período): {solar_energy.get('energia_estimada_kwh', 0):.1f} kWh
            - Dias com boa insolação: {solar_energy.get('dias_boa_insolacao', 0)}
            - Porcentagem de bom sol: {solar_energy.get('porcentagem_dias_bom_sol', 0):.1f}%
            """)


def show_top_days(df_daily):
    """Exibe ranking dos dias mais extremos."""
    st.markdown("## 📋 Top 10 - Dias Extremos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 Dias Mais Quentes")
        
        if 'temperatura_max' in df_daily.columns:
            top_hot = df_daily.nlargest(10, 'temperatura_max')[['data', 'temperatura_max']].copy()
            top_hot['data'] = top_hot['data'].dt.strftime('%d/%m/%Y')
            top_hot.columns = ['Data', 'Temp. Máxima (°C)']
            top_hot.reset_index(drop=True, inplace=True)
            top_hot.index = top_hot.index + 1
            
            st.dataframe(top_hot, use_container_width=True)
    
    with col2:
        st.markdown("### ❄️ Dias Mais Frios")
        
        if 'temperatura_min' in df_daily.columns:
            top_cold = df_daily.nsmallest(10, 'temperatura_min')[['data', 'temperatura_min']].copy()
            top_cold['data'] = top_cold['data'].dt.strftime('%d/%m/%Y')
            top_cold.columns = ['Data', 'Temp. Mínima (°C)']
            top_cold.reset_index(drop=True, inplace=True)
            top_cold.index = top_cold.index + 1
            
            st.dataframe(top_cold, use_container_width=True)
    
    # Dias mais chuvosos
    chuva_col = None
    for col in ['chuva_total', 'chuva_dia', 'precipitacao']:
        if col in df_daily.columns:
            chuva_col = col
            break
    
    if chuva_col:
        st.markdown("### 🌧️ Dias Mais Chuvosos")
        
        top_rain = df_daily.nlargest(10, chuva_col)[['data', chuva_col]].copy()
        top_rain['data'] = top_rain['data'].dt.strftime('%d/%m/%Y')
        top_rain.columns = ['Data', 'Precipitação (mm)']
        top_rain.reset_index(drop=True, inplace=True)
        top_rain.index = top_rain.index + 1
        
        st.dataframe(top_rain, use_container_width=True)


def show(df_daily, df_monthly):
    """Função principal da página de estatísticas."""
    
    # Cabeçalho
    st.markdown('<p class="main-header">📊 Estatísticas e Recordes</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Análise detalhada dos dados meteorológicos</p>', unsafe_allow_html=True)
    
    # Estatísticas gerais
    show_general_statistics(df_daily)
    
    st.markdown("---")
    
    # Recordes
    show_records(df_daily)
    
    st.markdown("---")
    
    # Índices agrícolas
    show_agricultural_indices(df_daily)
    
    st.markdown("---")
    
    # Top 10
    show_top_days(df_daily)
