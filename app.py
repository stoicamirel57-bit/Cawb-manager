import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Iesire Sorter Manager",
    page_icon="🚚",
    layout="wide"
)

# ── CSS personalizat ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #ffffff; }
  [data-testid="stHeader"] { background: #ffffff; }

  h1 { font-size: 28px !important; font-weight: 800 !important; color: #111 !important; }

  div[data-testid="metric-container"] {
    background: #f8f8f8;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 12px 20px;
  }
  div[data-testid="metric-container"] label { color: #777 !important; font-size: 12px !important; }
  div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px !important; font-weight: 800 !important; color: #111 !important;
  }

  .legend-box {
    display: flex; gap: 12px; flex-wrap: wrap; margin: 8px 0 20px 0;
  }
  .leg { padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; }
  .leg-verde  { background: #c8f0c8; color: #1a5c1a; }
  .leg-rosu   { background: #f44336; color: #fff; }
  .leg-mov    { background: #ce93d8; color: #4a1060; }
  .leg-galben { background: #f9e79f; color: #7a6000; }

  .stDataFrame { border: 1px solid #e8e8e8 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Zone mapping ──────────────────────────────────────────────────────────────
SUD   = {'GL','BR','VN','BZ','IL','CL','GR','TR','CT','TL','PH','DB','AG'}
NORDV = {'IS','NT','BC','VS','BT','SV','MM','BH','SM','SJ','CJ','BN',
          'MS','HR','CV','BV','SB','AB','HD','TM','AR','CS','MH','GJ','VL','OT','DJ'}

def get_zone(agency):
    if not agency or pd.isna(agency):
        return 'galben'
    prefix = str(agency).split('_')[0].upper()
    if prefix == 'B':  return 'mov'
    if prefix in SUD:  return 'verde'
    if prefix in NORDV: return 'rosu'
    return 'galben'

ZONE_COLORS = {
    'verde':  '#eafaea',
    'rosu':   '#fdecea',
    'mov':    '#f3e5f5',
    'galben': '#fffde7',
}
ZONE_TEXT = {
    'verde':  '#1a5c1a',
    'rosu':   '#c62828',
    'mov':    '#6a1b9a',
    'galben': '#7a6000',
}

def color_agency(val, col):
    zone = get_zone(val)
    bg   = ZONE_COLORS.get(zone, '#fff')
    fg   = ZONE_TEXT.get(zone, '#333')
    return f'background-color: {bg}; color: {fg}; font-weight: 500; border-radius: 4px;'

def highlight_row(row):
    zone = get_zone(row.get('Agentie livrare', ''))
    colors = {
        'verde':  '#f0fdf0',
        'rosu':   '#fff5f5',
        'mov':    '#fdf5ff',
        'galben': '#fffef0',
    }
    bg = colors.get(zone, '#fff')
    return [f'background-color: {bg}'] * len(row)

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🚚 Iesire Sorter Manager")
st.markdown("---")

uploaded = st.file_uploader(
    "Incarca fisier CSV sau Excel",
    type=["csv", "xlsx", "xls"],
    help="Formate acceptate: CSV, XLSX, XLS"
)

if uploaded:
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Eroare la citirea fisierului: {e}")
        st.stop()

    st.success(f"✅ Fisier incarcat cu succes: **{uploaded.name}** ({len(df):,} randuri)")
    st.markdown("---")

    # ── Statistici ────────────────────────────────────────────────────────────
    st.markdown("### 📊 Statistici Generale")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Colete",      f"{len(df):,}")
    c2.metric("Agentii Ridicare",  f"{df['Agentie ridicare'].nunique():,}")
    c3.metric("Agentii Livrare",   f"{df['Agentie livrare'].nunique():,}")
    c4.metric("Statusuri Unice",   f"{df['Status'].nunique():,}")
    c5.metric("Fisiere incarcate", "1")

    # ── Legenda ───────────────────────────────────────────────────────────────
    st.markdown("**Legenda culori:**")
    st.markdown("""
    <div class="legend-box">
      <div class="leg leg-verde">🟢 Verde – Sud</div>
      <div class="leg leg-rosu">🔴 Rosu – Nord / Vest / International</div>
      <div class="leg leg-mov">🟣 Mov – Bucuresti / Hub-uri</div>
      <div class="leg leg-galben">🟡 Galben – Alte zone</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Filtre & Sortare ──────────────────────────────────────────────────────
    col_f, col_s1, col_s2 = st.columns([3, 1, 1])
    with col_f:
        search = st.text_input("🔍 Cauta dupa colet, agentie, status...", "")
    with col_s1:
        sort_col = st.selectbox("Sorteaza dupa:", [
            "Agentie livrare",
            "Agentie ridicare",
            "Nr colet",
            "Status",
            "Data receptie",
            "Data ultim status",
        ])
    with col_s2:
        sort_dir = st.radio("Directie:", ["↑ A-Z", "↓ Z-A"], horizontal=True)

    # ── Aplicare filtre ───────────────────────────────────────────────────────
    view = df.copy()
    if search.strip():
        mask = view.apply(lambda r: r.astype(str).str.contains(search, case=False, na=False).any(), axis=1)
        view = view[mask]

    ascending = sort_dir == "↑ A-Z"
    view = view.sort_values(by=sort_col, ascending=ascending, na_position='last')

    # ── Randuri per pagina ────────────────────────────────────────────────────
    rpp_col, _, count_col = st.columns([1, 3, 1])
    with rpp_col:
        rpp = st.selectbox("Randuri per pagina:", [25, 50, 100, 200], index=1)
    with count_col:
        st.markdown(f"<div style='padding-top:28px;font-size:13px;color:#555;'>"
                    f"<b>{len(view):,}</b> randuri gasite</div>", unsafe_allow_html=True)

    total_pages = max(1, (len(view) - 1) // rpp + 1)
    page = st.number_input("Pagina:", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * rpp
    page_data = view.iloc[start:start + rpp].reset_index(drop=True)

    st.caption(f"Pagina {page} din {total_pages}  •  "
               f"Randuri {start+1}–{min(start+rpp, len(view))} din {len(view):,}")

    # ── Styling tabel ─────────────────────────────────────────────────────────
    styled = (
        page_data.style
        .apply(highlight_row, axis=1)
        .applymap(lambda v: color_agency(v, 'Agentie ridicare'), subset=['Agentie ridicare'])
        .applymap(lambda v: color_agency(v, 'Agentie livrare'),  subset=['Agentie livrare'])
        .set_properties(**{'font-size': '13px'})
    )

    st.dataframe(styled, use_container_width=True, height=600)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    csv_exp = view.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Descarca datele filtrate (CSV)",
        data=csv_exp,
        file_name="iesire_sorter_export.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Incarca un fisier CSV sau Excel pentru a incepe.")
