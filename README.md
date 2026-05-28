# 🏎️ DataGrid F1 — Explorer Interativo de Dados da Fórmula 1

[![Python](https://img.shields.io/badge/Python-100%25-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

Aplicação desenvolvida em **Streamlit** para explorar, filtrar e visualizar dados históricos da **Fórmula 1** (corridas, pilotos, construtoras, circuitos e campeonatos) de forma simples, visual e interativa.

> **Destaques:** dashboard global com KPIs, gráficos evolutivos, análise detalhada nas páginas temáticas, imagens e mapas interativos, recursos exclusivos como identificação automática de Hat Trick, Grand Chelem e muito mais. Todas as informações vêm de um banco **SQLite** baseado no projeto open-source [F1DB](https://github.com/f1db/f1db).

---

## 🔗 Deploy

- [Acesse o DataGrid F1 aqui](https://datagrid-f1-ir6anpvbyigxkktxwrgugq.streamlit.app/)

---

## 🧭 O que você encontra no app

O **DataGrid F1** é organizado em páginas temáticas para uma imersão visual e analítica nos dados históricos da F1:

- **🏠 Visão Global (Dashboard)**
  - KPIs do banco: quantidade total de **pilotos**, **equipes**, **GPs** e **circuitos**.
  - Gráfico evolutivo: **Corridas por temporada** desde 1950.
  - **Top 10 países-sede** de GPs — com gráfico de barras mostrando os países que mais receberam corridas.

- **🏁 Corridas (Explorador de GPs)**
  - **Filtros em cascata** para selecionar temporada e etapa.
  - **Resultados oficiais**: posição, pilotos, equipes, voltas, tempo/gap, pontos e situação.
  - **Grid de largada**.
  - **Insights da corrida** em destaque:
    - Pole Position.
    - Vencedor.
    - Volta mais rápida.
    - **Hat Trick** *(pole + vitória + volta mais rápida, aparece se ocorreu)*.
    - **Grand Chelem** *(pole, vitória, volta mais rápida & liderou todas voltas — aparece se ocorreu)*.
  - **Gráfico de confiabilidade** (concluíram vs abandonaram) e motivos dos abandonos.

- **🧑‍🚀 Pilotos (Central Analítica)**
  - Busca rápida por piloto.
  - Painel com os principais indicadores de carreira:
    - Títulos.
    - Vitórias.
    - Pódios.
    - Poles.
    - Idade / nacionalidade.
  - Visualizações exclusivas:
    - **Funil de conversão** (largadas → pódios → vitórias).
    - **Vitórias por equipe** (barras).
    - **Radar de desempenho**: taxas percentuais de vitória/pódio/pole no total de largadas.

- **🏭 Construtoras (Domínio da Engenharia)**
  - Ranking histórico das equipes (top 50 por vitórias), com país, títulos e pódios.
  - Relatório detalhado por equipe:
    - Top 5 pilotos por vitórias naquela equipe.
    - Top 10 motivos de abandono (falhas históricas).

- **🗺️ Circuitos (Geografia e Estatísticas de Pista)**
  - Mapa interativo mostrando todos os circuitos, países e corridas sediadas.
  - Ficha técnica do circuito (localização, extensão, curvas, corridas).
  - Análises avançadas:
    - “Reis da pista” (piloto/equipe com mais vitórias no traçado).
    - **Relação entre grid de largada e vitória** — gráfico mostra de onde mais se vence naquela pista.
    - Insight (%) de vitórias partindo da pole position.
  - **Imagem do circuito**, com seleção do traçado desejado (pistas com múltiplos desenhos/traçados permitem escolher e visualizar cada variação).

- **🏆 Campeonatos (Classificação Final por temporada)**
  - Seleção da temporada desejada.
  - **Tabelas finais** do Mundial de Pilotos e Mundial de Construtores (alerta e tratamento especial para anos antes de 1958, quando ainda não havia campeonato de equipes).
  - **Destaque visual para os campeões** do ano.
  - **Dois gráficos de evolução da pontuação**: um mostra a evolução corrida a corrida dos pontos acumulados por piloto, outro faz o mesmo para as construtoras.

---

## 🛠️ Stack e ferramentas

- **Python**
- **Streamlit** (interface e deploy)
- **Pandas** (manipulação e transformação de dados)
- **Plotly** (visualizações interativas)
- **SQLite** (camada local de dados/repositório)

---

## 📦 Como executar localmente

### 1) Clone o repositório

```bash
git clone https://github.com/diegobrnrd/datagrid-f1.git
cd datagrid-f1
```

### 2) Crie e ative um ambiente virtual (opcional, recomendado)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3) Instale as dependências

```bash
pip install -r requirements.txt
```

### 4) Rode o app

```bash
streamlit run 🏠DataGrid_F1.py
```

---

## 🗃️ Fonte de dados / Créditos

- O projeto utiliza um banco **SQLite** (`f1db.db`) na raiz do repositório.
- Créditos da base de dados: [**F1DB**](https://github.com/f1db/f1db) (licença **CC BY 4.0**), conforme exibido no app.

---

## 👤 Autor

[**Diego Bernardo**](https://github.com/diegobrnrd)

---

## Licença

Este projeto está licenciado sob a **Apache License 2.0**.  
Veja o arquivo [LICENSE](LICENSE).
