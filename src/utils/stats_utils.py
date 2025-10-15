"""
Utilitários para cálculos estatísticos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


class StatsUtils:
    """Utilitários para cálculos estatísticos."""
    
    @staticmethod
    def calculate_percentile(series: pd.Series, percentile: int) -> float:
        """
        Calcula percentil de uma série.
        
        Args:
            series: Série de dados
            percentile: Percentil desejado (0-100)
            
        Returns:
            Valor do percentil
        """
        return series.quantile(percentile / 100)
    
    @staticmethod
    def calculate_outliers(series: pd.Series, method: str = 'iqr') -> Tuple[float, float]:
        """
        Calcula limites para outliers.
        
        Args:
            series: Série de dados
            method: Método ('iqr' ou 'zscore')
            
        Returns:
            Tupla (limite_inferior, limite_superior)
        """
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
        else:  # zscore
            mean = series.mean()
            std = series.std()
            lower = mean - 3 * std
            upper = mean + 3 * std
        
        return lower, upper
    
    @staticmethod
    def detect_outliers(series: pd.Series, method: str = 'iqr') -> pd.Series:
        """
        Detecta outliers em uma série.
        
        Args:
            series: Série de dados
            method: Método de detecção
            
        Returns:
            Série booleana indicando outliers
        """
        lower, upper = StatsUtils.calculate_outliers(series, method)
        return (series < lower) | (series > upper)
    
    @staticmethod
    def calculate_moving_average(series: pd.Series, window: int = 7) -> pd.Series:
        """
        Calcula média móvel.
        
        Args:
            series: Série de dados
            window: Tamanho da janela
            
        Returns:
            Série com média móvel
        """
        return series.rolling(window=window, min_periods=1).mean()
    
    @staticmethod
    def calculate_correlation(series1: pd.Series, series2: pd.Series, 
                             method: str = 'pearson') -> float:
        """
        Calcula correlação entre duas séries.
        
        Args:
            series1: Primeira série
            series2: Segunda série
            method: Método ('pearson', 'spearman', 'kendall')
            
        Returns:
            Coeficiente de correlação
        """
        # Remover NaNs
        df_temp = pd.DataFrame({'s1': series1, 's2': series2}).dropna()
        
        if len(df_temp) < 2:
            return np.nan
        
        return df_temp['s1'].corr(df_temp['s2'], method=method)
    
    @staticmethod
    def calculate_trend(series: pd.Series) -> Dict:
        """
        Calcula tendência linear de uma série.
        
        Args:
            series: Série de dados
            
        Returns:
            Dicionário com slope, intercept, r_value, p_value
        """
        # Remover NaNs
        series_clean = series.dropna()
        
        if len(series_clean) < 2:
            return {'slope': 0, 'intercept': 0, 'r_value': 0, 'p_value': 1}
        
        x = np.arange(len(series_clean))
        y = series_clean.values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_value': r_value,
            'p_value': p_value,
            'std_err': std_err
        }
    
    @staticmethod
    def calculate_summary_stats(series: pd.Series) -> Dict:
        """
        Calcula estatísticas resumidas.
        
        Args:
            series: Série de dados
            
        Returns:
            Dicionário com estatísticas
        """
        return {
            'count': series.count(),
            'mean': series.mean(),
            'std': series.std(),
            'min': series.min(),
            'q25': series.quantile(0.25),
            'median': series.median(),
            'q75': series.quantile(0.75),
            'max': series.max(),
            'range': series.max() - series.min(),
            'cv': (series.std() / series.mean() * 100) if series.mean() != 0 else 0
        }
    
    @staticmethod
    def calculate_cumulative(series: pd.Series) -> pd.Series:
        """
        Calcula soma acumulada.
        
        Args:
            series: Série de dados
            
        Returns:
            Série acumulada
        """
        return series.cumsum()
    
    @staticmethod
    def normalize_series(series: pd.Series, method: str = 'minmax') -> pd.Series:
        """
        Normaliza uma série.
        
        Args:
            series: Série de dados
            method: Método ('minmax' ou 'zscore')
            
        Returns:
            Série normalizada
        """
        if method == 'minmax':
            return (series - series.min()) / (series.max() - series.min())
        else:  # zscore
            return (series - series.mean()) / series.std()
    
    @staticmethod
    def calculate_growth_rate(series: pd.Series, periods: int = 1) -> pd.Series:
        """
        Calcula taxa de crescimento.
        
        Args:
            series: Série de dados
            periods: Número de períodos para comparação
            
        Returns:
            Série com taxa de crescimento (%)
        """
        return series.pct_change(periods=periods) * 100
