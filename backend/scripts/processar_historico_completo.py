"""
Script para processar e estruturar dados históricos de chuva do Sr. Luiz
Converte tabela mensal em formato longo (long format) para análise
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent.parent
EXCEL_PATH = BASE_DIR / "Dados" / "Sr Luiz" / "Pluviometro Sr. Luiz.xlsx"
OUTPUT_MENSAL_PATH = BASE_DIR / "Dados" / "Sr Luiz" / "precipitacao_mensal_1995_2025.csv"
OUTPUT_ANUAL_PATH = BASE_DIR / "Dados" / "Sr Luiz" / "precipitacao_anual_1995_2025.csv"

def processar_dados_historicos():
    """Processa e estrutura os dados históricos."""
    print("\n" + "=" * 70)
    print("🔄 PROCESSANDO DADOS HISTÓRICOS")
    print("=" * 70)
    
    # Ler Excel pulando as linhas de cabeçalho
    print("\n📖 Lendo arquivo Excel...")
    df_raw = pd.read_excel(EXCEL_PATH, sheet_name='Planilha1', header=1)
    
    # Remover linhas vazias e colunas desnecessárias
    print("🧹 Limpando dados...")
    
    # A primeira coluna é o ano
    df_raw.columns = ['Ano', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez', 'Total/ano', 'Média/ano']
    
    # Filtrar apenas linhas com anos válidos
    df_clean = df_raw[df_raw['Ano'].notna()].copy()
    df_clean = df_clean[pd.to_numeric(df_clean['Ano'], errors='coerce').notna()].copy()
    df_clean['Ano'] = df_clean['Ano'].astype(int)
    
    # Filtrar anos válidos (1995-2025)
    df_clean = df_clean[(df_clean['Ano'] >= 1995) & (df_clean['Ano'] <= 2025)]
    
    print(f"✅ {len(df_clean)} anos de dados encontrados ({df_clean['Ano'].min()} - {df_clean['Ano'].max()})")
    
    # === FORMATO 1: DADOS MENSAIS (LONG FORMAT) ===
    print("\n📊 Criando dataset mensal...")
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    dados_mensais = []
    
    for _, row in df_clean.iterrows():
        ano = int(row['Ano'])
        for mes_num, mes_nome in enumerate(meses, start=1):
            valor = row[mes_nome]
            
            # Converter para float, tratar vazios como 0
            try:
                precipitacao = float(valor) if pd.notna(valor) else 0.0
            except (ValueError, TypeError):
                precipitacao = 0.0
            
            # Criar data (primeiro dia de cada mês)
            data = pd.Timestamp(year=ano, month=mes_num, day=1)
            
            dados_mensais.append({
                'data': data,
                'ano': ano,
                'mes': mes_num,
                'mes_nome': mes_nome,
                'precipitacao_mm': precipitacao
            })
    
    df_mensal = pd.DataFrame(dados_mensais)
    df_mensal = df_mensal.sort_values('data').reset_index(drop=True)
    
    print(f"✅ Dataset mensal criado: {len(df_mensal)} registros")
    print(f"   Período: {df_mensal['data'].min().strftime('%m/%Y')} até {df_mensal['data'].max().strftime('%m/%Y')}")
    print(f"   Total acumulado: {df_mensal['precipitacao_mm'].sum():.1f} mm")
    
    # === FORMATO 2: DADOS ANUAIS ===
    print("\n📊 Criando dataset anual...")
    
    # Recalcular totais anuais a partir dos dados mensais
    df_anual = df_mensal.groupby('ano').agg({
        'precipitacao_mm': ['sum', 'mean', 'std', 'min', 'max']
    }).reset_index()
    
    df_anual.columns = ['ano', 'total_anual_mm', 'media_mensal_mm', 
                        'desvio_padrao_mm', 'mes_minimo_mm', 'mes_maximo_mm']
    
    # Contar meses com dados
    meses_com_dados = df_mensal[df_mensal['precipitacao_mm'] > 0].groupby('ano').size()
    df_anual['meses_com_chuva'] = df_anual['ano'].map(meses_com_dados).fillna(0).astype(int)
    
    print(f"✅ Dataset anual criado: {len(df_anual)} anos")
    print(f"   Média anual: {df_anual['total_anual_mm'].mean():.1f} mm")
    print(f"   Ano mais chuvoso: {df_anual.loc[df_anual['total_anual_mm'].idxmax(), 'ano']:.0f} ({df_anual['total_anual_mm'].max():.1f} mm)")
    print(f"   Ano mais seco: {df_anual.loc[df_anual['total_anual_mm'].idxmin(), 'ano']:.0f} ({df_anual['total_anual_mm'].min():.1f} mm)")
    
    # === SALVAR ARQUIVOS ===
    print("\n💾 Salvando arquivos...")
    
    df_mensal.to_csv(OUTPUT_MENSAL_PATH, index=False, encoding='utf-8')
    print(f"   ✅ Mensal: {OUTPUT_MENSAL_PATH.name}")
    
    df_anual.to_csv(OUTPUT_ANUAL_PATH, index=False, encoding='utf-8')
    print(f"   ✅ Anual: {OUTPUT_ANUAL_PATH.name}")
    
    return df_mensal, df_anual


def gerar_estatisticas(df_mensal, df_anual):
    """Gera estatísticas descritivas dos dados."""
    print("\n" + "=" * 70)
    print("📈 ESTATÍSTICAS DESCRITIVAS")
    print("=" * 70)
    
    # Estatísticas gerais
    print("\n📊 RESUMO GERAL (1995-2025)")
    print(f"   • Total de meses: {len(df_mensal)}")
    print(f"   • Total de anos: {len(df_anual)}")
    print(f"   • Precipitação total: {df_mensal['precipitacao_mm'].sum():.1f} mm")
    print(f"   • Média mensal: {df_mensal['precipitacao_mm'].mean():.1f} mm")
    print(f"   • Média anual: {df_anual['total_anual_mm'].mean():.1f} mm")
    
    # Estatísticas mensais
    print("\n📅 MÉDIAS POR MÊS (mm)")
    media_por_mes = df_mensal.groupby('mes_nome')['precipitacao_mm'].mean()
    for mes in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
        if mes in media_por_mes.index:
            print(f"   • {mes}: {media_por_mes[mes]:>6.1f} mm")
    
    # Top 5 meses mais chuvosos
    print("\n🌧️ TOP 5 MESES MAIS CHUVOSOS")
    top_meses = df_mensal.nlargest(5, 'precipitacao_mm')[['data', 'precipitacao_mm']]
    for idx, row in top_meses.iterrows():
        print(f"   • {row['data'].strftime('%m/%Y')}: {row['precipitacao_mm']:.1f} mm")
    
    # Top 5 anos mais chuvosos
    print("\n🌧️ TOP 5 ANOS MAIS CHUVOSOS")
    top_anos = df_anual.nlargest(5, 'total_anual_mm')[['ano', 'total_anual_mm']]
    for idx, row in top_anos.iterrows():
        print(f"   • {row['ano']:.0f}: {row['total_anual_mm']:.1f} mm")
    
    # Década mais chuvosa
    print("\n📊 PRECIPITAÇÃO POR DÉCADA")
    df_mensal['decada'] = (df_mensal['ano'] // 10) * 10
    por_decada = df_mensal.groupby('decada')['precipitacao_mm'].sum()
    for decada, total in por_decada.items():
        anos_na_decada = df_mensal[df_mensal['decada'] == decada]['ano'].nunique()
        media_anual = total / anos_na_decada
        print(f"   • {decada}s: {total:.1f} mm total ({media_anual:.1f} mm/ano)")


if __name__ == "__main__":
    print("\n🌧️ PROCESSAMENTO DE DADOS HISTÓRICOS - SR. LUIZ")
    print("📍 Ribeirão Claro - PR")
    print("📅 Período: 1995 - 2025")
    print("=" * 70)
    print(f"🕐 Processamento iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Processar dados
    df_mensal, df_anual = processar_dados_historicos()
    
    # Gerar estatísticas
    gerar_estatisticas(df_mensal, df_anual)
    
    print("\n" + "=" * 70)
    print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO")
    print("=" * 70)
    print("\n📁 Arquivos gerados:")
    print(f"   1. {OUTPUT_MENSAL_PATH.name} - Dados mensais (long format)")
    print(f"   2. {OUTPUT_ANUAL_PATH.name} - Dados anuais agregados")
    print("\n✨ Os dados estão prontos para análise!")
    print("\n")
