"""
Utilitários para manipulação de datas
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List

from config import MESES_PT, MESES_PT_FULL


class DateUtils:
    """Utilitários para trabalhar com datas."""
    
    @staticmethod
    def format_date_br(date: pd.Timestamp) -> str:
        """
        Formata data no padrão brasileiro.
        
        Args:
            date: Data para formatar
            
        Returns:
            String formatada (dd/mm/yyyy)
        """
        if pd.isna(date):
            return ''
        return date.strftime('%d/%m/%Y')
    
    @staticmethod
    def format_datetime_br(date: pd.Timestamp) -> str:
        """
        Formata data/hora no padrão brasileiro.
        
        Args:
            date: Data/hora para formatar
            
        Returns:
            String formatada (dd/mm/yyyy HH:MM)
        """
        if pd.isna(date):
            return ''
        return date.strftime('%d/%m/%Y %H:%M')
    
    @staticmethod
    def get_month_name(month: int, short: bool = True) -> str:
        """
        Retorna nome do mês em português.
        
        Args:
            month: Número do mês (1-12)
            short: Se True, retorna nome abreviado
            
        Returns:
            Nome do mês
        """
        if short:
            return MESES_PT.get(month, '')
        return MESES_PT_FULL.get(month, '')
    
    @staticmethod
    def get_season(month: int) -> str:
        """
        Retorna estação do ano baseada no mês.
        
        Args:
            month: Número do mês (1-12)
            
        Returns:
            Nome da estação
        """
        if month in [12, 1, 2]:
            return 'Verão'
        elif month in [3, 4, 5]:
            return 'Outono'
        elif month in [6, 7, 8]:
            return 'Inverno'
        else:
            return 'Primavera'
    
    @staticmethod
    def get_date_range(df: pd.DataFrame, date_column: str = 'data') -> Tuple[pd.Timestamp, pd.Timestamp]:
        """
        Retorna intervalo de datas no DataFrame.
        
        Args:
            df: DataFrame com coluna de data
            date_column: Nome da coluna de data
            
        Returns:
            Tupla (data_inicio, data_fim)
        """
        if df.empty or date_column not in df.columns:
            return None, None
        
        return df[date_column].min(), df[date_column].max()
    
    @staticmethod
    def count_days(start_date: pd.Timestamp, end_date: pd.Timestamp) -> int:
        """
        Conta número de dias entre duas datas.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Número de dias
        """
        if pd.isna(start_date) or pd.isna(end_date):
            return 0
        
        return (end_date - start_date).days + 1
    
    @staticmethod
    def get_last_n_days(df: pd.DataFrame, n: int, date_column: str = 'data') -> pd.DataFrame:
        """
        Filtra DataFrame para os últimos N dias.
        
        Args:
            df: DataFrame com coluna de data
            n: Número de dias
            date_column: Nome da coluna de data
            
        Returns:
            DataFrame filtrado
        """
        if df.empty or date_column not in df.columns:
            return df
        
        cutoff_date = df[date_column].max() - pd.Timedelta(days=n)
        return df[df[date_column] >= cutoff_date].copy()
    
    @staticmethod
    def filter_by_month(df: pd.DataFrame, month: int, date_column: str = 'data') -> pd.DataFrame:
        """
        Filtra DataFrame por mês.
        
        Args:
            df: DataFrame com coluna de data
            month: Número do mês (1-12)
            date_column: Nome da coluna de data
            
        Returns:
            DataFrame filtrado
        """
        if df.empty or date_column not in df.columns:
            return df
        
        return df[df[date_column].dt.month == month].copy()
    
    @staticmethod
    def filter_by_date_range(df: pd.DataFrame, 
                            start_date: datetime, 
                            end_date: datetime,
                            date_column: str = 'data') -> pd.DataFrame:
        """
        Filtra DataFrame por intervalo de datas.
        
        Args:
            df: DataFrame com coluna de data
            start_date: Data inicial
            end_date: Data final
            date_column: Nome da coluna de data
            
        Returns:
            DataFrame filtrado
        """
        if df.empty or date_column not in df.columns:
            return df
        
        mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
        return df[mask].copy()
