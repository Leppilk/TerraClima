"""
Script de teste para validar o processamento de dados
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.data.aggregator import DataAggregator


def main():
    """Testa o pipeline completo de processamento."""
    
    print("\n" + "="*70)
    print("🧪 TESTE DO SISTEMA DE PROCESSAMENTO TerraClima")
    print("="*70)
    
    # 1. Carregar dados
    print("\n📥 ETAPA 1: CARREGAMENTO DE DADOS")
    print("-" * 70)
    loader = DataLoader()
    df_raw = loader.load_all_csvs()
    
    if df_raw.empty:
        print("❌ Erro: Nenhum dado foi carregado")
        return 1
    
    print(f"\n✅ Dados carregados com sucesso!")
    print(f"   • Registros: {len(df_raw):,}")
    print(f"   • Colunas: {len(df_raw.columns)}")
    print(f"   • Período: {df_raw['data'].min()} até {df_raw['data'].max()}")
    
    # 2. Processar dados
    print("\n" + "="*70)
    print("🔄 ETAPA 2: PROCESSAMENTO DE DADOS")
    print("-" * 70)
    processor = DataProcessor()
    df_daily = processor.process_full_pipeline(df_raw)
    
    if df_daily.empty:
        print("❌ Erro: Falha no processamento")
        return 1
    
    print(f"\n✅ Processamento concluído!")
    print(f"   • Dias processados: {len(df_daily)}")
    print(f"   • Variáveis geradas: {len(df_daily.columns)}")
    
    # Mostrar algumas colunas importantes
    print(f"\n📊 Colunas disponíveis (primeiras 20):")
    for i, col in enumerate(df_daily.columns[:20], 1):
        print(f"   {i:2d}. {col}")
    if len(df_daily.columns) > 20:
        print(f"   ... e mais {len(df_daily.columns) - 20} colunas")
    
    # 3. Agregações
    print("\n" + "="*70)
    print("📊 ETAPA 3: AGREGAÇÕES TEMPORAIS")
    print("-" * 70)
    aggregator = DataAggregator()
    
    # Agregação mensal
    df_monthly = aggregator.aggregate_monthly(df_daily)
    print(f"\n✅ Agregação mensal: {len(df_monthly)} meses")
    
    # Estatísticas gerais
    stats = aggregator.get_statistics_summary(df_daily)
    
    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    
    if 'temperatura' in stats:
        print(f"\n🌡️  TEMPERATURA:")
        print(f"   • Máxima absoluta: {stats['temperatura']['max_absoluta']:.1f}°C")
        print(f"   • Mínima absoluta: {stats['temperatura']['min_absoluta']:.1f}°C")
        print(f"   • Média: {stats['temperatura']['media']:.1f}°C")
    
    if 'chuva' in stats:
        print(f"\n🌧️  CHUVA:")
        print(f"   • Total: {stats['chuva']['total']:.1f}mm")
        print(f"   • Máxima em 1 dia: {stats['chuva']['max_dia']:.1f}mm")
        print(f"   • Dias com chuva: {stats['chuva']['dias_com_chuva']}")
        print(f"   • Dias sem chuva: {stats['chuva']['dias_sem_chuva']}")
    
    if 'umidade' in stats:
        print(f"\n💧 UMIDADE:")
        print(f"   • Máxima: {stats['umidade']['max']:.0f}%")
        print(f"   • Mínima: {stats['umidade']['min']:.0f}%")
        print(f"   • Média: {stats['umidade']['media']:.1f}%")
    
    if 'vento' in stats:
        print(f"\n💨 VENTO:")
        print(f"   • Rajada máxima: {stats['vento']['rajada_maxima']:.1f} m/s ({stats['vento']['rajada_maxima']*3.6:.1f} km/h)")
    
    # Períodos de seca
    dry_spell = aggregator.calculate_dry_spell(df_daily)
    if dry_spell:
        print(f"\n🏜️  MAIOR PERÍODO SECO:")
        print(f"   • Duração: {dry_spell['periodo_max']} dias consecutivos")
        if dry_spell['data_inicio']:
            print(f"   • De {dry_spell['data_inicio'].strftime('%d/%m/%Y')} até {dry_spell['data_fim'].strftime('%d/%m/%Y')}")
    
    # Períodos chuvosos
    rainy_spell = aggregator.calculate_rainy_spell(df_daily)
    if rainy_spell:
        print(f"\n🌧️  MAIOR PERÍODO CHUVOSO:")
        print(f"   • Duração: {rainy_spell['periodo_max']} dias consecutivos")
    
    # 4. Salvar amostra
    print("\n" + "="*70)
    print("💾 ETAPA 4: SALVANDO AMOSTRA DOS DADOS")
    print("-" * 70)
    
    output_file = Path('output/teste_dados_diarios.csv')
    df_daily.to_csv(output_file, sep=';', decimal=',', index=False, encoding='utf-8-sig')
    print(f"✅ Arquivo salvo: {output_file}")
    
    # Mostrar primeiras linhas
    print(f"\n📋 AMOSTRA DOS DADOS (5 primeiras linhas):")
    # Usar colunas que existem de fato
    cols_to_show = []
    if 'data' in df_daily.columns:
        cols_to_show.append('data')
    if 'temperatura_max' in df_daily.columns:
        cols_to_show.append('temperatura_max')
    if 'temperatura_min' in df_daily.columns:
        cols_to_show.append('temperatura_min')
    if 'umidade_media' in df_daily.columns:
        cols_to_show.append('umidade_media')
    if 'chuva_acumulada' in df_daily.columns:
        cols_to_show.append('chuva_acumulada')
    
    if cols_to_show:
        print(df_daily[cols_to_show].head().to_string(index=False))
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\n💡 Próximos passos:")
    print("   1. Os dados foram processados corretamente")
    print("   2. Agora podemos criar os módulos de análise")
    print("   3. E depois desenvolver o dashboard web")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
