# 🏎️ DataGrid F1

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Data Source](https://img.shields.io/badge/Data-F1DB-E10600)](https://github.com/f1db/f1db)

**DataGrid F1** é uma aplicação interativa desenvolvida com **Streamlit** para explorar dados históricos da **Fórmula 1**. O app reúne dashboards, rankings, mapas, estatísticas de corridas, pilotos, construtoras, circuitos e campeonatos em uma experiência visual, rápida e organizada.

A proposta do projeto é transformar a base histórica da F1 em uma plataforma de análise acessível, com filtros intuitivos, visualizações interativas e páginas temáticas para diferentes formas de exploração dos dados.

---

## 🔗 Deploy

Acesse a aplicação publicada no Streamlit:

👉 **[DataGrid F1 — Streamlit App](https://datagrid-f1-ir6anpvbyigxkktxwrgugq.streamlit.app/)**

---

## 📌 Visão geral

O app é dividido em páginas temáticas:

| Página | Objetivo |
|---|---|
| 🏠 **Visão Global** | Apresentar um panorama histórico da F1 com KPIs e gráficos gerais. |
| 🏁 **Corridas** | Explorar resultados oficiais, grid de largada e destaques de cada Grande Prêmio. |
| 🧑‍🚀 **Pilotos** | Analisar estatísticas individuais, evolução de carreira e rankings históricos. |
| 🏭 **Construtoras** | Comparar equipes, domínio histórico, pilotos mais relevantes e confiabilidade. |
| 🗺️ **Circuitos** | Visualizar mapas, traçados, recordes por pista e impacto da posição de largada. |
| 🏆 **Campeonatos** | Consultar classificações finais e evolução de pontos por temporada. |

---

## ✨ Funcionalidades principais

### 🏠 Dashboard global

- KPIs com totais históricos de:
  - pilotos cadastrados;
  - construtoras/equipes;
  - Grandes Prêmios;
  - circuitos utilizados.
- Evolução do calendário de corridas por temporada.
- Ranking dos países que mais sediaram corridas.
- Evolução do grid de largada ao longo das temporadas.
- Ranking dos países de origem de pilotos.
- Evolução da quantidade de construtoras ativas por temporada.
- Ranking dos países de origem de construtoras.

### 🏁 Corridas

- Filtros em cascata por **temporada** e **Grande Prêmio**.
- Painel resumido da corrida selecionada:
  - data;
  - circuito;
  - localização;
  - voltas realizadas.
- Tabela com resultado oficial:
  - posição;
  - piloto;
  - equipe;
  - voltas;
  - tempo/gap;
  - pontos;
  - situação/status.
- Aba dedicada ao **grid de largada**.
- Insights automáticos da corrida:
  - pole position;
  - vencedor;
  - volta mais rápida;
  - Hat Trick;
  - Grand Chelem.
- Gráfico de confiabilidade com proporção de pilotos que concluíram a prova versus abandonos/não largadas.
- Tabela com principais motivos de abandono quando aplicável.

### 🧑‍🚀 Pilotos

A página de pilotos possui duas áreas principais: **Estatísticas Individuais** e **Estatísticas Gerais**.

#### Estatísticas Individuais

- Busca rápida por nome do piloto.
- Cartão biográfico com nacionalidade, idade/ano de nascimento e número permanente quando disponível.
- Métricas principais da carreira:
  - títulos mundiais;
  - vitórias;
  - pódios;
  - poles;
  - voltas mais rápidas;
  - Hat Tricks;
  - Grand Chelems.
- Funil de conversão: **largadas → pódios → vitórias**.
- Gráfico de vitórias por equipe.
- Radar de desempenho com taxas percentuais de vitória, pódio e pole.
- Evolução anual da carreira com gráficos acumulados e gráficos lollipop para:
  - títulos;
  - vitórias;
  - pódios;
  - poles;
  - voltas mais rápidas;
  - Hat Tricks;
  - Grand Chelems.

#### Estatísticas Gerais

- Tabelas de ranking histórico de pilotos para:
  - campeonatos;
  - vitórias;
  - pódios;
  - poles;
  - voltas mais rápidas;
  - Hat Tricks;
  - Grand Chelems;
  - largadas/corridas disputadas.

### 🏭 Construtoras

- Ranking histórico global das equipes.
- Indicadores por construtora:
  - país de origem;
  - títulos mundiais de construtores;
  - títulos de pilotos;
  - vitórias;
  - pódios;
  - poles.
- Relatório detalhado por equipe selecionada.
- Top 10 pilotos da equipe por:
  - vitórias;
  - poles;
  - pódios;
  - corridas disputadas.
- Evolução temporal de:
  - vitórias por temporada;
  - poles por temporada;
  - pódios por temporada;
  - títulos mundiais de construtores;
  - títulos mundiais de pilotos conquistados com a equipe.
- Ranking dos principais motivos de abandono por equipe.

### 🗺️ Circuitos

- Mapa interativo com circuitos da temporada atual.
- Mapa global com todos os circuitos que já sediaram GPs oficiais.
- Raio-X do circuito selecionado:
  - localização;
  - extensão;
  - número de curvas;
  - total de corridas realizadas.
- Análise dos “reis da pista”:
  - piloto com mais vitórias;
  - equipe com mais vitórias;
  - piloto/equipe com mais pódios;
  - piloto/equipe com mais poles.
- Gráfico mostrando a relação entre posição no grid e vitórias no circuito.
- Cálculo do percentual de vitórias obtidas partindo da pole position.
- Exibição de SVGs dos traçados dos circuitos, com variantes:
  - preto;
  - preto com contorno;
  - branco;
  - branco com contorno.

### 🏆 Campeonatos

- Seleção de temporada.
- Destaque visual para campeão/líder do Mundial de Pilotos.
- Destaque visual para campeã/líder do Mundial de Construtores.
- Tratamento histórico para temporadas anteriores a 1958, período em que o campeonato de construtores ainda não existia.
- Tabela de classificação de pilotos.
- Tabela de classificação de construtoras.
- Evolução acumulada de pontos corrida a corrida:
  - pilotos;
  - construtoras.

---

## 🛠️ Tecnologias utilizadas

- **Python** — linguagem principal do projeto.
- **Streamlit** — construção da interface, páginas e deploy.
- **Pandas** — manipulação, limpeza e transformação dos dados.
- **Plotly Express / Graph Objects** — gráficos interativos.
- **SQLite** — armazenamento local dos dados da Fórmula 1.
- **F1DB** — fonte principal dos dados históricos.

---

## 🧱 Estrutura do projeto

A estrutura principal esperada do projeto é:

```text
.
├── 🏠DataGrid_F1.py
├── pages/
│   ├── 1_🏁_Corridas.py
│   ├── 2_🧑‍🚀_Pilotos.py
│   ├── 3_🏭_Construtoras.py
│   ├── 4_🗺️_Circuitos.py
│   └── 5_🏆_Campeonatos.py
├── utils/
│   ├── __init__.py
│   ├── circuit_assets.py
│   ├── constants.py
│   ├── db.py
│   └── ui.py
├── assets/
│   └── circuits/
│       ├── black/
│       ├── black-outline/
│       ├── white/
│       └── white-outline/
├── f1db.db
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
```

### Organização do código

- `🏠DataGrid_F1.py`: página inicial e dashboard global.
- `pages/`: páginas temáticas da aplicação Streamlit.
- `utils/db.py`: camada de acesso ao banco SQLite e consultas reutilizáveis.
- `utils/constants.py`: traduções e constantes auxiliares.
- `utils/circuit_assets.py`: localização e tratamento dos arquivos SVG dos circuitos.
- `utils/ui.py`: componentes visuais compartilhados, como sidebar e rodapé.
- `assets/circuits/`: imagens dos traçados dos circuitos.
- `f1db.db`: banco de dados SQLite utilizado pela aplicação.

---

## 📦 Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/diegobrnrd/datagrid-f1.git
cd datagrid-f1
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Verifique os arquivos necessários

Antes de iniciar o app, confirme que estes itens existem na raiz do projeto:

```text
f1db.db
assets/circuits/
```

O banco `f1db.db` é necessário para as consultas da aplicação. A pasta `assets/circuits/` é utilizada para exibir os traçados dos circuitos.

### 5. Execute a aplicação

```bash
streamlit run 🏠DataGrid_F1.py
```

---

## 🗃️ Fonte de dados

Este projeto utiliza dados históricos da Fórmula 1 a partir do projeto open-source **F1DB**.

- Repositório da fonte de dados: [f1db/f1db](https://github.com/f1db/f1db)
- Licença dos dados: **CC BY 4.0**

> O app exibe os créditos do F1DB na barra lateral, mantendo a atribuição da fonte de dados.

---

## 🎨 Interface e experiência

A aplicação foi desenhada com foco em:

- navegação simples por páginas;
- visualizações em tela ampla;
- gráficos interativos;
- métricas de leitura rápida;
- textos e labels em português;
- tratamento de dados ausentes;
- tradução de países e status de corrida;
- análise visual consistente com a identidade da Fórmula 1.

---

## 🚧 Possíveis melhorias futuras

Algumas ideias para evolução do projeto:

- adicionar filtros comparativos entre pilotos;
- incluir comparação direta entre construtoras;
- permitir exportação de tabelas em CSV;
- adicionar testes automatizados para as consultas SQL;
- criar página de metodologia dos dados;
- incluir cards com recordes históricos gerais;
- adicionar opção de tema claro/escuro personalizada no app.

---

## 👤 Autor

Desenvolvido por **Diego Bernardo**.

- GitHub: [@diegobrnrd](https://github.com/diegobrnrd)

---

## 📄 Licença

Este projeto está licenciado sob a **Apache License 2.0**.

Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.

> Observação: os dados utilizados pelo projeto seguem a licença da fonte original, **F1DB — CC BY 4.0**.
