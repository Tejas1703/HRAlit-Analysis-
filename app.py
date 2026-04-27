"""
HRAlit Interactive Dashboard — Hugging Face Spaces Deployment
Pre-aggregated data version for fast cloud loading.
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import os, json, time, warnings
warnings.filterwarnings('ignore')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="HRAlit Interactive Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    .stApp { background-color: #0a1628; }
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b3a4b 50%, #00647d 100%);
        padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
        border: 1px solid #2d4059;
    }
    .main-header h1 { color: #e0e0e0; font-size: 2rem; margin: 0; font-weight: 700; }
    .main-header p { color: #7a8c9e; margin: 0.3rem 0 0 0; font-size: 0.95rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #0d1b2a; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: #1b2838; border-radius: 6px; color: #7a8c9e; padding: 8px 20px; border: 1px solid #2d4059; }
    .stTabs [data-baseweb="tab"]:hover { background-color: #2d4059; color: #e0e0e0; }
    .stTabs [aria-selected="true"] { background-color: #00647d !important; color: white !important; border-color: #00b4d8 !important; }
    [data-testid="stSidebar"] { background-color: #0d1b2a; border-right: 1px solid #2d4059; }
    [data-testid="stSidebar"] .stMarkdown h3 { color: #00b4d8; font-size: 1.1rem; border-bottom: 1px solid #2d4059; padding-bottom: 0.5rem; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stSelectbox label, .stMultiSelect label, .stSlider label, .stCheckbox label, .stRadio label { color: #e0e0e0 !important; }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA LOADING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@st.cache_data
def load_data():
    d = {}
    d['trends'] = pd.read_csv(f'{DATA_DIR}/trends_organ_year.csv')
    d['sankey'] = pd.read_csv(f'{DATA_DIR}/sankey_funder_organ_year.csv')
    d['ds_counts'] = pd.read_csv(f'{DATA_DIR}/dataset_counts.csv')
    d['heatmap'] = pd.read_csv(f'{DATA_DIR}/heatmap_inst_funder.csv')
    d['geo_authors'] = pd.read_csv(f'{DATA_DIR}/geo_authors.csv')
    d['geo_organ_authors'] = pd.read_csv(f'{DATA_DIR}/geo_organ_authors.csv')
    d['geo_collabs'] = pd.read_csv(f'{DATA_DIR}/geo_collaborations.csv')
    d['geo_organ_collabs'] = pd.read_csv(f'{DATA_DIR}/geo_organ_collaborations.csv')
    d['geo_funding'] = pd.read_csv(f'{DATA_DIR}/geo_funding_intensity.csv')
    d['geo_pubs'] = pd.read_csv(f'{DATA_DIR}/geo_pubs.csv')
    d['geo_organ_pubs'] = pd.read_csv(f'{DATA_DIR}/geo_organ_pubs.csv')
    
    # Sorted lists
    d['all_organs_trends'] = d['trends'].groupby('organ')['pub_count'].sum().sort_values(ascending=False).index.tolist()
    d['all_funders'] = d['sankey'].groupby('funder')['pub_count'].sum().sort_values(ascending=False).index.tolist()
    d['all_organs_sankey'] = d['sankey'].groupby('organ')['pub_count'].sum().sort_values(ascending=False).index.tolist()
    d['all_countries'] = d['heatmap'].groupby('country')['pub_count'].sum().sort_values(ascending=False).index.tolist()
    d['all_funders_heat'] = d['heatmap'].groupby('funder')['pub_count'].sum().sort_values(ascending=False).index.tolist()
    d['all_organs_geo'] = d['geo_organ_authors'].groupby('organ')['author_count'].sum().sort_values(ascending=False).index.tolist()
    
    # Precompute trends pivot
    d['organ_yearly'] = {}
    for organ in d['all_organs_trends']:
        organ_data = d['trends'][d['trends']['organ'] == organ].set_index('year')['pub_count']
        d['organ_yearly'][organ] = {y: organ_data.get(y, 0) for y in range(1950, 2023)}
    
    # Load world boundaries GeoJSON for map basemap
    geo_path = os.path.join(DATA_DIR, 'world_boundaries.json')
    if os.path.exists(geo_path):
        with open(geo_path) as gf:
            d['world_geo'] = json.load(gf)
    else:
        d['world_geo'] = None
    
    # Load institution collaboration data (Enhancement 6)
    inst_path = os.path.join(DATA_DIR, 'inst_collaborations.csv')
    if os.path.exists(inst_path):
        d['inst_collabs'] = pd.read_csv(inst_path).dropna()
    else:
        d['inst_collabs'] = None
    
    return d


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DARK_BG = '#0d1b2a'
FUNDER_COLORS = {
    'NIH': '#ff6b6b', 'Wellcome': '#6bcb77', 'MRC': '#4ecdc4',
    'DFG': '#ffd93d', 'HHMI': '#a78bfa', 'CIHR': '#f97316',
    'BHF': '#ec4899', 'NSFC': '#facc15', 'JSPS': '#22d3ee', 'NSF': '#818cf8',
}
ORGAN_COLORS = {
    'brain': '#60a5fa', 'heart': '#ef4444', 'kidney': '#34d399',
    'liver': '#f59e0b', 'lung': '#8b5cf6', 'eye': '#06b6d4',
    'skin': '#fb923c', 'large intestine': '#a3e635',
    'pancreas': '#22d3ee', 'bone marrow': '#e879f9',
}
COUNTRY_NAMES = {
    'US': 'United States', 'CN': 'China', 'GB': 'United Kingdom',
    'JP': 'Japan', 'DE': 'Germany', 'IT': 'Italy', 'KR': 'South Korea',
    'AU': 'Australia', 'CA': 'Canada', 'FR': 'France', 'ES': 'Spain',
    'NL': 'Netherlands', 'IN': 'India', 'BR': 'Brazil', 'CH': 'Switzerland',
    'SE': 'Sweden', 'DK': 'Denmark', 'BE': 'Belgium',
}
COUNTRY_POS = {
    'US': (-98, 39), 'CN': (104, 35), 'GB': (-1, 53), 'JP': (138, 36),
    'DE': (10, 51), 'IT': (12, 42), 'KR': (128, 36), 'AU': (134, -25),
    'CA': (-106, 56), 'FR': (2, 47), 'ES': (-4, 40), 'NL': (5, 52),
    'IN': (79, 22), 'BR': (-51, -10), 'CH': (8, 47), 'SE': (15, 62),
    'DK': (10, 56), 'BE': (4, 51), 'AT': (14, 47), 'NO': (9, 62),
    'FI': (26, 64), 'IL': (35, 31), 'SG': (104, 1), 'TW': (121, 24),
    'HK': (114, 22), 'MX': (-102, 23), 'RU': (37, 55), 'TR': (35, 39),
    'PL': (20, 52), 'GR': (22, 39), 'PT': (-8, 39), 'IE': (-8, 53),
    'ZA': (25, -29), 'NZ': (172, -42),
}
MPL_STYLE = {
    'figure.facecolor': DARK_BG, 'axes.facecolor': DARK_BG,
    'axes.edgecolor': '#2d4059', 'text.color': '#e0e0e0',
    'xtick.color': '#7a8c9e', 'ytick.color': '#7a8c9e',
    'grid.color': '#1b3a4b', 'grid.alpha': 0.3,
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: SANKEY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_sankey(data):
    st.sidebar.markdown("### 🔗 Sankey Filters")
    sel_funders = st.sidebar.multiselect("Funders", data['all_funders'], default=data['all_funders'][:6], key='s_f')
    sel_organs = st.sidebar.multiselect("Organs", data['all_organs_sankey'], default=data['all_organs_sankey'][:6], key='s_o')
    yr = st.sidebar.slider("Year Range", 1950, 2022, (2000, 2022), key='s_yr')
    show_flow_labels = st.sidebar.checkbox("Show Labels", value=True, key='s_labels')
    
    if not sel_funders or not sel_organs:
        st.warning("Select at least one funder and one organ."); return
    
    df = data['sankey']
    df = df[(df['funder'].isin(sel_funders)) & (df['organ'].isin(sel_organs)) & (df['year'] >= yr[0]) & (df['year'] <= yr[1])]
    
    if len(df) == 0:
        st.warning("No data for selected filters."); return
    
    flow_fo = df.groupby(['funder', 'organ'])['pub_count'].sum().reset_index()
    funder_totals = flow_fo.groupby('funder')['pub_count'].sum().sort_values(ascending=False)
    organ_totals = flow_fo.groupby('organ')['pub_count'].sum().sort_values(ascending=False)
    funders_sorted = funder_totals.index.tolist()
    organs_sorted = organ_totals.index.tolist()
    
    ds_by_organ = data['ds_counts']
    organ_outputs = []
    for organ in organs_sorted:
        pub_c = organ_totals.get(organ, 0)
        ds_match = ds_by_organ[ds_by_organ['organ_clean'].str.contains(organ.split()[0], case=False, na=False)]
        ds_c = ds_match['dataset_count'].sum() if len(ds_match) > 0 else 0
        organ_outputs.append({'organ': organ, 'Publications': pub_c, 'Datasets': max(ds_c, 1)})
    flow_oo = pd.DataFrame(organ_outputs)
    output_totals = {'Publications': flow_oo['Publications'].sum(), 'Datasets': flow_oo['Datasets'].sum()}
    total_output = sum(output_totals.values())
    
    plt.rcParams.update(MPL_STYLE)
    fig, ax = plt.subplots(1, 1, figsize=(16, max(8, len(organs_sorted) * 0.8)))
    x_f, x_o, x_out = 0.08, 0.45, 0.82
    col_w, gap = 0.04, 0.015
    total_flow = funder_totals.sum()
    
    def compute_pos(items, totals, total_sum):
        h, p = {}, {}; y = 0.95
        for i in items:
            hh = max((totals[i] / total_sum) * 0.75, 0.02); h[i] = hh; p[i] = y; y -= hh + gap
        return h, p
    
    f_h, f_y = compute_pos(funders_sorted, funder_totals, total_flow)
    o_h, o_y = compute_pos(organs_sorted, organ_totals, total_flow)
    out_h, out_y = {}, {}; y = 0.80
    for name in ['Publications', 'Datasets']:
        h = max((output_totals[name] / total_output) * 0.5, 0.04); out_h[name] = h; out_y[name] = y; y -= h + gap * 3
    
    for f in funders_sorted:
        c = FUNDER_COLORS.get(f, '#888')
        ax.add_patch(plt.Rectangle((x_f, f_y[f]-f_h[f]), col_w, f_h[f], facecolor=c, alpha=0.9, edgecolor='white', linewidth=0.5, transform=ax.transAxes, zorder=5))
        f_label = f'{f}  ({funder_totals[f]:,})'
        ax.text(x_f-0.01, f_y[f]-f_h[f]/2, f_label, transform=ax.transAxes, fontsize=8, ha='right', va='center', color='white', fontweight='bold', path_effects=[pe.withStroke(linewidth=1, foreground='black')])
    for o in organs_sorted:
        c = ORGAN_COLORS.get(o, '#888')
        ax.add_patch(plt.Rectangle((x_o, o_y[o]-o_h[o]), col_w, o_h[o], facecolor=c, alpha=0.9, edgecolor='white', linewidth=0.5, transform=ax.transAxes, zorder=5))
        ax.text(x_o+col_w+0.01, o_y[o]-o_h[o]/2, o.title(), transform=ax.transAxes, fontsize=8, ha='left', va='center', color='white', fontweight='bold', path_effects=[pe.withStroke(linewidth=2, foreground='black')])
    for name in ['Publications', 'Datasets']:
        c = '#00b4d8' if name == 'Publications' else '#e9c46a'
        ax.add_patch(plt.Rectangle((x_out, out_y[name]-out_h[name]), col_w, out_h[name], facecolor=c, alpha=0.9, edgecolor='white', linewidth=0.5, transform=ax.transAxes, zorder=5))
        ax.text(x_out+col_w+0.01, out_y[name]-out_h[name]/2, f'{name}\n({output_totals[name]:,})', transform=ax.transAxes, fontsize=9, ha='left', va='center', color='white', fontweight='bold')
    
    min_label_flow = total_flow * 0.01  # Only label flows > 1% of total
    f_cur = {f: f_y[f] for f in funders_sorted}; o_cur = {o: o_y[o] for o in organs_sorted}
    for _, row in flow_fo.sort_values('pub_count', ascending=False).iterrows():
        f, o, cnt = row['funder'], row['organ'], row['pub_count']
        if f not in f_h or o not in o_h: continue
        bh_f = (cnt/funder_totals[f])*f_h[f]; bh_o = (cnt/organ_totals[o])*o_h[o]
        y1t, y2t = f_cur[f], o_cur[o]; y1b, y2b = y1t-bh_f, y2t-bh_o
        f_cur[f] = y1b; o_cur[o] = y2b
        t = np.linspace(0,1,50); xp = (x_f+col_w)+t*(x_o-x_f-col_w)
        yt = y1t+t**2*(3-2*t)*(y2t-y1t); yb = y1b+t**2*(3-2*t)*(y2b-y1b)
        ax.fill_between(xp, yb, yt, alpha=0.2, color=FUNDER_COLORS.get(f,'#888'), transform=ax.transAxes, zorder=2)
        # Enhancement 5: Add count label on flow band (gated by Show Labels toggle)
        if show_flow_labels and cnt >= min_label_flow:
            mid_x = (x_f + col_w + x_o) / 2
            mid_y = (y1t + y1b + y2t + y2b) / 4
            ax.text(mid_x, mid_y, f'{cnt:,}', transform=ax.transAxes, fontsize=6, ha='center', va='center',
                    color='white', fontweight='bold', alpha=0.85, path_effects=[pe.withStroke(linewidth=2, foreground='black')], zorder=3)
    
    o_cur_r = {o: o_y[o] for o in organs_sorted}; out_cur = {n: out_y[n] for n in ['Publications','Datasets']}
    for _, row in flow_oo.iterrows():
        o = row['organ']
        if o not in o_h: continue
        ot = organ_totals.get(o, 1)
        for name in ['Publications','Datasets']:
            cnt = row[name]
            if cnt <= 0: continue
            bh_o = (cnt/ot)*o_h[o]; bh_out = (cnt/output_totals[name])*out_h[name]
            y1t, y2t = o_cur_r[o], out_cur[name]; y1b, y2b = y1t-bh_o, y2t-bh_out
            o_cur_r[o] = y1b; out_cur[name] = y2b
            t = np.linspace(0,1,50); xp = (x_o+col_w)+t*(x_out-x_o-col_w)
            yt = y1t+t**2*(3-2*t)*(y2t-y1t); yb = y1b+t**2*(3-2*t)*(y2b-y1b)
            ax.fill_between(xp, yb, yt, alpha=0.15, color=ORGAN_COLORS.get(o,'#888'), transform=ax.transAxes, zorder=2)
    
    ax.text(x_f+col_w/2, 0.99, 'FUNDERS', transform=ax.transAxes, fontsize=11, ha='center', fontweight='bold', color='#00b4d8')
    ax.text(x_o+col_w/2, 0.99, 'ORGANS', transform=ax.transAxes, fontsize=11, ha='center', fontweight='bold', color='#00b4d8')
    ax.text(x_out+col_w/2, 0.99, 'OUTPUTS', transform=ax.transAxes, fontsize=11, ha='center', fontweight='bold', color='#00b4d8')
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    fig.suptitle(f'Grant-Linkage Sankey ({yr[0]}–{yr[1]})', fontsize=15, fontweight='bold', color='white', y=0.99)
    st.pyplot(fig); plt.close(fig)
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Funded Publications", f"{int(df['pub_count'].sum()):,}")
    c2.metric("Funders", len(funders_sorted)); c3.metric("Organs", len(organs_sorted))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: TRENDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_trends(data):
    st.sidebar.markdown("### 📈 Trend Filters")
    presets = st.sidebar.radio("Quick Select", ["Top 5","Top 10","All","Custom"], key='t_p', horizontal=True)
    all_organs = data['all_organs_trends']
    
    # Sync Quick Select radio with multiselect via session state
    preset_map = {"Top 5": all_organs[:5], "Top 10": all_organs[:10], "All": all_organs}
    if presets != "Custom":
        desired = preset_map[presets]
        if st.session_state.get('t_o') != desired:
            st.session_state['t_o'] = desired
    
    sel = st.sidebar.multiselect("Organs", all_organs, default=all_organs[:5], key='t_o')
    yr = st.sidebar.slider("Year Range", 1950, 2022, (1950, 2022), key='t_yr')
    fc = st.sidebar.checkbox("Show Forecast", value=True, key='t_fc')
    fc_n = st.sidebar.slider("Forecast Years", 1, 10, 5, key='t_fn') if fc else 0
    
    # Enhancement 4: Animation controls
    animate = st.sidebar.button("▶ Animate", key='t_anim')
    anim_speed = st.sidebar.select_slider("Animation Speed", options=["Slow","Medium","Fast"], value="Medium", key='t_spd')
    speed_map = {"Slow": 0.2, "Medium": 0.08, "Fast": 0.03}
    
    if not sel: st.warning("Select at least one organ."); return
    
    organ_yearly = data['organ_yearly']
    yr_range = list(range(max(yr[0],1950), min(yr[1]+1,2023)))
    forecast_range = list(range(yr[1]+1, yr[1]+1+fc_n)) if fc else []
    cmap_tab = plt.cm.get_cmap('tab20', len(all_organs))
    
    # Precompute colors and forecast data
    organ_colors = {}
    organ_fc = {}
    for organ in sel:
        if organ not in organ_yearly: continue
        organ_colors[organ] = ORGAN_COLORS.get(organ, cmap_tab(all_organs.index(organ) if organ in all_organs else 0))
        if fc and len(forecast_range) > 0:
            ts = max(yr[0], yr[1]-19); ty = list(range(ts, yr[1])); tc = [organ_yearly[organ].get(y,0) for y in ty]
            X = np.array(ty).reshape(-1,1); y_a = np.array(tc)
            poly = PolynomialFeatures(degree=2); Xp = poly.fit_transform(X)
            model = LinearRegression(); model.fit(Xp, y_a)
            Xf = np.array(forecast_range).reshape(-1,1); yp = np.maximum(model.predict(poly.transform(Xf)),0)
            res = y_a - model.predict(Xp); ci = 1.96*np.std(res)*np.linspace(1,2.5,len(forecast_range))
            organ_fc[organ] = (yp, ci)
    
    def _draw_trends_frame(years_to_show, fc_years_to_show=0):
        plt.rcParams.update(MPL_STYLE)
        fig, ax = plt.subplots(1, 1, figsize=(14, 7))
        for organ in sel:
            if organ not in organ_yearly: continue
            color = organ_colors.get(organ, '#888')
            yrs = years_to_show; cts = [organ_yearly[organ].get(y,0) for y in yrs]
            ax.plot(yrs, cts, '-', color=color, linewidth=2.5, label=organ.title(), path_effects=[pe.withStroke(linewidth=4, foreground=DARK_BG)])
            if fc and fc_years_to_show > 0 and organ in organ_fc:
                yp, ci = organ_fc[organ]
                fc_yrs = forecast_range[:fc_years_to_show]; yp_s = yp[:fc_years_to_show]; ci_s = ci[:fc_years_to_show]
                ax.plot([yrs[-1], fc_yrs[0]], [cts[-1], yp_s[0]], '--', color=color, linewidth=1.5, alpha=0.7)
                ax.plot(fc_yrs, yp_s, '--', color=color, linewidth=1.5, alpha=0.8)
                ax.fill_between(fc_yrs, np.maximum(yp_s-ci_s,0), yp_s+ci_s, color=color, alpha=0.12)
        if fc and fc_years_to_show > 0:
            ax.axvline(x=yr[1]+0.5, color='#7a8c9e', linewidth=1.5, linestyle=':', alpha=0.7)
            ax.axvline(x=2026, color='#7a8c9e', linewidth=1.5, linestyle='-', alpha=0.7)
            ax.text(2026, ax.get_ylim()[1]*0.95, '  Today', fontsize=10, color='#7a8c9e', fontstyle='italic', va='top')
        ax.set_xlabel('Year', fontsize=12, fontweight='bold', color='#e0e0e0'); ax.set_ylabel('Publication Count', fontsize=12, fontweight='bold', color='#e0e0e0')
        # Set consistent axis limits for animation
        all_x = yr_range + forecast_range
        ax.set_xlim(min(all_x)-1, max(all_x)+3); ax.set_ylim(bottom=0); ax.grid(True)
        ncol = 2 if len(sel) > 8 else 1
        ax.legend(loc='upper left', fontsize=8 if len(sel)>8 else 9, framealpha=0.3, edgecolor='#2d4059', facecolor=DARK_BG, labelcolor='#e0e0e0', ncol=ncol)
        title = f'Publication Trends: {", ".join(o.title() for o in sel[:3])}' + (f' + {len(sel)-3} more' if len(sel) > 3 else '')
        fig.suptitle(title, fontsize=15, fontweight='bold', color='white', y=0.98)
        plt.tight_layout()
        return fig
    
    if animate:
        chart_placeholder = st.empty()
        delay = speed_map.get(anim_speed, 0.08)
        # Animate historical data in chunks of 5 years
        step = max(1, len(yr_range) // 30)
        for i in range(step, len(yr_range)+1, step):
            fig = _draw_trends_frame(yr_range[:i])
            chart_placeholder.pyplot(fig); plt.close(fig)
            time.sleep(delay)
        # Show full historical
        fig = _draw_trends_frame(yr_range)
        chart_placeholder.pyplot(fig); plt.close(fig)
        time.sleep(delay * 2)
        # Animate forecast year by year
        if fc and len(forecast_range) > 0:
            for i in range(1, len(forecast_range)+1):
                fig = _draw_trends_frame(yr_range, fc_years_to_show=i)
                chart_placeholder.pyplot(fig); plt.close(fig)
                time.sleep(delay * 3)
    else:
        # Static rendering (original behavior)
        fig = _draw_trends_frame(yr_range, fc_years_to_show=len(forecast_range) if fc else 0)
        st.pyplot(fig); plt.close(fig)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3: HEATMAP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_heatmap(data):
    st.sidebar.markdown("### 🗺️ Heatmap Filters")
    co = {f"{COUNTRY_NAMES.get(c,c)} ({c})": c for c in data['all_countries'][:20]}
    sel_label = st.sidebar.selectbox("Country", list(co.keys()), key='h_c')
    sel_country = co[sel_label]
    n_inst = st.sidebar.slider("Top N Institutions", 3, 20, 10, key='h_n')
    yr = st.sidebar.slider("Year Range", 2000, 2022, (2000, 2022), key='h_yr')
    #sel_funders = st.sidebar.multiselect("Funders", data['all_funders_heat'], default=data['all_funders_heat'], key='h_f')
    
    df = data['heatmap']
    mask = (df['country']==sel_country) & (df['year']>=yr[0]) & (df['year']<=yr[1])
    #if sel_funders: mask = mask & (df['funder'].isin(sel_funders))
    filtered = df[mask]
    
    if len(filtered) == 0:
        st.warning(f"No data for {COUNTRY_NAMES.get(sel_country,sel_country)} in {yr[0]}–{yr[1]}"); return
    
    top_insts = filtered.groupby('institution')['pub_count'].sum().sort_values(ascending=False).head(n_inst).index.tolist()
    #avail_funders = sel_funders if sel_funders else filtered.groupby('funder')['pub_count'].sum().sort_values(ascending=False).index.tolist()[:10]
    avail_funders = filtered.groupby('funder')['pub_count'].sum().sort_values(ascending=False).index.tolist()[:10]

    mat = filtered[filtered['institution'].isin(top_insts)].groupby(['institution','funder'])['pub_count'].sum().unstack(fill_value=0)
    mat = mat.reindex(index=top_insts, columns=avail_funders).fillna(0)
    mat = mat.loc[:, mat.sum() > 0]
    if mat.empty: st.warning("No co-linked publications found"); return
    
    plt.rcParams.update(MPL_STYLE)
    fig, ax = plt.subplots(1,1, figsize=(max(10, len(mat.columns)*1.5), max(6, len(mat)*0.7)))
    cmap = LinearSegmentedColormap.from_list('c', [DARK_BG,'#1b3a4b','#00647d','#00b4d8','#48cae4','#e9c46a','#f4a261','#e76f51'], N=256)
    d = mat.values.astype(float)
    im = ax.imshow(d, cmap=cmap, aspect='auto', interpolation='nearest', vmin=0, vmax=max(d.max(),1))
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = int(d[i,j])
            if v > 0: ax.text(j,i,f'{v:,}',ha='center',va='center',fontsize=8,fontweight='bold',color='black' if v>d.max()*0.55 else 'white')
    short = [n[:35]+'...' if len(n)>35 else n for n in mat.index]
    ax.set_yticks(range(len(short))); ax.set_yticklabels(short, fontsize=9)
    ax.set_xticks(range(len(mat.columns))); ax.set_xticklabels([label[:50] for label in mat.columns], fontsize=10, fontweight='bold', rotation=30, ha='right')
    for i in range(d.shape[0]+1): ax.axhline(i-0.5, color='#2d4059', linewidth=0.3)
    for j in range(d.shape[1]+1): ax.axvline(j-0.5, color='#2d4059', linewidth=0.3)
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label('Co-linked Publications', fontsize=10, color='#e0e0e0'); cbar.ax.tick_params(colors='#7a8c9e', labelsize=9)
    total = int(filtered['pub_count'].sum())
    ax.set_title(f'{COUNTRY_NAMES.get(sel_country,sel_country)} — Top {len(mat)} Institutions × Funders ({yr[0]}–{yr[1]})\n{total:,} funded publications - Institution Pairs', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Funded Publications", f"{total:,}"); c2.metric("Institutions Shown", len(mat)); c3.metric("Active Funders", len(mat.columns))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4: GEO MAP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _get_geo_data(data, organ, yr_start, yr_end, top_n):
    """Helper: compute author counts, collaboration edges, funding intensity for a given organ+year range."""
    if organ == 'All':
        ac = data['geo_authors']
        ac = ac[(ac['year']>=yr_start)&(ac['year']<=yr_end)].groupby('country')['author_count'].sum()
        pubs_df = data['geo_pubs']
        pubs_df = pubs_df[(pubs_df['year']>=yr_start)&(pubs_df['year']<=yr_end)]
        total_pubs = int(pubs_df['pub_count'].sum())
    else:
        ac = data['geo_organ_authors']
        ac = ac[(ac['organ']==organ)&(ac['year']>=yr_start)&(ac['year']<=yr_end)].groupby('country')['author_count'].sum()
        pubs_df = data['geo_organ_pubs']
        pubs_df = pubs_df[(pubs_df['organ']==organ)&(pubs_df['year']>=yr_start)&(pubs_df['year']<=yr_end)]
        total_pubs = int(pubs_df['pub_count'].sum())
    if organ == 'All':
        collabs = data['geo_collabs']
    else:
        collabs = data['geo_organ_collabs']
        collabs = collabs[collabs['organ']==organ]
    collabs = collabs[(collabs['period_start']>=yr_start-4)&(collabs['period_end']<=yr_end+4)]
    top_edges = collabs.groupby(['c1','c2'])['collab_count'].sum().sort_values(ascending=False).head(top_n)
    fi = data['geo_funding']
    fi = fi[(fi['year']>=yr_start)&(fi['year']<=yr_end)].groupby('country')['avg_funders'].mean()
    return ac, total_pubs, top_edges, fi

def _draw_geo_map(ax, data, ac, top_edges, fi, min_auth, show_labels, title_str):
    """Helper: render the actual map on a given axes."""
    from matplotlib.patches import Polygon as MplPolygon
    from matplotlib.collections import PatchCollection
    ax.set_facecolor(DARK_BG)
    world_geo = data.get('world_geo')
    if world_geo:
        patches = []
        for feat in world_geo['features']:
            geom = feat['geometry']
            if geom['type'] == 'Polygon':
                for ring in geom['coordinates']:
                    if len(ring) > 2:
                        patches.append(MplPolygon(ring, closed=True))
            elif geom['type'] == 'MultiPolygon':
                for poly in geom['coordinates']:
                    for ring in poly:
                        if len(ring) > 2:
                            patches.append(MplPolygon(ring, closed=True))
        if patches:
            pc = PatchCollection(patches, facecolor="#203552", edgecolor='#2d4059', linewidth=1, alpha=1, zorder=1)
            ax.add_collection(pc)
    max_edge = top_edges.max() if len(top_edges) > 0 else 1
    for (c1,c2), count in top_edges.items():
        if c1 not in COUNTRY_POS or c2 not in COUNTRY_POS: continue
        x1,y1 = COUNTRY_POS[c1]; x2,y2 = COUNTRY_POS[c2]
        lw = 0.5+(count/max_edge)*4; alp = 0.2+(count/max_edge)*0.5
        ax.plot([x1,x2],[y1,y2],'-',color='#00b4d8',linewidth=lw,alpha=alp,zorder=2)
    max_count = ac.max() if len(ac) > 0 else 1
    cmap_fund = LinearSegmentedColormap.from_list('f',['#34d399','#f59e0b','#ef4444'],N=256)
    max_fund = fi.max() if len(fi) > 0 else 1
    for cc, count in ac.items():
        if cc not in COUNTRY_POS or count < min_auth: continue
        x,y = COUNTRY_POS[cc]; size = 30+(count/max_count)*600
        fv = fi.get(cc, 0); color = cmap_fund(fv/max_fund) if max_fund > 0 else '#34d399'
        ax.scatter(x,y,s=size,c=[color],alpha=0.85,edgecolors='white',linewidth=0.5,zorder=4)
        if show_labels and count >= max_count * 0.05:
            ax.text(x,y+3,COUNTRY_NAMES.get(cc,cc),ha='center',va='bottom',fontsize=7,color='white',fontweight='bold',
                    path_effects=[pe.withStroke(linewidth=2,foreground=DARK_BG)],zorder=5)
    ax.set_xlim(-180,180); ax.set_ylim(-60,85); ax.set_xticks([]); ax.set_yticks([])
    
    # Dynamic abbreviation legend: show full names for short country codes
    abbrev_entries = []
    for cc in ac.index:
        if cc in COUNTRY_POS and cc not in COUNTRY_NAMES and ac[cc] >= min_auth:
            abbrev_entries.append(f"{cc} = {cc}")  # no full name known, just show code
        elif cc in COUNTRY_POS and len(COUNTRY_NAMES.get(cc, cc)) > 2 and COUNTRY_NAMES.get(cc, cc) == cc:
            abbrev_entries.append(f"{cc}")
    # For codes that ARE in COUNTRY_NAMES but display as short (2-letter) labels
    displayed_abbrevs = []
    for cc in ac.index:
        if cc in COUNTRY_POS and ac[cc] >= ac.max() * 0.05:
            full_name = COUNTRY_NAMES.get(cc, cc)
            if full_name == cc and len(cc) <= 3:  # still abbreviated
                displayed_abbrevs.append(cc)
    # Build legend mapping for ALL known short codes visible on the map  
    FULL_COUNTRY_NAMES = {
        'TR': 'Turkey', 'TW': 'Taiwan', 'PL': 'Poland', 'HK': 'Hong Kong',
        'SG': 'Singapore', 'IL': 'Israel', 'MX': 'Mexico', 'RU': 'Russia',
        'AT': 'Austria', 'NO': 'Norway', 'FI': 'Finland', 'GR': 'Greece',
        'PT': 'Portugal', 'IE': 'Ireland', 'ZA': 'South Africa', 'NZ': 'New Zealand',
    }
    legend_lines = []
    for cc in sorted(ac.index):
        if cc in COUNTRY_POS and ac[cc] >= ac.max() * 0.05:
            if cc not in COUNTRY_NAMES and cc in FULL_COUNTRY_NAMES:
                legend_lines.append(f"{cc} = {FULL_COUNTRY_NAMES[cc]}")
            elif cc not in COUNTRY_NAMES and cc not in FULL_COUNTRY_NAMES:
                legend_lines.append(f"{cc}")
    if legend_lines:
        legend_text = '\n'.join(legend_lines)
        ax.text(175, 80, legend_text, fontsize=6, color='#7a8c9e', ha='right', va='top',
                fontfamily='monospace', bbox=dict(boxstyle='round,pad=0.3', facecolor=DARK_BG, edgecolor='#2d4059', alpha=0.8), zorder=10)
    
    ax.set_title(title_str, fontsize=11, fontweight='bold', color='white', pad=10)

def render_geo(data):
    st.sidebar.markdown("### 🌍 Map Filters")
    all_organs = data['all_organs_geo']
    
    # Enhancement 3: Compare Mode
    compare_mode = st.sidebar.checkbox("Compare Mode (2 organs)", value=False, key='g_cmp')
    if compare_mode:
        organ_a = st.sidebar.selectbox("Organ A", ['All'] + all_organs, index=1, key='g_oa')
        organ_b = st.sidebar.selectbox("Organ B", ['All'] + all_organs, index=2, key='g_ob')
    else:
        sel_organ = st.sidebar.selectbox("Organ", ['All'] + all_organs, key='g_o')
    
    # Enhancement 2: Time Mode
    time_mode = st.sidebar.radio("Time Mode", ["Range", "Step-Through"], key='g_tm', horizontal=True)
    if time_mode == "Step-Through":
        window = st.sidebar.select_slider("Window Size", options=[1,3,5], value=3, key='g_win')
        current_year = st.sidebar.slider("Year", 1950+window, 2023, 2022, key='g_sy')
        yr_start, yr_end = current_year - window + 1, current_year
    else:
        yr_range = st.sidebar.slider("Year Range", 1950, 2023, (2018, 2023), key='g_yr')
        yr_start, yr_end = yr_range[0], yr_range[1]
    
    top_n = st.sidebar.slider("Top N Edges", 5, 100, 30, step=5, key='g_e')
    min_auth = st.sidebar.slider("Min Authors", 1, 500, 50, step=10, key='g_m')
    show_labels = st.sidebar.checkbox("Show Labels", value=True, key='g_l')
    
    plt.rcParams.update(MPL_STYLE)
    
    if compare_mode:
        # Side-by-side rendering
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        ac_a, pubs_a, edges_a, fi_a = _get_geo_data(data, organ_a, yr_start, yr_end, top_n)
        ac_b, pubs_b, edges_b, fi_b = _get_geo_data(data, organ_b, yr_start, yr_end, top_n)
        label_a = organ_a.title() if organ_a != 'All' else 'All Organs'
        label_b = organ_b.title() if organ_b != 'All' else 'All Organs'
        intl_a = int(edges_a.sum()) if len(edges_a) > 0 else 0
        intl_b = int(edges_b.sum()) if len(edges_b) > 0 else 0
        _draw_geo_map(ax1, data, ac_a, edges_a, fi_a, min_auth, show_labels,
                      f'{label_a} — {yr_start}–{yr_end}\n{pubs_a:,} pubs  •  {intl_a:,} links')
        _draw_geo_map(ax2, data, ac_b, edges_b, fi_b, min_auth, show_labels,
                      f'{label_b} — {yr_start}–{yr_end}\n{pubs_b:,} pubs  •  {intl_b:,} links')
        plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        col1, col2 = st.columns(2)
        col1.metric(f"{label_a} Publications", f"{pubs_a:,}")
        col2.metric(f"{label_b} Publications", f"{pubs_b:,}")
    else:
        # Single map
        ac, total_pubs, top_edges, fi = _get_geo_data(data, sel_organ, yr_start, yr_end, top_n)
        if len(ac) == 0:
            st.warning(f"No data for {sel_organ} in {yr_start}–{yr_end}"); return
        intl_count = int(top_edges.sum()) if len(top_edges) > 0 else 0
        organ_label = sel_organ.title() if sel_organ != 'All' else 'All Organs'
        fig, ax = plt.subplots(1, 1, figsize=(16, 9))
        _draw_geo_map(ax, data, ac, top_edges, fi, min_auth, show_labels,
                      f'{organ_label} — {yr_start}–{yr_end}\n{total_pubs:,} publications  •  {intl_count:,} collaboration links  •  {len(ac)} countries')
        plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        c1,c2,c3 = st.columns(3)
        c1.metric("Publications", f"{total_pubs:,}"); c2.metric("Collaboration Links", f"{intl_count:,}"); c3.metric("Countries", len(ac))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5: INSTITUTION COLLABORATIONS (Enhancement 6 — Plotly Interactive)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_inst_collab(data):
    inst_collabs = data.get('inst_collabs')
    if inst_collabs is None or len(inst_collabs) == 0:
        st.info("Institution collaboration data is not yet available. Run the pre-aggregation script to generate it.")
        return
    
    import plotly.graph_objects as go
    
    st.sidebar.markdown("### 🏛️ Institution Filters")
    countries_list = sorted(set(inst_collabs['country_a'].unique().tolist() + inst_collabs['country_b'].unique().tolist()))
    countries_list = [c for c in countries_list if c in COUNTRY_NAMES]
    country_labels = {c: COUNTRY_NAMES.get(c, c) for c in countries_list}
    sorted_countries = sorted(countries_list, key=lambda c: country_labels[c])
    
    default_a = 'US' if 'US' in sorted_countries else sorted_countries[0]
    default_b = 'CN' if 'CN' in sorted_countries else sorted_countries[1] if len(sorted_countries) > 1 else sorted_countries[0]
    
    country_a = st.sidebar.selectbox("Country A", sorted_countries, index=sorted_countries.index(default_a),
                                      format_func=lambda c: f"{COUNTRY_NAMES.get(c,c)} ({c})", key='ic_a')
    country_b = st.sidebar.selectbox("Country B", sorted_countries, index=sorted_countries.index(default_b),
                                      format_func=lambda c: f"{COUNTRY_NAMES.get(c,c)} ({c})", key='ic_b')
    top_n = st.sidebar.slider("Top N Institutions", 5, 20, 10, key='ic_n')
    
    # Filter data for selected country pair (either direction)
    df = inst_collabs[
        ((inst_collabs['country_a']==country_a)&(inst_collabs['country_b']==country_b)) |
        ((inst_collabs['country_a']==country_b)&(inst_collabs['country_b']==country_a))
    ]
    
    if len(df) == 0:
        st.warning(f"No collaboration data between {COUNTRY_NAMES.get(country_a,country_a)} and {COUNTRY_NAMES.get(country_b,country_b)}.")
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
    total_collabs = int(edges['collab_count'].sum())
    
    # Get top institutions per country
    top_a = edges.groupby('inst_a')['collab_count'].sum().sort_values(ascending=False).head(top_n).index.tolist()
    top_a_totals = edges.groupby('inst_a')['collab_count'].sum().sort_values(ascending=False).head(top_n)
    top_b = edges.groupby('inst_b')['collab_count'].sum().sort_values(ascending=False).head(top_n).index.tolist()
    top_b_totals = edges.groupby('inst_b')['collab_count'].sum().sort_values(ascending=False).head(top_n)
    edges = edges[edges['inst_a'].isin(top_a) & edges['inst_b'].isin(top_b)]
    
    if len(edges) == 0:
        st.warning("No edges to display for selected filters."); return
    
    # ── Plotly interactive bipartite network ──
    import plotly.graph_objects as go
    
    n_a, n_b = len(top_a), len(top_b)
    x_left, x_right = 0.0, 1.0
    
    y_a = {inst: 1 - (i + 0.5) / n_a for i, inst in enumerate(top_a)}
    y_b = {inst: 1 - (i + 0.5) / n_b for i, inst in enumerate(top_b)}
    
    totals_a = edges.groupby('inst_a')['collab_count'].sum()
    totals_b = edges.groupby('inst_b')['collab_count'].sum()
    
    max_count = edges['collab_count'].max()
    #total_collabs = int(edges['collab_count'].sum())
    label_a = COUNTRY_NAMES.get(country_a, country_a)
    label_b = COUNTRY_NAMES.get(country_b, country_b)
    
    fig = go.Figure()
    
    # Draw edges as individual traces (each gets its own hover tooltip)
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
    
    # Draw nodes — Country A (left, blue)
    node_x_a = [x_left] * n_a
    node_y_a = [y_a[inst] for inst in top_a]
    node_text_a = [f"<b>{inst}</b><br>Total co-pubs with {label_b}: {int(top_a_totals.get(inst, 0)):,}" for inst in top_a]
    fig.add_trace(go.Scatter(
        x=node_x_a, y=node_y_a, mode='markers',
        marker=dict(size=14, color='#60a5fa', line=dict(width=1.5, color='white')),
        hoverinfo='text', hovertext=node_text_a, showlegend=False,
    ))
    
    # Draw nodes — Country B (right, red)
    node_x_b = [x_right] * n_b
    node_y_b = [y_b[inst] for inst in top_b]
    node_text_b = [f"<b>{inst}</b><br>Total co-pubs with {label_a}: {int(top_b_totals.get(inst, 0)):,}" for inst in top_b]
    fig.add_trace(go.Scatter(
        x=node_x_b, y=node_y_b, mode='markers',
        marker=dict(size=14, color='#ef4444', line=dict(width=1.5, color='white')),
        hoverinfo='text', hovertext=node_text_b, showlegend=False,
    ))
    
    # Institution name annotations (left — right-aligned)
    for i, inst in enumerate(top_a):
        y = y_a[inst]
        short = inst[:40] + '...' if len(inst) > 40 else inst
        total = int(top_a_totals.get(inst, 0))
        fig.add_annotation(
            x=x_left, y=y, xanchor='right', yanchor='middle',
            text=f"<b>{short}</b>  ({total:,})",
            showarrow=False, xshift=-12,
            font=dict(size=10, color='white'),
        )
    
    # Institution name annotations (right — left-aligned)
    for inst in top_b:
        y = y_b[inst]
        short = inst[:40] + '...' if len(inst) > 40 else inst
        total = int(top_b_totals.get(inst, 0))
        fig.add_annotation(
            x=x_right, y=y, xanchor='left', yanchor='middle',
            text=f"({total:,})  <b>{short}</b>",
            showarrow=False, xshift=12,
            font=dict(size=10, color='white'),
        )
    
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
            text=f"Top Institution Collaborations: {label_a} ↔ {label_b}<br><sup>{total_collabs:,} co-publications</sup>",
            font=dict(size=16, color='white'),
            x=0.5, xanchor='center',
        ),
        plot_bgcolor='#0d1b2a',
        paper_bgcolor='#0d1b2a',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.35, 1.35]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.12]),
        height=fig_height,
        margin=dict(l=20, r=20, t=60, b=20),
        hoverlabel=dict(bgcolor='#1b2838', font_size=12, font_color='white', bordercolor='#00b4d8'),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Co-publications", f"{total_collabs:,}")
    c2.metric(f"{label_a} Institutions", len(top_a))
    c3.metric(f"{label_b} Institutions", len(top_b))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🧬 HRAlit Interactive Dashboard</h1>
        <p>Exploring publication, funding, and collaboration patterns in the Human Reference Atlas literature database</p>
    </div>
    """, unsafe_allow_html=True)
    
    data = load_data()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔗 Grant-Linkage Sankey",
        "📈 Publication Trends",
        "🗺️ Institution–Funder Heatmap",
        "🌍 Global Collaboration Map",
        "🏛️ Institution Collaborations",
    ])
    
    with tab1:
        st.markdown("#### Funder → Organ → Output Flow")
        st.caption("Band width represents the number of co-linked publications. Use sidebar filters to explore.")
        render_sankey(data)
    with tab2:
        st.markdown("#### Publication Count Trends with Forecast")
        st.caption("Historical trends from 1950–2022 with polynomial regression forecast. Click ▶ Animate to watch trends grow.")
        render_trends(data)
    with tab3:
        st.markdown("#### Top Institutions × Funders by Country")
        st.caption("Cell values = co-linked publication count. Select a country to see its funding landscape.")
        render_heatmap(data)
    with tab4:
        st.markdown("#### International Co-Publication Network")
        st.caption("Bubble size = author count, color = funding intensity. Lines = collaborations. Toggle Compare Mode or Step-Through time.")
        render_geo(data)
    with tab5:
        st.markdown("#### Bipartite Institution–Institution Co-Publication Network")
        st.caption("Select two countries to see which institutions collaborate most. Edge thickness = co-publication count.")
        render_inst_collab(data)
    
    st.markdown("---")
    st.caption("Data: HRAlit Database (Kong & Börner, 2024) • Built with Streamlit & Matplotlib")

if __name__ == '__main__':
    main()


### Changes:
# 1. Heatmap - change data file to include all funders, changed grouping of NIH to get anything with 'NIH' in string, 
# change avail_funders line, comment out select funders box and references to it, instead taking top 10 per country.
# Limit length of title funder title to 50 characters

# 2. Institution-Institution Colab Network - Changed totals next to institution names to be total for all collaborations with other country

# 3. Change year to max year to 2023 from 2021, except for trend data, which requires complete year data for accurate predictions.