# %% [markdown]
# # 4.2 Sankey — Grant-Linkage: Funder → Organ → Outputs
# **Interactive Notebook** — Filter by year range, select funders and organs
#
# Data: HRAlit Database (Kong & Börner, 2024)

# %% — Imports
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
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

print("Loading data...")
pff = pd.read_csv(f'{DATA}/hralit_pub_funding_funder.csv.gz', compression='gzip',
                  usecols=['pmid', 'funder_name_pubmed'])
pub_organ = pd.read_csv(f'{DATA}/hralit_publication_subject.csv.gz', compression='gzip')
pub = pd.read_csv(f'{DATA}/hralit_publication.csv.gz', compression='gzip', usecols=['pmid', 'pubyear'])
datasets = pd.read_csv(f'{DATA}/hralit_dataset.csv', usecols=['dataset_id', 'organ'])

pub = pub.dropna(subset=['pubyear'])
pub['pubyear'] = pub['pubyear'].astype(int)

print(f"  Funding-pub links: {len(pff):,}")
print(f"  Pub-organ links: {len(pub_organ):,}")
print(f"  Datasets: {len(datasets):,}")

# %% — Process: Group funders
# NIH sub-agencies
NIH_NAMES = ['NHLBI NIH HHS', 'NCI NIH HHS', 'NIDDK NIH HHS', 'NINDS NIH HHS',
             'NIGMS NIH HHS', 'NICHD NIH HHS', 'NIA NIH HHS', 'NIAID NIH HHS',
             'NIMH NIH HHS', 'NEI NIH HHS', 'NCRR NIH HHS', 'NIEHS NIH HHS',
             'NIBIB NIH HHS', 'Intramural NIH HHS']
funder_groups = {n: 'NIH' for n in NIH_NAMES}
funder_groups.update({
    'Medical Research Council': 'MRC (UK)', 'Wellcome Trust': 'Wellcome Trust',
    'Deutsche Forschungsgemeinschaft': 'DFG', 'Howard Hughes Medical Institute': 'HHMI',
    'Canadian Institutes of Health Research': 'CIHR', 'British Heart Foundation': 'BHF',
})
# NSFC
for n in pff[pff['funder_name_pubmed'].str.contains('National Natural Science Foundation of China', case=False, na=False)]['funder_name_pubmed'].unique():
    funder_groups[n] = 'NSFC'
# JSPS
for n in pff[pff['funder_name_pubmed'].str.contains('Japan Society|JSPS', case=False, na=False)]['funder_name_pubmed'].unique():
    funder_groups[n] = 'JSPS'

pff['funder_clean'] = pff['funder_name_pubmed'].map(funder_groups)
pff_clean = pff.dropna(subset=['funder_clean'])

# Add year
pff_clean = pff_clean.merge(pub[['pmid', 'pubyear']], on='pmid', how='inner')

# Link funder → organ
funder_organ = pff_clean.merge(pub_organ, on='pmid', how='inner')

# Available organs & funders
ALL_FUNDERS = funder_organ.groupby('funder_clean')['pmid'].nunique().sort_values(ascending=False).index.tolist()
ALL_ORGANS = funder_organ.groupby('organ')['pmid'].nunique().sort_values(ascending=False).index.tolist()

# Dataset counts per organ
ds_by_organ = datasets.groupby('organ').size().reset_index(name='dataset_count')
ds_by_organ['organ_clean'] = ds_by_organ['organ'].str.replace(r'\s*\(.*\)', '', regex=True).str.strip().str.lower()

print(f"✅ Data ready: {len(ALL_FUNDERS)} funders, {len(ALL_ORGANS)} organs")

# %% — Sankey Drawing Function
FUNDER_COLORS = {
    'NIH': '#ff6b6b', 'Wellcome Trust': '#6bcb77', 'MRC (UK)': '#4ecdc4',
    'DFG': '#ffd93d', 'HHMI': '#a78bfa', 'CIHR': '#f97316',
    'BHF': '#ec4899', 'NSFC': '#facc15', 'JSPS': '#22d3ee',
}
ORGAN_COLORS = {
    'brain': '#60a5fa', 'heart': '#ef4444', 'kidney': '#34d399',
    'liver': '#f59e0b', 'lung': '#8b5cf6', 'eye': '#06b6d4',
    'skin': '#fb923c', 'large intestine': '#a3e635',
    'pancreas': '#22d3ee', 'bone marrow': '#e879f9',
}

def plot_sankey(selected_funders, selected_organs, year_start=2000, year_end=2021):
    """Draw Sankey: Funder → Organ → Outputs for given filters."""
    # Filter data
    mask = (funder_organ['funder_clean'].isin(selected_funders)) & \
           (funder_organ['organ'].isin(selected_organs)) & \
           (funder_organ['pubyear'] >= year_start) & \
           (funder_organ['pubyear'] <= year_end)
    filtered = funder_organ[mask]
    
    if len(filtered) == 0:
        print("⚠️  No data for selected filters")
        return
    
    # Compute flows: Funder → Organ
    flow_fo = filtered.groupby(['funder_clean', 'organ'])['pmid'].nunique().reset_index()
    flow_fo.columns = ['funder', 'organ', 'pub_count']
    
    # Funder & organ totals
    funder_totals = flow_fo.groupby('funder')['pub_count'].sum().sort_values(ascending=False)
    organ_totals = flow_fo.groupby('organ')['pub_count'].sum().sort_values(ascending=False)
    funders_sorted = funder_totals.index.tolist()
    organs_sorted = organ_totals.index.tolist()
    
    # Organ → Output (Publications vs Datasets)
    organ_outputs = []
    for organ in organs_sorted:
        pub_c = organ_totals.get(organ, 0)
        ds_match = ds_by_organ[ds_by_organ['organ_clean'].str.contains(organ.split()[0], case=False, na=False)]
        ds_c = ds_match['dataset_count'].sum() if len(ds_match) > 0 else 0
        organ_outputs.append({'organ': organ, 'Publications': pub_c, 'Datasets': max(ds_c, 1)})
    flow_oo = pd.DataFrame(organ_outputs)
    
    output_totals = {'Publications': flow_oo['Publications'].sum(), 'Datasets': flow_oo['Datasets'].sum()}
    total_output = sum(output_totals.values())
    
    # ---- DRAW ----
    fig, ax = plt.subplots(1, 1, figsize=(16, max(8, len(organs_sorted) * 0.8)))
    
    x_f, x_o, x_out = 0.08, 0.45, 0.82
    col_w = 0.04
    gap = 0.015
    total_flow = funder_totals.sum()
    
    # Compute positions
    def compute_positions(sorted_items, totals, total_sum):
        heights, positions = {}, {}
        y = 0.95
        for item in sorted_items:
            h = max((totals[item] / total_sum) * 0.75, 0.02)
            heights[item] = h
            positions[item] = y
            y -= h + gap
        return heights, positions
    
    f_h, f_y = compute_positions(funders_sorted, funder_totals, total_flow)
    o_h, o_y = compute_positions(organs_sorted, organ_totals, total_flow)
    
    out_h, out_y = {}, {}
    y = 0.80
    for name in ['Publications', 'Datasets']:
        h = max((output_totals[name] / total_output) * 0.5, 0.04)
        out_h[name] = h
        out_y[name] = y
        y -= h + gap * 3
    
    # Draw bars
    for f in funders_sorted:
        color = FUNDER_COLORS.get(f, '#888')
        rect = plt.Rectangle((x_f, f_y[f] - f_h[f]), col_w, f_h[f], facecolor=color, alpha=0.9,
                              edgecolor='white', linewidth=0.5, transform=ax.transAxes, zorder=5)
        ax.add_patch(rect)
        ax.text(x_f - 0.01, f_y[f] - f_h[f]/2, f, transform=ax.transAxes, fontsize=8,
                ha='right', va='center', color='white', fontweight='bold',
                path_effects=[pe.withStroke(linewidth=1, foreground='black')])
    
    for o in organs_sorted:
        color = ORGAN_COLORS.get(o, '#888')
        rect = plt.Rectangle((x_o, o_y[o] - o_h[o]), col_w, o_h[o], facecolor=color, alpha=0.9,
                              edgecolor='white', linewidth=0.5, transform=ax.transAxes, zorder=5)
        ax.add_patch(rect)
        ax.text(x_o + col_w/2, o_y[o] - o_h[o]/2, o.title(), transform=ax.transAxes, fontsize=7,
                ha='center', va='center', color='white', fontweight='bold',
                path_effects=[pe.withStroke(linewidth=2, foreground='black')])
    
    for name in ['Publications', 'Datasets']:
        color = '#00b4d8' if name == 'Publications' else '#e9c46a'
        rect = plt.Rectangle((x_out, out_y[name] - out_h[name]), col_w, out_h[name], facecolor=color, alpha=0.9,
                              edgecolor='white', linewidth=0.5, transform=ax.transAxes, zorder=5)
        ax.add_patch(rect)
        ax.text(x_out + col_w + 0.01, out_y[name] - out_h[name]/2, f'{name}\n({output_totals[name]:,})',
                transform=ax.transAxes, fontsize=9, ha='left', va='center', color='white', fontweight='bold')
    
    # Draw flows: Funder → Organ
    f_cursor = {f: f_y[f] for f in funders_sorted}
    o_cursor_l = {o: o_y[o] for o in organs_sorted}
    
    for _, row in flow_fo.sort_values('pub_count', ascending=False).iterrows():
        f, o, count = row['funder'], row['organ'], row['pub_count']
        if f not in f_h or o not in o_h:
            continue
        bh_f = (count / funder_totals[f]) * f_h[f]
        bh_o = (count / organ_totals[o]) * o_h[o]
        y1t, y2t = f_cursor[f], o_cursor_l[o]
        y1b, y2b = y1t - bh_f, y2t - bh_o
        f_cursor[f] = y1b
        o_cursor_l[o] = y2b
        
        color = FUNDER_COLORS.get(f, '#888')
        t = np.linspace(0, 1, 50)
        x_pts = (x_f + col_w) + t * (x_o - x_f - col_w)
        y_top = y1t + t**2 * (3 - 2*t) * (y2t - y1t)
        y_bot = y1b + t**2 * (3 - 2*t) * (y2b - y1b)
        ax.fill_between(x_pts, y_bot, y_top, alpha=0.2, color=color, transform=ax.transAxes, zorder=2)
    
    # Draw flows: Organ → Output
    o_cursor_r = {o: o_y[o] for o in organs_sorted}
    out_cursor = {n: out_y[n] for n in ['Publications', 'Datasets']}
    
    for _, row in flow_oo.iterrows():
        o = row['organ']
        if o not in o_h:
            continue
        color = ORGAN_COLORS.get(o, '#888')
        ot = organ_totals.get(o, 1)
        for name in ['Publications', 'Datasets']:
            count = row[name]
            if count <= 0:
                continue
            bh_o = (count / ot) * o_h[o]
            bh_out = (count / output_totals[name]) * out_h[name]
            y1t, y2t = o_cursor_r[o], out_cursor[name]
            y1b, y2b = y1t - bh_o, y2t - bh_out
            o_cursor_r[o] = y1b
            out_cursor[name] = y2b
            t = np.linspace(0, 1, 50)
            x_pts = (x_o + col_w) + t * (x_out - x_o - col_w)
            y_top = y1t + t**2 * (3 - 2*t) * (y2t - y1t)
            y_bot = y1b + t**2 * (3 - 2*t) * (y2b - y1b)
            ax.fill_between(x_pts, y_bot, y_top, alpha=0.15, color=color, transform=ax.transAxes, zorder=2)
    
    # Headers
    ax.text(x_f + col_w/2, 0.99, 'FUNDERS', transform=ax.transAxes, fontsize=11, ha='center', fontweight='bold', color='#00b4d8')
    ax.text(x_o + col_w/2, 0.99, 'ORGANS', transform=ax.transAxes, fontsize=11, ha='center', fontweight='bold', color='#00b4d8')
    ax.text(x_out + col_w/2, 0.99, 'OUTPUTS', transform=ax.transAxes, fontsize=11, ha='center', fontweight='bold', color='#00b4d8')
    
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    
    fig.suptitle(f'Grant-Linkage Sankey ({year_start}–{year_end})', fontsize=15, fontweight='bold', color='white', y=0.99)
    plt.show()

print("✅ Sankey function ready")

# %% — Interactive Controls
funder_sel = widgets.SelectMultiple(
    options=ALL_FUNDERS, value=ALL_FUNDERS[:6], rows=min(10, len(ALL_FUNDERS)),
    description='Funders:', layout=widgets.Layout(width='250px'), style={'description_width': '60px'}
)
organ_sel = widgets.SelectMultiple(
    options=ALL_ORGANS, value=ALL_ORGANS[:6], rows=min(12, len(ALL_ORGANS)),
    description='Organs:', layout=widgets.Layout(width='250px'), style={'description_width': '60px'}
)
yr_start = widgets.IntSlider(value=2000, min=1950, max=2018, description='Year Start:', style={'description_width': '80px'}, layout=widgets.Layout(width='350px'))
yr_end = widgets.IntSlider(value=2021, min=1960, max=2021, description='Year End:', style={'description_width': '80px'}, layout=widgets.Layout(width='350px'))

# Quick buttons
top6f = widgets.Button(description='Top 6 Funders', button_style='info')
allf = widgets.Button(description='All Funders', button_style='warning')
top6o = widgets.Button(description='Top 6 Organs', button_style='info')
allo = widgets.Button(description='All Organs', button_style='warning')

top6f.on_click(lambda b: setattr(funder_sel, 'value', ALL_FUNDERS[:6]))
allf.on_click(lambda b: setattr(funder_sel, 'value', ALL_FUNDERS))
top6o.on_click(lambda b: setattr(organ_sel, 'value', ALL_ORGANS[:6]))
allo.on_click(lambda b: setattr(organ_sel, 'value', ALL_ORGANS))

output = widgets.Output()

def on_change(*args):
    with output:
        clear_output(wait=True)
        if len(funder_sel.value) > 0 and len(organ_sel.value) > 0:
            plot_sankey(list(funder_sel.value), list(organ_sel.value), yr_start.value, yr_end.value)
        else:
            print("⚠️  Select at least one funder and one organ")

for w in [funder_sel, organ_sel, yr_start, yr_end]:
    w.observe(on_change, names='value')

controls = widgets.HBox([
    widgets.VBox([funder_sel, widgets.HBox([top6f, allf])]),
    widgets.VBox([organ_sel, widgets.HBox([top6o, allo])]),
    widgets.VBox([yr_start, yr_end]),
])
display(controls, output)
on_change()

# %% [markdown]
# ## How to Use
# - **Funders**: Select which funding agencies to include
# - **Organs**: Select which organs to include
# - **Year range**: Filter to specific time periods
# - Band width = co-linked publication count
