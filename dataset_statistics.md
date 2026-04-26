# 📊 HRAlit Analysis — Dataset Statistics

## Data Source

- **Database**: HRAlit (Kong & Börner, 2024)
- **Download**: [Figshare DOI: 10.6084/m9.figshare.24580669.v2](https://doi.org/10.6084/m9.figshare.24580669.v2)
- **HRA Version**: v1.4
- **Full database**: 22 tables, ~20.9 million records (~612 MB compressed)
- **Local workspace**: 14 CSV tables (82,801 rows) + 12 pre-aggregated tables (338,016 rows)

---

## Raw Database Tables (14 CSVs in workspace)

| Table | Rows | Columns | Description |
|-------|-----:|---------|-------------|
| `hralit_organ` | 31 | 1 | Organs in the HRA |
| `hralit_digital_objects` | 295 | 8 | HRA digital objects (ASCT+B tables, FTUs, OMAPs, 3D ref organs) |
| `hralit_anatomical_structures` | 4,378 | 3 | Anatomical structure terms |
| `hralit_cell_types` | 1,395 | 3 | Cell type terms |
| `hralit_biomarkers` | 2,522 | 3 | Biomarker terms |
| `hralit_asctb_linkage` | 25,277 | 3 | ASCT+B ontology linkages |
| `hralit_asct_publication` | 1,290 | 5 | Publications linked to ASCT+B tables |
| `hralit_creator` | 550 | 9 | HRA digital object creators |
| `hralit_reviewer` | 602 | 9 | HRA digital object reviewers |
| `hralit_dataset` | 7,337 | 46 | Experimental datasets (HuBMAP, GTEx, etc.) |
| `hralit_donor` | 4,639 | 24 | Tissue donor demographics |
| `hralit_institution` | 26,235 | 5 | Research institutions (196 countries) |
| `hralit_funder_cleaned` | 6,427 | 3 | Cleaned funder names (107 countries) |
| `hralit_other_publication` | 1,823 | 3 | Additional publications from external sources |

> **Note**: The full HRAlit database also includes large tables not in the workspace CSVs — `hralit_publication` (7.1M rows), `hralit_publication_author` (1.08M), `hralit_pub_funding_funder` (2.6M), `hralit_publication_subject` (7.9M), `hralit_author` (583K), `hralit_author_institution`, and `hralit_funding` (896K) — totaling ~20.9M records.

---

## Key Counts

| Metric | Count |
|--------|------:|
| **Organs** | 31 |
| **Digital Objects** (HRA v1.4) | 295 |
| **Anatomical Structures** | 4,378 |
| **Cell Types** | 1,395 |
| **Biomarkers** | 2,522 |
| **ASCT+B Linkages** | 25,277 |
| **Creators** | 550 |
| **Reviewers** | 602 |
| **Datasets** | 7,337 |
| **Donors** | 4,639 |
| **Institutions** | 26,235 (across **196 countries**) |
| **Funders** (cleaned) | 6,427 (across **107 countries**) |
| **Publications** (full DB) | ~7.1 million |
| **Funded Projects** (full DB) | ~896,680 |
| **Authors/Experts** (full DB) | ~583,117 |

---

## Top 10 Organs by Publication Count (1950–2023)

| Rank | Organ | Total Publications |
|------|-------|-------------------:|
| 1 | Liver | 1,193,841 |
| 2 | Brain | 1,057,247 |
| 3 | Heart | 940,158 |
| 4 | Kidney | 705,037 |
| 5 | Lung | 642,526 |
| 6 | Skin | 558,672 |
| 7 | Eye | 274,822 |
| 8 | Skeletal | 270,435 |
| 9 | Bone Marrow | 164,938 |
| 10 | Prostate | 163,380 |

---

## Top 10 Funders by Publication Co-Link Frequency

| Rank | Funder | Co-Linked Publications |
|------|--------|----------------------:|
| 1 | NIH | 714,535 |
| 2 | MRC | 35,181 |
| 3 | NSFC | 16,656 |
| 4 | Wellcome | 14,928 |
| 5 | BHF | 7,466 |
| 6 | CIHR | 5,637 |
| 7 | JSPS | 3,813 |
| 8 | NSF | 2,484 |
| 9 | DFG | 1,777 |
| 10 | HHMI | 180 |

---

## Top 10 Countries by Author Count

| Rank | Country | Total Authors |
|------|---------|-------------:|
| 1 | 🇺🇸 US | 159,716 |
| 2 | 🇨🇳 CN | 81,345 |
| 3 | 🇬🇧 GB | 39,548 |
| 4 | 🇮🇹 IT | 38,269 |
| 5 | 🇯🇵 JP | 33,363 |
| 6 | 🇩🇪 DE | 32,647 |
| 7 | 🇰🇷 KR | 28,691 |
| 8 | 🇦🇺 AU | 23,757 |
| 9 | 🇪🇸 ES | 22,315 |
| 10 | 🇧🇷 BR | 21,115 |

---

## Top International Collaboration Pairs (2020–2024)

| Country Pair | Co-Publications |
|-------------|----------------:|
| 🇨🇳 China ↔ 🇺🇸 US | 4,570 |
| 🇬🇧 UK ↔ 🇺🇸 US | 3,404 |
| 🇨🇦 Canada ↔ 🇺🇸 US | 2,676 |
| 🇩🇪 Germany ↔ 🇺🇸 US | 2,300 |
| 🇮🇹 Italy ↔ 🇺🇸 US | 1,750 |

---

## Pre-Aggregated Dashboard Data (12 tables, 338K rows)

| Table | Rows | Purpose |
|-------|-----:|---------|
| `trends_organ_year.csv` | 2,238 | Publication trends by organ & year (1950–2023) |
| `sankey_funder_organ_year.csv` | 4,210 | Funder→Organ flows (1960–2023) |
| `heatmap_inst_funder.csv` | 45,662 | Institution–Funder matrix (144 countries, 10,245 institutions) |
| `inst_collaborations.csv` | 252,086 | Institution co-authorship pairs (18,055 institutions, 188 countries) |
| `geo_authors.csv` | 1,405 | Author counts by country & year (195 countries) |
| `geo_pubs.csv` | 1,405 | Publication counts by country & year |
| `geo_collaborations.csv` | 511 | Country-pair collaboration counts (5-year windows) |
| `geo_organ_authors.csv` | 14,172 | Author counts by country, organ & year |
| `geo_organ_pubs.csv` | 14,172 | Publication counts by country, organ & year |
| `geo_organ_collaborations.csv` | 1,143 | Organ-specific country-pair collaborations |
| `dataset_counts.csv` | 57 | Dataset counts per organ |

---

## Dataset Counts by Organ (Top 15)

| Organ | Datasets |
|-------|--------:|
| Blood | 1,788 |
| Brain | 1,666 |
| Lung | 404 |
| Small Intestine | 307 |
| Large Intestine | 264 |
| Eye | 256 |
| Uterus | 239 |
| Kidney (left) | 234 |
| Kidney (right) | 230 |
| Breast | 225 |
| Kidney | 161 |
| Spinal Cord | 134 |
| Stomach | 122 |
| Respiratory System | 113 |
| Liver | 89 |

---

## Temporal Coverage

| Data Type | Range |
|-----------|-------|
| Publications | 1950 – September 2023 |
| Funding data | 1960 – 2023 |
| Author data | 1984 – 2023 |
| Forecast horizon | 2024 – 2028 (5-year polynomial regression) |

---

## Institution Collaboration Network Stats

| Metric | Value |
|--------|------:|
| Total institution pairs | 252,086 |
| Unique institutions | 18,055 |
| Unique countries | 188 |
| Top collaborating pair | UCL Australia ↔ University College London (57 co-pubs) |

---

## File Sizes (Raw CSVs)

| File | Size (MB) |
|------|----------:|
| `hralit_dataset.csv` | 3.50 |
| `hralit_asctb_linkage.csv` | 2.43 |
| `hralit_institution.csv` | 2.63 |
| `hralit_donor.csv` | 0.53 |
| `hralit_funder_cleaned.csv` | 0.47 |
| `hralit_anatomical_structures.csv` | 0.36 |
| `hralit_asct_publication.csv` | 0.18 |
| `hralit_other_publication.csv` | 0.08 |
| `hralit_digital_objects.csv` | 0.07 |
| `hralit_reviewer.csv` | 0.06 |
| `hralit_creator.csv` | 0.05 |
| `hralit_biomarkers.csv` | 0.11 |
| `hralit_cell_types.csv` | 0.09 |
| `hralit_organ.csv` | <0.01 |

---

## 🔍 Dashboard Insights (from Live Deployment)

**Live Dashboard**: https://huggingface.co/spaces/Tejas1703/hralit-dashboard

### Tab 1: 🔗 Grant-Linkage Sankey

- **NIH dominates funding** — with 714,535 co-linked publications, it accounts for ~90% of all funder–organ flows, dwarfing MRC (35K), NSFC (17K), and Wellcome (15K) combined.
- **Funding is heavily concentrated** in the top 6 organs (brain, liver, heart, lung, kidney, skeletal) — smaller organs like thymus, ureter, and placenta receive negligible grant-linkage attention.
- **The Sankey reveals a "rich-get-richer" pattern**: well-funded organs produce more publications AND datasets, reinforcing future funding cycles.

### Tab 2: 📈 Publication Trends & Forecast

- **Liver leads globally** at ~1.19M publications, but **lung research surged 41% (2015–2021)**, likely COVID-driven, while **brain plateaued at only 14% growth** despite being the 2nd largest field.
- **Polynomial regression forecast** (degree 2) with 95% confidence bands projects that HRA-relevant publications could **nearly double within 5–7 years** at current exponential growth rates.
- **MAPE of ~4.4%** across top 5 organs indicates the forecast is reliable for near-term planning.
- The **animated build-up** feature shows how publication acceleration really took off post-2000, with exponential growth in the last two decades.

### Tab 3: 🗺️ Institution–Funder Heatmap

- **In the US**, NIH overwhelmingly funds the top institutions (Harvard, Stanford, Mayo Clinic, etc.), with very little funder diversity — creating a single-point-of-failure risk.
- **Other countries show more funder diversity**: UK institutions receive from both MRC and Wellcome; German institutions from DFG and other EU funders.
- **Cross-country funder partnerships are rare** — most institutions are funded almost exclusively by domestic agencies, suggesting an opportunity for international co-funding initiatives.

### Tab 4: 🌍 Global Collaboration Map

- **476,196 publications** across **194 countries** with **50,541 collaboration links** (2018–2023, all organs).
- **US–China is the #1 bilateral collaboration pair** with 4,570 co-publications (2020–2024), followed by US–UK (3,404) and US–Canada (2,676).
- **Funding intensity** (color gradient: green→yellow→red) shows the US and UK have the highest average funder counts per publication, while many developing nations have minimal funding diversity.
- **Compare Mode** reveals stark differences: e.g., brain research is US/EU-dominated, while liver research has stronger Asian representation.
- **Step-Through time** shows collaboration networks expanding dramatically post-2010, with China's author count growing exponentially.

### Tab 5: 🏛️ Institution Collaborations (US ↔ China)

- **273 co-publications** between the top 10 US and top 10 Chinese institutions.
- **Top US collaborators with China**: UC San Diego (38), Stanford (36), Mayo Clinic (30), MD Anderson (33), U Michigan (28).
- **Top Chinese collaborators with US**: Chinese University of Hong Kong (37), Zhejiang University (35), Shanghai Jiao Tong (33), Peking University (29), Ministry of Agriculture (30).
- **The network is sparse but high-impact**: most institution pairs have only 1–5 co-publications, but a few "bridge institutions" (Stanford, Zhejiang, CUHK) serve as hubs connecting the two countries.

---

## 🎯 Cross-Cutting Actionable Insights

| Insight | Implication |
|---------|-------------|
| NIH funds ~90% of top-organ research | HRA is vulnerable to NIH policy shifts; need funder diversification |
| Lung surged 41% while brain plateaued | COVID redirected research priorities; brain may be under-invested relative to disease burden |
| Publications could double in 5–7 years | Atlas curation efforts must scale proportionally |
| US–China is #1 collab pair (4,570 co-pubs) | Geopolitical tensions could disrupt the most productive bilateral research relationship |
| Smaller organs (thymus, ureter, placenta) are severely underfunded | Targeted funding calls needed for atlas completeness |
| Most institutions rely on a single domestic funder | International co-funding mechanisms could strengthen collaboration |
| A few "bridge institutions" connect US–China | These hubs are strategic assets for maintaining scientific cooperation |
