# %% [markdown]
# # 4.1 Geo Maps — Global Collaboration Network
# **Interactive Notebook** — Filter by organ, time period, view collaboration edges & funding intensity
#
# Data: HRAlit Database (Kong & Börner, 2024)

# %% — Imports
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize, LinearSegmentedColormap
from collections import Counter
import geopandas as gpd
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#0d1b2a', 'axes.facecolor': '#0d1b2a',
    'axes.edgecolor': '#2d4059', 'text.color': '#e0e0e0',
})

print("✅ Imports loaded")

# %% — Load Data
DATA = '/Users/tejassarma/Downloads/Client_Project/Client_Project_Info_Viz_Dataset'

print("Loading data (this takes ~60 seconds)...")
pub = pd.read_csv(f'{DATA}/hralit_publication.csv.gz', compression='gzip', usecols=['pmid', 'pubyear'])
pa = pd.read_csv(f'{DATA}/hralit_publication_author.csv.gz', compression='gzip', usecols=['pmid', 'author_id'])
ai = pd.read_csv(f'{DATA}/hralit_author_institution.csv.gz', compression='gzip', usecols=['author_id', 'soa_institution_id'])
inst = pd.read_csv(f'{DATA}/hralit_institution.csv', usecols=['soa_institution_id', 'institution_name', 'country_code'])
pub_organ = pd.read_csv(f'{DATA}/hralit_publication_subject.csv.gz', compression='gzip')
pff = pd.read_csv(f'{DATA}/hralit_pub_funding_funder.csv.gz', compression='gzip', usecols=['pmid', 'funder_name_pubmed'])

pub = pub.dropna(subset=['pubyear'])
pub['pubyear'] = pub['pubyear'].astype(int)

# Load world map
world = gpd.read_file(f'{DATA}/ne_countries/ne_110m_admin_0_countries.shp')

print(f"  Publications: {len(pub):,}")
print(f"  Pub-Author: {len(pa):,}")
print(f"  Author-Inst: {len(ai):,}")

# %% — Process & Join Data
print("Joining tables...")
# pub → author → institution → country
merged = pa.merge(ai, on='author_id', how='inner')
merged = merged.merge(inst[['soa_institution_id', 'country_code']], on='soa_institution_id', how='inner')
merged = merged.merge(pub[['pmid', 'pubyear']], on='pmid', how='inner')

# Add organ
merged_organ = merged.merge(pub_organ, on='pmid', how='inner')

# Add funding info
pff['has_funding'] = 1
funding_pmids = pff.groupby('pmid')['funder_name_pubmed'].nunique().reset_index()
funding_pmids.columns = ['pmid', 'n_funders']

ALL_ORGANS = merged_organ.groupby('organ')['pmid'].nunique().sort_values(ascending=False).index.tolist()
print(f"\n✅ Data ready: {len(merged):,} records, {len(ALL_ORGANS)} organs")

# %% — Country coordinates (centroids)
COUNTRY_POS = {
    'US': (-98, 39), 'CN': (104, 35), 'GB': (-1, 53), 'JP': (138, 36),
    'DE': (10, 51), 'IT': (12, 42), 'KR': (128, 36), 'AU': (134, -25),
    'CA': (-106, 56), 'FR': (2, 47), 'ES': (-4, 40), 'NL': (5, 52),
    'IN': (79, 22), 'BR': (-51, -10), 'CH': (8, 47), 'SE': (15, 62),
    'DK': (10, 56), 'BE': (4, 51), 'AT': (14, 47), 'NO': (9, 62),
    'FI': (26, 64), 'IL': (35, 31), 'SG': (104, 1), 'TW': (121, 24),
    'HK': (114, 22), 'MX': (-102, 23), 'RU': (37, 55), 'TR': (35, 39),
    'PL': (20, 52), 'GR': (22, 39), 'PT': (-8, 39), 'IE': (-8, 53),
    'ZA': (25, -29), 'NZ': (172, -42), 'CL': (-71, -33), 'AR': (-64, -34),
    'CZ': (15, 50), 'HU': (20, 47), 'MY': (102, 4), 'TH': (101, 15),
    'PH': (122, 13), 'PK': (70, 30), 'EG': (31, 30), 'NG': (8, 10),
    'SA': (45, 24), 'IR': (53, 32), 'CO': (-74, 4),
}

COUNTRY_NAMES = {
    'US': 'USA', 'CN': 'China', 'GB': 'UK', 'JP': 'Japan', 'DE': 'Germany',
    'IT': 'Italy', 'KR': 'S. Korea', 'AU': 'Australia', 'CA': 'Canada',
    'FR': 'France', 'ES': 'Spain', 'NL': 'Netherlands', 'IN': 'India',
    'BR': 'Brazil', 'CH': 'Switzerland', 'SE': 'Sweden',
}

print(f"✅ {len(COUNTRY_POS)} country positions loaded")

# %% — Compute panel data function
def compute_geo_data(year_start, year_end, organ='All'):
    """Compute country counts, collaboration edges, and funding intensity."""
    data = merged_organ if organ != 'All' else merged
    
    if organ != 'All':
        data = data[data['organ'] == organ]
    
    data = data[(data['pubyear'] >= year_start) & (data['pubyear'] <= year_end)]
    
    # Author counts per country
    author_counts = data.groupby('country_code')['author_id'].nunique()
    
    # Collaboration pairs (international co-publication)
    pub_countries = data.groupby('pmid')['country_code'].apply(set)
    collab_pairs = Counter()
    intl_count = 0
    for countries in pub_countries:
        if len(countries) > 1:
            intl_count += 1
            sorted_c = sorted(countries)
            for i in range(len(sorted_c)):
                for j in range(i + 1, len(sorted_c)):
                    collab_pairs[(sorted_c[i], sorted_c[j])] += 1
    
    # Funding intensity (unique funders per country)
    fund_data = data.merge(funding_pmids, on='pmid', how='left')
    funding_by_country = fund_data.dropna(subset=['n_funders']).groupby('country_code')['n_funders'].mean()
    
    total_pubs = data['pmid'].nunique()
    
    return author_counts, collab_pairs, funding_by_country, total_pubs, intl_count

# %% — Plotting function
def plot_geo(organ='All', year_start=2003, year_end=2023, top_n_edges=30, 
             show_labels=True, min_authors=50):
    """Draw geo collaboration map."""
    author_counts, collab_pairs, funding_intensity, total_pubs, intl_count = \
        compute_geo_data(year_start, year_end, organ)
    
    if len(author_counts) == 0:
        print(f"⚠️  No data for {organ} in {year_start}–{year_end}")
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    
    # Draw world map
    world.plot(ax=ax, color='#1b2838', edgecolor='#2d4059', linewidth=0.3)
    
    # Top edges
    top_edges = sorted(collab_pairs.items(), key=lambda x: -x[1])[:top_n_edges]
    max_edge = top_edges[0][1] if top_edges else 1
    
    for (c1, c2), count in top_edges:
        if c1 not in COUNTRY_POS or c2 not in COUNTRY_POS:
            continue
        x1, y1 = COUNTRY_POS[c1]
        x2, y2 = COUNTRY_POS[c2]
        lw = 0.5 + (count / max_edge) * 4
        alpha = 0.2 + (count / max_edge) * 0.5
        ax.plot([x1, x2], [y1, y2], '-', color='#00b4d8', linewidth=lw, alpha=alpha, zorder=2)
    
    # Bubbles
    max_count = author_counts.max() if len(author_counts) > 0 else 1
    cmap = LinearSegmentedColormap.from_list('fund', ['#34d399', '#f59e0b', '#ef4444'], N=256)
    max_fund = funding_intensity.max() if len(funding_intensity) > 0 else 1
    
    for cc, count in author_counts.items():
        if cc not in COUNTRY_POS or count < min_authors:
            continue
        x, y = COUNTRY_POS[cc]
        size = 30 + (count / max_count) * 600
        
        fund_val = funding_intensity.get(cc, 0)
        color = cmap(fund_val / max_fund) if max_fund > 0 else '#34d399'
        
        ax.scatter(x, y, s=size, c=[color], alpha=0.85, edgecolors='white', linewidth=0.5, zorder=4)
        
        if show_labels and count >= max_count * 0.05:
            label = COUNTRY_NAMES.get(cc, cc)
            ax.text(x, y + 3, label, ha='center', va='bottom', fontsize=7, color='white',
                    fontweight='bold', path_effects=[pe.withStroke(linewidth=2, foreground='#0d1b2a')],
                    zorder=5)
    
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xticks([]); ax.set_yticks([])
    
    organ_label = organ.title() if organ != 'All' else 'All Organs'
    ax.set_title(f'{organ_label} — {year_start}–{year_end}\n'
                 f'{total_pubs:,} publications  •  {intl_count:,} international collaborations  •  '
                 f'{len(author_counts)} countries',
                 fontsize=13, fontweight='bold', color='white', pad=12)
    
    plt.tight_layout()
    plt.show()

print("✅ Geo plot function ready")

# %% — Interactive Controls
organ_dropdown = widgets.Dropdown(
    options=['All'] + ALL_ORGANS,
    value='All',
    description='Organ:',
    style={'description_width': '50px'},
    layout=widgets.Layout(width='250px')
)

year_start_slider = widgets.IntSlider(
    value=2018, min=1950, max=2020, step=1,
    description='Year Start:', style={'description_width': '80px'},
    layout=widgets.Layout(width='350px')
)

year_end_slider = widgets.IntSlider(
    value=2023, min=1960, max=2023, step=1,
    description='Year End:', style={'description_width': '80px'},
    layout=widgets.Layout(width='350px')
)

edges_slider = widgets.IntSlider(
    value=30, min=5, max=100, step=5,
    description='Top N Edges:', style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
)

min_authors_slider = widgets.IntSlider(
    value=50, min=1, max=500, step=10,
    description='Min Authors:', style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
)

labels_toggle = widgets.Checkbox(value=True, description='Show Labels')

# Quick period buttons
period_btns = []
for label, ys, ye in [('2003-07', 2003, 2007), ('2008-12', 2008, 2012),
                       ('2013-17', 2013, 2017), ('2018-23', 2018, 2023), ('All Time', 1950, 2023)]:
    btn = widgets.Button(description=label, button_style='info', layout=widgets.Layout(width='80px'))
    def make_cb(s, e):
        def cb(b):
            year_start_slider.value = s
            year_end_slider.value = e
        return cb
    btn.on_click(make_cb(ys, ye))
    period_btns.append(btn)

output = widgets.Output()

def on_change(*args):
    with output:
        clear_output(wait=True)
        plot_geo(
            organ=organ_dropdown.value,
            year_start=year_start_slider.value,
            year_end=year_end_slider.value,
            top_n_edges=edges_slider.value,
            show_labels=labels_toggle.value,
            min_authors=min_authors_slider.value,
        )

for w in [organ_dropdown, year_start_slider, year_end_slider, edges_slider, 
          min_authors_slider, labels_toggle]:
    w.observe(on_change, names='value')

controls_row1 = widgets.HBox([organ_dropdown, labels_toggle])
controls_row2 = widgets.HBox([year_start_slider, year_end_slider])
controls_row3 = widgets.HBox([edges_slider, min_authors_slider])
period_box = widgets.HBox(period_btns)

display(widgets.VBox([controls_row1, controls_row2, controls_row3, period_box]), output)
on_change()

# %% [markdown]
# ## How to Use
# - **Organ dropdown** — filter to a specific organ (brain, kidney, etc.) or "All"
# - **Year sliders** — adjust time window
# - **Quick period buttons** — jump to 5-year blocks or all time
# - **Top N Edges** — show more/fewer collaboration lines
# - **Min Authors** — threshold for showing country bubbles
# - **Show Labels** — toggle country name labels
# - Bubble **size** = author count, **color** = avg funding intensity
# - Edge **thickness** = co-publication count
