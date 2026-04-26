# 🧬 HRAlit Analysis

> **Interactive visualization and analysis of the Human Reference Atlas (HRA) literature database — uncovering publication trends, funding flows, global collaborations, and institutional research networks.**

[![Live Dashboard](https://img.shields.io/badge/🚀_Live_Dashboard-Hugging_Face-yellow?style=for-the-badge)](https://huggingface.co/spaces/Tejas1703/hralit-dashboard)

---

## Problem

The **Human Reference Atlas (HRA)** is a comprehensive, open, 3D atlas of the human body at the cellular level. Thousands of research publications contribute to the HRA across organs, institutions, and countries — but there is no unified way to understand:

- **Which organs** are receiving the most research attention, and how is that changing?
- **Which funders** (NIH, Wellcome, NSFC, etc.) are driving this research, and through which institutions?
- **How do countries and institutions collaborate** on HRA-relevant research?
- **What will future publication trends look like** for key organs?

This project provides **5 interactive visualizations** deployed as a live Streamlit dashboard to answer these questions, enabling HRA stakeholders (researchers, funders, policy makers) to make data-driven decisions about resource allocation and collaboration priorities.

---

## Visualizations

| # | Visualization | What It Shows |
|---|--------------|---------------|
| 1 | **Grant-Linkage Sankey** | Funding flows from major funders through organs to research outputs (publications & datasets) |
| 2 | **Publication Trends & Forecast** | Organ-wise publication counts (1950–2023) with animated year-by-year build-up and 5-year polynomial regression forecast with uncertainty bands |
| 3 | **Institution–Funder Heatmap** | Which institutions in a selected country are funded by which agencies, with cell intensity = co-linked publication counts |
| 4 | **Global Collaboration Map** | International co-publication networks on a world map with bubble size = author counts, color = funding intensity |
| 5 | **Institution Collaborations** | Interactive Plotly bipartite network — hover over any edge to see the exact co-publication count between two institutions across countries |

---

## Key Insights

- **Lung research surged 41%** (2015–2021), likely driven by COVID-19, while brain research plateaued at 14% growth despite being the 2nd largest field.
- **Liver** is the most-published organ at ~1.2M publications, with **brain** (~1.05M) and **heart** (~940K) following.
- At the current exponential growth rate, HRA-relevant publications could **nearly double within 5–7 years**, requiring proportional scaling of atlas curation efforts.
- The polynomial regression forecast achieves an approximate **MAPE of 4.4%** across the top 5 organs.

---

## Project Structure

```
HRAlit-Analysis/
│
├── app.py                              # 🚀 Streamlit dashboard (5 tabs, Plotly + Matplotlib)
├── preaggregate_inst_collabs.py        # Script to build institution collaboration CSV from raw data
├── README.md
├── .gitignore
├── LICENSE                             # Apache 2.0 for code
├── NOTICE                              # Project-level attribution notice
├── DATA_NOTICE.md                      # Data-use terms for HRAlit-derived data assets
├── CITATION.cff                        # Machine-readable citation metadata
├── dataset_statistics.md               # Full stats and slide-ready insights
│
├── Pre-Aggregated Data/                # Pre-aggregated datasets used by the dashboard
│   ├── sankey_funder_organ_year.csv
│   ├── trends_organ_year.csv
│   ├── heatmap_inst_funder.csv
│   ├── geo_authors.csv
│   ├── geo_collaborations.csv
│   ├── geo_funding_intensity.csv
│   ├── geo_pubs.csv
│   ├── geo_organ_authors.csv
│   ├── geo_organ_collaborations.csv
│   ├── geo_organ_pubs.csv
│   ├── inst_collaborations.csv         # 252K rows — full co-authorship edges
│   ├── dataset_counts.csv
│   └── world_boundaries.json
│
├── Visualization Python Files/          # Standalone interactive scripts (ipywidgets)
│   ├── viz_4_1_geo_interactive.py
│   ├── viz_4_2_sankey_interactive.py
│   ├── viz_4_3_trends_interactive.py
│   ├── viz_4_4_heatmap_interactive.py
│   └── viz_4_5_inst_collab_interactive.py
│
├── Visualization Notebooks/             # Jupyter notebooks (.ipynb versions of the above)
│   ├── viz_4_1_geo_interactive.ipynb
│   ├── viz_4_2_sankey_interactive.ipynb
│   ├── viz_4_3_trends_interactive.ipynb
│   ├── viz_4_4_heatmap_interactive.ipynb
│   └── viz_4_5_inst_collab_interactive.ipynb
│
└── Raw Data/                            # Raw HRAlit database tables
    ├── hralit_institution.csv
    ├── hralit_organ.csv
    ├── hralit_funder_cleaned.csv
    ├── hralit_author.csv.gz
    ├── hralit_author_institution.csv.gz
    ├── hralit_funding.csv.gz
    ├── hralit_publication.csv.gz        # (gitignored — >100MB)
    ├── hralit_publication_subject.csv.gz # (gitignored — >100MB)
    ├── hralit_pub_funding_funder.csv.gz  # (gitignored — >100MB)
    ├── hralit.sql.gz                    # (gitignored — >100MB)
    └── ...                              # 15+ additional tables
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Dashboard** | Streamlit |
| **Visualizations** | Matplotlib, Plotly |
| **Forecasting** | Polynomial Regression (scikit-learn) |
| **Data Processing** | Pandas, NumPy |
| **Notebooks** | Jupyter + ipywidgets |
| **Deployment** | Hugging Face Spaces |

---

## Getting Started

### Run the Dashboard Locally

```bash
# Clone the repo
git clone https://github.com/Tejas1703/HRAlit-Analysis.git
cd HRAlit-Analysis

# Install dependencies
pip install streamlit pandas numpy matplotlib scikit-learn plotly

# Run
streamlit run app.py
```

### Run the Notebooks

```bash
cd HRAlit-Analysis
pip install jupyter ipywidgets plotly matplotlib pandas numpy scikit-learn

# Launch Jupyter
jupyter notebook "Visualization Notebooks/"
```

> **Note:** The notebooks load raw data from `Raw Data/`. Some compressed files (`.csv.gz`) exceed GitHub's 100MB limit and are gitignored — contact the authors for the full dataset.

---

## Useful Links

- Live dashboard: https://huggingface.co/spaces/Tejas1703/hralit-dashboard
- Code license: [LICENSE](LICENSE)
- Project notice: [NOTICE](NOTICE)
- Data notice: [DATA_NOTICE.md](DATA_NOTICE.md)
- Citation file: [CITATION.cff](CITATION.cff)
- Dataset statistics: [dataset_statistics.md](dataset_statistics.md)
- Root dashboard app: [app.py](app.py)
- Pre-aggregation script: [preaggregate_inst_collabs.py](preaggregate_inst_collabs.py)

---

## Data Source

All data is sourced from the **HRAlit Database** (Kong & Börner, 2024) — a curated collection of publications, funding records, author affiliations, and institutional metadata related to the Human Reference Atlas.

- **Full database:** 22 tables, about 20.9M records
- **Raw CSVs in this workspace:** 14 tables, 82,801 rows
- **Pre-aggregated dashboard tables:** 12 tables, 338,016 rows

For a full breakdown of rows, organs, funders, collaborations, and file sizes, see [dataset_statistics.md](dataset_statistics.md).

---

## Future Work

- **ARIMA / time-series models** for more robust publication forecasting that captures sequential patterns and handles external shocks (e.g., COVID-19)
- **Additional organ coverage** as the HRA database expands
- **Author-level collaboration networks** for finer-grained analysis

---

## Authors

Developed as part of the Indiana University Information Visualization course (E538/E438).

---

## How to Cite This Project

If you use the code, dashboard, or derived analyses, please cite the repository and the source HRAlit publication.

```text
Athkia, Tejas Sarma, Sarrthak, Jonathan Browning, and Jaswanth. HRAlit Analysis. GitHub repository, 2026.
https://github.com/Tejas1703/HRAlit-Analysis
```

```text
Kong, Y., Börner, K. Publication, funding, and experimental data in support of Human Reference Atlas construction and usage. Scientific Data 11, 574 (2024).
https://doi.org/10.1038/s41597-024-03416-8
```

If you use the underlying HRAlit data, also cite the Figshare dataset:

```text
Figshare DOI: 10.6084/m9.figshare.24580669.v2
```

The machine-readable citation metadata is available in [CITATION.cff](CITATION.cff).

---

## License

This repository contains two different kinds of assets:

- **Code**: this repository's code is licensed under **Apache 2.0**. See [LICENSE](LICENSE).
- **Data**: do **not** assume Apache 2.0 covers the HRAlit tables. See [DATA_NOTICE.md](DATA_NOTICE.md) for the data-use terms and restrictions.

If any files are proprietary or redistributed under restricted terms, keep them separate from the code license and document the data-use rules clearly in the repo. A common pattern is:

- `LICENSE` for the code
- `DATA_NOTICE.md` or a dedicated data notice for the dataset terms
- `NOTICE` for attribution and project-level notices
- `CITATION.cff` for citation metadata

This project is for academic and research use. The HRAlit data remains subject to its original licensing terms and the additional guidance in [DATA_NOTICE.md](DATA_NOTICE.md).
