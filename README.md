# 🌧️ Sistema de Análise de Chuvas - Estação Meteorológica

Sistema automatizado para análise de dados pluviométricos da estação meteorológica Weathercloud.

## 📋 Funcionalidades

- 🔄 **Processamento Automático**: Lê todos os arquivos CSV da pasta `Dados/`
- 🌧️ **Extração de Dados de Chuva**: Extrai apenas colunas relacionadas à precipitação
- 📊 **Agregação Diária**: Converte dados de 10 em 10 minutos para resumos diários
- 📈 **Geração de Gráficos**: Cria automaticamente 2 relatórios completos com análises
- 🌾 **Foco Agrícola**: Estatísticas voltadas para planejamento de irrigação

## 🚀 Instalação Rápida

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd Estacao_Meteorologica
```

2. Crie e ative o ambiente virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Como Usar

Execute um único comando para processar tudo:

```bash
python processar_chuvas.py
```

O sistema irá automaticamente:
1. ✅ Ler todos os CSVs da pasta `Dados/`
2. ✅ Extrair apenas dados de chuva
3. ✅ Gerar CSV diário consolidado
4. ✅ Criar todos os gráficos de análise

### Método 3: Processar Arquivo Específico
```bash
python app/main.py --file "Dados/Weathercloud Galinhada 2025-10.csv" --output "output/"
```
## 📂 Arquivos Gerados

Após a execução, você encontrará:

### CSV Consolidado
- **`output/chuvas_diarias_[timestamp].csv`**: Dados diários de chuva
  - Data
  - Chuva total (mm)
  - Intensidade máxima (mm/h)
  - Classificação (Sem chuva, Fraca, Moderada, Forte, Muito Forte)
  - Dados auxiliares (mês, ano, semana)

### Gráficos de Análise
- **`output/graficos_chuva/relatorio_completo_chuvas.png`**: Relatório com 6 painéis
  - Distribuição mensal de chuvas
  - Linha do tempo acumulada
  - Distribuição por intensidade
  - Top 10 dias mais chuvosos
  - Distribuição por semana do mês
  - Painel de estatísticas agrícolas

- **`output/graficos_chuva/analise_mensal_detalhada.png`**: Comparativo mensal
  - Tabela completa mês a mês
  - Estatísticas detalhadas

## 📊 Estrutura do Projeto

```
Estacao_Meteorologica/
├── processar_chuvas.py    # Script principal (processamento + gráficos)
├── relatorio_chuvas.py    # Gerador de gráficos
├── Dados/                 # Arquivos CSV originais (entrada)
├── output/                # Arquivos gerados (saída)
│   ├── chuvas_diarias_*.csv
│   └── graficos_chuva/
│       ├── relatorio_completo_chuvas.png
│       └── analise_mensal_detalhada.png
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🌾 Estatísticas Agrícolas

O sistema calcula automaticamente:

- 💧 **Total de chuva no período**
- 📅 **Dias com/sem chuva**
- 🏜️ **Maior período de seca** (importante para irrigação)
- 📊 **Média diária de precipitação**
- 🌧️ **Distribuição por intensidade** (fraca, moderada, forte)
- 📈 **Análise mensal** (totais, médias, dias chuvosos)
- 🏆 **Recordes** (dia mais chuvoso, maior intensidade)

## ⚙️ Detalhes Técnicos

### Formato dos Dados de Entrada
- **Separador**: ponto e vírgula (;)
- **Decimal**: vírgula (,)
- **Encoding**: UTF-16 LE (detectado automaticamente com fallbacks)
- **Frequência**: Leituras a cada 10 minutos

### Cálculos de Precipitação
- **Chuva diária**: `max()` da coluna "Chuva (mm)" (valor acumulado no dia)
- **Intensidade máxima**: `max()` da coluna "Intensidade de chuva (mm/h)"
- **Classificação**: Baseada em critérios meteorológicos padrão

### Gráficos
- **Resolução**: 300 DPI (alta qualidade para impressão)
- **Tamanho**: 24x20 polegadas
- **Formato**: PNG com fundo branco
- **Layout**: GridSpec otimizado (hspace=0.8 para evitar sobreposição)

## 📝 Notas Importantes

- ⚠️ Arquivos CSV devem estar na pasta `Dados/`
- ⚠️ O sistema processa automaticamente todos os arquivos `.csv` encontrados
- ⚠️ CSVs com formato de data incompatível são ignorados (será exibido aviso)
- ✅ O timestamp no nome do CSV garante que execuções anteriores não sejam sobrescritas

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

Este projeto é de código aberto para uso pessoal e educacional.
