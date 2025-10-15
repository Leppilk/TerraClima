"""
Configurações globais do Sistema TerraClima
"""

import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'Dados'
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'graficos_chuva'

# Criar diretórios se não existirem
OUTPUT_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

# Configurações da Estação
STATION_CONFIG = {
    'nome': 'Estação Meteorológica Galinhada',
    'localizacao': 'Baggio, Ribeirão Claro - PR',
    'coordenadas_utm': {
        'este': 622279,
        'norte': 7431301,
        'fuso': '22S',
        'datum': 'SIRGAS 2000'
    },
    'frequencia_leitura': '10 minutos'
}

# Constantes para fácil acesso
STATION_NAME = STATION_CONFIG['nome']
STATION_LOCATION = STATION_CONFIG['localizacao']
STATION_UTM = f"UTM {STATION_CONFIG['coordenadas_utm']['este']} E / {STATION_CONFIG['coordenadas_utm']['norte']} N"
STATION_ZONE = STATION_CONFIG['coordenadas_utm']['fuso']

# Mapeamento de colunas do CSV
COLUMN_MAPPING = {
    'Data (America/Sao_Paulo)': 'data',
    'Temperatura (°C)': 'temperatura',
    'Temperatura interior (°C)': 'temp_interior',
    'Sensação térmica (°C)': 'sensacao_termica',
    'Ponto de orvalho (°C)': 'ponto_orvalho',
    'Índice de calor (°C)': 'indice_calor',
    'Humidade (%)': 'umidade',
    'Humidade interior (%)': 'umidade_interior',
    'Velocidade média do vento (m/s)': 'vento_velocidade',
    'Rajada máxima do vento (m/s)': 'vento_rajada',
    'Direção média do vento (°)': 'vento_direcao',
    'Pressão atmosférica (hPa)': 'pressao',
    'Chuva (mm)': 'chuva_acumulada',
    'Intensidade de chuva (mm/h)': 'chuva_intensidade',
    'Radiação solar (W/m²)': 'radiacao_solar',
    'Índice UV': 'indice_uv'
}

# Categorias de variáveis
VARIABLE_CATEGORIES = {
    'temperatura': ['temperatura', 'temp_interior', 'sensacao_termica', 
                    'ponto_orvalho', 'indice_calor'],
    'umidade': ['umidade', 'umidade_interior', 'ponto_orvalho'],
    'vento': ['vento_velocidade', 'vento_rajada', 'vento_direcao'],
    'precipitacao': ['chuva_acumulada', 'chuva_intensidade'],
    'solar': ['radiacao_solar', 'indice_uv'],
    'pressao': ['pressao']
}

# Configurações de CSV
CSV_CONFIG = {
    'separator': ';',
    'decimal': ',',
    'encodings': ['utf-16-le', 'utf-16', 'utf-8', 'latin-1', 'cp1252'],
    'date_format': '%d/%m/%Y %H:%M:%S'
}

# Classificações
RAIN_CLASSIFICATION = {
    'sem_chuva': (0, 0),
    'fraca': (0.1, 5),
    'moderada': (5, 15),
    'forte': (15, 25),
    'muito_forte': (25, float('inf'))
}

TEMP_ZONES = {
    'congelamento': (-float('inf'), 0),
    'frio': (0, 10),
    'fresco': (10, 18),
    'confortavel': (18, 26),
    'quente': (26, 32),
    'muito_quente': (32, 38),
    'extremo': (38, float('inf'))
}

# Cores para gráficos
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#95a5a6',
    'dark': '#34495e'
}

# Configurações de exportação
EXPORT_CONFIG = {
    'dpi': 300,
    'format': 'png',
    'quality': 95
}

# Meses em português
MESES_PT = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 
    5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 
    9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

MESES_PT_FULL = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# Configurações Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'TerraClima - Estação Meteorológica',
    'page_icon': '🌧️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}
