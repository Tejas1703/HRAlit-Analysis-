# %% [markdown]
# # 4.4 University–Funder Relationship Heatmap
# **Interactive Notebook** — Filter by country, adjust year range
#
# Data: HRAlit Database (Kong & Börner, 2024) • 2000 onwards

# %% — Imports
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#0d1b2a', 'axes.facecolor': '#0d1b2a',
    'axes.edgecolor': '#2d4059', 'text.color': '#e0e0e0',
    'xtick.color': '#7a8c9e', 'ytick.color': '#7a8c9e',
})

print("✅ Imports loaded")

# %% — Load Data
DATA = '/Users/tejassarma/Downloads/Client_Project/Client_Project_Info_Viz_Dataset'

print("Loading data (this may take ~30 seconds)...")
pff = pd.read_csv(f'{DATA}/hralit_pub_funding_funder.csv.gz', compression='gzip',
                  usecols=['pmid', 'funder_name_pubmed'])
pa = pd.read_csv(f'{DATA}/hralit_publication_author.csv.gz', compression='gzip',
                 usecols=['pmid', 'author_id'])
ai = pd.read_csv(f'{DATA}/hralit_author_institution.csv.gz', compression='gzip',
                 usecols=['author_id', 'soa_institution_id'])
inst = pd.read_csv(f'{DATA}/hralit_institution.csv',
                   usecols=['soa_institution_id', 'institution_name', 'country_code'])
pub = pd.read_csv(f'{DATA}/hralit_publication.csv.gz', compression='gzip',
                  usecols=['pmid', 'pubyear'])

# Filter 2000+
pub = pub.dropna(subset=['pubyear'])
pub['pubyear'] = pub['pubyear'].astype(int)
pub = pub[pub['pubyear'] >= 2000]

print(f"  Funding links: {len(pff):,}")
print(f"  Publications (2000+): {len(pub):,}")

# %% — Process Data: Build joined table
print("Joining tables...")

# Funder grouping
funder_groups = {}
# NIH sub-agencies
for name in ['NHLBI NIH HHS', 'NCI NIH HHS', 'NIDDK NIH HHS', 'NINDS NIH HHS',
             'NIGMS NIH HHS', 'NICHD NIH HHS', 'NIA NIH HHS', 'NIAID NIH HHS',
             'NIMH NIH HHS', 'NEI NIH HHS', 'NCRR NIH HHS', 'NIEHS NIH HHS',
             'NIBIB NIH HHS', 'Intramural NIH HHS']:
    funder_groups[name] = 'NIH'

funder_groups.update({
    'Medical Research Council': 'MRC',
    'Wellcome Trust': 'Wellcome',
    'Deutsche Forschungsgemeinschaft': 'DFG',
    'Howard Hughes Medical Institute': 'HHMI',
    'Canadian Institutes of Health Research': 'CIHR',
    'British Heart Foundation': 'BHF',
})

# NSFC
nsfc = pff[pff['funder_name_pubmed'].str.contains('National Natural Science Foundation of China', case=False, na=False)]['funder_name_pubmed'].unique()
for n in nsfc:
    funder_groups[n] = 'NSFC'

# JSPS
jsps = pff[pff['funder_name_pubmed'].str.contains('Japan Society|JSPS|MEXT', case=False, na=False)]['funder_name_pubmed'].unique()
for n in jsps:
    funder_groups[n] = 'JSPS'

# NSF (US)
nsf = pff[pff['funder_name_pubmed'].str.contains('^NSF$|National Science Foundation', case=False, na=False)]['funder_name_pubmed'].unique()
for n in nsf:
    funder_groups[n] = 'NSF'

pff['funder_clean'] = pff['funder_name_pubmed'].map(funder_groups)
pff_clean = pff.dropna(subset=['funder_clean'])

# All available funders
ALL_FUNDERS = pff_clean.groupby('funder_clean')['pmid'].nunique().sort_values(ascending=False).index.tolist()
print(f"  Funders mapped: {len(ALL_FUNDERS)} → {ALL_FUNDERS}")

# Join pub → author → institution → country
pa_inst = pa.merge(ai, on='author_id', how='inner')
pa_inst = pa_inst.merge(inst, on='soa_institution_id', how='inner')
pub_inst = pa_inst[['pmid', 'institution_name', 'country_code']].drop_duplicates()
pub_inst = pub_inst.merge(pub[['pmid', 'pubyear']], on='pmid', how='inner')

# Add funder
pub_fund = pff_clean[['pmid', 'funder_clean']].drop_duplicates()
inst_funder = pub_inst.merge(pub_fund, on='pmid', how='inner')

print(f"  Total inst-funder-year links: {len(inst_funder):,}")

# %% — Discover available countries
COUNTRY_NAMES = {
    'US': 'United States', 'CN': 'China', 'GB': 'United Kingdom',
    'JP': 'Japan', 'DE': 'Germany', 'IT': 'Italy', 'KR': 'South Korea',
    'AU': 'Australia', 'CA': 'Canada', 'FR': 'France', 'ES': 'Spain',
    'NL': 'Netherlands', 'IN': 'India', 'BR': 'Brazil', 'CH': 'Switzerland',
    'SE': 'Sweden', 'DK': 'Denmark', 'BE': 'Belgium', 'AT': 'Austria',
    'NO': 'Norway', 'FI': 'Finland', 'IL': 'Israel', 'SG': 'Singapore',
    'TW': 'Taiwan', 'HK': 'Hong Kong',
}

country_pubs = inst_funder.groupby('country_code')['pmid'].nunique().sort_values(ascending=False)
ALL_COUNTRIES = country_pubs.index.tolist()

print(f"\n📊 Countries with funding-linked data:")
for cc in ALL_COUNTRIES[:15]:
    name = COUNTRY_NAMES.get(cc, cc)
    print(f"  {cc} ({name}): {country_pubs[cc]:,} pubs")

# %% — Plotting function
def plot_heatmap(country='US', n_institutions=10, year_start=2000, year_end=2021, 
                 funders=None):
    """
    Plot heatmap for a single country.
    
    Args:
        country: country code (e.g., 'US', 'CN', 'GB')
        n_institutions: how many top institutions to show
        year_start, year_end: year filter
        funders: list of funders to include (None = all)
    """
    # Filter data
    mask = (inst_funder['country_code'] == country) & \
           (inst_funder['pubyear'] >= year_start) & \
           (inst_funder['pubyear'] <= year_end)
    
    if funders:
        mask = mask & (inst_funder['funder_clean'].isin(funders))
    
    filtered = inst_funder[mask]
    
    if len(filtered) == 0:
        print(f"⚠️  No data for {COUNTRY_NAMES.get(country, country)} in {year_start}–{year_end}")
        return
    
    # Top institutions
    top_insts = filtered.groupby('institution_name')['pmid'].nunique().sort_values(ascending=False).head(n_institutions).index.tolist()
    
    # Available funders for this country
    avail_funders = funders if funders else filtered.groupby('funder_clean')['pmid'].nunique().sort_values(ascending=False).index.tolist()
    
    # Build matrix
    mat = filtered[filtered['institution_name'].isin(top_insts)].groupby(
        ['institution_name', 'funder_clean'])['pmid'].nunique().unstack(fill_value=0)
    mat = mat.reindex(index=top_insts, columns=avail_funders).fillna(0)
    
    # Remove empty columns
    mat = mat.loc[:, mat.sum() > 0]
    
    if mat.empty:
        print(f"⚠️  No co-linked publications found")
        return
    
    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(max(10, len(mat.columns) * 1.5), max(6, len(mat) * 0.7)))
    
    cmap = LinearSegmentedColormap.from_list('custom',
        ['#0d1b2a', '#1b3a4b', '#00647d', '#00b4d8', '#48cae4', '#e9c46a', '#f4a261', '#e76f51'], N=256)
    
    data = mat.values.astype(float)
    im = ax.imshow(data, cmap=cmap, aspect='auto', interpolation='nearest',
                   vmin=0, vmax=max(data.max(), 1))
    
    # Cell text
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = int(data[i, j])
            if val > 0:
                text_color = 'black' if val > data.max() * 0.55 else 'white'
                ax.text(j, i, f'{val:,}', ha='center', va='center',
                        fontsize=8, fontweight='bold', color=text_color)
    
    # Short labels
    short_names = [n[:35] + '...' if len(n) > 35 else n for n in mat.index]
    ax.set_yticks(range(len(short_names)))
    ax.set_yticklabels(short_names, fontsize=9)
    ax.set_xticks(range(len(mat.columns)))
    ax.set_xticklabels(mat.columns, fontsize=10, fontweight='bold', rotation=30, ha='right')
    
    # Grid
    for i in range(data.shape[0] + 1):
        ax.axhline(i - 0.5, color='#2d4059', linewidth=0.3)
    for j in range(data.shape[1] + 1):
        ax.axvline(j - 0.5, color='#2d4059', linewidth=0.3)
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label('Co-linked Publications', fontsize=10, color='#e0e0e0')
    cbar.ax.tick_params(colors='#7a8c9e', labelsize=9)
    
    country_name = COUNTRY_NAMES.get(country, country)
    total_pubs = int(filtered['pmid'].nunique())
    ax.set_title(f'{country_name} — Top {len(mat)} Institutions × Funders ({year_start}–{year_end})\n'
                 f'{total_pubs:,} funded publications', fontsize=13, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.show()

print("✅ Plot function ready")

# %% — Interactive Widgets
country_dropdown = widgets.Dropdown(
    options=[(f"{COUNTRY_NAMES.get(cc, cc)} ({cc})", cc) for cc in ALL_COUNTRIES[:20]],
    value='US',
    description='Country:',
    style={'description_width': '70px'},
    layout=widgets.Layout(width='300px')
)

n_inst_slider = widgets.IntSlider(
    value=10, min=3, max=20, step=1,
    description='Top N Institutions:',
    style={'description_width': '120px'},
    layout=widgets.Layout(width='400px')
)

year_start_slider = widgets.IntSlider(
    value=2000, min=2000, max=2018, step=1,
    description='Year Start:',
    style={'description_width': '80px'},
    layout=widgets.Layout(width='350px')
)

year_end_slider = widgets.IntSlider(
    value=2021, min=2005, max=2021, step=1,
    description='Year End:',
    style={'description_width': '80px'},
    layout=widgets.Layout(width='350px')
)

funder_selector = widgets.SelectMultiple(
    options=ALL_FUNDERS,
    value=ALL_FUNDERS[:8],
    rows=min(10, len(ALL_FUNDERS)),
    description='Funders:',
    layout=widgets.Layout(width='200px'),
    style={'description_width': '60px'}
)

all_funders_btn = widgets.Button(description='All Funders', button_style='info')
def select_all_funders(b):
    funder_selector.value = ALL_FUNDERS
all_funders_btn.on_click(select_all_funders)

output = widgets.Output()

def on_change(*args):
    with output:
        clear_output(wait=True)
        plot_heatmap(
            country=country_dropdown.value,
            n_institutions=n_inst_slider.value,
            year_start=year_start_slider.value,
            year_end=year_end_slider.value,
            funders=list(funder_selector.value) if funder_selector.value else None,
        )

country_dropdown.observe(on_change, names='value')
n_inst_slider.observe(on_change, names='value')
year_start_slider.observe(on_change, names='value')
year_end_slider.observe(on_change, names='value')
funder_selector.observe(on_change, names='value')

# Layout
controls_left = widgets.VBox([country_dropdown, n_inst_slider])
controls_right = widgets.VBox([year_start_slider, year_end_slider])
controls_funders = widgets.VBox([funder_selector, all_funders_btn])
controls = widgets.HBox([controls_left, controls_right, controls_funders])

display(controls, output)
on_change()

# %% [markdown]
# ## How to Use
# - **Country dropdown** — switch between US, China, UK, Japan, Germany, etc.
# - **Top N** — show more or fewer institutions
# - **Year range** — drill down to specific years (e.g., 2015–2021)
# - **Funders** — select specific funders to compare (Ctrl/Cmd+Click)
# - Plot updates automatically on any change
