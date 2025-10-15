"""
Módulo de análise de correlações entre variáveis meteorológicas
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


class CorrelationAnalyzer:
    """Análises de correlações entre variáveis meteorológicas."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o analisador de correlações."""
        self.df = df.copy()
        
    def calculate_all_correlations(self) -> pd.DataFrame:
        """
        Calcula matriz de correlação entre todas as variáveis numéricas.
        """
        # Selecionar apenas colunas numéricas
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # Excluir colunas de data/tempo
        exclude_cols = ['ano', 'mes', 'dia', 'semana_ano', 'dia_semana', 'dia_ano']
        cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if len(cols) < 2:
            return pd.DataFrame()
        
        return self.df[cols].corr()
    
    def temperature_humidity_correlation(self) -> Dict:
        """
        Analisa correlação entre temperatura e umidade.
        """
        result = {}
        
        # Temperatura média x Umidade média
        if 'temperatura_media' in self.df.columns and 'umidade_media' in self.df.columns:
            temp = self.df['temperatura_media'].dropna()
            umid = self.df['umidade_media'].dropna()
            
            # Alinhar índices
            common_idx = temp.index.intersection(umid.index)
            temp = temp.loc[common_idx]
            umid = umid.loc[common_idx]
            
            if len(temp) > 0:
                corr, p_value = stats.pearsonr(temp, umid)
                result['temp_media_umid_media'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        # Temperatura máxima x Umidade mínima
        if 'temperatura_max' in self.df.columns and 'umidade_min' in self.df.columns:
            temp_max = self.df['temperatura_max'].dropna()
            umid_min = self.df['umidade_min'].dropna()
            
            common_idx = temp_max.index.intersection(umid_min.index)
            temp_max = temp_max.loc[common_idx]
            umid_min = umid_min.loc[common_idx]
            
            if len(temp_max) > 0:
                corr, p_value = stats.pearsonr(temp_max, umid_min)
                result['temp_max_umid_min'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        return result
    
    def pressure_rain_correlation(self) -> Dict:
        """
        Analisa correlação entre pressão atmosférica e chuva.
        """
        result = {}
        
        if 'pressao_atmosferica' not in self.df.columns:
            return result
        
        # Pressão x Chuva diária
        chuva_col = None
        for col in ['chuva_total', 'chuva_dia', 'precipitacao']:
            if col in self.df.columns:
                chuva_col = col
                break
        
        if chuva_col:
            pressao = self.df['pressao_atmosferica'].dropna()
            chuva = self.df[chuva_col].dropna()
            
            common_idx = pressao.index.intersection(chuva.index)
            pressao = pressao.loc[common_idx]
            chuva = chuva.loc[common_idx]
            
            if len(pressao) > 0:
                corr, p_value = stats.pearsonr(pressao, chuva)
                result['pressao_chuva'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
                
                # Análise de dias com chuva vs sem chuva
                dias_chuva = self.df[self.df[chuva_col] > 0]['pressao_atmosferica']
                dias_sem_chuva = self.df[self.df[chuva_col] == 0]['pressao_atmosferica']
                
                if len(dias_chuva) > 0 and len(dias_sem_chuva) > 0:
                    result['comparacao_pressao'] = {
                        'pressao_media_com_chuva': dias_chuva.mean(),
                        'pressao_media_sem_chuva': dias_sem_chuva.mean(),
                        'diferenca': dias_sem_chuva.mean() - dias_chuva.mean()
                    }
        
        return result
    
    def wind_temperature_correlation(self) -> Dict:
        """
        Analisa correlação entre vento e temperatura.
        """
        result = {}
        
        if 'velocidade_vento_media' in self.df.columns and 'temperatura_media' in self.df.columns:
            vento = self.df['velocidade_vento_media'].dropna()
            temp = self.df['temperatura_media'].dropna()
            
            common_idx = vento.index.intersection(temp.index)
            vento = vento.loc[common_idx]
            temp = temp.loc[common_idx]
            
            if len(vento) > 0:
                corr, p_value = stats.pearsonr(vento, temp)
                result['vento_temperatura'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        return result
    
    def solar_temperature_correlation(self) -> Dict:
        """
        Analisa correlação entre radiação solar e temperatura.
        """
        result = {}
        
        if 'radiacao_solar_total' in self.df.columns and 'temperatura_max' in self.df.columns:
            rad = self.df['radiacao_solar_total'].dropna()
            temp = self.df['temperatura_max'].dropna()
            
            common_idx = rad.index.intersection(temp.index)
            rad = rad.loc[common_idx]
            temp = temp.loc[common_idx]
            
            if len(rad) > 0:
                corr, p_value = stats.pearsonr(rad, temp)
                result['radiacao_temp_max'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        return result
    
    def humidity_evapotranspiration_correlation(self) -> Dict:
        """
        Analisa correlação entre umidade e evapotranspiração.
        """
        result = {}
        
        if 'umidade_media' in self.df.columns and 'evapotranspiracao' in self.df.columns:
            umid = self.df['umidade_media'].dropna()
            et = self.df['evapotranspiracao'].dropna()
            
            common_idx = umid.index.intersection(et.index)
            umid = umid.loc[common_idx]
            et = et.loc[common_idx]
            
            if len(umid) > 0:
                corr, p_value = stats.pearsonr(umid, et)
                result['umidade_et'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        return result
    
    def wind_humidity_correlation(self) -> Dict:
        """
        Analisa correlação entre vento e umidade.
        """
        result = {}
        
        if 'velocidade_vento_media' in self.df.columns and 'umidade_media' in self.df.columns:
            vento = self.df['velocidade_vento_media'].dropna()
            umid = self.df['umidade_media'].dropna()
            
            common_idx = vento.index.intersection(umid.index)
            vento = vento.loc[common_idx]
            umid = umid.loc[common_idx]
            
            if len(vento) > 0:
                corr, p_value = stats.pearsonr(vento, umid)
                result['vento_umidade'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        return result
    
    def uv_temperature_correlation(self) -> Dict:
        """
        Analisa correlação entre índice UV e temperatura.
        """
        result = {}
        
        if 'indice_uv' in self.df.columns and 'temperatura_max' in self.df.columns:
            uv = self.df['indice_uv'].dropna()
            temp = self.df['temperatura_max'].dropna()
            
            common_idx = uv.index.intersection(temp.index)
            uv = uv.loc[common_idx]
            temp = temp.loc[common_idx]
            
            if len(uv) > 0:
                corr, p_value = stats.pearsonr(uv, temp)
                result['uv_temp_max'] = {
                    'correlacao': corr,
                    'p_valor': p_value,
                    'significativo': p_value < 0.05,
                    'interpretacao': self._interpret_correlation(corr)
                }
        
        return result
    
    def get_strongest_correlations(self, threshold: float = 0.5) -> List[Tuple]:
        """
        Retorna as correlações mais fortes (acima do threshold).
        
        Args:
            threshold: Valor mínimo de correlação (em módulo)
        
        Returns:
            Lista de tuplas (var1, var2, correlacao)
        """
        corr_matrix = self.calculate_all_correlations()
        
        if corr_matrix.empty:
            return []
        
        # Extrair correlações únicas (triangular superior)
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                var1 = corr_matrix.columns[i]
                var2 = corr_matrix.columns[j]
                corr_val = corr_matrix.iloc[i, j]
                
                if not pd.isna(corr_val) and abs(corr_val) >= threshold:
                    correlations.append((var1, var2, corr_val))
        
        # Ordenar por valor absoluto de correlação (decrescente)
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        return correlations
    
    def get_comprehensive_report(self) -> Dict:
        """
        Gera relatório completo de todas as correlações analisadas.
        """
        return {
            'temperatura_umidade': self.temperature_humidity_correlation(),
            'pressao_chuva': self.pressure_rain_correlation(),
            'vento_temperatura': self.wind_temperature_correlation(),
            'radiacao_temperatura': self.solar_temperature_correlation(),
            'umidade_evapotranspiracao': self.humidity_evapotranspiration_correlation(),
            'vento_umidade': self.wind_humidity_correlation(),
            'uv_temperatura': self.uv_temperature_correlation(),
            'correlacoes_fortes': self.get_strongest_correlations(),
            'matriz_completa': self.calculate_all_correlations()
        }
    
    @staticmethod
    def _interpret_correlation(corr: float) -> str:
        """
        Interpreta o valor de correlação.
        """
        abs_corr = abs(corr)
        direction = 'positiva' if corr > 0 else 'negativa'
        
        if abs_corr < 0.3:
            strength = 'Fraca'
        elif abs_corr < 0.5:
            strength = 'Moderada'
        elif abs_corr < 0.7:
            strength = 'Forte'
        else:
            strength = 'Muito forte'
        
        return f'{strength} {direction}'
