"""
Script para processar dados históricos de chuva do Sr. Luiz
Converte arquivo Excel para CSV e padroniza formato
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent.parent
EXCEL_PATH = BASE_DIR / "Dados" / "Sr Luiz" / "Pluviometro Sr. Luiz.xlsx"
OUTPUT_PATH = BASE_DIR / "Dados" / "Sr Luiz" / "dados_pluviometro_convertido.csv"

def analisar_estrutura_excel():
    """Analisa a estrutura do arquivo Excel."""
    print("=" * 70)
    print("📊 ANÁLISE DO ARQUIVO EXCEL")
    print("=" * 70)
    
    # Ler Excel
    xl = pd.ExcelFile(EXCEL_PATH)
    
    print(f"\n📑 Planilhas encontradas: {len(xl.sheet_names)}")
    for sheet in xl.sheet_names:
        print(f"   • {sheet}")
    
    print("\n" + "=" * 70)
    print("📋 ANALISANDO CONTEÚDO DE CADA PLANILHA")
    print("=" * 70)
    
    for sheet_name in xl.sheet_names:
        print(f"\n{'─' * 70}")
        print(f"📄 Planilha: {sheet_name}")
        print(f"{'─' * 70}")
        
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
        
        print(f"\n📏 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
        print(f"\n📊 Colunas encontradas:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n🔍 Primeiras 5 linhas:")
        print(df.head())
        
        print(f"\n📈 Informações dos dados:")
        print(df.info())
        
        print(f"\n🔢 Estatísticas descritivas:")
        print(df.describe())
        
        # Verificar valores nulos
        print(f"\n⚠️ Valores nulos por coluna:")
        nulls = df.isnull().sum()
        for col, count in nulls.items():
            if count > 0:
                print(f"   • {col}: {count} ({count/len(df)*100:.1f}%)")


def converter_para_csv():
    """Converte dados para formato CSV padronizado."""
    print("\n" + "=" * 70)
    print("🔄 CONVERSÃO PARA CSV")
    print("=" * 70)
    
    # Ler primeira planilha (assumindo que contém os dados)
    xl = pd.ExcelFile(EXCEL_PATH)
    sheet_name = xl.sheet_names[0]
    
    print(f"\n📖 Lendo planilha: {sheet_name}")
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
    
    print(f"\n✅ Dados carregados: {len(df)} registros")
    
    # Salvar CSV
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    
    print(f"\n💾 Arquivo CSV salvo em:")
    print(f"   {OUTPUT_PATH}")
    
    print(f"\n📊 Tamanho do arquivo: {OUTPUT_PATH.stat().st_size / 1024:.2f} KB")
    
    return df


if __name__ == "__main__":
    print("\n🌧️ PROCESSAMENTO DE DADOS HISTÓRICOS - SR. LUIZ")
    print("=" * 70)
    print(f"📂 Arquivo origem: {EXCEL_PATH.name}")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    # Análise completa
    analisar_estrutura_excel()
    
    # Conversão
    df_convertido = converter_para_csv()
    
    print("\n" + "=" * 70)
    print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO")
    print("=" * 70)
    print(f"\n📊 Resumo:")
    print(f"   • Registros: {len(df_convertido)}")
    print(f"   • Colunas: {len(df_convertido.columns)}")
    print(f"   • Arquivo CSV: {OUTPUT_PATH.name}")
    print("\n")
