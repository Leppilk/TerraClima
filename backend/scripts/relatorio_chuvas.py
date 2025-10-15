import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime
import os
import sys

# Configuração para português
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Meses abreviados em português
MESES_PT = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}


def carregar_dados(arquivo_csv):
    """Carrega e prepara os dados de chuva."""
    df = pd.read_csv(arquivo_csv, sep=';', decimal=',', parse_dates=['data'])
    df['mes'] = df['data'].dt.month
    df['mes_nome'] = df['mes'].map(MESES_PT)
    df['dia_mes'] = df['data'].dt.day
    df['ano'] = df['data'].dt.year
    df['semana'] = df['data'].dt.isocalendar().week
    
    # Classifica dias por intensidade de chuva
    def classificar_chuva(mm):
        if mm == 0:
            return 'Sem chuva'
        elif mm < 5:
            return 'Fraca (< 5mm)'
        elif mm < 15:
            return 'Moderada (5-15mm)'
        elif mm < 25:
            return 'Forte (15-25mm)'
        else:
            return 'Muito Forte (>25mm)'
    
    df['intensidade'] = df['chuva_total'].apply(classificar_chuva)
    
    return df


def calcular_estatisticas(df):
    """Calcula estatísticas importantes para agricultura."""
    total_dias = len(df)
    dias_com_chuva = len(df[df['chuva_total'] > 0])
    dias_sem_chuva = total_dias - dias_com_chuva
    
    # Maior período sem chuva (importante para planejamento de irrigação)
    df['choveu'] = df['chuva_total'] > 0
    periodo_seco_atual = 0
    periodo_seco_max = 0
    data_inicio_seca = None
    data_fim_seca = None
    inicio_temp = None
    
    for idx, row in df.iterrows():
        if not row['choveu']:
            if periodo_seco_atual == 0:
                inicio_temp = row['data']
            periodo_seco_atual += 1
            if periodo_seco_atual > periodo_seco_max:
                periodo_seco_max = periodo_seco_atual
                data_inicio_seca = inicio_temp
                data_fim_seca = row['data']
        else:
            periodo_seco_atual = 0
            inicio_temp = None
    
    # Maior sequência de dias com chuva
    periodo_chuvoso_atual = 0
    periodo_chuvoso_max = 0
    
    for idx, row in df.iterrows():
        if row['choveu']:
            periodo_chuvoso_atual += 1
            if periodo_chuvoso_atual > periodo_chuvoso_max:
                periodo_chuvoso_max = periodo_chuvoso_atual
        else:
            periodo_chuvoso_atual = 0
    
    # Estatísticas mensais
    mensal = df.groupby('mes').agg({
        'chuva_total': ['sum', 'mean', 'max', 'count'],
        'choveu': 'sum'
    }).round(2)
    
    mes_mais_chuvoso = mensal[('chuva_total', 'sum')].idxmax()
    mes_menos_chuvoso = mensal[('chuva_total', 'sum')].idxmin()
    
    # Dia mais chuvoso
    dia_max_chuva = df.loc[df['chuva_total'].idxmax()]
    
    stats = {
        'total_dias': total_dias,
        'dias_com_chuva': dias_com_chuva,
        'dias_sem_chuva': dias_sem_chuva,
        'porcentagem_dias_chuva': (dias_com_chuva / total_dias * 100),
        'chuva_total': df['chuva_total'].sum(),
        'chuva_media_dia': df['chuva_total'].mean(),
        'chuva_media_dia_chuvoso': df[df['chuva_total'] > 0]['chuva_total'].mean(),
        'chuva_maxima_dia': df['chuva_total'].max(),
        'data_max_chuva': dia_max_chuva['data'],
        'periodo_seco_max': periodo_seco_max,
        'data_inicio_seca': data_inicio_seca,
        'data_fim_seca': data_fim_seca,
        'periodo_chuvoso_max': periodo_chuvoso_max,
        'mes_mais_chuvoso': MESES_PT[mes_mais_chuvoso],
        'chuva_mes_mais_chuvoso': mensal.loc[mes_mais_chuvoso, ('chuva_total', 'sum')],
        'mes_menos_chuvoso': MESES_PT[mes_menos_chuvoso],
        'chuva_mes_menos_chuvoso': mensal.loc[mes_menos_chuvoso, ('chuva_total', 'sum')],
        'mensal': mensal
    }
    
    return stats


def criar_relatorio_a2_paisagem(df, stats, output_dir):
    """
    Cria relatório em formato A2 paisagem (594x420mm = 23.39x16.54 polegadas)
    Layout: 2/3 da página com gráficos (2 por linha) + 1/3 com dados em caixas coloridas
    """
    
    # A2 paisagem: 594mm x 420mm = 23.39" x 16.54"
    fig = plt.figure(figsize=(23.39, 16.54))
    
    # Layout: 2/3 esquerda para gráficos (4 gráficos 2x2), 1/3 direita para dados
    # GridSpec: 4 linhas x 3 colunas
    gs = GridSpec(5, 3, figure=fig, 
                  hspace=0.75, wspace=0.3,
                  left=0.04, right=0.97, top=0.97, bottom=0.05,
                  width_ratios=[1, 1, 0.7])  # 2 colunas para gráficos, 1 para dados
    
    # Cores das caixas de dados
    cores_caixas = {
        'periodo': '#E3F2FD',      # Azul claro
        'totais': '#E8F5E9',       # Verde claro
        'recordes': '#FFF3E0',     # Laranja claro
        'secos': '#FCE4EC'         # Rosa claro
    }
    
    # ============= GRÁFICO 1: Distribuição Mensal (topo esquerdo) =============
    ax1 = fig.add_subplot(gs[0, 0])
    mensal = df.groupby(['mes', 'mes_nome'])['chuva_total'].sum().reset_index()
    mensal = mensal.sort_values('mes')
    
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(mensal)))
    bars = ax1.bar(mensal['mes_nome'], mensal['chuva_total'], 
                   color=colors, edgecolor='navy', linewidth=1.5)
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax1.set_xlabel('Mês', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Chuva (mm)', fontsize=11, fontweight='bold')
    ax1.set_title('Distribuição Mensal', fontsize=13, fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # ============= GRÁFICO 2: Linha do Tempo (topo direito) =============
    ax2 = fig.add_subplot(gs[0, 1])
    df_sorted = df.sort_values('data')
    df_sorted['chuva_acumulada'] = df_sorted['chuva_total'].cumsum()
    
    ax2.plot(df_sorted['data'], df_sorted['chuva_acumulada'], 
            color='#1f77b4', linewidth=2.5, marker='o', markersize=2)
    ax2.fill_between(df_sorted['data'], 0, df_sorted['chuva_acumulada'], 
                     alpha=0.3, color='#1f77b4')
    
    ax2.set_xlabel('Data', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Chuva Acumulada (mm)', fontsize=11, fontweight='bold')
    ax2.set_title('Evolução Acumulada', fontsize=13, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Formatar eixo X com meses abreviados
    from matplotlib.dates import DateFormatter
    ax2.xaxis.set_major_formatter(DateFormatter('%b'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # ============= GRÁFICO 3: Pizza de Intensidade (meio esquerdo) =============
    ax3 = fig.add_subplot(gs[1, 0])
    intensidade_counts = df['intensidade'].value_counts()
    ordem_intensidade = ['Sem chuva', 'Fraca (< 5mm)', 'Moderada (5-15mm)', 
                         'Forte (15-25mm)', 'Muito Forte (>25mm)']
    intensidade_counts = intensidade_counts.reindex(ordem_intensidade, fill_value=0)
    
    colors_intensidade = ['#E8E8E8', '#A8DADC', '#457B9D', '#1D3557', '#E63946']
    wedges, texts, autotexts = ax3.pie(intensidade_counts, 
                                        labels=intensidade_counts.index,
                                        autopct='%1.1f%%',
                                        colors=colors_intensidade,
                                        startangle=90,
                                        textprops={'fontsize': 9, 'weight': 'bold'})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
    
    ax3.set_title('Distribuição por Intensidade', fontsize=13, fontweight='bold', pad=15)
    
    # ============= GRÁFICO 4: Top 10 Dias (meio direito) =============
    ax4 = fig.add_subplot(gs[1, 1])
    df_com_chuva = df[df['chuva_total'] > 0].copy()
    top10 = df_com_chuva.nlargest(10, 'chuva_total')
    top10['data_str'] = top10['data'].dt.strftime('%d/%m')
    
    cores_top10 = plt.cm.RdYlBu_r(np.linspace(0.2, 0.9, len(top10)))
    bars = ax4.barh(range(len(top10)), top10['chuva_total'], color=cores_top10, edgecolor='black')
    ax4.set_yticks(range(len(top10)))
    ax4.set_yticklabels(top10['data_str'], fontsize=9)
    
    for i, (idx, row) in enumerate(top10.iterrows()):
        ax4.text(row['chuva_total'] + 0.5, i, f"{row['chuva_total']:.1f}mm",
                va='center', fontsize=8, fontweight='bold')
    
    ax4.set_xlabel('Chuva (mm)', fontsize=11, fontweight='bold')
    ax4.set_title('Top 10 Dias Mais Chuvosos', fontsize=13, fontweight='bold', pad=15)
    ax4.grid(axis='x', alpha=0.3, linestyle='--')
    ax4.invert_yaxis()
    
    # ============= GRÁFICO 5: Distribuição Semanal (baixo esquerdo) =============
    ax5 = fig.add_subplot(gs[2, 0])
    df['semana_mes'] = ((df['dia_mes'] - 1) // 7) + 1
    semana_stats = df.groupby('semana_mes')['chuva_total'].agg(['sum', 'count']).reset_index()
    
    cores_semana = ['#8ecae6', '#219ebc', '#023047', '#fb8500']
    bars = ax5.bar(semana_stats['semana_mes'], semana_stats['sum'], 
                  color=cores_semana, edgecolor='black', linewidth=1.5)
    
    for i, row in semana_stats.iterrows():
        ax5.text(row['semana_mes'], row['sum'] + 2, 
                f"{row['sum']:.1f}mm",
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax5.set_xlabel('Semana do Mês', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Chuva (mm)', fontsize=11, fontweight='bold')
    ax5.set_title('Distribuição por Semana', fontsize=13, fontweight='bold', pad=15)
    ax5.set_xticks([1, 2, 3, 4])
    ax5.set_xticklabels(['1ª', '2ª', '3ª', '4ª'])
    ax5.grid(axis='y', alpha=0.3, linestyle='--')
    
    # ============= GRÁFICO 6: Meses Comparativo (baixo direito) =============
    ax6 = fig.add_subplot(gs[2, 1])
    mensal_dias = df.groupby('mes_nome').agg({
        'chuva_total': 'sum',
        'data': 'count'
    }).reindex(['Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'], fill_value=0)
    
    x = np.arange(len(mensal_dias))
    width = 0.35
    
    ax6_twin = ax6.twinx()
    bars1 = ax6.bar(x - width/2, mensal_dias['chuva_total'], width, 
                    label='Chuva (mm)', color='#4A90E2', alpha=0.8)
    bars2 = ax6_twin.bar(x + width/2, mensal_dias['data'], width,
                         label='Dias', color='#7CB342', alpha=0.8)
    
    ax6.set_xlabel('Mês', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Chuva (mm)', fontsize=11, fontweight='bold', color='#4A90E2')
    ax6_twin.set_ylabel('Nº Dias', fontsize=11, fontweight='bold', color='#7CB342')
    ax6.set_title('Comparativo Mensal', fontsize=13, fontweight='bold', pad=15)
    ax6.set_xticks(x)
    ax6.set_xticklabels(mensal_dias.index, fontsize=9)
    ax6.tick_params(axis='y', labelcolor='#4A90E2')
    ax6_twin.tick_params(axis='y', labelcolor='#7CB342')
    ax6.grid(axis='y', alpha=0.3, linestyle='--')
    
    # ============= COLUNA DIREITA: CAIXAS DE DADOS =============
    # Caixa 0: Localização (topo)
    ax_info0 = fig.add_subplot(gs[0:1, 2])
    ax_info0.axis('off')
    ax_info0.set_xlim(0, 10)
    ax_info0.set_ylim(0, 10)
    
    fancy_box0 = FancyBboxPatch((0.3, 0.3), 9.4, 9.4,
                                boxstyle="round,pad=0.1", 
                                facecolor='#FFF9C4',
                                edgecolor='#F57F17', linewidth=3, zorder=0)
    ax_info0.add_patch(fancy_box0)
    
    ax_info0.text(5, 8.8, '📍 LOCALIZAÇÃO', 
                 ha='center', va='top', fontsize=12, fontweight='bold', color='#F57F17')
    
    local_text = """Coordenadas UTM (SIRGAS 2000):
622279 E / 7431301 N
Fuso: 22S

Localidade: Baggio
Município: Ribeirão Claro - PR"""
    
    ax_info0.text(5, 4.8, local_text,
                 ha='center', va='center', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#F57F17', linewidth=1.5, alpha=0.9))
    
    # Caixa 1: Período (linha 1, coluna 2)
    ax_info1 = fig.add_subplot(gs[1:2, 2])
    ax_info1.axis('off')
    ax_info1.set_xlim(0, 10)
    ax_info1.set_ylim(0, 10)
    
    fancy_box1 = FancyBboxPatch((0.3, 0.3), 9.4, 9.4,
                                boxstyle="round,pad=0.1", 
                                facecolor=cores_caixas['periodo'],
                                edgecolor='#1976D2', linewidth=3, zorder=0)
    ax_info1.add_patch(fancy_box1)
    
    ax_info1.text(5, 8.8, '📅 PERÍODO ANALISADO', 
                 ha='center', va='top', fontsize=12, fontweight='bold', color='#0D47A1')
    
    info_text = f"""Total de dias: {stats['total_dias']}
Período: {df['data'].min().strftime('%d/%m/%Y')} até
         {df['data'].max().strftime('%d/%m/%Y')}

Dias com chuva: {stats['dias_com_chuva']} ({stats['porcentagem_dias_chuva']:.1f}%)
Dias sem chuva: {stats['dias_sem_chuva']} ({100-stats['porcentagem_dias_chuva']:.1f}%)"""
    
    ax_info1.text(5, 4.8, info_text,
                 ha='center', va='center', fontsize=9, 
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                          edgecolor='#1976D2', linewidth=1.5, alpha=0.9))
    
    # Caixa 2: Totais (linha 2, coluna 2)
    ax_info2 = fig.add_subplot(gs[2:3, 2])
    ax_info2.axis('off')
    ax_info2.set_xlim(0, 10)
    ax_info2.set_ylim(0, 10)
    
    fancy_box2 = FancyBboxPatch((0.3, 0.3), 9.4, 9.4,
                                boxstyle="round,pad=0.1",
                                facecolor=cores_caixas['totais'],
                                edgecolor='#388E3C', linewidth=3, zorder=0)
    ax_info2.add_patch(fancy_box2)
    
    ax_info2.text(5, 8.8, '💧 TOTAIS DE CHUVA',
                 ha='center', va='top', fontsize=12, fontweight='bold', color='#1B5E20')
    
    totais_text = f"""Chuva total: {stats['chuva_total']:.1f} mm

Média diária: {stats['chuva_media_dia']:.2f} mm/dia
Média (dias c/ chuva): {stats['chuva_media_dia_chuvoso']:.2f} mm

Chuva máxima: {stats['chuva_maxima_dia']:.1f} mm"""
    
    ax_info2.text(5, 4.8, totais_text,
                 ha='center', va='center', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#388E3C', linewidth=1.5, alpha=0.9))
    
    # Caixa 3: Recordes (linha 3, coluna 2)
    ax_info3 = fig.add_subplot(gs[3:4, 2])
    ax_info3.axis('off')
    ax_info3.set_xlim(0, 10)
    ax_info3.set_ylim(0, 10)
    
    fancy_box3 = FancyBboxPatch((0.3, 0.3), 9.4, 9.4,
                                boxstyle="round,pad=0.1",
                                facecolor=cores_caixas['recordes'],
                                edgecolor='#F57C00', linewidth=3, zorder=0)
    ax_info3.add_patch(fancy_box3)
    
    ax_info3.text(5, 8.8, '🏆 RECORDES',
                 ha='center', va='top', fontsize=12, fontweight='bold', color='#E65100')
    
    recordes_text = f"""Dia mais chuvoso:
{stats['data_max_chuva'].strftime('%d/%m/%Y')} - {stats['chuva_maxima_dia']:.1f} mm

Maior período chuvoso:
{stats['periodo_chuvoso_max']} dias consecutivos

Mês mais chuvoso: {stats['mes_mais_chuvoso']}
{stats['chuva_mes_mais_chuvoso']:.1f} mm"""
    
    ax_info3.text(5, 4.8, recordes_text,
                 ha='center', va='center', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#F57C00', linewidth=1.5, alpha=0.9))
    
    # Caixa 4: Períodos Secos (linha 4, coluna 2)
    ax_info4 = fig.add_subplot(gs[4:5, 2])
    ax_info4.axis('off')
    ax_info4.set_xlim(0, 10)
    ax_info4.set_ylim(0, 10)
    
    fancy_box4 = FancyBboxPatch((0.3, 0.3), 9.4, 9.4,
                                boxstyle="round,pad=0.1",
                                facecolor=cores_caixas['secos'],
                                edgecolor='#C2185B', linewidth=3, zorder=0)
    ax_info4.add_patch(fancy_box4)
    
    ax_info4.text(5, 8.8, '🏜️ PERÍODOS SECOS',
                 ha='center', va='top', fontsize=12, fontweight='bold', color='#880E4F')
    
    if stats['data_inicio_seca'] and stats['data_fim_seca']:
        periodo_texto = f"{stats['data_inicio_seca'].strftime('%d/%m')} até {stats['data_fim_seca'].strftime('%d/%m/%Y')}"
    else:
        periodo_texto = "N/A"
    
    secos_text = f"""Maior período sem chuva:
{stats['periodo_seco_max']} dias consecutivos

Período: {periodo_texto}

⚠️ Importante para planejamento
de irrigação"""
    
    ax_info4.text(5, 4.8, secos_text,
                 ha='center', va='center', fontsize=9,
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#C2185B', linewidth=1.5, alpha=0.9))
    
    # Salvar (SEM título geral)
    output_path = os.path.join(output_dir, 'relatorio_a2_paisagem.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Relatório A2 paisagem salvo: relatorio_a2_paisagem.png")
    plt.close()


def criar_relatorio_completo(df, stats, output_dir):
    """Cria relatório visual completo sobre chuvas."""
    
    # Configuração da figura com grid complexo - MUITO mais espaço entre elementos
    fig = plt.figure(figsize=(24, 20))
    gs = GridSpec(5, 3, figure=fig, hspace=0.8, wspace=0.4, 
                  left=0.06, right=0.96, top=0.97, bottom=0.03,
                  height_ratios=[1.2, 1.1, 1.1, 0.75, 1.0])
    
    # Cores personalizadas
    cor_principal = '#2E86AB'
    cor_destaque = '#A23B72'
    cor_sucesso = '#06A77D'
    cor_alerta = '#F18F01'
    
    # ============= GRÁFICO 1: Distribuição Mensal (Grande) =============
    ax1 = fig.add_subplot(gs[0, :])
    
    mensal = df.groupby(['mes', 'mes_nome'])['chuva_total'].sum().reset_index()
    mensal = mensal.sort_values('mes')
    
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(mensal)))
    bars = ax1.bar(mensal['mes_nome'], mensal['chuva_total'], 
                   color=colors, edgecolor='darkblue', linewidth=2, alpha=0.85)
    
    # Adiciona valores em cima das barras
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}mm',
                ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Destaca mês mais chuvoso
    max_idx = mensal['chuva_total'].idxmax()
    bars[max_idx].set_color(cor_destaque)
    bars[max_idx].set_edgecolor('darkred')
    bars[max_idx].set_linewidth(3)
    
    ax1.set_ylabel('Precipitação Total (mm)', fontweight='bold', fontsize=14)
    ax1.set_title('DISTRIBUIÇÃO MENSAL DE CHUVAS', 
                  fontweight='bold', fontsize=16, pad=30)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_axisbelow(True)
    ax1.tick_params(axis='both', which='major', labelsize=11)
    
    # ============= GRÁFICO 2: Chuva Acumulada ao Longo do Tempo =============
    ax2 = fig.add_subplot(gs[1, :2])
    
    df_sorted = df.sort_values('data')
    chuva_acumulada = df_sorted['chuva_total'].cumsum()
    
    ax2.plot(df_sorted['data'], chuva_acumulada, 
             color=cor_principal, linewidth=3, label='Acumulado')
    ax2.fill_between(df_sorted['data'], chuva_acumulada, 
                     alpha=0.3, color=cor_principal)
    
    # Marca eventos importantes
    dias_muita_chuva = df_sorted[df_sorted['chuva_total'] >= 20]
    if len(dias_muita_chuva) > 0:
        for idx, row in dias_muita_chuva.iterrows():
            y_val = chuva_acumulada[df_sorted['data'] == row['data']].values[0]
            ax2.plot(row['data'], y_val, 'ro', markersize=8, 
                    markeredgecolor='darkred', markeredgewidth=2)
    
    ax2.set_xlabel('Data', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Chuva Acumulada (mm)', fontweight='bold', fontsize=12)
    ax2.set_title('ACUMULADO DE CHUVA AO LONGO DO PERÍODO', 
                  fontweight='bold', fontsize=14, pad=25)
    ax2.grid(True, alpha=0.3)
    ax2.legend(['Acumulado', 'Dias com >20mm'], loc='upper left', fontsize=11)
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    # ============= GRÁFICO 3: Distribuição por Intensidade =============
    ax3 = fig.add_subplot(gs[1, 2])
    
    intensidade_counts = df['intensidade'].value_counts()
    ordem_intensidade = ['Sem chuva', 'Fraca (< 5mm)', 'Moderada (5-15mm)', 
                         'Forte (15-25mm)', 'Muito Forte (>25mm)']
    intensidade_counts = intensidade_counts.reindex(ordem_intensidade, fill_value=0)
    
    colors_intensidade = ['#E8E8E8', '#A8DADC', '#457B9D', '#1D3557', '#E63946']
    wedges, texts, autotexts = ax3.pie(intensidade_counts, 
                                        labels=intensidade_counts.index,
                                        autopct='%1.1f%%',
                                        colors=colors_intensidade,
                                        startangle=90,
                                        textprops={'fontsize': 10, 'weight': 'bold'},
                                        pctdistance=0.75)
    
    # Melhora legibilidade dos textos
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
    
    ax3.set_title('DISTRIBUIÇÃO POR\nINTENSIDADE', 
                  fontweight='bold', fontsize=13, pad=25)
    
    # ============= GRÁFICO 4: Top 10 Dias Mais Chuvosos =============
    ax4 = fig.add_subplot(gs[2, :2])
    
    top10 = df.nlargest(10, 'chuva_total')[['data', 'chuva_total']].copy()
    top10['data_str'] = top10['data'].dt.strftime('%d/%b')
    
    colors_top = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(top10)))
    bars_top = ax4.barh(range(len(top10)), top10['chuva_total'], 
                        color=colors_top, edgecolor='black', linewidth=1.5)
    
    ax4.set_yticks(range(len(top10)))
    ax4.set_yticklabels(top10['data_str'], fontsize=11)
    ax4.invert_yaxis()
    ax4.set_xlabel('Precipitação (mm)', fontweight='bold', fontsize=12)
    ax4.set_title('TOP 10 DIAS MAIS CHUVOSOS', 
                  fontweight='bold', fontsize=14, pad=25)
    ax4.grid(True, alpha=0.3, axis='x')
    
    # Adiciona valores
    for i, (bar, val) in enumerate(zip(bars_top, top10['chuva_total'])):
        ax4.text(val + 1, i, f'{val:.1f}mm', 
                va='center', fontweight='bold', fontsize=11)
    
    # ============= GRÁFICO 5: Análise Semanal =============
    ax5 = fig.add_subplot(gs[2, 2])
    
    semanal = df.groupby('semana')['chuva_total'].sum()
    
    ax5.bar(semanal.index, semanal.values, 
            color=cor_sucesso, alpha=0.7, edgecolor='darkgreen')
    ax5.set_xlabel('Semana do Ano', fontweight='bold', fontsize=12)
    ax5.set_ylabel('Chuva (mm)', fontweight='bold', fontsize=12)
    ax5.set_title('DISTRIBUIÇÃO SEMANAL', fontweight='bold', fontsize=14, pad=25)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.tick_params(axis='both', which='major', labelsize=10)
    
    # ============= PAINEL 6: Estatísticas Importantes - PARTE 1 (MAIS LARGO) =============
    ax6 = fig.add_subplot(gs[3, :])
    ax6.axis('off')
    
    stats_text_1 = f"""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                            📊 ESTATÍSTICAS GERAIS DE PRECIPITAÇÃO                              ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

    📅 Período: {df['data'].min().strftime('%d/%m/%Y')} até {df['data'].max().strftime('%d/%m/%Y')} ({stats['total_dias']} dias)
    
    💧 Chuva Total Acumulada: {stats['chuva_total']:.1f} mm
    
    📊 Média Diária (todos os dias): {stats['chuva_media_dia']:.2f} mm/dia
    
    📊 Média em Dias Chuvosos: {stats['chuva_media_dia_chuvoso']:.2f} mm/dia
    
    ☔ Dias com Chuva: {stats['dias_com_chuva']} dias ({stats['porcentagem_dias_chuva']:.1f}% do período)
    
    ☀️ Dias Sem Chuva: {stats['dias_sem_chuva']} dias ({100-stats['porcentagem_dias_chuva']:.1f}% do período)
    """
    
    ax6.text(0.5, 0.5, stats_text_1, 
             transform=ax6.transAxes,
             fontsize=11.5, 
             verticalalignment='center',
             horizontalalignment='center',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=1.5', 
                      facecolor='#E3F2FD', 
                      alpha=0.95,
                      edgecolor='#1976D2',
                      linewidth=3))
    
    # ============= PAINEL 7: Eventos Extremos (Tamanho Padronizado) =============
    ax7 = fig.add_subplot(gs[4, 0])
    ax7.axis('off')
    ax7.set_xlim(0, 1)
    ax7.set_ylim(0, 1)
    
    stats_text_2 = f"""
╔══════════════════════════════════╗
║      🌧️ EVENTOS EXTREMOS        ║
╚══════════════════════════════════╝

📍 Dia Mais Chuvoso:
   {stats['data_max_chuva'].strftime('%d/%m/%Y')}
   {stats['chuva_maxima_dia']:.1f} mm

🏜️ Maior Período Seco:
   {stats['periodo_seco_max']} dias consecutivos
"""
    
    if stats['data_inicio_seca'] and stats['data_fim_seca']:
        stats_text_2 += f"   {stats['data_inicio_seca'].strftime('%d/%m/%Y')} até\n   {stats['data_fim_seca'].strftime('%d/%m/%Y')}\n"
    
    stats_text_2 += f"""
🌧️ Maior Período Chuvoso:
   {stats['periodo_chuvoso_max']} dias consecutivos
    """
    
    ax7.text(0.5, 0.5, stats_text_2, 
             transform=ax7.transAxes,
             fontsize=10.5, 
             verticalalignment='center',
             horizontalalignment='center',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=1.2', 
                      facecolor='#FFF3E0', 
                      alpha=0.95,
                      edgecolor='#F57C00',
                      linewidth=3))
    
    # ============= PAINEL 8: Análise Mensal (Tamanho Padronizado) =============
    ax8 = fig.add_subplot(gs[4, 1])
    ax8.axis('off')
    ax8.set_xlim(0, 1)
    ax8.set_ylim(0, 1)
    
    stats_text_3 = f"""
╔══════════════════════════════════╗
║      📊 ANÁLISE MENSAL           ║
╚══════════════════════════════════╝

🏆 Mês Mais Chuvoso:
   {stats['mes_mais_chuvoso']}
   {stats['chuva_mes_mais_chuvoso']:.1f} mm

📉 Mês Menos Chuvoso:
   {stats['mes_menos_chuvoso']}
   {stats['chuva_mes_menos_chuvoso']:.1f} mm

📊 Média Mensal:
   {stats['chuva_total']/len(df['mes'].unique()):.1f} mm/mês
    """
    
    ax8.text(0.5, 0.5, stats_text_3, 
             transform=ax8.transAxes,
             fontsize=10.5, 
             verticalalignment='center',
             horizontalalignment='center',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=1.2', 
                      facecolor='#E8F5E9', 
                      alpha=0.95,
                      edgecolor='#388E3C',
                      linewidth=3))
    
    # ============= PAINEL 9: Indicadores Agrícolas (Tamanho Padronizado) =============
    ax9 = fig.add_subplot(gs[4, 2])
    ax9.axis('off')
    ax9.set_xlim(0, 1)
    ax9.set_ylim(0, 1)
    
    stats_text_4 = f"""
╔══════════════════════════════════╗
║   🌾 INDICADORES AGRÍCOLAS       ║
╚══════════════════════════════════╝

🌱 Regularidade:
   {'✅ BOM' if stats['periodo_seco_max'] < 15 else '⚠️ ATENÇÃO'}
   {'Bem distribuído' if stats['periodo_seco_max'] < 15 else 'Secos longos'}

💦 Irrigação:
   {'✅ BAIXA' if stats['porcentagem_dias_chuva'] > 30 else '⚠️ ALTA'}
   {'Chuvas frequentes' if stats['porcentagem_dias_chuva'] > 30 else 'Poucas chuvas'}

🌊 Encharcamento:
   {'⚠️ ALTO' if stats['chuva_maxima_dia'] > 50 else '✅ MODERADO' if stats['chuva_maxima_dia'] > 30 else '✅ BAIXO'}

📊 Volume Total:
   {('✅ EXCELENTE' if stats['chuva_total'] > 1200 else '✅ BOM' if stats['chuva_total'] > 800 else '⚠️ REGULAR' if stats['chuva_total'] > 400 else '❌ BAIXO')}
    """
    
    ax9.text(0.5, 0.5, stats_text_4, 
             transform=ax9.transAxes,
             fontsize=10.5, 
             verticalalignment='center',
             horizontalalignment='center',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=1.2', 
                      facecolor='#F3E5F5', 
                      alpha=0.95,
                      edgecolor='#7B1FA2',
                      linewidth=3))
    
    # Título principal
    fig.suptitle('🌧️ RELATÓRIO COMPLETO DE PRECIPITAÇÃO - ANÁLISE AGRÍCOLA 🌾', 
                 fontsize=20, fontweight='bold', y=0.985)
    
    # Salva
    output_path = os.path.join(output_dir, 'relatorio_completo_chuvas.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Relatório completo salvo: relatorio_completo_chuvas.png")
    plt.close()


def criar_analise_mensal_detalhada(df, stats, output_dir):
    """Cria análise detalhada mês a mês."""
    
    fig = plt.figure(figsize=(20, 13))
    gs = GridSpec(3, 1, figure=fig, hspace=0.5, 
                  left=0.08, right=0.95, top=0.94, bottom=0.06,
                  height_ratios=[1, 1, 1.2])
    
    # Prepara dados mensais
    mensal_detalhado = df.groupby(['mes', 'mes_nome']).agg({
        'chuva_total': ['sum', 'mean', 'max', 'min', 'count'],
        'data': ['min', 'max']
    }).reset_index()
    
    mensal_detalhado.columns = ['mes', 'mes_nome', 'total', 'media', 'maxima', 
                                 'minima', 'dias', 'data_inicio', 'data_fim']
    mensal_detalhado = mensal_detalhado.sort_values('mes')
    
    # Conta dias com chuva por mês
    dias_chuva_mes = df[df['chuva_total'] > 0].groupby('mes').size()
    mensal_detalhado['dias_com_chuva'] = mensal_detalhado['mes'].map(dias_chuva_mes).fillna(0)
    
    # ============= GRÁFICO 1: Comparação de Totais e Médias =============
    ax1 = fig.add_subplot(gs[0])
    
    x = np.arange(len(mensal_detalhado))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, mensal_detalhado['total'], width, 
                    label='Total Mensal (mm)', color='#2E86AB', alpha=0.8)
    
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, mensal_detalhado['media'], width,
                    label='Média Diária (mm)', color='#F18F01', alpha=0.8)
    
    ax1.set_xlabel('Mês', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Total Mensal (mm)', fontweight='bold', fontsize=13, color='#2E86AB')
    ax2.set_ylabel('Média Diária (mm)', fontweight='bold', fontsize=13, color='#F18F01')
    ax1.set_title('TOTAL MENSAL vs MÉDIA DIÁRIA', fontweight='bold', fontsize=15, pad=20)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(mensal_detalhado['mes_nome'], fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#2E86AB', labelsize=11)
    ax2.tick_params(axis='y', labelcolor='#F18F01', labelsize=11)
    
    ax1.legend(loc='upper left', fontsize=11)
    ax2.legend(loc='upper right', fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # ============= GRÁFICO 2: Dias com Chuva vs Dias Secos =============
    ax3 = fig.add_subplot(gs[1])
    
    x = np.arange(len(mensal_detalhado))
    dias_secos = mensal_detalhado['dias'] - mensal_detalhado['dias_com_chuva']
    
    bars_chuva = ax3.bar(x, mensal_detalhado['dias_com_chuva'], 
                         label='Dias com Chuva', color='#06A77D', alpha=0.8)
    bars_secos = ax3.bar(x, dias_secos, bottom=mensal_detalhado['dias_com_chuva'],
                         label='Dias Secos', color='#F4A261', alpha=0.8)
    
    ax3.set_ylabel('Número de Dias', fontweight='bold', fontsize=13)
    ax3.set_title('FREQUÊNCIA DE CHUVAS POR MÊS', fontweight='bold', fontsize=15, pad=20)
    ax3.set_xticks(x)
    ax3.set_xticklabels(mensal_detalhado['mes_nome'], fontsize=12)
    ax3.legend(loc='upper right', fontsize=12)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.tick_params(axis='both', which='major', labelsize=11)
    
    # Adiciona percentuais
    for i, (chuva, total) in enumerate(zip(mensal_detalhado['dias_com_chuva'], 
                                            mensal_detalhado['dias'])):
        if chuva > 0:
            percent = (chuva / total * 100)
            ax3.text(i, chuva/2, f'{percent:.0f}%', 
                    ha='center', va='center', fontweight='bold', fontsize=11, color='white')
    
    # ============= TABELA: Resumo Detalhado =============
    ax4 = fig.add_subplot(gs[2])
    ax4.axis('tight')
    ax4.axis('off')
    
    # Prepara dados para tabela
    table_data = []
    for _, row in mensal_detalhado.iterrows():
        table_data.append([
            row['mes_nome'],
            f"{row['total']:.1f}",
            f"{row['media']:.2f}",
            f"{row['maxima']:.1f}",
            f"{int(row['dias_com_chuva'])}/{int(row['dias'])}",
            f"{row['dias_com_chuva']/row['dias']*100:.0f}%"
        ])
    
    headers = ['Mês', 'Total\n(mm)', 'Média/Dia\n(mm)', 'Máxima\n(mm)', 
               'Dias Chuva/\nTotal', 'Freq.\n(%)']
    
    table = ax4.table(cellText=table_data, colLabels=headers,
                     cellLoc='center', loc='center',
                     colWidths=[0.15, 0.15, 0.15, 0.15, 0.2, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 3)
    
    # Estiliza cabeçalho
    for i in range(len(headers)):
        cell = table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white')
    
    # Estiliza linhas alternadas
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#E8F4F8')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor('#2E86AB')
            cell.set_linewidth(1.5)
    
    # Destaca mês com mais chuva
    mes_max_idx = mensal_detalhado['total'].idxmax() + 1
    for j in range(len(headers)):
        cell = table[(mes_max_idx, j)]
        cell.set_facecolor('#FFE5B4')
        cell.set_text_props(weight='bold')
    
    ax4.text(0.5, 0.95, 'RESUMO MENSAL DETALHADO', 
            transform=ax4.transAxes,
            fontsize=15, fontweight='bold',
            ha='center', va='top')
    
    # Título principal
    fig.suptitle('📊 ANÁLISE MENSAL DETALHADA DE PRECIPITAÇÃO', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    output_path = os.path.join(output_dir, 'analise_mensal_detalhada.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Análise mensal detalhada salva: analise_mensal_detalhada.png")
    plt.close()


def criar_graficos_individuais(df, stats, output_dir):
    """Cria gráficos individuais separados para uso em outros documentos."""
    
    print("   📊 Gerando gráficos individuais...")
    
    # Cria subpasta para gráficos individuais
    individuais_dir = os.path.join(output_dir, 'individuais')
    os.makedirs(individuais_dir, exist_ok=True)
    
    # ============= 1. DISTRIBUIÇÃO MENSAL =============
    fig, ax = plt.subplots(figsize=(12, 7))
    df_mensal = df.groupby('mes_nome')['chuva_total'].sum().reindex(
        ['Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'], fill_value=0
    )
    cores_mes = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_mensal)))
    bars = ax.bar(df_mensal.index, df_mensal.values, color=cores_mes, edgecolor='navy', linewidth=1.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}mm',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Mês', fontsize=13, fontweight='bold')
    ax.set_ylabel('Chuva Total (mm)', fontsize=13, fontweight='bold')
    ax.set_title('Distribuição Mensal de Chuvas', fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(individuais_dir, '01_distribuicao_mensal.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # ============= 2. LINHA DO TEMPO ACUMULADA =============
    fig, ax = plt.subplots(figsize=(14, 6))
    df_sorted = df.sort_values('data')
    df_sorted['chuva_acumulada'] = df_sorted['chuva_total'].cumsum()
    
    ax.plot(df_sorted['data'], df_sorted['chuva_acumulada'], 
            color='#1f77b4', linewidth=2.5, marker='o', markersize=3)
    ax.fill_between(df_sorted['data'], 0, df_sorted['chuva_acumulada'], 
                     alpha=0.3, color='#1f77b4')
    
    ax.set_xlabel('Data', fontsize=13, fontweight='bold')
    ax.set_ylabel('Chuva Acumulada (mm)', fontsize=13, fontweight='bold')
    ax.set_title('Evolução da Chuva Acumulada', fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(individuais_dir, '02_chuva_acumulada.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # ============= 3. DISTRIBUIÇÃO POR INTENSIDADE =============
    fig, ax = plt.subplots(figsize=(10, 8))
    intensidade_counts = df['intensidade'].value_counts()
    ordem_intensidade = ['Sem chuva', 'Fraca (< 5mm)', 'Moderada (5-15mm)', 
                         'Forte (15-25mm)', 'Muito Forte (>25mm)']
    intensidade_counts = intensidade_counts.reindex(ordem_intensidade, fill_value=0)
    
    colors_intensidade = ['#E8E8E8', '#A8DADC', '#457B9D', '#1D3557', '#E63946']
    wedges, texts, autotexts = ax.pie(intensidade_counts, 
                                        labels=intensidade_counts.index,
                                        autopct='%1.1f%%',
                                        colors=colors_intensidade,
                                        startangle=90,
                                        textprops={'fontsize': 12, 'weight': 'bold'})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_weight('bold')
    
    ax.set_title('Distribuição por Intensidade', fontsize=15, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(individuais_dir, '03_distribuicao_intensidade.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # ============= 4. TOP 10 DIAS MAIS CHUVOSOS =============
    fig, ax = plt.subplots(figsize=(12, 8))
    df_com_chuva = df[df['chuva_total'] > 0].copy()
    top10 = df_com_chuva.nlargest(10, 'chuva_total')
    top10['data_str'] = top10['data'].dt.strftime('%d/%m')
    
    cores_top10 = plt.cm.RdYlBu_r(np.linspace(0.2, 0.9, len(top10)))
    bars = ax.barh(range(len(top10)), top10['chuva_total'], color=cores_top10, edgecolor='black')
    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels(top10['data_str'], fontsize=11)
    
    for i, (idx, row) in enumerate(top10.iterrows()):
        ax.text(row['chuva_total'] + 0.5, i, f"{row['chuva_total']:.1f} mm",
                va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Chuva (mm)', fontsize=13, fontweight='bold')
    ax.set_title('Top 10 Dias Mais Chuvosos', fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(individuais_dir, '04_top10_dias.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # ============= 5. DISTRIBUIÇÃO POR SEMANA DO MÊS =============
    fig, ax = plt.subplots(figsize=(10, 6))
    df['semana_mes'] = ((df['dia_mes'] - 1) // 7) + 1
    semana_stats = df.groupby('semana_mes')['chuva_total'].agg(['sum', 'count']).reset_index()
    semana_stats.columns = ['semana', 'total', 'dias']
    
    cores_semana = ['#8ecae6', '#219ebc', '#023047', '#fb8500']
    bars = ax.bar(semana_stats['semana'], semana_stats['total'], 
                  color=cores_semana, edgecolor='black', linewidth=1.5)
    
    for i, row in semana_stats.iterrows():
        ax.text(row['semana'], row['total'] + 1, 
                f"{row['total']:.1f}mm\n({int(row['dias'])} dias)",
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Semana do Mês', fontsize=13, fontweight='bold')
    ax.set_ylabel('Chuva Total (mm)', fontsize=13, fontweight='bold')
    ax.set_title('Distribuição por Semana do Mês', fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(['1ª Semana', '2ª Semana', '3ª Semana', '4ª Semana'])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(individuais_dir, '05_distribuicao_semanal.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # ============= 6. PAINEL DE ESTATÍSTICAS =============
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Título
    ax.text(5, 9.2, 'ESTATÍSTICAS COMPLETAS', 
            ha='center', va='top', fontsize=18, fontweight='bold', color='#023047')
    
    # Estatísticas em caixas
    estatisticas_texto = [
        ('📊 DADOS GERAIS', [
            f"Total de dias: {stats['total_dias']}",
            f"Dias com chuva: {stats['dias_com_chuva']} ({stats['porcentagem_dias_chuva']:.1f}%)",
            f"Dias sem chuva: {stats['dias_sem_chuva']} ({100-stats['porcentagem_dias_chuva']:.1f}%)"
        ], 8.2),
        ('💧 TOTAIS', [
            f"Chuva total: {stats['chuva_total']:.1f} mm",
            f"Média diária: {stats['chuva_media_dia']:.2f} mm/dia",
            f"Média (dias c/ chuva): {stats['chuva_media_dia_chuvoso']:.2f} mm"
        ], 6.8),
        ('🏆 RECORDES', [
            f"Dia mais chuvoso: {stats['chuva_maxima_dia']:.1f} mm",
            f"Data: {stats['data_max_chuva'].strftime('%d/%m/%Y')}",
            f"Maior período chuvoso: {stats['periodo_chuvoso_max']} dias"
        ], 5.4),
        ('🏜️ PERÍODOS SECOS', [
            f"Maior seca: {stats['periodo_seco_max']} dias consecutivos",
            f"Período: {stats['data_inicio_seca'].strftime('%d/%m') if stats['data_inicio_seca'] else 'N/A'} até {stats['data_fim_seca'].strftime('%d/%m') if stats['data_fim_seca'] else 'N/A'}"
        ], 4.0)
    ]
    
    for titulo, items, y_pos in estatisticas_texto:
        # Caixa
        rect = plt.Rectangle((0.5, y_pos-0.5), 9, 1.1, 
                            facecolor='#f0f0f0', edgecolor='#023047', linewidth=2)
        ax.add_patch(rect)
        
        # Título da seção
        ax.text(1, y_pos + 0.35, titulo, 
                ha='left', va='top', fontsize=13, fontweight='bold', color='#023047')
        
        # Itens
        for i, item in enumerate(items):
            ax.text(1.2, y_pos - 0.15 - (i * 0.25), f"• {item}",
                   ha='left', va='top', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(individuais_dir, '06_estatisticas_completas.png'), 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"   ✅ 6 gráficos individuais salvos em: individuais/")
    return individuais_dir


def main():
    print("🌧️ GERADOR DE RELATÓRIO COMPLETO DE CHUVAS")
    print("=" * 70)
    
    # Procura arquivo CSV mais recente
    output_dir = 'output'
    arquivos_csv = [f for f in os.listdir(output_dir) 
                    if f.startswith('dados_diarios_') and f.endswith('.csv')]
    
    if not arquivos_csv:
        print("❌ Erro: Nenhum arquivo de dados encontrado em output/")
        return 1
    
    arquivo_csv = sorted(arquivos_csv)[-1]
    caminho_csv = os.path.join(output_dir, arquivo_csv)
    
    print(f"📂 Carregando dados: {arquivo_csv}")
    
    # Carrega e processa dados
    df = carregar_dados(caminho_csv)
    print(f"✅ {len(df)} dias carregados")
    print(f"📅 Período: {df['data'].min().strftime('%d/%m/%Y')} até {df['data'].max().strftime('%d/%m/%Y')}")
    print()
    
    # Calcula estatísticas
    print("📊 Calculando estatísticas agrícolas...")
    stats = calcular_estatisticas(df)
    print(f"   • Chuva total: {stats['chuva_total']:.1f} mm")
    print(f"   • Dias com chuva: {stats['dias_com_chuva']}")
    print(f"   • Maior período seco: {stats['periodo_seco_max']} dias")
    print()
    
    # Cria diretório para relatórios
    relatorios_dir = os.path.join(output_dir, 'relatorios_chuva')
    os.makedirs(relatorios_dir, exist_ok=True)
    
    # Gera relatórios
    print("📊 Gerando relatório completo...")
    criar_relatorio_completo(df, stats, relatorios_dir)
    print()
    
    print("📊 Gerando análise mensal detalhada...")
    criar_analise_mensal_detalhada(df, stats, relatorios_dir)
    print()
    
    print("✅ RELATÓRIOS GERADOS COM SUCESSO!")
    print(f"📂 Arquivos salvos em: {relatorios_dir}/")
    print()
    print("📄 Arquivos gerados:")
    print("   1. relatorio_completo_chuvas.png - Relatório visual completo")
    print("   2. analise_mensal_detalhada.png - Análise mês a mês")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
