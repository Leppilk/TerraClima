# �️ TerraClima - Sistema de Análise Meteorológica

Sistema completo de análise meteorológica para agricultura de precisão, com interface web interativa e módulos especializados de análise.

## 📋 Visão Geral

TerraClima é uma plataforma moderna para análise de dados meteorológicos da estação **Weathercloud Galinhada** em Ribeirão Claro-PR. O sistema processa dados de 10 em 10 minutos e oferece análises detalhadas através de uma interface web intuitiva.

### ✨ Destaques

- 🔄 **Processamento Automático**: Pipeline completo de ETL com validação de dados
- 📊 **6 Módulos de Análise**: Especializados em Chuva, Temperatura, Umidade, Vento, Solar e Correlações
- � **Dashboard Web**: Interface Streamlit com 4 páginas de análises
- 🌾 **Foco Agrícola**: Indicadores para irrigação, aplicação de defensivos e conforto animal
- 📈 **Visualizações Interativas**: Gráficos dinâmicos com Plotly
- 💾 **Sistema de Cache**: Performance otimizada com cache inteligente

## 🎯 Funcionalidades Principais

### Dashboard Principal
- 📊 **4 KPIs em tempo real**: Temperatura, Umidade, Chuva 7 dias, Dias sem chuva
- 📈 **Gráficos de tendência**: Últimos 30 dias por variável
- 🚨 **3 Alertas agrícolas**: Irrigação, Aplicação de defensivos, Conforto térmico

### Análise de Gráficos
- 🌡️ **Temperatura**: Evolução temporal, distribuições, zonas térmicas
- � **Umidade**: Máximas, mínimas, médias e histogramas
- 🌧️ **Precipitação**: Diária, acumulada e mensal
- 💨 **Vento**: Velocidade média, rajadas, distribuição
- ☀️ **Radiação Solar**: Total diária, índice UV
- 🌐 **Pressão**: Evolução e distribuição

### Estatísticas e Recordes
- 📊 **Estatísticas descritivas** completas de todas as variáveis
- 🏆 **Recordes históricos**: Dias mais quentes, frios, chuvosos e ventosos
- 🌾 **Índices agrícolas**: Necessidade de irrigação, adequação para aplicação
- 📋 **Top 10**: Rankings dos dias mais extremos

### Análise de Correlações
- � **Matriz de correlação** interativa com todas as variáveis
- 💪 **Top 15 correlações** mais fortes
- 🔍 **4 análises específicas**: Temp×Umidade, Pressão×Chuva, Vento×Temp, Solar×Temp
- 📖 **Guia de interpretação** completo

## 🏗️ Arquitetura

```
TerraClima/
├── config.py                 # Configurações globais
├── requirements.txt          # Dependências Python
├── test_processing.py        # Testes do pipeline de dados
├── test_analyzers.py         # Testes dos analyzers
│
├── src/                      # Código-fonte principal
│   ├── data/                 # Módulos de dados
│   │   ├── loader.py         # Carregamento de CSVs
│   │   ├── processor.py      # Agregação diária
│   │   └── aggregator.py     # Agregações temporais
│   │
│   ├── analysis/             # Módulos de análise
│   │   ├── rainfall.py       # Análise de chuvas
│   │   ├── temperature.py    # Análise de temperatura
│   │   ├── humidity.py       # Análise de umidade
│   │   ├── wind.py           # Análise de vento
│   │   ├── solar.py          # Análise de radiação solar
│   │   └── correlation.py    # Análise de correlações
│   │
│   └── utils/                # Utilitários
│       ├── date_utils.py     # Manipulação de datas
│       ├── stats_utils.py    # Cálculos estatísticos
│       └── formatters.py     # Formatação de dados
│
├── web/                      # Aplicação Streamlit
│   ├── app.py                # Aplicação principal
│   └── pages/                # Páginas da aplicação
│       ├── dashboard.py      # Dashboard principal
│       ├── graficos.py       # Página de gráficos
│       ├── estatisticas.py   # Página de estatísticas
│       └── correlacoes.py    # Página de correlações
│
├── Dados/                    # Dados brutos (CSVs)
├── output/                   # Saídas geradas
└── docs/                     # Documentação

```

## 🚀 Instalação

### Pré-requisitos
- Python 3.13+ (testado com 3.13.1)
- pip (gerenciador de pacotes Python)
- Git

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/Leppilk/TerraClima.git
cd TerraClima
```

2. **Crie o ambiente virtual:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

## 💻 Como Usar

### 1. Executar Dashboard Web (Recomendado)

```bash
streamlit run web/app.py
```

Acesse: `http://localhost:8501`

### 2. Testar Pipeline de Dados

```bash
python test_processing.py
```

### 3. Testar Analyzers

```bash
python test_analyzers.py
```

## 📊 Estrutura dos Dados

### Dados de Entrada
- **Formato**: CSV (UTF-16-LE, separador `;`, decimal `,`)
- **Frequência**: Leituras a cada 10 minutos
- **Período**: Abril - Outubro 2025 (196 dias)
- **Registros**: 27,735 leituras processadas

### Variáveis Monitoradas
1. 🌡️ **Temperatura**: Máxima, Mínima, Média, Interior
2. 💧 **Umidade**: Máxima, Mínima, Média
3. 🌧️ **Precipitação**: Total diária, Intensidade
4. 💨 **Vento**: Velocidade média, Rajadas, Direção
5. ☀️ **Radiação Solar**: Total, Máxima, Índice UV
6. 🌐 **Pressão Atmosférica**
7. 🌡️ **Ponto de Orvalho**
8. 🔥 **Índice de Calor**
9. ❄️ **Sensação Térmica**

## 🔬 Módulos de Análise

### RainfallAnalyzer
- Estatísticas de precipitação
- Períodos secos e chuvosos
- Classificação por intensidade
- Necessidade de irrigação
- Distribuição semanal

### TemperatureAnalyzer
- Detecção de ondas de calor
- Períodos de frio intenso
- Zonas térmicas
- Conforto térmico para gado
- Graus-dia de crescimento (GDD)

### HumidityAnalyzer
- Impacto agrícola
- Risco de doenças fúngicas
- Classificação por níveis
- Estatísticas mensais

### WindAnalyzer
- Adequação para aplicação de defensivos
- Escala Beaufort
- Rosa dos ventos
- Estatísticas por direção

### SolarAnalyzer
- Classificação de índice UV
- Potencial energético fotovoltaico
- Impacto agrícola
- Dias com boa insolação

### CorrelationAnalyzer
- Matriz de correlação completa
- 8 análises específicas
- Interpretações automáticas
- Significância estatística

## 📦 Dependências Principais

```
streamlit==1.50.0         # Framework web
pandas==2.3.3             # Manipulação de dados
numpy==2.3.4              # Computação numérica
plotly==6.3.1             # Visualizações interativas
scipy==1.16.2             # Análises estatísticas
scikit-learn==1.7.2       # Machine learning
matplotlib==3.10.7        # Gráficos estáticos
seaborn==0.13.2           # Visualizações estatísticas
```

## 🌾 Aplicações Agrícolas

### Irrigação
- ✅ Monitora períodos sem chuva significativa
- ✅ Calcula necessidade de irrigação
- ✅ Recomendações personalizadas

### Aplicação de Defensivos
- ✅ Analisa condições de vento
- ✅ Identifica janelas ideais
- ✅ Previne deriva e perdas

### Conforto Animal
- ✅ Índice de conforto térmico para gado
- ✅ Alertas de estresse térmico
- ✅ Recomendações de manejo

### Planejamento
- ✅ Graus-dia de crescimento (GDD)
- ✅ Análise de tendências
- ✅ Previsão de safras

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

### Outputs
- `output/chuvas_diarias_*.csv` - Dados diários consolidados
- `output/dados_meteorologicos_completos_*.csv` - Dataset completo processado
- `output/graficos_chuva/` - Visualizações geradas

## 🧪 Testes e Validação

### Cobertura de Testes
- ✅ **test_processing.py**: Valida pipeline completo de dados (27,735 → 196 registros)
- ✅ **test_analyzers.py**: Testa todos os 6 módulos de análise
- ✅ Taxa de sucesso: 100%

### Métricas Validadas
- Temperatura: 3.3°C a 35.4°C
- Umidade: 17% a 98%
- Precipitação máxima: 28.8mm
- 196 dias processados com sucesso

## 🔧 Configuração Avançada

### Customização de Thresholds

Edite `config.py` para ajustar:
- Classificação de chuva (fraca, moderada, forte)
- Zonas térmicas
- Limites para alertas agrícolas

### Performance

O sistema utiliza cache inteligente do Streamlit:
```python
@st.cache_data
def load_data():
    # Dados são carregados apenas uma vez
    ...
```

## 🐛 Solução de Problemas

### Erro de Encoding
**Problema**: "Sem dados válidos após conversão de data"
**Solução**: O sistema tenta múltiplos encodings automaticamente. Verifique formato do CSV.

### Erro de Memória
**Problema**: Out of memory ao processar
**Solução**: Processe arquivos em lotes menores ou aumente RAM disponível

### Streamlit não inicia
**Problema**: Porta 8501 ocupada
**Solução**: 
```bash
streamlit run web/app.py --server.port 8502
```

## 📊 Benchmarks

- **Carregamento**: ~2s para 27,735 registros
- **Processamento**: ~1s para agregação diária
- **Renderização web**: <500ms (com cache)
- **Memória**: ~150MB em operação

## 🌐 Deploy

### Streamlit Cloud (Recomendado)

1. Faça push para GitHub
2. Conecte ao [Streamlit Cloud](https://streamlit.io/cloud)
3. Configure:
   - Main file: `web/app.py`
   - Python version: 3.13

### Docker (Alternativa)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "web/app.py"]
```

## 📚 Documentação Adicional

- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Docs](https://plotly.com/python/)
- [Pandas Docs](https://pandas.pydata.org/docs/)

## 🗺️ Roadmap

### Próximas Funcionalidades
- [ ] Exportação de relatórios em PDF
- [ ] Integração com API de previsão do tempo
- [ ] Alertas por e-mail/SMS
- [ ] Comparação com dados históricos de anos anteriores
- [ ] Dashboard mobile responsivo
- [ ] Integração com sistema de irrigação

### Em Consideração
- [ ] Machine Learning para previsão de chuvas
- [ ] API REST para integração com outros sistemas
- [ ] Suporte multi-estação
- [ ] Modo offline

## 👥 Autores

- **Lucas Kosta** - Desenvolvimento inicial

## 🙏 Agradecimentos

- Weathercloud pela infraestrutura de estação meteorológica
- Comunidade Python/Streamlit pelo suporte
- Agricultores de Ribeirão Claro pela validação dos índices agrícolas

## 📞 Contato

- 📧 Email: lucaskosta@gmail.com
- 🐙 GitHub: [@Leppilk](https://github.com/Leppilk)
- 🌐 Projeto: [TerraClima](https://github.com/Leppilk/TerraClima)

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**🌦️ TerraClima** - *Inteligência meteorológica para agricultura de precisão*

⭐ Se este projeto foi útil, considere dar uma estrela!

</div>
