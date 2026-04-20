# %% [markdown]
# # 4.3 Publication Trend Lines with 5-Year Prediction
# **Interactive Notebook** — Filter by organ, adjust year range, toggle forecast
#
# Data: HRAlit Database (Kong & Börner, 2024)

# %% — Imports
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

# Set dark theme
plt.rcParams.update({
    'figure.facecolor': '#0d1b2a',
    'axes.facecolor': '#0d1b2a',
    'axes.edgecolor': '#2d4059',
    'text.color': '#e0e0e0',
    'xtick.color': '#7a8c9e',
    'ytick.color': '#7a8c9e',
    'grid.color': '#1b3a4b',
    'grid.alpha': 0.3,
})

print("✅ Imports loaded")

# %% — Load Data
DATA = '/Users/tejassarma/Downloads/Client_Project/Client_Project_Info_Viz_Dataset'

print("Loading publications...")
pub = pd.read_csv(f'{DATA}/hralit_publication.csv.gz', compression='gzip', usecols=['pmid', 'pubyear'])

print("Loading publication-organ links...")
pub_organ = pd.read_csv(f'{DATA}/hralit_publication_subject.csv.gz', compression='gzip')

print(f"  Publications: {len(pub):,}")
print(f"  Pub-organ links: {len(pub_organ):,}")

# %% — Process Data
# Join pub → organ with year
pub_organ_year = pub_organ.merge(pub, on='pmid', how='inner')
pub_organ_year = pub_organ_year.dropna(subset=['pubyear'])
pub_organ_year['pubyear'] = pub_organ_year['pubyear'].astype(int)

# Filter to 1950+ as requested
pub_organ_year = pub_organ_year[pub_organ_year['pubyear'] >= 1950]

# Get ALL unique organs and sort by total publications
organ_totals = pub_organ_year.groupby('organ')['pmid'].nunique().sort_values(ascending=False)
ALL_ORGANS = organ_totals.index.tolist()

print(f"\n📊 Data ready: {len(pub_organ_year):,} records, {len(ALL_ORGANS)} organs")
print(f"Year range: {pub_organ_year['pubyear'].min()} – {pub_organ_year['pubyear'].max()}")
print(f"\nAll {len(ALL_ORGANS)} organs (sorted by publication count):")
for i, organ in enumerate(ALL_ORGANS):
    print(f"  {i+1:2d}. {organ}: {organ_totals[organ]:,} pubs")

# %% — Precompute yearly counts for all organs (this speeds up interactivity)
print("Precomputing yearly counts for all organs...")
year_range = range(1950, 2022)  # 2022-2023 incomplete

organ_yearly = {}
for organ in ALL_ORGANS:
    yearly = pub_organ_year[pub_organ_year['organ'] == organ].groupby('pubyear')['pmid'].nunique()
    organ_yearly[organ] = {y: yearly.get(y, 0) for y in year_range}

print(f"✅ Precomputed {len(ALL_ORGANS)} organs × {len(list(year_range))} years")

# %% — Color palette for organs
ORGAN_COLORS = {}
cmap = plt.cm.get_cmap('tab20', len(ALL_ORGANS))
for i, organ in enumerate(ALL_ORGANS):
    ORGAN_COLORS[organ] = cmap(i)

# Override top organs with distinctive colors
ORGAN_COLORS.update({
    'brain': '#60a5fa', 'heart': '#ef4444', 'kidney': '#34d399',
    'liver': '#f59e0b', 'lung': '#8b5cf6', 'eye': '#06b6d4',
    'skin': '#fb923c', 'large intestine': '#a3e635',
    'pancreas': '#22d3ee', 'bone marrow': '#e879f9',
})

print(f"✅ Colors assigned for {len(ORGAN_COLORS)} organs")

# %% — Define plotting function
def plot_trends(selected_organs, year_start=1950, year_end=2021, 
                show_forecast=True, forecast_years=5):
    """
    Plot publication trends for selected organs.
    
    Args:
        selected_organs: list of organ names to plot
        year_start: start year for display
        year_end: end year for actual data
        show_forecast: whether to show forecast lines
        forecast_years: how many years to forecast (1-10)
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    
    yr_range = range(max(year_start, 1950), min(year_end + 1, 2022))
    forecast_range = range(year_end + 1, year_end + 1 + forecast_years) if show_forecast else []
    
    for organ in selected_organs:
        if organ not in organ_yearly:
            continue
        color = ORGAN_COLORS.get(organ, '#888888')
        
        # Historical data
        years = list(yr_range)
        counts = [organ_yearly[organ].get(y, 0) for y in yr_range]
        
        ax.plot(years, counts, '-', color=color, linewidth=2.5, label=organ.title(),
                path_effects=[pe.withStroke(linewidth=4, foreground='#0d1b2a')])
        
        # Forecast
        if show_forecast and len(forecast_range) > 0:
            # Train on last 20 years of available data
            train_start = max(year_start, year_end - 19)
            train_years = list(range(train_start, year_end + 1))
            train_counts = [organ_yearly[organ].get(y, 0) for y in train_years]
            
            X = np.array(train_years).reshape(-1, 1)
            y = np.array(train_counts)
            
            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(X)
            model = LinearRegression()
            model.fit(X_poly, y)
            
            X_fut = np.array(list(forecast_range)).reshape(-1, 1)
            y_pred = np.maximum(model.predict(poly.transform(X_fut)), 0)
            
            # CI
            residuals = y - model.predict(X_poly)
            ci = 1.96 * np.std(residuals) * np.linspace(1, 2.5, len(forecast_range))
            
            # Bridge
            ax.plot([years[-1], list(forecast_range)[0]], 
                    [counts[-1], y_pred[0]], '--', color=color, linewidth=1.5, alpha=0.7)
            ax.plot(list(forecast_range), y_pred, '--', color=color, linewidth=1.5, alpha=0.8)
            ax.fill_between(list(forecast_range), np.maximum(y_pred - ci, 0), y_pred + ci,
                           color=color, alpha=0.12)
    
    # Today line
    if show_forecast:
        ax.axvline(x=year_end + 0.5, color='#7a8c9e', linewidth=1.5, linestyle=':', alpha=0.7)
        ax.text(year_end + 0.5, ax.get_ylim()[1] * 0.95, '  Today', fontsize=10,
                color='#7a8c9e', fontstyle='italic', va='top')
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Publication Count', fontsize=12, fontweight='bold')
    ax.set_ylim(bottom=0)
    ax.grid(True)
    
    n_organs = len(selected_organs)
    if n_organs <= 8:
        ax.legend(loc='upper left', fontsize=9, framealpha=0.3, edgecolor='#2d4059',
                 facecolor='#0d1b2a', labelcolor='#e0e0e0')
    else:
        ax.legend(loc='upper left', fontsize=7, framealpha=0.3, edgecolor='#2d4059',
                 facecolor='#0d1b2a', labelcolor='#e0e0e0', ncol=2)
    
    title = f'Publication Trends: {", ".join(o.title() for o in selected_organs[:3])}'
    if n_organs > 3:
        title += f' + {n_organs - 3} more'
    fig.suptitle(title, fontsize=15, fontweight='bold', color='white', y=0.98)
    
    plt.tight_layout()
    plt.show()

print("✅ Plot function ready")

# %% — Interactive Widget
# Organ selector (multi-select)
organ_selector = widgets.SelectMultiple(
    options=ALL_ORGANS,
    value=['brain', 'heart', 'kidney', 'liver', 'lung'],
    rows=min(15, len(ALL_ORGANS)),
    description='Organs:',
    layout=widgets.Layout(width='300px'),
    style={'description_width': '60px'}
)

year_start_slider = widgets.IntSlider(
    value=1950, min=1950, max=2015, step=5,
    description='Start Year:', style={'description_width': '80px'},
    layout=widgets.Layout(width='400px')
)

year_end_slider = widgets.IntSlider(
    value=2021, min=1960, max=2021, step=1,
    description='End Year:', style={'description_width': '80px'},
    layout=widgets.Layout(width='400px')
)

forecast_toggle = widgets.Checkbox(
    value=True, description='Show Forecast',
    style={'description_width': '100px'}
)

forecast_years_slider = widgets.IntSlider(
    value=5, min=1, max=10, step=1,
    description='Forecast Years:', style={'description_width': '100px'},
    layout=widgets.Layout(width='300px')
)

# Quick-select buttons
top5_btn = widgets.Button(description='Top 5 Organs', button_style='info')
top10_btn = widgets.Button(description='Top 10 Organs', button_style='info')
all_btn = widgets.Button(description='All Organs', button_style='warning')
clear_btn = widgets.Button(description='Clear', button_style='danger')

def select_top5(b):
    organ_selector.value = ALL_ORGANS[:5]
def select_top10(b):
    organ_selector.value = ALL_ORGANS[:10]
def select_all(b):
    organ_selector.value = ALL_ORGANS
def clear_all(b):
    organ_selector.value = []

top5_btn.on_click(select_top5)
top10_btn.on_click(select_top10)
all_btn.on_click(select_all)
clear_btn.on_click(clear_all)

output = widgets.Output()

def on_change(*args):
    with output:
        clear_output(wait=True)
        if len(organ_selector.value) > 0:
            plot_trends(
                list(organ_selector.value),
                year_start_slider.value,
                year_end_slider.value,
                forecast_toggle.value,
                forecast_years_slider.value
            )
        else:
            print("⚠️  Select at least one organ")

organ_selector.observe(on_change, names='value')
year_start_slider.observe(on_change, names='value')
year_end_slider.observe(on_change, names='value')
forecast_toggle.observe(on_change, names='value')
forecast_years_slider.observe(on_change, names='value')

# Layout
buttons = widgets.HBox([top5_btn, top10_btn, all_btn, clear_btn])
controls_left = widgets.VBox([organ_selector, buttons])
controls_right = widgets.VBox([year_start_slider, year_end_slider, forecast_toggle, forecast_years_slider])
controls = widgets.HBox([controls_left, controls_right])

display(controls, output)

# Trigger initial plot
on_change()

# %% [markdown]
# ## How to Use
# - **Select organs** from the list (Ctrl/Cmd+Click for multiple)
# - Use **Top 5/Top 10/All** buttons for quick selection
# - Adjust **year range** with the sliders
# - Toggle **forecast** on/off and set prediction window
# - The plot updates automatically when you change any filter
