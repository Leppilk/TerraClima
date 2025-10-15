"""
Módulo de análise de vento
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class WindAnalyzer:
    """Análises especializadas para dados de vento."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o analisador de vento."""
        self.df = df.copy()
        
    def calculate_statistics(self) -> Dict:
        """Calcula estatísticas completas de vento."""
        stats = {}
        
        if 'vento_rajada' in self.df.columns:
            rajada = self.df['vento_rajada']
            stats['rajada'] = {
                'maxima': rajada.max(),
                'media': rajada.mean(),
                'data_maxima': self.df.loc[rajada.idxmax(), 'data'] if not rajada.empty else None
            }
        
        if 'vento_velocidade_media' in self.df.columns:
            vel = self.df['vento_velocidade_media']
            stats['velocidade'] = {
                'maxima': vel.max(),
                'media': vel.mean(),
                'desvio_padrao': vel.std()
            }
        
        return stats
    
    def classify_wind_intensity(self) -> pd.DataFrame:
        """
        Classifica intensidade do vento (Escala Beaufort simplificada).
        """
        if 'vento_velocidade_media' not in self.df.columns:
            return pd.DataFrame()
        
        def classificar(vel_ms):
            """Velocidade em m/s"""
            if vel_ms < 1.6:
                return 'Calmo'
            elif vel_ms < 5.5:
                return 'Brisa Leve'
            elif vel_ms < 8.0:
                return 'Brisa Moderada'
            elif vel_ms < 10.8:
                return 'Brisa Forte'
            elif vel_ms < 13.9:
                return 'Vento Moderado'
            else:
                return 'Vento Forte'
        
        df_class = self.df[['data', 'vento_velocidade_media']].copy()
        df_class['classificacao'] = df_class['vento_velocidade_media'].apply(classificar)
        return df_class
    
    def get_wind_rose_data(self) -> Dict:
        """
        Prepara dados para rosa dos ventos.
        Retorna frequência por direção.
        """
        if 'vento_direcao' not in self.df.columns:
            return {}
        
        def get_cardinal_direction(degrees):
            """Converte graus para direção cardinal."""
            if pd.isna(degrees):
                return None
            
            directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                         'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
            idx = int((degrees + 11.25) / 22.5) % 16
            return directions[idx]
        
        df_dir = self.df[['vento_direcao']].copy()
        df_dir['direcao_cardinal'] = df_dir['vento_direcao'].apply(get_cardinal_direction)
        
        freq = df_dir['direcao_cardinal'].value_counts().to_dict()
        total = len(df_dir.dropna())
        freq_pct = {k: (v / total * 100) for k, v in freq.items() if k is not None}
        
        return {
            'frequencia': freq,
            'porcentagem': freq_pct,
            'direcao_predominante': max(freq_pct, key=freq_pct.get) if freq_pct else None
        }
    
    def detect_strong_wind_days(self, threshold: float = 10.0) -> List[Dict]:
        """
        Detecta dias com ventos fortes (rajadas acima do limiar).
        
        Args:
            threshold: Velocidade mínima em m/s (padrão: 10 m/s = 36 km/h)
        """
        if 'vento_rajada' not in self.df.columns:
            return []
        
        strong_days = self.df[self.df['vento_rajada'] >= threshold].copy()
        strong_days = strong_days.sort_values('vento_rajada', ascending=False)
        
        return strong_days[['data', 'vento_rajada', 'vento_velocidade_media']].to_dict('records')
    
    def calculate_application_suitability(self) -> Dict:
        """
        Analisa adequabilidade para aplicação de defensivos.
        Ideal: vento entre 3-10 km/h (0.8-2.8 m/s)
        """
        if 'vento_velocidade_media' not in self.df.columns:
            return {}
        
        vel = self.df['vento_velocidade_media']
        total = len(vel)
        
        # Converter limites para m/s
        ideal_min = 0.8  # 3 km/h
        ideal_max = 2.8  # 10 km/h
        
        dias_ideais = len(vel[(vel >= ideal_min) & (vel <= ideal_max)])
        dias_calmo = len(vel[vel < ideal_min])
        dias_ventoso = len(vel[vel > ideal_max])
        
        # Últimos 7 dias
        recent = vel.tail(7)
        dias_ideais_recente = len(recent[(recent >= ideal_min) & (recent <= ideal_max)])
        
        return {
            'dias_ideais_aplicacao': dias_ideais,
            'dias_muito_calmo': dias_calmo,
            'dias_muito_ventoso': dias_ventoso,
            'porcentagem_ideal': (dias_ideais / total * 100),
            'dias_ideais_ultima_semana': dias_ideais_recente,
            'status': 'FAVORÁVEL' if dias_ideais_recente >= 3 else 'ATENÇÃO'
        }
