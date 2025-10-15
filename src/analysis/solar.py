"""
Módulo de análise de radiação solar
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class SolarAnalyzer:
    """Análises especializadas para radiação solar."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o analisador de radiação solar."""
        self.df = df.copy()
        
    def calculate_statistics(self) -> Dict:
        """Calcula estatísticas completas de radiação solar."""
        stats = {}
        
        if 'radiacao_solar_total' in self.df.columns:
            rad_total = self.df['radiacao_solar_total']
            stats['radiacao_total'] = {
                'acumulada': rad_total.sum(),
                'media_diaria': rad_total.mean(),
                'maxima_dia': rad_total.max(),
                'desvio_padrao': rad_total.std()
            }
        
        if 'radiacao_solar_max' in self.df.columns:
            rad_max = self.df['radiacao_solar_max']
            stats['radiacao_maxima'] = {
                'absoluta': rad_max.max(),
                'media': rad_max.mean()
            }
        
        if 'indice_uv' in self.df.columns:
            uv = self.df['indice_uv']
            stats['indice_uv'] = {
                'maximo': uv.max(),
                'medio': uv.mean()
            }
        
        return stats
    
    def classify_uv_index(self) -> pd.DataFrame:
        """
        Classifica índice UV por risco.
        """
        if 'indice_uv' not in self.df.columns:
            return pd.DataFrame()
        
        def classificar(uv):
            if pd.isna(uv):
                return 'Indisponível'
            elif uv < 3:
                return 'Baixo'
            elif uv < 6:
                return 'Moderado'
            elif uv < 8:
                return 'Alto'
            elif uv < 11:
                return 'Muito Alto'
            else:
                return 'Extremo'
        
        df_class = self.df[['data', 'indice_uv']].copy()
        df_class['classificacao_uv'] = df_class['indice_uv'].apply(classificar)
        return df_class
    
    def get_uv_distribution(self) -> Dict:
        """Calcula distribuição por níveis de UV."""
        df_class = self.classify_uv_index()
        if df_class.empty:
            return {}
        
        dist = df_class['classificacao_uv'].value_counts().to_dict()
        total = len(df_class)
        dist_pct = {k: (v / total * 100) for k, v in dist.items()}
        
        return {'contagem': dist, 'porcentagem': dist_pct}
    
    def calculate_solar_energy_potential(self) -> Dict:
        """
        Calcula potencial de energia solar.
        Estimativa para sistemas fotovoltaicos.
        """
        if 'radiacao_solar_total' not in self.df.columns:
            return {}
        
        # Radiação solar total (soma diária em W/m²)
        # Converter para kWh/m²/dia: dividir por 1000 * (10min/60min) * registros
        # Simplificado: usar valor direto como Wh/m² e converter
        
        rad_total = self.df['radiacao_solar_total'].sum()
        media_diaria = self.df['radiacao_solar_total'].mean()
        
        # Estimativa de geração (assumindo eficiência de painel de 15%)
        eficiencia_painel = 0.15
        geracao_estimada_kwh = (rad_total / 1000) * eficiencia_painel
        
        # Dias com boa insolação (> 4 kWh/m²/dia equivalente)
        dias_boa_insolacao = len(self.df[self.df['radiacao_solar_total'] > 4000])
        
        return {
            'radiacao_total_periodo': rad_total,
            'radiacao_media_diaria': media_diaria,
            'energia_estimada_kwh': geracao_estimada_kwh,
            'dias_boa_insolacao': dias_boa_insolacao,
            'porcentagem_dias_bom_sol': (dias_boa_insolacao / len(self.df) * 100)
        }
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """Calcula resumo mensal de radiação solar."""
        if 'mes' not in self.df.columns:
            return pd.DataFrame()
        
        agg_dict = {}
        if 'radiacao_solar_total' in self.df.columns:
            agg_dict['radiacao_solar_total'] = ['sum', 'mean', 'max']
        if 'indice_uv' in self.df.columns:
            agg_dict['indice_uv'] = ['max', 'mean']
        
        if not agg_dict:
            return pd.DataFrame()
        
        monthly = self.df.groupby(['ano', 'mes', 'mes_nome']).agg(agg_dict).reset_index()
        monthly.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col 
                          for col in monthly.columns]
        
        return monthly
    
    def calculate_agricultural_impact(self) -> Dict:
        """
        Analisa impacto da radiação solar na agricultura.
        """
        if 'radiacao_solar_total' not in self.df.columns:
            return {}
        
        rad = self.df['radiacao_solar_total']
        
        # Classificação simplificada
        dias_baixa_rad = len(rad[rad < 2000])  # < 2000 W/m²
        dias_adequada = len(rad[(rad >= 2000) & (rad <= 6000)])
        dias_alta_rad = len(rad[rad > 6000])
        
        total = len(rad)
        
        return {
            'dias_radiacao_baixa': dias_baixa_rad,
            'dias_radiacao_adequada': dias_adequada,
            'dias_radiacao_alta': dias_alta_rad,
            'porcentagem_adequada': (dias_adequada / total * 100),
            'status': 'IDEAL' if (dias_adequada / total) > 0.6 else 'VARIÁVEL'
        }
