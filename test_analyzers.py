#!/usr/bin/env python3
"""
Script de teste para validar todos os analyzers
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.analysis import (
    RainfallAnalyzer,
    TemperatureAnalyzer,
    HumidityAnalyzer,
    WindAnalyzer,
    SolarAnalyzer,
    CorrelationAnalyzer
)


def print_section(title: str):
    """Imprime separador de seção."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_rainfall_analyzer(df):
    """Testa o RainfallAnalyzer."""
    print_section("RAINFALL ANALYZER")
    
    analyzer = RainfallAnalyzer(df)
    
    # Estatísticas básicas
    stats = analyzer.calculate_statistics()
    print("\n📊 Estatísticas de Chuva:")
    if stats:
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    # Períodos secos
    dry_spells = analyzer.calculate_dry_spells()
    print(f"\n🏜️  Períodos secos detectados: {len(dry_spells)}")
    if len(dry_spells) > 0:
        longest = max(dry_spells, key=lambda x: x['duracao'])
        print(f"  Período mais longo: {longest['duracao']} dias ({longest['inicio']} a {longest['fim']})")
    
    # Distribuição de intensidade
    dist = analyzer.get_distribution_by_intensity()
    if dist and 'contagem' in dist:
        print("\n💧 Distribuição por Intensidade:")
        for intensity, count in dist['contagem'].items():
            pct = dist['porcentagem'][intensity]
            print(f"  {intensity}: {count} dias ({pct:.1f}%)")
    else:
        print("\n💧 Sem dados de distribuição de intensidade")


def test_temperature_analyzer(df):
    """Testa o TemperatureAnalyzer."""
    print_section("TEMPERATURE ANALYZER")
    
    analyzer = TemperatureAnalyzer(df)
    
    # Estatísticas
    stats = analyzer.calculate_statistics()
    print("\n🌡️  Estatísticas de Temperatura:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Ondas de calor
    heat_waves = analyzer.detect_heat_waves()
    print(f"\n🔥 Ondas de calor detectadas: {len(heat_waves)}")
    
    # Períodos de frio
    cold_spells = analyzer.detect_cold_spells()
    print(f"❄️  Períodos de frio detectados: {len(cold_spells)}")
    
    # Distribuição por zona térmica
    dist = analyzer.get_thermal_distribution()
    if dist and 'contagem' in dist:
        print("\n🌡️  Distribuição por Zona Térmica:")
        for zone, count in dist['contagem'].items():
            pct = dist['porcentagem'][zone]
            print(f"  {zone}: {count} dias ({pct:.1f}%)")


def test_humidity_analyzer(df):
    """Testa o HumidityAnalyzer."""
    print_section("HUMIDITY ANALYZER")
    
    analyzer = HumidityAnalyzer(df)
    
    # Estatísticas
    stats = analyzer.calculate_statistics()
    print("\n💨 Estatísticas de Umidade:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Impacto agrícola
    impact = analyzer.calculate_agricultural_impact()
    print("\n🌾 Impacto Agrícola:")
    for key, value in impact.items():
        print(f"  {key}: {value}")


def test_wind_analyzer(df):
    """Testa o WindAnalyzer."""
    print_section("WIND ANALYZER")
    
    analyzer = WindAnalyzer(df)
    
    # Estatísticas
    stats = analyzer.calculate_statistics()
    print("\n💨 Estatísticas de Vento:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Adequação para aplicação
    suitability = analyzer.calculate_application_suitability()
    print("\n🚜 Adequação para Aplicação de Defensivos:")
    for key, value in suitability.items():
        print(f"  {key}: {value}")


def test_solar_analyzer(df):
    """Testa o SolarAnalyzer."""
    print_section("SOLAR ANALYZER")
    
    analyzer = SolarAnalyzer(df)
    
    # Estatísticas
    stats = analyzer.calculate_statistics()
    print("\n☀️  Estatísticas de Radiação Solar:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Potencial energético
    energy = analyzer.calculate_solar_energy_potential()
    print("\n⚡ Potencial de Energia Solar:")
    for key, value in energy.items():
        print(f"  {key}: {value}")
    
    # Impacto agrícola
    impact = analyzer.calculate_agricultural_impact()
    print("\n🌾 Impacto Agrícola:")
    for key, value in impact.items():
        print(f"  {key}: {value}")


def test_correlation_analyzer(df):
    """Testa o CorrelationAnalyzer."""
    print_section("CORRELATION ANALYZER")
    
    analyzer = CorrelationAnalyzer(df)
    
    # Correlações mais fortes
    strong = analyzer.get_strongest_correlations(threshold=0.5)
    print("\n🔗 Correlações Fortes (|r| > 0.5):")
    for var1, var2, corr in strong[:10]:  # Top 10
        print(f"  {var1} × {var2}: {corr:.3f}")
    
    # Temperatura x Umidade
    temp_umid = analyzer.temperature_humidity_correlation()
    if temp_umid:
        print("\n🌡️💧 Temperatura × Umidade:")
        for key, value in temp_umid.items():
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
    
    # Pressão x Chuva
    press_rain = analyzer.pressure_rain_correlation()
    if press_rain:
        print("\n🌧️  Pressão × Chuva:")
        for key, value in press_rain.items():
            print(f"\n  {key}:")
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {value}")


def main():
    """Função principal."""
    print("🚀 Iniciando teste dos analyzers...")
    
    # 1. Carregar dados
    print_section("CARREGAMENTO DE DADOS")
    loader = DataLoader(config.DATA_DIR)
    df_raw = loader.load_all_csvs()
    print(f"✅ Carregados {len(df_raw):,} registros de {len(df_raw.columns)} variáveis")
    
    # 2. Processar dados
    print_section("PROCESSAMENTO DE DADOS")
    processor = DataProcessor()
    df_daily = processor.aggregate_to_daily(df_raw)
    print(f"✅ Agregados para {len(df_daily):,} dias")
    
    # 3. Testar analyzers
    test_rainfall_analyzer(df_daily)
    test_temperature_analyzer(df_daily)
    test_humidity_analyzer(df_daily)
    test_wind_analyzer(df_daily)
    test_solar_analyzer(df_daily)
    test_correlation_analyzer(df_daily)
    
    print_section("TESTE CONCLUÍDO COM SUCESSO")
    print("✅ Todos os analyzers foram validados!")


if __name__ == "__main__":
    main()
