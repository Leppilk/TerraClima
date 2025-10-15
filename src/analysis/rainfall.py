"""
Módulo de análise de precipitação (chuvas)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class RainfallAnalyzer:
    """Análises especializadas para dados de precipitação."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador de chuvas.
        
        Args:
            df: DataFrame com dados diários processados
        """
        self.df = df.copy()
        self.rain_col = self._identify_rain_column()
        
    def _identify_rain_column(self) -> str:
        """Identifica a coluna de chuva no DataFrame."""
        possible_cols = ['chuva_acumulada', 'chuva', 'precipitacao', 'rain']
        for col in possible_cols:
            if col in self.df.columns:
                return col
        return None
    
    def calculate_statistics(self) -> Dict:
        """
        Calcula estatísticas completas de chuva.
        
        Returns:
            Dicionário com estatísticas
        """
        if self.rain_col is None:
            return {}
        
        rain_data = self.df[self.rain_col]
        days_with_rain = len(self.df[rain_data > 0])
        total_days = len(self.df)
        
        stats = {
            'total_dias': total_days,
            'dias_com_chuva': days_with_rain,
            'dias_sem_chuva': total_days - days_with_rain,
            'porcentagem_dias_chuva': (days_with_rain / total_days * 100) if total_days > 0 else 0,
            'chuva_total': rain_data.sum(),
            'chuva_media_dia': rain_data.mean(),
            'chuva_media_dia_chuvoso': rain_data[rain_data > 0].mean() if days_with_rain > 0 else 0,
            'chuva_maxima_dia': rain_data.max(),
            'chuva_minima_dia_chuvoso': rain_data[rain_data > 0].min() if days_with_rain > 0 else 0,
            'desvio_padrao': rain_data.std(),
            'mediana': rain_data.median(),
            'quartil_25': rain_data.quantile(0.25),
            'quartil_75': rain_data.quantile(0.75)
        }
        
        # Data do dia mais chuvoso
        if not rain_data.empty and rain_data.max() > 0:
            idx_max = rain_data.idxmax()
            stats['data_max_chuva'] = self.df.loc[idx_max, 'data']
        
        return stats
    
    def classify_rain_days(self) -> pd.DataFrame:
        """
        Classifica os dias por intensidade de chuva.
        
        Returns:
            DataFrame com classificações
        """
        if self.rain_col is None:
            return pd.DataFrame()
        
        def classificar(mm):
            if mm == 0:
                return 'Sem chuva'
            elif mm < 5:
                return 'Fraca'
            elif mm < 15:
                return 'Moderada'
            elif mm < 25:
                return 'Forte'
            else:
                return 'Muito Forte'
        
        df_classified = self.df[['data', self.rain_col]].copy()
        df_classified['classificacao'] = df_classified[self.rain_col].apply(classificar)
        
        return df_classified
    
    def get_distribution_by_intensity(self) -> Dict:
        """
        Calcula distribuição por intensidade.
        
        Returns:
            Dicionário com contagens por intensidade
        """
        df_classified = self.classify_rain_days()
        
        if df_classified.empty:
            return {}
        
        distribution = df_classified['classificacao'].value_counts().to_dict()
        
        # Calcular porcentagens
        total = len(df_classified)
        distribution_pct = {k: (v / total * 100) for k, v in distribution.items()}
        
        return {
            'contagem': distribution,
            'porcentagem': distribution_pct
        }
    
    def calculate_dry_spells(self) -> List[Dict]:
        """
        Identifica todos os períodos secos (consecutivos sem chuva).
        
        Returns:
            Lista de dicionários com períodos secos
        """
        if self.rain_col is None:
            return []
        
        df_sorted = self.df.sort_values('data').reset_index(drop=True)
        
        dry_spells = []
        current_spell = 0
        start_date = None
        
        for idx, row in df_sorted.iterrows():
            if row[self.rain_col] == 0:
                if current_spell == 0:
                    start_date = row['data']
                current_spell += 1
            else:
                if current_spell > 0:
                    dry_spells.append({
                        'duracao': current_spell,
                        'inicio': start_date,
                        'fim': df_sorted.loc[idx-1, 'data']
                    })
                current_spell = 0
        
        # Adicionar último período se terminar em seca
        if current_spell > 0:
            dry_spells.append({
                'duracao': current_spell,
                'inicio': start_date,
                'fim': df_sorted.iloc[-1]['data']
            })
        
        return sorted(dry_spells, key=lambda x: x['duracao'], reverse=True)
    
    def calculate_rainy_spells(self) -> List[Dict]:
        """
        Identifica todos os períodos chuvosos (consecutivos com chuva).
        
        Returns:
            Lista de dicionários com períodos chuvosos
        """
        if self.rain_col is None:
            return []
        
        df_sorted = self.df.sort_values('data').reset_index(drop=True)
        
        rainy_spells = []
        current_spell = 0
        start_date = None
        total_rain = 0
        
        for idx, row in df_sorted.iterrows():
            if row[self.rain_col] > 0:
                if current_spell == 0:
                    start_date = row['data']
                current_spell += 1
                total_rain += row[self.rain_col]
            else:
                if current_spell > 0:
                    rainy_spells.append({
                        'duracao': current_spell,
                        'inicio': start_date,
                        'fim': df_sorted.loc[idx-1, 'data'],
                        'chuva_total': total_rain
                    })
                current_spell = 0
                total_rain = 0
        
        # Adicionar último período se terminar com chuva
        if current_spell > 0:
            rainy_spells.append({
                'duracao': current_spell,
                'inicio': start_date,
                'fim': df_sorted.iloc[-1]['data'],
                'chuva_total': total_rain
            })
        
        return sorted(rainy_spells, key=lambda x: x['duracao'], reverse=True)
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """
        Calcula resumo mensal de chuvas.
        
        Returns:
            DataFrame com resumo mensal
        """
        if self.rain_col is None or 'mes' not in self.df.columns:
            return pd.DataFrame()
        
        monthly = self.df.groupby(['ano', 'mes', 'mes_nome']).agg({
            self.rain_col: ['sum', 'mean', 'max', 'count'],
            'data': 'count'
        }).reset_index()
        
        # Renomear colunas
        monthly.columns = ['ano', 'mes', 'mes_nome', 'chuva_total', 
                          'chuva_media', 'chuva_maxima', 'dias_chuva', 'total_dias']
        
        # Calcular dias sem chuva
        monthly['dias_sem_chuva'] = monthly['total_dias'] - monthly['dias_chuva']
        
        return monthly
    
    def get_top_rainy_days(self, n: int = 10) -> pd.DataFrame:
        """
        Retorna os N dias mais chuvosos.
        
        Args:
            n: Número de dias a retornar
            
        Returns:
            DataFrame com top N dias
        """
        if self.rain_col is None:
            return pd.DataFrame()
        
        df_rainy = self.df[self.df[self.rain_col] > 0].copy()
        top_days = df_rainy.nlargest(n, self.rain_col)[['data', self.rain_col]]
        
        return top_days.reset_index(drop=True)
    
    def calculate_cumulative_rain(self) -> pd.Series:
        """
        Calcula chuva acumulada ao longo do tempo.
        
        Returns:
            Series com chuva acumulada
        """
        if self.rain_col is None:
            return pd.Series()
        
        df_sorted = self.df.sort_values('data')
        return df_sorted[self.rain_col].cumsum()
    
    def get_rain_by_weekday(self) -> Dict:
        """
        Analisa padrão de chuva por dia da semana.
        
        Returns:
            Dicionário com estatísticas por dia da semana
        """
        if self.rain_col is None or 'dia_semana' not in self.df.columns:
            return {}
        
        weekday_names = {
            0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta',
            4: 'Sexta', 5: 'Sábado', 6: 'Domingo'
        }
        
        weekday_stats = self.df.groupby('dia_semana').agg({
            self.rain_col: ['sum', 'mean', 'count']
        }).reset_index()
        
        weekday_stats.columns = ['dia_semana', 'total', 'media', 'dias']
        weekday_stats['nome_dia'] = weekday_stats['dia_semana'].map(weekday_names)
        
        return weekday_stats.to_dict('records')
    
    def calculate_irrigation_need(self, threshold_days: int = 7, 
                                  threshold_rain: float = 10.0) -> Dict:
        """
        Calcula necessidade de irrigação baseada em períodos secos.
        
        Args:
            threshold_days: Dias sem chuva para alerta
            threshold_rain: Chuva mínima (mm) para considerar adequada
            
        Returns:
            Dicionário com análise de irrigação
        """
        if self.rain_col is None:
            return {}
        
        # Últimos 7 dias
        recent_days = self.df.tail(threshold_days)
        recent_rain = recent_days[self.rain_col].sum()
        days_without_rain = len(recent_days[recent_days[self.rain_col] == 0])
        
        # Determinar status
        if days_without_rain >= threshold_days:
            status = 'CRÍTICO'
            acao = 'Irrigação urgente necessária'
        elif recent_rain < threshold_rain:
            status = 'ALERTA'
            acao = 'Considerar irrigação'
        else:
            status = 'OK'
            acao = 'Sem necessidade de irrigação'
        
        return {
            'status': status,
            'acao': acao,
            'dias_sem_chuva': days_without_rain,
            'chuva_ultimos_dias': recent_rain,
            'periodo_analisado': threshold_days
        }
