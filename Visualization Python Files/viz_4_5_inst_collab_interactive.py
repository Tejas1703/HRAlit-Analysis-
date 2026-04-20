# %% [markdown]
# # 4.5 Institution–Institution Collaboration Network (Plotly Interactive)
# **Interactive Notebook** — Select two countries, adjust top-N, hover to explore
#
# Data: HRAlit Database (Kong & Börner, 2024) • Cross-country co-authorship collaborations

# %% — Imports
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

print("✅ Imports loaded")

# %% — Load Data
DATA = '/Users/tejassarma/Downloads/Client_Project/Client_Project_Info_Viz_Dataset'

print("Loading data (this may take ~60 seconds)...")
pa = pd.read_csv(f'{DATA}/hralit_publication_author.csv.gz', compression='gzip',
                 usecols=['pmid', 'author_id'])
ai = pd.read_csv(f'{DATA}/hralit_author_institution.csv.gz', compression='gzip',
                 usecols=['author_id', 'soa_institution_id'])
inst = pd.read_csv(f'{DATA}/hralit_institution.csv',
                   usecols=['soa_institution_id', 'institution_name', 'country_code'])
inst = inst.dropna(subset=['country_code', 'institution_name'])

print(f"  Publication-author links: {len(pa):,}")
print(f"  Author-institution links: {len(ai):,}")
print(f"  Institutions: {len(inst):,}")

# %% — Process Data: Build co-authorship based institution-to-institution collaboration table
from itertools import combinations

print("Joining tables...")

# author → institution → country
ai_inst = ai.merge(inst, on='soa_institution_id', how='inner')
pub_inst = pa.merge(ai_inst[['author_id', 'institution_name', 'country_code']],
                    on='author_id', how='inner')
pub_inst = pub_inst.drop_duplicates(subset=['pmid', 'institution_name', 'country_code'])
print(f"  Unique (pmid, institution, country) triples: {len(pub_inst):,}")

# Group by pmid → list of (institution, country)
print("Finding cross-country institution pairs...")
grouped = pub_inst.groupby('pmid').apply(
    lambda g: list(zip(g['institution_name'], g['country_code']))
).reset_index(name='institutions')

# Papers with ≥2 countries
multi_country = grouped[grouped['institutions'].apply(
    lambda inst_list: len(set(c for _, c in inst_list)) >= 2
)]
print(f"  {len(multi_country):,} publications with authors from ≥2 countries")

# Generate all cross-country institution pairs
edges = []
for _, row in multi_country.iterrows():
    unique_insts = list(set(row['institutions']))
    for (inst_a, cc_a), (inst_b, cc_b) in combinations(unique_insts, 2):
        if cc_a != cc_b:
            if cc_a > cc_b:
                inst_a, cc_a, inst_b, cc_b = inst_b, cc_b, inst_a, cc_a
            edges.append((inst_a, cc_a, inst_b, cc_b))

edge_df = pd.DataFrame(edges, columns=['inst_a', 'country_a', 'inst_b', 'country_b'])
COLLAB_DATA = edge_df.groupby(['inst_a', 'country_a', 'inst_b', 'country_b']).size().reset_index(name='collab_count')
COLLAB_DATA = COLLAB_DATA.sort_values('collab_count', ascending=False)

print(f"  Unique institution pairs: {len(COLLAB_DATA):,}")
print(f"  Total co-publications: {COLLAB_DATA['collab_count'].sum():,}")

# %% — Country Name Mapping
COUNTRY_NAMES = {
    'US': 'United States', 'CN': 'China', 'GB': 'United Kingdom',
    'JP': 'Japan', 'DE': 'Germany', 'IT': 'Italy', 'KR': 'South Korea',
    'AU': 'Australia', 'CA': 'Canada', 'FR': 'France', 'ES': 'Spain',
    'NL': 'Netherlands', 'IN': 'India', 'BR': 'Brazil', 'CH': 'Switzerland',
    'SE': 'Sweden', 'DK': 'Denmark', 'BE': 'Belgium', 'AT': 'Austria',
    'NO': 'Norway', 'FI': 'Finland', 'IL': 'Israel', 'SG': 'Singapore',
    'TW': 'Taiwan', 'HK': 'Hong Kong',
}

ALL_COUNTRIES = sorted(
    set(COLLAB_DATA['country_a'].unique().tolist() + COLLAB_DATA['country_b'].unique().tolist()),
    key=lambda c: COUNTRY_NAMES.get(c, c)
)
ALL_COUNTRIES = [c for c in ALL_COUNTRIES if c in COUNTRY_NAMES]

print(f"\n📊 Available countries: {len(ALL_COUNTRIES)}")
for cc in ALL_COUNTRIES[:10]:
    print(f"  {cc} ({COUNTRY_NAMES.get(cc, cc)})")

# %% — Plotting Function
def plot_inst_collab(country_a='US', country_b='CN', top_n=10):
    """
    Plot an interactive bipartite institution-to-institution collaboration network
    between two countries using Plotly.
    
    Args:
        country_a: country code for the left side
        country_b: country code for the right side
        top_n: number of top institutions per country to display
    """
    # Filter data for selected country pair (either direction)
    df = COLLAB_DATA[
        ((COLLAB_DATA['country_a']==country_a)&(COLLAB_DATA['country_b']==country_b)) |
        ((COLLAB_DATA['country_a']==country_b)&(COLLAB_DATA['country_b']==country_a))
    ]
    
    if len(df) == 0:
        print(f"⚠️  No collaboration data between {COUNTRY_NAMES.get(country_a, country_a)} and {COUNTRY_NAMES.get(country_b, country_b)}.")
        return
    
    # Normalize direction: ensure inst_a is always from country_a
    def normalize_row(row):
        if row['country_a'] == country_a:
            return row['inst_a'], row['inst_b'], row['collab_count']
        else:
            return row['inst_b'], row['inst_a'], row['collab_count']
    
    edges = df.apply(normalize_row, axis=1, result_type='expand')
    edges.columns = ['inst_a', 'inst_b', 'collab_count']
    edges = edges.groupby(['inst_a','inst_b'])['collab_count'].sum().reset_index()
    
    # Get top institutions per country
    top_a = edges.groupby('inst_a')['collab_count'].sum().sort_values(ascending=False).head(top_n).index.tolist()
    top_b = edges.groupby('inst_b')['collab_count'].sum().sort_values(ascending=False).head(top_n).index.tolist()
    edges = edges[edges['inst_a'].isin(top_a) & edges['inst_b'].isin(top_b)]
    
    if len(edges) == 0:
        print("⚠️  No edges to display for selected filters.")
        return
    
    # Positions
    n_a, n_b = len(top_a), len(top_b)
    x_left, x_right = 0.0, 1.0
    y_a = {inst: 1 - (i + 0.5) / n_a for i, inst in enumerate(top_a)}
    y_b = {inst: 1 - (i + 0.5) / n_b for i, inst in enumerate(top_b)}
    
    totals_a = edges.groupby('inst_a')['collab_count'].sum()
    totals_b = edges.groupby('inst_b')['collab_count'].sum()
    max_count = edges['collab_count'].max()
    total_collabs = int(edges['collab_count'].sum())
    label_a = COUNTRY_NAMES.get(country_a, country_a)
    label_b = COUNTRY_NAMES.get(country_b, country_b)
    
    fig = go.Figure()
    
    # Draw edges (each with its own hover tooltip)
    for _, row in edges.iterrows():
        if row['inst_a'] in y_a and row['inst_b'] in y_b:
            ya_pos, yb_pos = y_a[row['inst_a']], y_b[row['inst_b']]
            count = int(row['collab_count'])
            lw = 1 + (count / max_count) * 6
            alp = 0.15 + (count / max_count) * 0.65
            
            t = np.linspace(0, 1, 50)
            xp = x_left + t * (x_right - x_left)
            yp = ya_pos + t**2 * (3 - 2*t) * (yb_pos - ya_pos)
            
            fig.add_trace(go.Scatter(
                x=xp, y=yp, mode='lines',
                line=dict(color=f'rgba(0, 180, 216, {alp})', width=lw),
                hoverinfo='text',
                hovertext=f"<b>{row['inst_a']}</b><br>↔<br><b>{row['inst_b']}</b><br><br>Co-publications: <b>{count:,}</b>",
                showlegend=False,
            ))
    
    # Nodes — Country A (left, blue)
    fig.add_trace(go.Scatter(
        x=[x_left]*n_a, y=[y_a[i] for i in top_a], mode='markers',
        marker=dict(size=14, color='#60a5fa', line=dict(width=1.5, color='white')),
        hoverinfo='text',
        hovertext=[f"<b>{i}</b><br>Total co-pubs: {int(totals_a.get(i,0)):,}" for i in top_a],
        showlegend=False,
    ))
    
    # Nodes — Country B (right, red)
    fig.add_trace(go.Scatter(
        x=[x_right]*n_b, y=[y_b[i] for i in top_b], mode='markers',
        marker=dict(size=14, color='#ef4444', line=dict(width=1.5, color='white')),
        hoverinfo='text',
        hovertext=[f"<b>{i}</b><br>Total co-pubs: {int(totals_b.get(i,0)):,}" for i in top_b],
        showlegend=False,
    ))
    
    # Annotations — Left side labels
    for inst_name in top_a:
        y = y_a[inst_name]
        short = inst_name[:40] + '...' if len(inst_name) > 40 else inst_name
        total = int(totals_a.get(inst_name, 0))
        fig.add_annotation(x=x_left, y=y, xanchor='right', yanchor='middle',
                           text=f"<b>{short}</b>  ({total:,})", showarrow=False, xshift=-12,
                           font=dict(size=10, color='white'))
    
    # Annotations — Right side labels
    for inst_name in top_b:
        y = y_b[inst_name]
        short = inst_name[:40] + '...' if len(inst_name) > 40 else inst_name
        total = int(totals_b.get(inst_name, 0))
        fig.add_annotation(x=x_right, y=y, xanchor='left', yanchor='middle',
                           text=f"({total:,})  <b>{short}</b>", showarrow=False, xshift=12,
                           font=dict(size=10, color='white'))
    
    # Country headers
    fig.add_annotation(x=x_left, y=1.05, xanchor='center', yanchor='bottom',
                       text=f"<b>{label_a}</b>", showarrow=False,
                       font=dict(size=14, color='#60a5fa'))
    fig.add_annotation(x=x_right, y=1.05, xanchor='center', yanchor='bottom',
                       text=f"<b>{label_b}</b>", showarrow=False,
                       font=dict(size=14, color='#ef4444'))
    
    fig_height = max(500, max(n_a, n_b) * 55)
    fig.update_layout(
        title=dict(
            text=f"Institution Collaborations: {label_a} ↔ {label_b}<br>"
                 f"<sup>{total_collabs:,} co-publications  •  {len(top_a)} × {len(top_b)} institutions</sup>",
            font=dict(size=16, color='white'), x=0.5, xanchor='center',
        ),
        plot_bgcolor='#0d1b2a', paper_bgcolor='#0d1b2a',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.35, 1.35]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.12]),
        height=fig_height, margin=dict(l=20, r=20, t=60, b=20),
        hoverlabel=dict(bgcolor='#1b2838', font_size=12, font_color='white', bordercolor='#00b4d8'),
    )
    
    fig.show()
    
    print(f"\n📊 Summary: {label_a} ↔ {label_b}")
    print(f"   Total Co-publications: {total_collabs:,}")
    print(f"   {label_a} Institutions: {len(top_a)}")
    print(f"   {label_b} Institutions: {len(top_b)}")

print("✅ Plot function ready")

# %% — Interactive Widgets
country_a_dropdown = widgets.Dropdown(
    options=[(f"{COUNTRY_NAMES.get(cc, cc)} ({cc})", cc) for cc in ALL_COUNTRIES],
    value='US',
    description='Country A:',
    style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
)

country_b_dropdown = widgets.Dropdown(
    options=[(f"{COUNTRY_NAMES.get(cc, cc)} ({cc})", cc) for cc in ALL_COUNTRIES],
    value='CN',
    description='Country B:',
    style={'description_width': '80px'},
    layout=widgets.Layout(width='300px')
)

n_inst_slider = widgets.IntSlider(
    value=10, min=3, max=20, step=1,
    description='Top N:',
    style={'description_width': '50px'},
    layout=widgets.Layout(width='350px')
)

output = widgets.Output()

def on_change(*args):
    with output:
        clear_output(wait=True)
        plot_inst_collab(
            country_a=country_a_dropdown.value,
            country_b=country_b_dropdown.value,
            top_n=n_inst_slider.value,
        )

country_a_dropdown.observe(on_change, names='value')
country_b_dropdown.observe(on_change, names='value')
n_inst_slider.observe(on_change, names='value')

# Layout
controls = widgets.HBox([country_a_dropdown, country_b_dropdown, n_inst_slider])
display(controls, output)
on_change()

# %% [markdown]
# ## How to Use
# - **Country A / Country B** — pick any two countries to compare
# - **Top N** — control how many institutions to show per side (3–20)
# - **Hover** over any curved edge to see the exact institution pair and co-publication count
# - **Hover** over any node to see the institution's total co-publications across all collaborators
# - Edge thickness and opacity scale with collaboration strength
