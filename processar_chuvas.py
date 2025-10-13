"""
Sistema de Processamento e Análise de Dados de Chuva
Autor: Estação Meteorológica Galinhada
Data: Outubro 2025

Este script processa dados de chuva da estação meteorológica,
gerando CSV diário e todos os gráficos de análise automaticamente.
"""

import pandas as pd
import os
import sys
from datetime import datetime
import glob

# Importa o gerador de relatórios
from relatorio_chuvas import (carregar_dados, calcular_estatisticas, 
                               criar_relatorio_completo, criar_analise_mensal_detalhada,
                               criar_graficos_individuais)


def processar_dados_chuva(pasta_dados='Dados'):
    """
    Processa todos os arquivos CSV da pasta de dados.
    Extrai apenas dados relevantes para análise de chuva.
    """
    print("🌧️ PROCESSADOR DE DADOS DE CHUVA")
    print("=" * 70)
    print()
    
    # Procura todos os arquivos CSV na pasta
    arquivos_csv = glob.glob(os.path.join(pasta_dados, '*.csv'))
    
    if not arquivos_csv:
        print(f"❌ Erro: Nenhum arquivo CSV encontrado em {pasta_dados}/")
        return None
    
    print(f"📂 Encontrados {len(arquivos_csv)} arquivos CSV:")
    for arquivo in arquivos_csv:
        print(f"   • {os.path.basename(arquivo)}")
    print()
    
    # Lista para armazenar dados processados
    dados_diarios = []
    
    # Processa cada arquivo
    for arquivo_csv in sorted(arquivos_csv):
        print(f"📊 Processando: {os.path.basename(arquivo_csv)}...", end=' ')
        
        try:
            # Tenta diferentes encodings
            df = None
            encodings = ['utf-16', 'utf-16-le', 'utf-16-be', 'latin1', 'iso-8859-1', 'cp1252', 'utf-8']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(arquivo_csv, sep=';', decimal=',', 
                                    encoding=encoding, on_bad_lines='skip', engine='python')
                    if df is not None and len(df) > 0:
                        break
                except:
                    continue
            
            if df is None or len(df) == 0:
                print("❌ Erro ao ler arquivo")
                continue
            
            # Limpa nomes das colunas
            df.columns = df.columns.str.strip()
            
            # Procura coluna de data
            col_data = None
            for col in df.columns:
                if 'data' in col.lower() or 'date' in col.lower():
                    col_data = col
                    break
            
            if not col_data:
                print("❌ Coluna de data não encontrada")
                continue
            
            # Procura coluna de chuva (exclui intensidade)
            col_chuva = None
            for col in df.columns:
                col_lower = col.lower()
                if 'chuva' in col_lower and 'mm' in col_lower and 'intensidade' not in col_lower:
                    col_chuva = col
                    break
            
            if not col_chuva:
                print("❌ Coluna de chuva não encontrada")
                continue
            
            # Procura coluna de intensidade (opcional)
            col_intensidade = None
            for col in df.columns:
                col_lower = col.lower()
                if 'intensidade' in col_lower and 'chuva' in col_lower:
                    col_intensidade = col
                    break
            
            # Converte coluna de data
            df[col_data] = pd.to_datetime(df[col_data], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            if df[col_data].isna().all():
                # Tenta outro formato
                df[col_data] = pd.to_datetime(df[col_data], format='%d/%m/%Y %H:%M', errors='coerce')
            
            # Remove linhas com data inválida
            df = df.dropna(subset=[col_data])
            
            if len(df) == 0:
                print("❌ Sem dados válidos após conversão de data")
                continue
            
            # Agrupa por dia
            df['data'] = df[col_data].dt.date
            
            # Para cada dia, pega o máximo da chuva acumulada
            agg_dict = {col_chuva: 'max'}
            if col_intensidade:
                agg_dict[col_intensidade] = 'max'
            
            dados_por_dia = df.groupby('data').agg(agg_dict).reset_index()
            
            # Renomeia colunas
            if col_intensidade:
                dados_por_dia.columns = ['data', 'chuva_total', 'intensidade_maxima']
            else:
                dados_por_dia.columns = ['data', 'chuva_total']
                dados_por_dia['intensidade_maxima'] = 0.0
            
            dados_diarios.append(dados_por_dia)
            print(f"✅ {len(dados_por_dia)} dias processados")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            continue
    
    if not dados_diarios:
        print("\n❌ Nenhum dado foi processado com sucesso")
        return None
    
    # Combina todos os dados
    df_final = pd.concat(dados_diarios, ignore_index=True)
    
    # Remove duplicatas (caso haja sobreposição de datas)
    df_final = df_final.drop_duplicates(subset=['data'], keep='last')
    
    # Ordena por data
    df_final = df_final.sort_values('data').reset_index(drop=True)
    
    # Converte data para datetime
    df_final['data'] = pd.to_datetime(df_final['data'])
    
    # Adiciona colunas auxiliares para os gráficos
    df_final['mes'] = df_final['data'].dt.month
    df_final['mes_nome'] = df_final['mes'].map({
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    })
    df_final['ano'] = df_final['data'].dt.year
    df_final['semana'] = df_final['data'].dt.isocalendar().week
    df_final['dia_mes'] = df_final['data'].dt.day
    
    # Classifica dias por intensidade de chuva
    def classificar_chuva(mm):
        if mm == 0:
            return 'Sem chuva'
        elif mm < 5:
            return 'Fraca (< 5mm)'
        elif mm < 15:
            return 'Moderada (5-15mm)'
        elif mm < 25:
            return 'Forte (15-25mm)'
        else:
            return 'Muito Forte (>25mm)'
    
    df_final['intensidade'] = df_final['chuva_total'].apply(classificar_chuva)
    
    print()
    print(f"✅ Processamento concluído!")
    print(f"   • Total de dias: {len(df_final)}")
    print(f"   • Período: {df_final['data'].min().strftime('%d/%m/%Y')} a {df_final['data'].max().strftime('%d/%m/%Y')}")
    print(f"   • Chuva total: {df_final['chuva_total'].sum():.1f} mm")
    print(f"   • Dias com chuva: {len(df_final[df_final['chuva_total'] > 0])}")
    print()
    
    return df_final


def salvar_csv_diario(df, pasta_saida='output'):
    """Salva CSV com dados diários de chuva."""
    
    # Cria pasta se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f'chuvas_diarias_{timestamp}.csv'
    caminho_completo = os.path.join(pasta_saida, nome_arquivo)
    
    # Cria dataframe simplificado apenas com as 3 colunas
    df_csv = pd.DataFrame({
        'data': df['data'].dt.strftime('%d/%m/%Y'),
        'chuva(mm)': df['chuva_total'],
        'intensidade_de_chuva(mm/h)': df['intensidade_maxima']
    })
    
    # Salva CSV
    df_csv.to_csv(caminho_completo, sep=';', decimal=',', index=False)
    
    print(f"💾 CSV salvo: {nome_arquivo}")
    print(f"   📂 Local: {caminho_completo}")
    print()
    
    return caminho_completo


def gerar_todos_graficos(df, pasta_saida='output'):
    """Gera todos os gráficos de análise de chuva."""
    
    print("📊 Gerando gráficos de análise...")
    print()
    
    # Cria pasta para gráficos
    pasta_graficos = os.path.join(pasta_saida, 'graficos_chuva')
    os.makedirs(pasta_graficos, exist_ok=True)
    
    # Calcula estatísticas
    print("   📈 Calculando estatísticas...")
    stats = calcular_estatisticas(df)
    
    # Gera relatório completo
    print("   📊 Gerando relatório completo...")
    criar_relatorio_completo(df, stats, pasta_graficos)
    
    # Gera análise mensal
    print("   📊 Gerando análise mensal detalhada...")
    criar_analise_mensal_detalhada(df, stats, pasta_graficos)
    
    # Gera gráficos individuais
    criar_graficos_individuais(df, stats, pasta_graficos)
    
    print()
    print(f"✅ Gráficos salvos em: {pasta_graficos}/")
    print()


def main():
    """Função principal - executa todo o pipeline."""
    
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     SISTEMA DE ANÁLISE DE CHUVAS - ESTAÇÃO METEOROLÓGICA      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    # 1. Processa dados
    df = processar_dados_chuva(pasta_dados='Dados')
    
    if df is None:
        return 1
    
    # 2. Salva CSV diário
    arquivo_csv = salvar_csv_diario(df, pasta_saida='output')
    
    # 3. Gera todos os gráficos
    gerar_todos_graficos(df, pasta_saida='output')
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                    ✅ PROCESSAMENTO CONCLUÍDO                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print("📂 Arquivos gerados:")
    print(f"   • CSV: output/chuvas_diarias_*.csv")
    print(f"   • Gráficos: output/graficos_chuva/")
    print()
    print("💡 Para reprocessar, execute novamente: python processar_chuvas.py")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
