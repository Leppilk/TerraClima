"""
Script para integrar dados históricos (Sr. Luiz) com dados da estação (Weathercloud)
Cria dataset unificado de precipitação mensal de 1995 até hoje
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent.parent
DADOS_HISTORICOS = BASE_DIR / "Dados" / "Sr Luiz" / "precipitacao_mensal_1995_2025.csv"
DADOS_DIR = BASE_DIR / "Dados"
OUTPUT_INTEGRADO = BASE_DIR / "Dados" / "precipitacao_integrada_1995_2025.csv"

def carregar_dados_historicos():
    """Carrega dados históricos do Sr. Luiz."""
    print("\n📖 Carregando dados históricos (Sr. Luiz)...")
    df = pd.read_csv(DADOS_HISTORICOS, parse_dates=['data'])
    print(f"   ✅ {len(df)} registros mensais (1995-2025)")
    print(f"   📅 Período: {df['data'].min().strftime('%m/%Y')} até {df['data'].max().strftime('%m/%Y')}")
    return df


def carregar_dados_estacao():
    """Carrega e agrega dados da estação Weathercloud."""
    print("\n📖 Carregando dados da estação Weathercloud...")
    
    # Ler arquivos CSV da estação diretamente
    import glob
    arquivos_csv = sorted(glob.glob(str(DADOS_DIR / "Weathercloud Galinhada 2025-*.csv")))
    
    if not arquivos_csv:
        print("   ⚠️ Nenhum arquivo CSV da estação encontrado")
        return pd.DataFrame()
    
    print(f"   📂 Encontrados {len(arquivos_csv)} arquivos CSV")
    
    # Carregar todos os arquivos
    dfs = []
    for arquivo in arquivos_csv:
        try:
            # Tentar diferentes encodings
            for encoding in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
                try:
                    df_temp = pd.read_csv(arquivo, sep=';', decimal=',', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"   ⚠️ Erro de encoding em {Path(arquivo).name}")
                continue
            # Padronizar nomes de colunas
            df_temp.columns = df_temp.columns.str.strip().str.lower()
            
            # Converter data
            if 'time' in df_temp.columns:
                df_temp['data'] = pd.to_datetime(df_temp['time'], format='%d/%m/%Y %H:%M')
            elif 'data' in df_temp.columns:
                df_temp['data'] = pd.to_datetime(df_temp['data'])
            
            # Encontrar coluna de chuva
            coluna_chuva = None
            for col in df_temp.columns:
                if 'rain' in col or 'chuva' in col or 'precip' in col:
                    coluna_chuva = col
                    break
            
            if coluna_chuva and 'data' in df_temp.columns:
                df_temp = df_temp[['data', coluna_chuva]].copy()
                df_temp.columns = ['data', 'chuva']
                df_temp['chuva'] = pd.to_numeric(df_temp['chuva'], errors='coerce').fillna(0)
                dfs.append(df_temp)
        except Exception as e:
            print(f"   ⚠️ Erro ao ler {Path(arquivo).name}: {e}")
            continue
    
    if not dfs:
        print("   ⚠️ Nenhum dado válido encontrado")
        return pd.DataFrame()
    
    # Concatenar todos os dados
    df_raw = pd.concat(dfs, ignore_index=True)
    df_raw = df_raw.sort_values('data').drop_duplicates(subset=['data'])
    
    print(f"   ✅ {len(df_raw)} registros carregados")
    print(f"   📅 Período: {df_raw['data'].min().strftime('%d/%m/%Y')} até {df_raw['data'].max().strftime('%d/%m/%Y')}")
    
    # Agregar por dia primeiro
    df_raw['data_dia'] = df_raw['data'].dt.date
    df_daily = df_raw.groupby('data_dia')['chuva'].sum().reset_index()
    df_daily.columns = ['data', 'chuva_acumulada']
    df_daily['data'] = pd.to_datetime(df_daily['data'])
    
    print(f"   ✅ {len(df_daily)} dias agregados")
    
    # Agregar por mês
    print("\n📊 Agregando dados por mês...")
    df_daily['ano'] = df_daily['data'].dt.year
    df_daily['mes'] = df_daily['data'].dt.month
    
    # Criar primeiro dia do mês para compatibilidade
    df_daily['mes_data'] = pd.to_datetime(df_daily[['ano', 'mes']].assign(dia=1))
    
    # Agregar precipitação por mês
    df_mensal = df_daily.groupby(['mes_data', 'ano', 'mes']).agg({
        'chuva_acumulada': 'sum'
    }).reset_index()
    
    df_mensal.columns = ['data', 'ano', 'mes', 'precipitacao_mm']
    
    # Adicionar nome do mês
    meses_nomes = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                   7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    df_mensal['mes_nome'] = df_mensal['mes'].map(meses_nomes)
    
    print(f"   ✅ {len(df_mensal)} registros mensais agregados")
    print(f"   📅 Período: {df_mensal['data'].min().strftime('%m/%Y')} até {df_mensal['data'].max().strftime('%m/%Y')}")
    print(f"   🌧️ Total: {df_mensal['precipitacao_mm'].sum():.1f} mm")
    
    return df_mensal


def integrar_dados(df_historico, df_estacao):
    """Integra dados históricos com dados da estação."""
    print("\n🔗 Integrando dados...")
    
    # Se não há dados da estação, usar apenas histórico
    if df_estacao.empty:
        print("   ℹ️ Usando apenas dados históricos (estação sem dados)")
        df_historico = df_historico.copy()
        df_historico['fonte'] = 'Sr. Luiz (Pluviômetro)'
        return df_historico
    
    # Adicionar coluna de fonte
    df_historico = df_historico.copy()
    df_historico['fonte'] = 'Sr. Luiz (Pluviômetro)'
    
    df_estacao = df_estacao.copy()
    df_estacao['fonte'] = 'Estação Weathercloud'
    
    # Garantir mesma estrutura
    colunas = ['data', 'ano', 'mes', 'mes_nome', 'precipitacao_mm', 'fonte']
    df_historico = df_historico[colunas]
    df_estacao = df_estacao[colunas]
    
    # Identificar overlap (meses que existem em ambos)
    datas_historico = set(df_historico['data'])
    datas_estacao = set(df_estacao['data'])
    datas_overlap = datas_historico.intersection(datas_estacao)
    
    print(f"   📊 Meses únicos Sr. Luiz: {len(datas_historico)}")
    print(f"   📊 Meses únicos Estação: {len(datas_estacao)}")
    print(f"   🔄 Overlap: {len(datas_overlap)} meses")
    
    # Estratégia: Priorizar dados da estação quando disponíveis
    # Remover do histórico os meses que já existem na estação
    df_historico_filtrado = df_historico[~df_historico['data'].isin(datas_overlap)]
    
    print(f"\n🎯 Estratégia de integração:")
    print(f"   • Usar estação quando disponível (mais preciso)")
    print(f"   • Usar Sr. Luiz para períodos sem estação")
    print(f"   • {len(df_estacao)} meses da estação")
    print(f"   • {len(df_historico_filtrado)} meses do Sr. Luiz (sem overlap)")
    
    # Combinar datasets
    df_integrado = pd.concat([df_historico_filtrado, df_estacao], ignore_index=True)
    df_integrado = df_integrado.sort_values('data').reset_index(drop=True)
    
    print(f"\n✅ Dataset integrado criado: {len(df_integrado)} meses")
    print(f"   📅 Período completo: {df_integrado['data'].min().strftime('%m/%Y')} até {df_integrado['data'].max().strftime('%m/%Y')}")
    print(f"   🌧️ Total acumulado: {df_integrado['precipitacao_mm'].sum():.1f} mm")
    
    return df_integrado


def calcular_estatisticas_avancadas(df):
    """Calcula estatísticas avançadas para a página de chuva."""
    print("\n📈 Calculando estatísticas avançadas...")
    
    stats = {}
    
    # Geral
    stats['total_acumulado'] = df['precipitacao_mm'].sum()
    stats['media_mensal'] = df['precipitacao_mm'].mean()
    stats['anos_cobertura'] = df['ano'].nunique()
    stats['meses_total'] = len(df)
    
    # Mês mais chuvoso de todos os tempos
    idx_max = df['precipitacao_mm'].idxmax()
    stats['mes_mais_chuvoso'] = {
        'data': df.loc[idx_max, 'data'],
        'valor': df.loc[idx_max, 'precipitacao_mm'],
        'ano': df.loc[idx_max, 'ano'],
        'mes': df.loc[idx_max, 'mes_nome']
    }
    
    # Ano mais chuvoso
    por_ano = df.groupby('ano')['precipitacao_mm'].sum()
    ano_max = por_ano.idxmax()
    stats['ano_mais_chuvoso'] = {
        'ano': int(ano_max),
        'total': por_ano[ano_max]
    }
    
    # Maior período de seca (meses consecutivos com <10mm)
    df['seca'] = (df['precipitacao_mm'] < 10).astype(int)
    df['grupo_seca'] = (df['seca'] != df['seca'].shift()).cumsum()
    periodos_seca = df[df['seca'] == 1].groupby('grupo_seca').agg({
        'data': ['first', 'last', 'count'],
        'precipitacao_mm': 'sum'
    })
    
    if len(periodos_seca) > 0:
        idx_seca_max = periodos_seca[('data', 'count')].idxmax()
        stats['maior_seca'] = {
            'inicio': periodos_seca.loc[idx_seca_max, ('data', 'first')],
            'fim': periodos_seca.loc[idx_seca_max, ('data', 'last')],
            'duracao_meses': int(periodos_seca.loc[idx_seca_max, ('data', 'count')]),
            'total_chuva': periodos_seca.loc[idx_seca_max, ('precipitacao_mm', 'sum')]
        }
    else:
        stats['maior_seca'] = None
    
    # Média por década
    df['decada'] = (df['ano'] // 10) * 10
    stats['por_decada'] = df.groupby('decada')['precipitacao_mm'].agg(['sum', 'mean', 'count']).to_dict('index')
    
    # Sazonalidade (média por mês do ano)
    stats['sazonalidade'] = df.groupby('mes')['precipitacao_mm'].mean().to_dict()
    
    # Tendência (últimos 10 anos vs 10 anteriores)
    anos_recentes = df[df['ano'] >= 2015]['precipitacao_mm'].mean()
    anos_anteriores = df[(df['ano'] >= 2005) & (df['ano'] < 2015)]['precipitacao_mm'].mean()
    stats['tendencia_10anos'] = {
        'recente': anos_recentes,
        'anterior': anos_anteriores,
        'variacao_pct': ((anos_recentes - anos_anteriores) / anos_anteriores * 100) if anos_anteriores > 0 else 0
    }
    
    print(f"   ✅ Estatísticas calculadas")
    
    return stats


def salvar_dataset(df, stats):
    """Salva dataset integrado e estatísticas."""
    print(f"\n💾 Salvando arquivos...")
    
    # Salvar CSV principal
    df.to_csv(OUTPUT_INTEGRADO, index=False, encoding='utf-8')
    print(f"   ✅ Dataset: {OUTPUT_INTEGRADO.name}")
    
    # Salvar estatísticas em JSON
    import json
    stats_path = OUTPUT_INTEGRADO.parent / "estatisticas_chuva.json"
    
    # Converter datas e números para formatos serializáveis
    stats_json = stats.copy()
    
    # Converter tipos numpy para tipos Python nativos
    def convert_to_native(obj):
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        return obj
    
    stats_json = convert_to_native(stats_json)
    
    # Converter datas específicas
    if stats_json['maior_seca']:
        if isinstance(stats_json['maior_seca']['inicio'], pd.Timestamp):
            stats_json['maior_seca']['inicio'] = stats_json['maior_seca']['inicio'].strftime('%Y-%m-%d')
        if isinstance(stats_json['maior_seca']['fim'], pd.Timestamp):
            stats_json['maior_seca']['fim'] = stats_json['maior_seca']['fim'].strftime('%Y-%m-%d')
    
    if isinstance(stats_json['mes_mais_chuvoso']['data'], pd.Timestamp):
        stats_json['mes_mais_chuvoso']['data'] = stats_json['mes_mais_chuvoso']['data'].strftime('%Y-%m-%d')
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats_json, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Estatísticas: {stats_path.name}")
    
    return stats_path


if __name__ == "__main__":
    print("\n🌧️ INTEGRAÇÃO DE DADOS HISTÓRICOS + ESTAÇÃO")
    print("=" * 70)
    print(f"🕐 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    # Carregar dados
    df_historico = carregar_dados_historicos()
    df_estacao = carregar_dados_estacao()
    
    # Integrar
    df_integrado = integrar_dados(df_historico, df_estacao)
    
    # Calcular estatísticas
    stats = calcular_estatisticas_avancadas(df_integrado)
    
    # Salvar
    stats_path = salvar_dataset(df_integrado, stats)
    
    print("\n" + "=" * 70)
    print("✅ INTEGRAÇÃO CONCLUÍDA COM SUCESSO")
    print("=" * 70)
    print(f"\n📊 Resumo Final:")
    print(f"   • Total de meses: {len(df_integrado)}")
    print(f"   • Anos cobertos: {stats['anos_cobertura']}")
    print(f"   • Precipitação total: {stats['total_acumulado']:.1f} mm")
    print(f"   • Média mensal: {stats['media_mensal']:.1f} mm")
    print(f"\n🏆 Recordes:")
    print(f"   • Mês mais chuvoso: {stats['mes_mais_chuvoso']['mes']}/{stats['mes_mais_chuvoso']['ano']} ({stats['mes_mais_chuvoso']['valor']:.1f} mm)")
    print(f"   • Ano mais chuvoso: {stats['ano_mais_chuvoso']['ano']} ({stats['ano_mais_chuvoso']['total']:.1f} mm)")
    if stats['maior_seca']:
        print(f"   • Maior seca: {stats['maior_seca']['duracao_meses']} meses consecutivos")
    print("\n")
