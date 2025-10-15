"""
Módulo de análise de temperatura
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class TemperatureAnalyzer:
    """Análises especializadas para dados de temperatura."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador de temperatura.
        
        Args:
            df: DataFrame com dados diários processados
        """
        self.df = df.copy()
        
    def calculate_statistics(self) -> Dict:
        """
        Calcula estatísticas completas de temperatura.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {}
        
        # Temperatura máxima
        if 'temperatura_max' in self.df.columns:
            temp_max = self.df['temperatura_max']
            stats['temp_max'] = {
                'absoluta': temp_max.max(),
                'media': temp_max.mean(),
                'desvio_padrao': temp_max.std(),
                'data_maxima': self.df.loc[temp_max.idxmax(), 'data'] if not temp_max.empty else None
            }
        
        # Temperatura mínima
        if 'temperatura_min' in self.df.columns:
            temp_min = self.df['temperatura_min']
            stats['temp_min'] = {
                'absoluta': temp_min.min(),
                'media': temp_min.mean(),
                'desvio_padrao': temp_min.std(),
                'data_minima': self.df.loc[temp_min.idxmin(), 'data'] if not temp_min.empty else None
            }
        
        # Temperatura média
        if 'temperatura_media' in self.df.columns:
            temp_media = self.df['temperatura_media']
            stats['temp_media'] = {
                'geral': temp_media.mean(),
                'desvio_padrao': temp_media.std(),
                'mediana': temp_media.median()
            }
        
        # Amplitude térmica
        if 'temperatura_amplitude' in self.df.columns:
            amplitude = self.df['temperatura_amplitude']
            stats['amplitude'] = {
                'maxima': amplitude.max(),
                'media': amplitude.mean(),
                'minima': amplitude.min(),
                'data_maxima_amplitude': self.df.loc[amplitude.idxmax(), 'data'] if not amplitude.empty else None
            }
        elif 'temperatura_max' in self.df.columns and 'temperatura_min' in self.df.columns:
            amplitude = self.df['temperatura_max'] - self.df['temperatura_min']
            stats['amplitude'] = {
                'maxima': amplitude.max(),
                'media': amplitude.mean(),
                'minima': amplitude.min()
            }
        
        return stats
    
    def classify_thermal_zones(self) -> pd.DataFrame:
        """
        Classifica dias por zona térmica.
        
        Returns:
            DataFrame com classificações
        """
        if 'temperatura_max' not in self.df.columns:
            return pd.DataFrame()
        
        def classificar(temp):
            if pd.isna(temp):
                return 'Indisponível'
            elif temp < 0:
                return 'Congelamento'
            elif temp < 10:
                return 'Muito Frio'
            elif temp < 18:
                return 'Frio'
            elif temp < 26:
                return 'Confortável'
            elif temp < 32:
                return 'Quente'
            elif temp < 38:
                return 'Muito Quente'
            else:
                return 'Extremo'
        
        df_classified = self.df[['data', 'temperatura_max']].copy()
        df_classified['zona_termica'] = df_classified['temperatura_max'].apply(classificar)
        
        return df_classified
    
    def get_thermal_distribution(self) -> Dict:
        """
        Calcula distribuição por zona térmica.
        
        Returns:
            Dicionário com contagens por zona
        """
        df_classified = self.classify_thermal_zones()
        
        if df_classified.empty:
            return {}
        
        distribution = df_classified['zona_termica'].value_counts().to_dict()
        total = len(df_classified)
        distribution_pct = {k: (v / total * 100) for k, v in distribution.items()}
        
        return {
            'contagem': distribution,
            'porcentagem': distribution_pct
        }
    
    def detect_heat_waves(self, threshold_temp: float = 32.0, 
                         min_days: int = 3) -> List[Dict]:
        """
        Detecta ondas de calor (dias consecutivos acima do limite).
        
        Args:
            threshold_temp: Temperatura mínima para onda de calor
            min_days: Número mínimo de dias consecutivos
            
        Returns:
            Lista de ondas de calor detectadas
        """
        if 'temperatura_max' not in self.df.columns:
            return []
        
        df_sorted = self.df.sort_values('data').reset_index(drop=True)
        
        heat_waves = []
        current_wave = 0
        start_date = None
        max_temp_in_wave = 0
        
        for idx, row in df_sorted.iterrows():
            if row['temperatura_max'] >= threshold_temp:
                if current_wave == 0:
                    start_date = row['data']
                    max_temp_in_wave = row['temperatura_max']
                else:
                    max_temp_in_wave = max(max_temp_in_wave, row['temperatura_max'])
                current_wave += 1
            else:
                if current_wave >= min_days:
                    heat_waves.append({
                        'duracao': current_wave,
                        'inicio': start_date,
                        'fim': df_sorted.loc[idx-1, 'data'],
                        'temp_maxima': max_temp_in_wave
                    })
                current_wave = 0
                max_temp_in_wave = 0
        
        # Adicionar última onda se terminar com calor
        if current_wave >= min_days:
            heat_waves.append({
                'duracao': current_wave,
                'inicio': start_date,
                'fim': df_sorted.iloc[-1]['data'],
                'temp_maxima': max_temp_in_wave
            })
        
        return sorted(heat_waves, key=lambda x: x['duracao'], reverse=True)
    
    def detect_cold_spells(self, threshold_temp: float = 10.0, 
                          min_days: int = 3) -> List[Dict]:
        """
        Detecta períodos de frio (dias consecutivos abaixo do limite).
        
        Args:
            threshold_temp: Temperatura máxima para período frio
            min_days: Número mínimo de dias consecutivos
            
        Returns:
            Lista de períodos frios detectados
        """
        if 'temperatura_min' not in self.df.columns:
            return []
        
        df_sorted = self.df.sort_values('data').reset_index(drop=True)
        
        cold_spells = []
        current_spell = 0
        start_date = None
        min_temp_in_spell = 999
        
        for idx, row in df_sorted.iterrows():
            if row['temperatura_min'] <= threshold_temp:
                if current_spell == 0:
                    start_date = row['data']
                    min_temp_in_spell = row['temperatura_min']
                else:
                    min_temp_in_spell = min(min_temp_in_spell, row['temperatura_min'])
                current_spell += 1
            else:
                if current_spell >= min_days:
                    cold_spells.append({
                        'duracao': current_spell,
                        'inicio': start_date,
                        'fim': df_sorted.loc[idx-1, 'data'],
                        'temp_minima': min_temp_in_spell
                    })
                current_spell = 0
                min_temp_in_spell = 999
        
        # Adicionar último período se terminar com frio
        if current_spell >= min_days:
            cold_spells.append({
                'duracao': current_spell,
                'inicio': start_date,
                'fim': df_sorted.iloc[-1]['data'],
                'temp_minima': min_temp_in_spell
            })
        
        return sorted(cold_spells, key=lambda x: x['duracao'], reverse=True)
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """
        Calcula resumo mensal de temperaturas.
        
        Returns:
            DataFrame com resumo mensal
        """
        if 'mes' not in self.df.columns:
            return pd.DataFrame()
        
        agg_dict = {}
        
        if 'temperatura_max' in self.df.columns:
            agg_dict['temperatura_max'] = ['max', 'mean']
        if 'temperatura_min' in self.df.columns:
            agg_dict['temperatura_min'] = ['min', 'mean']
        if 'temperatura_media' in self.df.columns:
            agg_dict['temperatura_media'] = 'mean'
        if 'temperatura_amplitude' in self.df.columns:
            agg_dict['temperatura_amplitude'] = ['max', 'mean']
        
        if not agg_dict:
            return pd.DataFrame()
        
        monthly = self.df.groupby(['ano', 'mes', 'mes_nome']).agg(agg_dict).reset_index()
        
        # Simplificar nomes de colunas
        monthly.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col 
                          for col in monthly.columns]
        
        return monthly
    
    def calculate_thermal_comfort_livestock(self) -> Dict:
        """
        Calcula índice de conforto térmico para animais (granja).
        
        Zona de conforto para aves: 18-26°C
        
        Returns:
            Dicionário com análise de conforto
        """
        if 'temperatura_media' not in self.df.columns:
            return {}
        
        comfort_min = 18
        comfort_max = 26
        
        df_temp = self.df[['data', 'temperatura_media']].copy()
        df_temp['conforto'] = df_temp['temperatura_media'].apply(
            lambda t: 'Confortável' if comfort_min <= t <= comfort_max 
                     else 'Frio' if t < comfort_min 
                     else 'Quente'
        )
        
        distribution = df_temp['conforto'].value_counts()
        total_dias = len(df_temp)
        
        # Dias recentes (últimos 7)
        recent = df_temp.tail(7)
        dias_desconforto_recente = len(recent[recent['conforto'] != 'Confortável'])
        
        return {
            'dias_confortaveis': distribution.get('Confortável', 0),
            'dias_frio': distribution.get('Frio', 0),
            'dias_quente': distribution.get('Quente', 0),
            'porcentagem_conforto': (distribution.get('Confortável', 0) / total_dias * 100),
            'status_recente': 'ALERTA' if dias_desconforto_recente > 3 else 'OK',
            'dias_desconforto_ultima_semana': dias_desconforto_recente
        }
    
    def calculate_growing_degree_days(self, base_temp: float = 10.0) -> pd.Series:
        """
        Calcula Graus-Dia de Crescimento (GDD) acumulado.
        Útil para previsão de desenvolvimento de culturas.
        
        Args:
            base_temp: Temperatura base para cálculo
            
        Returns:
            Series com GDD acumulado
        """
        if 'temperatura_media' not in self.df.columns:
            return pd.Series()
        
        df_sorted = self.df.sort_values('data').copy()
        df_sorted['gdd_diario'] = df_sorted['temperatura_media'].apply(
            lambda t: max(0, t - base_temp)
        )
        df_sorted['gdd_acumulado'] = df_sorted['gdd_diario'].cumsum()
        
        return df_sorted[['data', 'gdd_acumulado']].set_index('data')['gdd_acumulado']
    
    def get_temperature_extremes_by_month(self) -> pd.DataFrame:
        """
        Identifica extremos de temperatura por mês.
        
        Returns:
            DataFrame com extremos mensais
        """
        if 'mes' not in self.df.columns:
            return pd.DataFrame()
        
        extremes = []
        
        for (ano, mes, mes_nome), group in self.df.groupby(['ano', 'mes', 'mes_nome']):
            if 'temperatura_max' in group.columns:
                idx_max = group['temperatura_max'].idxmax()
                temp_max = group.loc[idx_max, 'temperatura_max']
                data_max = group.loc[idx_max, 'data']
            else:
                temp_max = None
                data_max = None
            
            if 'temperatura_min' in group.columns:
                idx_min = group['temperatura_min'].idxmin()
                temp_min = group.loc[idx_min, 'temperatura_min']
                data_min = group.loc[idx_min, 'data']
            else:
                temp_min = None
                data_min = None
            
            extremes.append({
                'ano': ano,
                'mes': mes,
                'mes_nome': mes_nome,
                'temp_maxima': temp_max,
                'data_maxima': data_max,
                'temp_minima': temp_min,
                'data_minima': data_min
            })
        
        return pd.DataFrame(extremes)
