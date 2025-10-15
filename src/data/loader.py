"""
Módulo para carregar dados CSV da estação meteorológica
"""

import pandas as pd
import glob
from pathlib import Path
from typing import List, Optional
import warnings

from config import CSV_CONFIG, DATA_DIR, COLUMN_MAPPING

warnings.filterwarnings('ignore')


class DataLoader:
    """Carrega dados CSV da estação meteorológica."""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        """
        Inicializa o carregador de dados.
        
        Args:
            data_dir: Diretório contendo os arquivos CSV
        """
        self.data_dir = Path(data_dir)
        self.csv_config = CSV_CONFIG
        
    def detect_encoding(self, file_path: Path) -> str:
        """
        Detecta o encoding do arquivo CSV.
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            Nome do encoding detectado
        """
        for encoding in self.csv_config['encodings']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except:
                continue
        return 'utf-8'
    
    def find_csv_files(self) -> List[Path]:
        """
        Encontra todos os arquivos CSV no diretório de dados.
        
        Returns:
            Lista de caminhos para arquivos CSV
        """
        csv_pattern = str(self.data_dir / '*.csv')
        files = sorted([Path(f) for f in glob.glob(csv_pattern)])
        return files
    
    def load_single_csv(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Carrega um único arquivo CSV.
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            DataFrame com os dados ou None se houver erro
        """
        print(f"📊 Carregando: {file_path.name}...", end=' ')
        
        try:
            encoding = self.detect_encoding(file_path)
            
            df = pd.read_csv(
                file_path,
                sep=self.csv_config['separator'],
                decimal=self.csv_config['decimal'],
                encoding=encoding,
                on_bad_lines='skip',
                low_memory=False
            )
            
            if df is None or len(df) == 0:
                print("❌ Arquivo vazio")
                return None
            
            # Converter data ANTES de renomear
            if 'Data (America/Sao_Paulo)' in df.columns:
                df['data_temp'] = pd.to_datetime(
                    df['Data (America/Sao_Paulo)'],
                    format=self.csv_config['date_format'],
                    errors='coerce'
                )
                
                # Remover linhas com data inválida
                df = df.dropna(subset=['data_temp'])
                
                if len(df) == 0:
                    print("❌ Sem dados válidos após conversão de data")
                    return None
                
                # Renomear colunas usando o mapeamento
                df = df.rename(columns=COLUMN_MAPPING)
                
                # Renomear data_temp para data (evita duplicação)
                df['data'] = df['data_temp']
                df = df.drop(columns=['data_temp'])
            else:
                print("❌ Coluna de data não encontrada")
                return None
            
            # Converter colunas numéricas
            numeric_columns = [
                'temperatura', 'temp_interior', 'sensacao_termica',
                'ponto_orvalho', 'indice_calor', 'umidade', 'umidade_interior',
                'vento_velocidade', 'vento_rajada', 'vento_direcao',
                'pressao', 'chuva_acumulada', 'chuva_intensidade',
                'radiacao_solar', 'indice_uv'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"✅ {len(df)} registros")
            return df
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return None
    
    def load_all_csvs(self) -> pd.DataFrame:
        """
        Carrega todos os arquivos CSV do diretório.
        
        Returns:
            DataFrame consolidado com todos os dados
        """
        print("\n🌧️ CARREGANDO DADOS DA ESTAÇÃO METEOROLÓGICA")
        print("=" * 70)
        
        csv_files = self.find_csv_files()
        
        if not csv_files:
            print(f"❌ Nenhum arquivo CSV encontrado em {self.data_dir}")
            return pd.DataFrame()
        
        print(f"\n📂 Encontrados {len(csv_files)} arquivos CSV:")
        for file in csv_files:
            print(f"   • {file.name}")
        
        print(f"\n{'=' * 70}")
        print("🔄 PROCESSANDO ARQUIVOS")
        print("=" * 70)
        
        # Carregar todos os arquivos
        dataframes = []
        for file_path in csv_files:
            df = self.load_single_csv(file_path)
            if df is not None and len(df) > 0:
                dataframes.append(df)
        
        if not dataframes:
            print("\n❌ Nenhum dado foi carregado com sucesso")
            return pd.DataFrame()
        
        # Concatenar todos os dados
        print(f"\n{'=' * 70}")
        print("🔗 CONSOLIDANDO DADOS")
        print("=" * 70)
        
        df_completo = pd.concat(dataframes, ignore_index=True)
        df_completo = df_completo.sort_values('data').reset_index(drop=True)
        
        # Remover duplicatas
        df_completo = df_completo.drop_duplicates(subset=['data'], keep='last')
        
        print(f"✅ Total de registros: {len(df_completo):,}")
        print(f"📅 Período: {df_completo['data'].min().strftime('%d/%m/%Y')} até {df_completo['data'].max().strftime('%d/%m/%Y')}")
        
        # Estatísticas rápidas
        print(f"\n📊 ESTATÍSTICAS RÁPIDAS:")
        if 'temperatura' in df_completo.columns:
            print(f"   🌡️  Temperatura: {df_completo['temperatura'].min():.1f}°C a {df_completo['temperatura'].max():.1f}°C")
        if 'umidade' in df_completo.columns:
            print(f"   💧 Umidade: {df_completo['umidade'].min():.0f}% a {df_completo['umidade'].max():.0f}%")
        if 'chuva_acumulada' in df_completo.columns:
            print(f"   🌧️  Chuva: {df_completo['chuva_acumulada'].max():.1f}mm (máx diária)")
        
        print()
        return df_completo
    
    def load_latest_data(self, days: int = 30) -> pd.DataFrame:
        """
        Carrega apenas os dados mais recentes.
        
        Args:
            days: Número de dias para carregar
            
        Returns:
            DataFrame com dados dos últimos N dias
        """
        df = self.load_all_csvs()
        
        if df.empty:
            return df
        
        cutoff_date = df['data'].max() - pd.Timedelta(days=days)
        df_recent = df[df['data'] >= cutoff_date].copy()
        
        print(f"📅 Dados carregados: últimos {days} dias ({len(df_recent):,} registros)")
        
        return df_recent
