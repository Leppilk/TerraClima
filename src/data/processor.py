"""
Módulo para processar dados meteorológicos
Converte dados de 10 em 10 minutos para dados diários
"""

import pandas as pd
import numpy as np
from typing import Dict, List

from config import RAIN_CLASSIFICATION, TEMP_ZONES, MESES_PT


class DataProcessor:
    """Processa dados brutos da estação meteorológica."""
    
    def __init__(self):
        """Inicializa o processador de dados."""
        self.rain_classification = RAIN_CLASSIFICATION
        self.temp_zones = TEMP_ZONES
        
    def aggregate_to_daily(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados de 10 minutos para valores diários.
        
        Args:
            df: DataFrame com dados de 10 em 10 minutos
            
        Returns:
            DataFrame com dados diários agregados
        """
        if df.empty:
            return df
        
        print("\n📅 AGREGANDO DADOS PARA VALORES DIÁRIOS")
        print("=" * 70)
        
        # Extrair apenas a data (sem hora)
        df['data_dia'] = df['data'].dt.date
        
        # Definir agregações para cada variável
        agregacao = {}
        
        # TEMPERATURA - Máx, Mín, Média
        if 'temperatura' in df.columns:
            agregacao['temperatura'] = ['max', 'min', 'mean']
        if 'temp_interior' in df.columns:
            agregacao['temp_interior'] = ['max', 'min', 'mean']
        if 'sensacao_termica' in df.columns:
            agregacao['sensacao_termica'] = ['max', 'min', 'mean']
        if 'ponto_orvalho' in df.columns:
            agregacao['ponto_orvalho'] = ['max', 'min', 'mean']
        if 'indice_calor' in df.columns:
            agregacao['indice_calor'] = ['max', 'mean']
        
        # UMIDADE - Máx, Mín, Média
        if 'umidade' in df.columns:
            agregacao['umidade'] = ['max', 'min', 'mean']
        if 'umidade_interior' in df.columns:
            agregacao['umidade_interior'] = ['max', 'min', 'mean']
        
        # VENTO - Máx e Média
        if 'vento_velocidade' in df.columns:
            agregacao['vento_velocidade'] = ['max', 'mean']
        if 'vento_rajada' in df.columns:
            agregacao['vento_rajada'] = 'max'
        if 'vento_direcao' in df.columns:
            # Direção predominante (moda)
            agregacao['vento_direcao'] = lambda x: x.mode()[0] if len(x.mode()) > 0 else x.mean()
        
        # PRESSÃO - Média
        if 'pressao' in df.columns:
            agregacao['pressao'] = ['max', 'min', 'mean']
        
        # CHUVA - Máximo do acumulado diário
        if 'chuva_acumulada' in df.columns:
            agregacao['chuva_acumulada'] = 'max'
        if 'chuva_intensidade' in df.columns:
            agregacao['chuva_intensidade'] = 'max'
        
        # RADIAÇÃO SOLAR - Soma (total diário) e Máx
        if 'radiacao_solar' in df.columns:
            # Somar e converter para energia total (W/m² * 10min = Wh/m² / 6)
            agregacao['radiacao_solar'] = ['sum', 'max', 'mean']
        if 'indice_uv' in df.columns:
            agregacao['indice_uv'] = 'max'
        
        # Agregar por dia
        df_diario = df.groupby('data_dia').agg(agregacao).reset_index()
        
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
                    # Para radiação solar, converter para kWh/m²
                    colunas_novas.append(f'{col[0]}_total')
                else:
                    colunas_novas.append(f'{col[0]}_{col[1]}')
            else:
                colunas_novas.append(col)
        
        df_diario.columns = colunas_novas
        
        # Verificar se data_dia existe antes de converter
        if 'data_dia' in df_diario.columns:
            # Converter data_dia de volta para datetime
            df_diario['data'] = pd.to_datetime(df_diario['data_dia'])
            df_diario = df_diario.drop('data_dia', axis=1)
        else:
            # Se não existe, usar a primeira coluna como data
            primeira_col = df_diario.columns[0]
            df_diario['data'] = pd.to_datetime(df_diario[primeira_col])
            df_diario = df_diario.drop(primeira_col, axis=1)
        
        # Reordenar colunas (data primeiro)
        cols = ['data'] + [col for col in df_diario.columns if col != 'data']
        df_diario = df_diario[cols]
        
        # Adicionar colunas temporais úteis
        df_diario = self.add_temporal_columns(df_diario)
        
        print(f"✅ Dados agregados: {len(df_diario)} dias")
        print(f"📊 Colunas geradas: {len(df_diario.columns)}")
        
        return df_diario
    
    def add_temporal_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona colunas temporais úteis para análise.
        
        Args:
            df: DataFrame com coluna 'data'
            
        Returns:
            DataFrame com colunas temporais adicionadas
        """
        df['ano'] = df['data'].dt.year
        df['mes'] = df['data'].dt.month
        df['mes_nome'] = df['mes'].map(MESES_PT)
        df['dia'] = df['data'].dt.day
        df['dia_semana'] = df['data'].dt.dayofweek  # 0=Segunda, 6=Domingo
        df['semana_ano'] = df['data'].dt.isocalendar().week
        df['dia_ano'] = df['data'].dt.dayofyear
        
        return df
    
    def classify_rain_intensity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica a intensidade da chuva diária.
        
        Args:
            df: DataFrame com coluna de chuva
            
        Returns:
            DataFrame com classificação de intensidade
        """
        if 'chuva_acumulada' not in df.columns:
            return df
        
        def classificar(mm):
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
        
        df['chuva_classificacao'] = df['chuva_acumulada'].apply(classificar)
        
        # Flag de chuva
        df['choveu'] = df['chuva_acumulada'] > 0
        
        return df
    
    def classify_temperature_zone(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica a temperatura em zonas.
        
        Args:
            df: DataFrame com coluna de temperatura
            
        Returns:
            DataFrame com classificação de zona térmica
        """
        if 'temperatura_max' not in df.columns:
            return df
        
        def classificar_temp(temp):
            if pd.isna(temp):
                return 'Indisponível'
            elif temp < 0:
                return 'Congelamento'
            elif temp < 10:
                return 'Frio'
            elif temp < 18:
                return 'Fresco'
            elif temp < 26:
                return 'Confortável'
            elif temp < 32:
                return 'Quente'
            elif temp < 38:
                return 'Muito Quente'
            else:
                return 'Extremo'
        
        df['temp_zona'] = df['temperatura_max'].apply(classificar_temp)
        
        return df
    
    def calculate_daily_amplitude(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula amplitude térmica diária.
        
        Args:
            df: DataFrame com temp_max e temp_min
            
        Returns:
            DataFrame com amplitude calculada
        """
        if 'temperatura_max' in df.columns and 'temperatura_min' in df.columns:
            df['temperatura_amplitude'] = df['temperatura_max'] - df['temperatura_min']
        
        if 'umidade_max' in df.columns and 'umidade_min' in df.columns:
            df['umidade_amplitude'] = df['umidade_max'] - df['umidade_min']
        
        return df
    
    def process_full_pipeline(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo de processamento.
        
        Args:
            df_raw: DataFrame com dados brutos (10 minutos)
            
        Returns:
            DataFrame processado com dados diários
        """
        print("\n🔄 PIPELINE DE PROCESSAMENTO COMPLETO")
        print("=" * 70)
        
        # 1. Agregar para diário
        df_daily = self.aggregate_to_daily(df_raw)
        
        if df_daily.empty:
            return df_daily
        
        # 2. Classificar chuva
        df_daily = self.classify_rain_intensity(df_daily)
        
        # 3. Classificar temperatura
        df_daily = self.classify_temperature_zone(df_daily)
        
        # 4. Calcular amplitudes
        df_daily = self.calculate_daily_amplitude(df_daily)
        
        print("\n✅ PROCESSAMENTO CONCLUÍDO")
        print(f"📊 Total de variáveis: {len(df_daily.columns)}")
        print(f"📅 Período: {df_daily['data'].min().strftime('%d/%m/%Y')} até {df_daily['data'].max().strftime('%d/%m/%Y')}")
        
        return df_daily
