"""
Módulo de análise de umidade
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class HumidityAnalyzer:
    """Análises especializadas para dados de umidade."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o analisador de umidade."""
        self.df = df.copy()
        
    def calculate_statistics(self) -> Dict:
        """Calcula estatísticas completas de umidade."""
        stats = {}
        
        if 'umidade_max' in self.df.columns:
            stats['umidade_max'] = {
                'absoluta': self.df['umidade_max'].max(),
                'media': self.df['umidade_max'].mean()
            }
        
        if 'umidade_min' in self.df.columns:
            stats['umidade_min'] = {
                'absoluta': self.df['umidade_min'].min(),
                'media': self.df['umidade_min'].mean()
            }
        
        if 'umidade_media' in self.df.columns:
            umid = self.df['umidade_media']
            stats['umidade_media'] = {
                'geral': umid.mean(),
                'desvio_padrao': umid.std(),
                'mediana': umid.median()
            }
        
        return stats
    
    def classify_humidity_levels(self) -> pd.DataFrame:
        """Classifica umidade em níveis."""
        if 'umidade_media' not in self.df.columns:
            return pd.DataFrame()
        
        def classificar(umid):
            if umid < 30:
                return 'Muito Baixa'
            elif umid < 50:
                return 'Baixa'
            elif umid < 70:
                return 'Adequada'
            elif umid < 85:
                return 'Alta'
            else:
                return 'Muito Alta'
        
        df_class = self.df[['data', 'umidade_media']].copy()
        df_class['classificacao'] = df_class['umidade_media'].apply(classificar)
        return df_class
    
    def get_humidity_distribution(self) -> Dict:
        """Calcula distribuição por níveis de umidade."""
        df_class = self.classify_humidity_levels()
        if df_class.empty:
            return {}
        
        dist = df_class['classificacao'].value_counts().to_dict()
        total = len(df_class)
        dist_pct = {k: (v / total * 100) for k, v in dist.items()}
        
        return {'contagem': dist, 'porcentagem': dist_pct}
    
    def calculate_agricultural_impact(self) -> Dict:
        """
        Analisa impacto agrícola da umidade.
        - < 50%: Baixa (risco de stress hídrico)
        - 70-90%: Ideal para a maioria das culturas
        - > 95%: Risco de doenças fúngicas
        """
        if 'umidade_media' not in self.df.columns:
            return {}
        
        umid = self.df['umidade_media']
        total = len(umid)
        
        dias_baixa = len(umid[umid < 50])
        dias_ideal = len(umid[(umid >= 70) & (umid <= 90)])
        dias_alta = len(umid[umid > 95])
        
        return {
            'dias_umidade_baixa': dias_baixa,
            'dias_umidade_ideal': dias_ideal,
            'dias_umidade_excessiva': dias_alta,
            'porcentagem_ideal': (dias_ideal / total * 100),
            'status': 'IDEAL' if (dias_ideal / total) > 0.5 else 'ATENÇÃO'
        }
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """Calcula resumo mensal de umidade."""
        if 'mes' not in self.df.columns:
            return pd.DataFrame()
        
        agg_dict = {}
        if 'umidade_max' in self.df.columns:
            agg_dict['umidade_max'] = 'max'
        if 'umidade_min' in self.df.columns:
            agg_dict['umidade_min'] = 'min'
        if 'umidade_media' in self.df.columns:
            agg_dict['umidade_media'] = 'mean'
        
        if not agg_dict:
            return pd.DataFrame()
        
        return self.df.groupby(['ano', 'mes', 'mes_nome']).agg(agg_dict).reset_index()
