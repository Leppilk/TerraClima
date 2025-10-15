"""
Módulo para agregações temporais avançadas
"""

import pandas as pd
import numpy as np
from typing import Dict, Literal

from config import MESES_PT_FULL


class DataAggregator:
    """Agrega dados em diferentes períodos temporais."""
    
    def __init__(self):
        """Inicializa o agregador."""
        pass
    
    def aggregate_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados diários para valores mensais.
        
        Args:
            df: DataFrame com dados diários
            
        Returns:
            DataFrame com dados mensais
        """
        if df.empty:
            return df
        
        # Criar chave ano-mês
        df['ano_mes'] = df['data'].dt.to_period('M')
        
        agregacao = {}
        
        # Temperatura
        for col in ['temperatura_max', 'temperatura_min', 'temperatura_media']:
            if col in df.columns:
                if 'max' in col:
                    agregacao[col] = ['max', 'mean']
                elif 'min' in col:
                    agregacao[col] = ['min', 'mean']
                else:
                    agregacao[col] = 'mean'
        
        # Umidade
        for col in ['umidade_max', 'umidade_min', 'umidade_media']:
            if col in df.columns:
                if 'max' in col:
                    agregacao[col] = 'max'
                elif 'min' in col:
                    agregacao[col] = 'min'
                else:
                    agregacao[col] = 'mean'
        
        # Chuva - soma mensal
        if 'chuva_acumulada' in df.columns:
            agregacao['chuva_acumulada'] = ['sum', 'max', 'count']
        
        # Vento
        if 'vento_velocidade_max' in df.columns:
            agregacao['vento_velocidade_max'] = 'max'
        if 'vento_rajada' in df.columns:
            agregacao['vento_rajada'] = 'max'
        
        # Radiação - soma mensal
        if 'radiacao_solar_total' in df.columns:
            agregacao['radiacao_solar_total'] = 'sum'
        
        # Pressão
        if 'pressao_media' in df.columns:
            agregacao['pressao_media'] = 'mean'
        
        df_mensal = df.groupby('ano_mes').agg(agregacao).reset_index()
        
        # Renomear colunas
        colunas_novas = []
        for col in df_mensal.columns:
            if isinstance(col, tuple):
                colunas_novas.append(f'{col[0]}_{col[1]}')
            else:
                colunas_novas.append(col)
        
        df_mensal.columns = colunas_novas
        
        # Adicionar informações temporais
        if 'ano_mes' in df_mensal.columns:
            df_mensal['ano'] = df_mensal['ano_mes'].dt.year
            df_mensal['mes'] = df_mensal['ano_mes'].dt.month
            df_mensal['mes_nome'] = df_mensal['mes'].map(MESES_PT_FULL)
        
        return df_mensal
    
    def aggregate_weekly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados diários para valores semanais.
        
        Args:
            df: DataFrame com dados diários
            
        Returns:
            DataFrame com dados semanais
        """
        if df.empty:
            return df
        
        # Criar chave ano-semana
        df['ano_semana'] = df['data'].dt.to_period('W')
        
        agregacao = {}
        
        # Temperatura
        if 'temperatura_max' in df.columns:
            agregacao['temperatura_max'] = ['max', 'mean']
        if 'temperatura_min' in df.columns:
            agregacao['temperatura_min'] = ['min', 'mean']
        if 'temperatura_media' in df.columns:
            agregacao['temperatura_media'] = 'mean'
        
        # Chuva
        if 'chuva_acumulada' in df.columns:
            agregacao['chuva_acumulada'] = ['sum', 'max']
        
        # Umidade
        if 'umidade_media' in df.columns:
            agregacao['umidade_media'] = 'mean'
        
        df_semanal = df.groupby('ano_semana').agg(agregacao).reset_index()
        
        # Renomear colunas
        colunas_novas = []
        for col in df_semanal.columns:
            if isinstance(col, tuple):
                colunas_novas.append(f'{col[0]}_{col[1]}')
            else:
                colunas_novas.append(col)
        
        df_semanal.columns = colunas_novas
        
        return df_semanal
    
    def get_statistics_summary(self, df: pd.DataFrame, 
                               period: Literal['daily', 'monthly', 'overall'] = 'overall') -> Dict:
        """
        Calcula estatísticas resumidas.
        
        Args:
            df: DataFrame com dados
            period: Período de agregação
            
        Returns:
            Dicionário com estatísticas
        """
        stats = {}
        
        # Estatísticas de temperatura
        if 'temperatura_max' in df.columns:
            stats['temperatura'] = {
                'max_absoluta': df['temperatura_max'].max(),
                'min_absoluta': df['temperatura_min'].min() if 'temperatura_min' in df.columns else None,
                'media': df['temperatura_media'].mean() if 'temperatura_media' in df.columns else None,
                'data_max': df.loc[df['temperatura_max'].idxmax(), 'data'] if 'data' in df.columns else None,
                'data_min': df.loc[df['temperatura_min'].idxmin(), 'data'] if 'temperatura_min' in df.columns and 'data' in df.columns else None
            }
        
        # Estatísticas de chuva
        if 'chuva_acumulada' in df.columns:
            dias_chuva = len(df[df['chuva_acumulada'] > 0])
            total_dias = len(df)
            
            stats['chuva'] = {
                'total': df['chuva_acumulada'].sum(),
                'max_dia': df['chuva_acumulada'].max(),
                'media_diaria': df['chuva_acumulada'].mean(),
                'dias_com_chuva': dias_chuva,
                'dias_sem_chuva': total_dias - dias_chuva,
                'porcentagem_dias_chuva': (dias_chuva / total_dias * 100) if total_dias > 0 else 0,
                'data_max': df.loc[df['chuva_acumulada'].idxmax(), 'data'] if 'data' in df.columns else None
            }
        
        # Estatísticas de umidade
        if 'umidade_media' in df.columns:
            stats['umidade'] = {
                'max': df['umidade_max'].max() if 'umidade_max' in df.columns else None,
                'min': df['umidade_min'].min() if 'umidade_min' in df.columns else None,
                'media': df['umidade_media'].mean()
            }
        
        # Estatísticas de vento
        if 'vento_rajada' in df.columns:
            stats['vento'] = {
                'rajada_maxima': df['vento_rajada'].max(),
                'velocidade_media': df['vento_velocidade_media'].mean() if 'vento_velocidade_media' in df.columns else None,
                'data_rajada_max': df.loc[df['vento_rajada'].idxmax(), 'data'] if 'data' in df.columns else None
            }
        
        # Estatísticas de radiação
        if 'radiacao_solar_total' in df.columns:
            stats['radiacao'] = {
                'total': df['radiacao_solar_total'].sum(),
                'max_dia': df['radiacao_solar_max'].max() if 'radiacao_solar_max' in df.columns else None,
                'media_diaria': df['radiacao_solar_total'].mean()
            }
        
        return stats
    
    def calculate_dry_spell(self, df: pd.DataFrame) -> Dict:
        """
        Calcula períodos de seca (dias consecutivos sem chuva).
        
        Args:
            df: DataFrame com dados de chuva
            
        Returns:
            Dicionário com informações sobre períodos secos
        """
        if 'chuva_acumulada' not in df.columns or df.empty:
            return {}
        
        # Ordenar por data
        df = df.sort_values('data').reset_index(drop=True)
        
        periodo_seco_atual = 0
        periodo_seco_max = 0
        data_inicio_seca = None
        data_fim_seca = None
        inicio_temp = None
        
        for idx, row in df.iterrows():
            if row['chuva_acumulada'] == 0:
                if periodo_seco_atual == 0:
                    inicio_temp = row['data']
                periodo_seco_atual += 1
                
                if periodo_seco_atual > periodo_seco_max:
                    periodo_seco_max = periodo_seco_atual
                    data_inicio_seca = inicio_temp
                    data_fim_seca = row['data']
            else:
                periodo_seco_atual = 0
        
        return {
            'periodo_max': periodo_seco_max,
            'data_inicio': data_inicio_seca,
            'data_fim': data_fim_seca
        }
    
    def calculate_rainy_spell(self, df: pd.DataFrame) -> Dict:
        """
        Calcula períodos chuvosos (dias consecutivos com chuva).
        
        Args:
            df: DataFrame com dados de chuva
            
        Returns:
            Dicionário com informações sobre períodos chuvosos
        """
        if 'chuva_acumulada' not in df.columns or df.empty:
            return {}
        
        df = df.sort_values('data').reset_index(drop=True)
        
        periodo_chuvoso_atual = 0
        periodo_chuvoso_max = 0
        data_inicio = None
        data_fim = None
        inicio_temp = None
        
        for idx, row in df.iterrows():
            if row['chuva_acumulada'] > 0:
                if periodo_chuvoso_atual == 0:
                    inicio_temp = row['data']
                periodo_chuvoso_atual += 1
                
                if periodo_chuvoso_atual > periodo_chuvoso_max:
                    periodo_chuvoso_max = periodo_chuvoso_atual
                    data_inicio = inicio_temp
                    data_fim = row['data']
            else:
                periodo_chuvoso_atual = 0
        
        return {
            'periodo_max': periodo_chuvoso_max,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        }
