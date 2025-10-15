"""
TerraClima - Sistema de Análise Meteorológica
Aplicação Web com Streamlit
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import config
from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.data.aggregator import DataAggregator


# Configuração da página
st.set_page_config(
    page_title="TerraClima - Análise Meteorológica",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para ocultar menu nativo e melhorar UI
st.markdown("""
<style>
    /* Ocultar menu de navegação nativo do Streamlit */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-danger {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Carrega e processa os dados meteorológicos (com cache)."""
    with st.spinner('🔄 Carregando dados da estação meteorológica...'):
        # Carregar dados brutos
        loader = DataLoader(config.DATA_DIR)
        df_raw = loader.load_all_csvs()
        
        # Processar para dados diários
        processor = DataProcessor()
        df_daily = processor.aggregate_to_daily(df_raw)
        
        # Criar agregações
        aggregator = DataAggregator()
        df_monthly = aggregator.aggregate_monthly(df_daily)
        
        return df_raw, df_daily, df_monthly


@st.cache_data
def get_data_period(_df):
    """Retorna informações sobre o período dos dados."""
    if 'data' not in _df.columns:
        return None
    
    min_date = _df['data'].min()
    max_date = _df['data'].max()
    total_days = len(_df)
    
    return {
        'inicio': min_date,
        'fim': max_date,
        'total_dias': total_days
    }


def show_sidebar():
    """Exibe a barra lateral com navegação e informações."""
    with st.sidebar:
        st.markdown("# 🌦️ TerraClima")
        st.markdown("---")
        
        # Seleção de página
        st.markdown("### 📊 Navegação")
        page = st.radio(
            "Selecione a página:",
            ["🏠 Dashboard", "📈 Gráficos", "📊 Estatísticas", "🔗 Correlações"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Informações da estação
        st.markdown("### 🌍 Estação")
        st.markdown(f"""
        **{config.STATION_NAME}**
        
        📍 {config.STATION_LOCATION}
        
        📐 UTM: {config.STATION_UTM}
        
        📅 Zona: {config.STATION_ZONE}
        """)
        
        st.markdown("---")
        
        # Informações dos dados
        if 'df_daily' in st.session_state:
            period = get_data_period(st.session_state.df_daily)
            if period:
                st.markdown("### 📅 Período dos Dados")
                st.markdown(f"""
                **Início:** {period['inicio'].strftime('%d/%m/%Y')}
                
                **Fim:** {period['fim'].strftime('%d/%m/%Y')}
                
                **Total:** {period['total_dias']} dias
                """)
        
        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.markdown("""
        Sistema de análise meteorológica para agricultura de precisão.
        
        **Versão:** 1.0.0
        """)
    
    return page


def main():
    """Função principal da aplicação."""
    
    # Carregar dados na primeira execução
    if 'df_raw' not in st.session_state:
        try:
            df_raw, df_daily, df_monthly = load_data()
            st.session_state.df_raw = df_raw
            st.session_state.df_daily = df_daily
            st.session_state.df_monthly = df_monthly
            st.success("✅ Dados carregados com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
            st.stop()
    
    # Exibir sidebar e obter página selecionada
    page = show_sidebar()
    
    # Importar e exibir a página selecionada
    if page == "🏠 Dashboard":
        from pages import dashboard
        dashboard.show(
            st.session_state.df_raw,
            st.session_state.df_daily,
            st.session_state.df_monthly
        )
    
    elif page == "📈 Gráficos":
        from pages import graficos
        graficos.show(
            st.session_state.df_daily,
            st.session_state.df_monthly
        )
    
    elif page == "📊 Estatísticas":
        from pages import estatisticas
        estatisticas.show(
            st.session_state.df_daily,
            st.session_state.df_monthly
        )
    
    elif page == "🔗 Correlações":
        from pages import correlacoes
        correlacoes.show(st.session_state.df_daily)


if __name__ == "__main__":
    main()
