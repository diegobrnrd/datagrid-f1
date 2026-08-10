# 🏎️ DataGrid F1

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Data Source](https://img.shields.io/badge/Data-F1DB-E10600)](https://github.com/f1db/f1db)

**DataGrid F1** is an interactive application built with **Streamlit** to explore historical **Formula 1** data. The app brings together dashboards, rankings, maps, race statistics, drivers, constructors, circuits, and championships in a visual, fast, and organized experience.

The goal of the project is to turn F1's historical database into an accessible analysis platform, with intuitive filters, interactive visualizations, and themed pages for different ways of exploring the data.

---

## 🔗 Deploy

Access the published application on Streamlit:

👉 **[DataGrid F1 — Streamlit App](https://datagrid-f1-ir6anpvbyigxkktxwrgugq.streamlit.app/)**

---

## 📌 Overview

The app is divided into themed pages:

| Page | Purpose |
|---|---|
| 🏠 **Global Overview** | Present a historical overview of F1 with KPIs and general charts. |
| 🏁 **Races** | Explore official results, starting grid, and highlights from each Grand Prix. |
| 🧑‍🚀 **Drivers** | Analyze individual statistics, career progression, and historical rankings. |
| 🏭 **Constructors** | Compare teams, historical dominance, top drivers, and reliability. |
| 🗺️ **Circuits** | View maps, track layouts, per-track records, and the impact of grid position. |
| 🏆 **Championships** | Check final standings and points progression by season. |

---

## ✨ Main Features

### 🏠 Global dashboard

- KPIs with historical totals of:
  - registered drivers;
  - constructors/teams;
  - Grands Prix;
  - circuits used.
- Race calendar evolution by season.
- Ranking of countries that have hosted the most races.
- Starting grid evolution over the seasons.
- Ranking of drivers' countries of origin.
- Evolution of the number of active constructors per season.
- Ranking of constructors' countries of origin.

### 🏁 Races

- Cascading filters by **season** and **Grand Prix**.
- Summary panel for the selected race:
  - date;
  - circuit;
  - location;
  - laps completed.
- Table with official results:
  - position;
  - driver;
  - team;
  - laps;
  - time/gap;
  - points;
  - status.
- Dedicated tab for the **starting grid**.
- Automatic race insights:
  - pole position;
  - winner;
  - fastest lap;
  - Hat Trick;
  - Grand Chelem.
- Reliability chart showing the proportion of drivers who finished the race versus retirements/no-shows.
- Table of main retirement reasons, when applicable.

### 🧑‍🚀 Drivers

The drivers page has two main areas: **Individual Statistics** and **General Statistics**.

#### Individual Statistics

- Quick search by driver name.
- Bio card with nationality, age/year of birth, and permanent number when available.
- Main career metrics:
  - world titles;
  - wins;
  - podiums;
  - poles;
  - fastest laps;
  - Hat Tricks;
  - Grand Chelems.
- Conversion funnel: **starts → podiums → wins**.
- Wins-by-team chart.
- Performance radar with win, podium, and pole percentage rates.
- Annual career evolution with cumulative charts and lollipop charts for:
  - titles;
  - wins;
  - podiums;
  - poles;
  - fastest laps;
  - Hat Tricks;
  - Grand Chelems.

#### General Statistics

- Historical driver ranking tables for:
  - championships;
  - wins;
  - podiums;
  - poles;
  - fastest laps;
  - Hat Tricks;
  - Grand Chelems;
  - starts/races contested.

### 🏭 Constructors

- Global historical team ranking.
- Indicators by constructor:
  - country of origin;
  - constructors' world titles;
  - drivers' titles;
  - wins;
  - podiums;
  - poles.
- Detailed report for the selected team.
- Top 10 drivers of the team by:
  - wins;
  - poles;
  - podiums;
  - races contested.
- Time evolution of:
  - wins per season;
  - poles per season;
  - podiums per season;
  - constructors' world titles;
  - drivers' world titles won with the team.
- Ranking of main retirement reasons by team.

### 🗺️ Circuits

- Interactive map with circuits from the current season.
- Global map with all circuits that have hosted official GPs.
- X-ray of the selected circuit:
  - location;
  - length;
  - number of corners;
  - total races held.
- "Track kings" analysis:
  - driver with the most wins;
  - team with the most wins;
  - driver/team with the most podiums;
  - driver/team with the most poles.
- Chart showing the relationship between grid position and wins at the circuit.
- Calculation of the percentage of wins achieved starting from pole position.
- Display of circuit layout SVGs, with variants:
  - black;
  - black with outline;
  - white;
  - white with outline.

### 🏆 Championships

- Season selection.
- Visual highlight for the Drivers' World Championship winner/leader.
- Visual highlight for the Constructors' World Championship winner/leader.
- Historical handling for seasons before 1958, when the constructors' championship did not yet exist.
- Drivers' standings table.
- Constructors' standings table.
- Cumulative points evolution race by race:
  - drivers;
  - constructors.

---

## 🛠️ Technologies Used

- **Python** — main project language.
- **Streamlit** — interface, pages, and deployment.
- **Pandas** — data manipulation, cleaning, and transformation.
- **Plotly Express / Graph Objects** — interactive charts.
- **SQLite** — local storage of Formula 1 data.
- **F1DB** — main source of historical data.

---

## 🧱 Project Structure

The project's main expected structure is:

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

### Code organization

- `🏠DataGrid_F1.py`: home page and global dashboard.
- `pages/`: themed pages of the Streamlit application.
- `utils/db.py`: SQLite database access layer and reusable queries.
- `utils/constants.py`: translations and auxiliary constants.
- `utils/circuit_assets.py`: location and handling of circuit SVG files.
- `utils/ui.py`: shared visual components, such as sidebar and footer.
- `assets/circuits/`: circuit layout images.
- `f1db.db`: SQLite database used by the application.

---

## 📦 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/diegobrnrd/datagrid-f1.git
cd datagrid-f1
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Check the required files

Before starting the app, confirm that these items exist in the project root:

```text
f1db.db
assets/circuits/
```

The `f1db.db` database is required for the application's queries. The `assets/circuits/` folder is used to display the circuit layouts.

### 5. Run the application

```bash
streamlit run 🏠DataGrid_F1.py
```

---

## 🗃️ Data Source

This project uses historical Formula 1 data from the open-source **F1DB** project.

- Data source repository: [f1db/f1db](https://github.com/f1db/f1db)
- Data license: **CC BY 4.0**

> The app displays F1DB credits in the sidebar, maintaining attribution of the data source.

---

## 🎨 Interface and Experience

The application was designed with a focus on:

- simple page navigation;
- wide-screen visualizations;
- interactive charts;
- quick-read metrics;
- text and labels in Portuguese;
- handling of missing data;
- translation of countries and race status;
- visual analysis consistent with the Formula 1 identity.

---

## 🚧 Possible Future Improvements

Some ideas for the project's evolution:

- add comparative filters between drivers;
- include direct comparison between constructors;
- allow table export to CSV;
- add automated tests for SQL queries;
- create a data methodology page;
- include cards with overall historical records;
- add a custom light/dark theme option in the app.

---

## 👤 Author

Developed by [**Diego Bernardo**](https://github.com/diegobrnrd).

---

## 📄 License

This project is licensed under the **Apache License 2.0**.

See the [`LICENSE`](LICENSE) file for more details.

> Note: the data used by the project follows the license of the original source, **F1DB — CC BY 4.0**.
