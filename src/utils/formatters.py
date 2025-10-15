"""
Formatadores de dados para exibição
"""

import pandas as pd
from typing import Union


class Formatters:
    """Formatadores de dados para exibição."""
    
    @staticmethod
    def format_number(value: float, decimals: int = 1) -> str:
        """
        Formata número com casas decimais.
        
        Args:
            value: Valor numérico
            decimals: Número de casas decimais
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.{decimals}f}"
    
    @staticmethod
    def format_temperature(value: float) -> str:
        """
        Formata temperatura.
        
        Args:
            value: Temperatura em °C
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.1f}°C"
    
    @staticmethod
    def format_humidity(value: float) -> str:
        """
        Formata umidade.
        
        Args:
            value: Umidade em %
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.0f}%"
    
    @staticmethod
    def format_rainfall(value: float) -> str:
        """
        Formata precipitação.
        
        Args:
            value: Chuva em mm
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.1f}mm"
    
    @staticmethod
    def format_wind_speed(value: float) -> str:
        """
        Formata velocidade do vento.
        
        Args:
            value: Velocidade em m/s
            
        Returns:
            String formatada (m/s e km/h)
        """
        if pd.isna(value):
            return '-'
        kmh = value * 3.6
        return f"{value:.1f} m/s ({kmh:.1f} km/h)"
    
    @staticmethod
    def format_pressure(value: float) -> str:
        """
        Formata pressão atmosférica.
        
        Args:
            value: Pressão em hPa
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.1f} hPa"
    
    @staticmethod
    def format_solar_radiation(value: float) -> str:
        """
        Formata radiação solar.
        
        Args:
            value: Radiação em W/m²
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.0f} W/m²"
    
    @staticmethod
    def format_energy(value: float) -> str:
        """
        Formata energia solar.
        
        Args:
            value: Energia em Wh/m²
            
        Returns:
            String formatada (kWh/m²)
        """
        if pd.isna(value):
            return '-'
        kwh = value / 1000
        return f"{kwh:.2f} kWh/m²"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        Formata porcentagem.
        
        Args:
            value: Valor em %
            decimals: Casas decimais
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_large_number(value: Union[int, float]) -> str:
        """
        Formata números grandes com separadores.
        
        Args:
            value: Valor numérico
            
        Returns:
            String formatada
        """
        if pd.isna(value):
            return '-'
        return f"{value:,.0f}".replace(',', '.')
    
    @staticmethod
    def format_wind_direction(degrees: float) -> str:
        """
        Converte graus para direção cardinal.
        
        Args:
            degrees: Direção em graus (0-360)
            
        Returns:
            Direção cardinal (N, NE, E, SE, S, SW, W, NW)
        """
        if pd.isna(degrees):
            return '-'
        
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        
        idx = int((degrees + 11.25) / 22.5) % 16
        return directions[idx]
    
    @staticmethod
    def format_uv_index(value: float) -> str:
        """
        Formata índice UV com classificação.
        
        Args:
            value: Índice UV
            
        Returns:
            String formatada com classificação
        """
        if pd.isna(value):
            return '-'
        
        if value < 3:
            risk = 'Baixo'
        elif value < 6:
            risk = 'Moderado'
        elif value < 8:
            risk = 'Alto'
        elif value < 11:
            risk = 'Muito Alto'
        else:
            risk = 'Extremo'
        
        return f"{value:.1f} ({risk})"
