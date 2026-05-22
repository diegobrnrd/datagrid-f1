# 🏎️ DataGrid F1 — Explorer Interativo de Dados da Fórmula 1

[![Python](https://img.shields.io/badge/Python-100%25-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

Aplicação desenvolvida em **Streamlit** para explorar, filtrar e visualizar dados históricos da **Fórmula 1** (corridas, pilotos, construtoras, circuitos e campeonatos) de forma simples e interativa.

> **Destaques:** dashboard com KPIs, gráficos interativos, páginas temáticas e consultas em banco **SQLite**.

---

## 🔗 Deploy

- [Acesse o DataGrid F1 aqui](https://datagrid-f1-ir6anpvbyigxkktxwrgugq.streamlit.app/)

---

## 🧭 O que você encontra no app

O **DataGrid F1** é uma aplicação em Streamlit organizada em uma **visão global** e **páginas temáticas** para exploração de dados históricos da Fórmula 1:

- **🏠 Visão Global (Dashboard)**  
  KPIs do banco (quantidade de pilotos, equipes, GPs e circuitos), além de gráficos com a **evolução do calendário** (corridas por temporada) e **Top 5 países sede** de Grandes Prêmios.

- **🏁 Corridas (Explorador de GPs)**  
  Filtros em cascata por **temporada** e **etapa**, com:
  - **Resultado oficial** (posição final, equipe, voltas, tempo/gap, pontos e situação)  
  - **Grid de largada**  
  - **Insights da corrida**: pole position, volta mais rápida, **taxa de confiabilidade** (concluíram vs abandonaram) e lista de **motivos de abandono**

- **🧑‍🚀 Pilotos (Central Analítica)**  
  Busca por piloto e painel com métricas de carreira (títulos, vitórias, pódios, poles), mais visualizações:
  - **Funil de conversão** (largadas → pódios → vitórias)  
  - **Vitórias por equipe**  
  - **Radar de desempenho** com taxas percentuais (vitória/pódio/pole)

- **🏭 Construtoras (Domínio da Engenharia)**  
  Ranking histórico (top 50) e relatório por equipe com:
  - Top pilotos por vitórias na equipe (Top 5)  
  - **Top 10 motivos de abandono** (histórico de falhas)

- **🗺️ Circuitos (Geografia e Estatísticas de Pista)**  
  Mapa interativo com todos os circuitos (quando há latitude/longitude), ficha técnica do circuito e análises:
  - “Reis da pista” (piloto/equipe com mais vitórias no circuito)  
  - Relação entre **posição de largada** e **vitórias** no circuito + insight de % de vitórias saindo da pole

- **🏆 Campeonatos (Classificação Final)**  
  Seleção de temporada e tabelas finais do **Mundial de Pilotos** e **Mundial de Construtores** (com aviso para temporadas anteriores a 1958).
---

## 🛠️ Stack e ferramentas

- **Python**
- **Streamlit** (interface e deploy)
- **Pandas** (manipulação e transformação de dados)
- **Plotly** (visualizações interativas)
- **SQLite** (camada de dados local)

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
- Crédito da base: [**F1DB**](https://github.com/f1db/f1db) (licença **CC BY 4.0**), conforme exibido no app.

---

## 👤 Autor

[**Diego Bernardo**](https://github.com/diegobrnrd)

---

## Licença

Este projeto está licenciado sob a **Apache License 2.0**.  
Veja o arquivo [LICENSE](LICENSE).
