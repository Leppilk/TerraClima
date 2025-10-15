#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROCESSADOR COMPLETO DE DADOS METEOROLÓGICOS
==============================================
Processa todos os CSVs da estação Weathercloud e gera:
1. CSV simplificado de CHUVAS (mantém compatibilidade)
2. CSV COMPLETO com todas as variáveis meteorológicas

Autor: Sistema de Análise Meteorológica
Data: Outubro 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import glob
import warnings
warnings.filterwarnings('ignore')


def detectar_encoding(arquivo):
    """Detecta o encoding do arquivo CSV."""
    encodings = ['utf-16-le', 'utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(arquivo, 'r', encoding=enc) as f:
                f.read(1024)
            return enc
        except:
            continue
    return 'utf-8'


def processar_csv_completo(arquivo_csv):
    """
    Processa um arquivo CSV e extrai TODOS os dados meteorológicos.
    
    Retorna DataFrame com dados de 10 em 10 minutos.
    """
    print(f"\n📊 Processando: {Path(arquivo_csv).name}...", end=" ")
    
    try:
        # Detectar encoding
        encoding = detectar_encoding(arquivo_csv)
        
        # Ler CSV com separador correto e on_bad_lines='skip' para ignorar linhas problemáticas
        df = pd.read_csv(arquivo_csv, sep=';', decimal=',', encoding=encoding, 
                        on_bad_lines='skip', low_memory=False)
        
        # Converter data para datetime
        df['data'] = pd.to_datetime(df['Data (America/Sao_Paulo)'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Remover linhas com data inválida
        df = df.dropna(subset=['data'])
        
        if len(df) == 0:
            print("❌ Sem dados válidos após conversão de data")
            return None
        
        # Renomear e selecionar colunas importantes
        colunas_mapeamento = {
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
        
        # Criar DataFrame processado
        df_processado = pd.DataFrame()
        df_processado['data'] = df['data']
        
        # Adicionar todas as colunas disponíveis
        for col_original, col_nova in colunas_mapeamento.items():
            if col_original in df.columns:
                df_processado[col_nova] = pd.to_numeric(df[col_original], errors='coerce')
        
        print(f"✅ {len(df_processado)} registros processados")
        return df_processado
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None


def agregar_dados_diarios(df):
    """
    Agrega dados de 10 minutos para valores diários.
    
    Retorna:
    - DataFrame com dados diários agregados
    """
    if df is None or len(df) == 0:
        return None
    
    # Extrair apenas a data (sem hora)
    df['data_dia'] = df['data'].dt.date
    
    # Agrupar por dia e calcular estatísticas
    agregacao = {
        # Temperatura
        'temperatura': ['max', 'min', 'mean'],
        'temp_interior': 'mean',
        'sensacao_termica': 'mean',
        'ponto_orvalho': 'mean',
        'indice_calor': 'max',
        
        # Umidade
        'umidade': ['mean', 'max', 'min'],
        'umidade_interior': 'mean',
        
        # Vento
        'vento_velocidade': 'mean',
        'vento_rajada': 'max',
        'vento_direcao': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.mean(),  # Direção predominante
        
        # Pressão
        'pressao': 'mean',
        
        # Chuva (usar MAX da chuva acumulada diária)
        'chuva_acumulada': 'max',
        'chuva_intensidade': 'max',
        
        # Radiação
        'radiacao_solar': ['sum', 'max', 'mean'],
        'indice_uv': 'max'
    }
    
    # Filtrar apenas agregações para colunas que existem
    agregacao_filtrada = {k: v for k, v in agregacao.items() if k in df.columns}
    
    df_diario = df.groupby('data_dia').agg(agregacao_filtrada).reset_index()
    
    # Renomear colunas com agregação múltipla
    colunas_novas = []
    for col in df_diario.columns:
        if isinstance(col, tuple):
            if col[1] == 'max':
                colunas_novas.append(f'{col[0]}_max')
            elif col[1] == 'min':
                colunas_novas.append(f'{col[0]}_min')
            elif col[1] == 'mean':
                colunas_novas.append(f'{col[0]}_media')
            elif col[1] == 'sum':
                colunas_novas.append(f'{col[0]}_total')
            else:
                colunas_novas.append(f'{col[0]}_{col[1]}')
        else:
            colunas_novas.append(col)
    
    df_diario.columns = colunas_novas
    
    # Converter data_dia de volta para datetime
    if 'data_dia' in df_diario.columns:
        df_diario['data'] = pd.to_datetime(df_diario['data_dia'])
        df_diario = df_diario.drop('data_dia', axis=1)
        
        # Reordenar colunas (data primeiro)
        cols = ['data'] + [col for col in df_diario.columns if col != 'data']
        df_diario = df_diario[cols]
    
    return df_diario


def salvar_csv_chuvas(df_diario, output_dir):
    """
    Salva CSV simplificado APENAS com dados de CHUVA.
    Mantém compatibilidade com scripts existentes.
    """
    if df_diario is None or len(df_diario) == 0:
        return None
    
    # Selecionar apenas colunas de chuva
    df_chuvas = pd.DataFrame()
    
    # Buscar coluna de data (pode ter nome diferente)
    col_data = None
    for col in df_diario.columns:
        if 'data' in col.lower() and 'dia' not in col.lower():
            col_data = col
            break
    
    if col_data is None:
        col_data = df_diario.columns[0]  # Usar primeira coluna como fallback
    
    df_chuvas['data'] = df_diario[col_data]
    
    # Verificar quais colunas de chuva existem
    for col in df_diario.columns:
        if 'chuva_acumulada' in col.lower() or 'chuva_max' in col.lower():
            df_chuvas['chuva_total'] = df_diario[col]
            break
    
    for col in df_diario.columns:
        if 'chuva_intensidade' in col.lower() or 'intensidade_max' in col.lower():
            df_chuvas['intensidade_chuva'] = df_diario[col]
            break
    
    # Salvar
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f'chuvas_diarias_{timestamp}.csv'
    caminho = Path(output_dir) / nome_arquivo
    
    df_chuvas.to_csv(caminho, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    
    return caminho


def salvar_csv_completo(df_diario, output_dir):
    """
    Salva CSV COMPLETO com TODAS as variáveis meteorológicas.
    """
    if df_diario is None or len(df_diario) == 0:
        return None
    
    # Salvar
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f'dados_meteorologicos_completos_{timestamp}.csv'
    caminho = Path(output_dir) / nome_arquivo
    
    df_diario.to_csv(caminho, index=False, sep=';', decimal=',', encoding='utf-8-sig')
    
    return caminho


def main():
    """Função principal."""
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   PROCESSADOR COMPLETO DE DADOS METEOROLÓGICOS - ESTAÇÃO      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    # Diretórios
    dados_dir = Path('Dados')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Encontrar todos os CSVs
    arquivos = sorted(glob.glob(str(dados_dir / '*.csv')))
    
    if not arquivos:
        print("\n❌ Nenhum arquivo CSV encontrado na pasta Dados/")
        return
    
    print(f"\n📂 Encontrados {len(arquivos)} arquivos CSV:")
    for arq in arquivos:
        print(f"   • {Path(arq).name}")
    
    print("\n" + "="*70)
    print("🌧️ PROCESSANDO DADOS METEOROLÓGICOS")
    print("="*70)
    
    # Processar todos os arquivos
    dados_todos = []
    
    for arquivo in arquivos:
        df_processado = processar_csv_completo(arquivo)
        
        if df_processado is not None and len(df_processado) > 0:
            dados_todos.append(df_processado)
    
    if not dados_todos:
        print("\n❌ Nenhum dado foi processado com sucesso!")
        return
    
    # Concatenar todos os dados
    print("\n📊 Consolidando dados...")
    df_completo = pd.concat(dados_todos, ignore_index=True)
    df_completo = df_completo.sort_values('data').reset_index(drop=True)
    
    print(f"✅ Total de registros (10 min): {len(df_completo)}")
    print(f"   Período: {df_completo['data'].min().strftime('%d/%m/%Y')} até {df_completo['data'].max().strftime('%d/%m/%Y')}")
    
    # Agregar para dados diários
    print("\n📅 Agregando dados para valores diários...")
    df_diario = agregar_dados_diarios(df_completo)
    
    if df_diario is None:
        print("❌ Erro ao agregar dados diários!")
        return
    
    print(f"✅ Total de dias: {len(df_diario)}")
    
    # Estatísticas gerais
    if 'chuva_acumulada' in df_diario.columns:
        chuva_total = df_diario['chuva_acumulada'].sum()
        dias_chuva = len(df_diario[df_diario['chuva_acumulada'] > 0])
        print(f"   • Chuva total: {chuva_total:.1f} mm")
        print(f"   • Dias com chuva: {dias_chuva}")
    
    if 'temperatura_max' in df_diario.columns:
        temp_max = df_diario['temperatura_max'].max()
        temp_min = df_diario['temperatura_min'].min()
        print(f"   • Temperatura: {temp_min:.1f}°C a {temp_max:.1f}°C")
    
    # Salvar CSV de CHUVAS (simplificado)
    print("\n💾 Salvando CSV de CHUVAS (simplificado)...")
    caminho_chuvas = salvar_csv_chuvas(df_diario, output_dir)
    
    if caminho_chuvas:
        print(f"✅ CSV de Chuvas salvo: {caminho_chuvas.name}")
        print(f"   📂 Local: {caminho_chuvas}")
    
    # Salvar CSV COMPLETO
    print("\n💾 Salvando CSV COMPLETO (todas as variáveis)...")
    caminho_completo = salvar_csv_completo(df_diario, output_dir)
    
    if caminho_completo:
        print(f"✅ CSV Completo salvo: {caminho_completo.name}")
        print(f"   📂 Local: {caminho_completo}")
        
        # Mostrar estrutura do arquivo completo
        print(f"\n📋 Variáveis no CSV completo ({len(df_diario.columns)} colunas):")
        for i, col in enumerate(df_diario.columns, 1):
            print(f"   {i:2d}. {col}")
    
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║                    ✅ PROCESSAMENTO CONCLUÍDO                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    print("\n📂 Arquivos gerados:")
    print(f"   • CSV Chuvas (simplificado): {caminho_chuvas.name}")
    print(f"   • CSV Completo (todas variáveis): {caminho_completo.name}")
    
    print("\n💡 Próximos passos:")
    print("   1. Use o CSV de chuvas para gráficos existentes")
    print("   2. Use o CSV completo para análises avançadas")
    print("   3. Calcule Evapotranspiração (ETP)")
    print("   4. Crie Balanço Hídrico")
    print("   5. Análise de Janelas de Plantio")


if __name__ == "__main__":
    main()
