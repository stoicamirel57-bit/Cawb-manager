import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="CAWB Manager",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .stDataFrame { font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 CAWB Manager")
st.markdown("---")

# Upload fisier
uploaded_file = st.file_uploader("📂 Încarcă fișierul CSV / Excel", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Citire fisier
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Curatare date
    df["Nr colete"] = pd.to_numeric(df["Nr colete"], errors="coerce").fillna(0).astype(int)
    df["Total colete descarcate"] = pd.to_numeric(df["Total colete descarcate"], errors="coerce").fillna(0).astype(int)

    # Extrage Origine si Destinatie din Ruta
    df[["Origine", "Destinatie"]] = df["Ruta"].str.split(" => ", expand=True, n=1)

    # Filtrare: fara parinte
    df_fara_parinte = df[df["CAWB parinte"] == "Fara parinte"].copy()
    df_cu_parinte = df[df["CAWB parinte"] != "Fara parinte"].copy()

    # ── KPIs ──────────────────────────────────────────────
    st.subheader("📊 Statistici Generale")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total CAWB-uri", f"{len(df):,}")
    col2.metric("Fără Părinte", f"{len(df_fara_parinte):,}")
    col3.metric("Cu Părinte", f"{len(df_cu_parinte):,}")
    col4.metric("Total Colete", f"{df['Nr colete'].sum():,}")

    st.markdown("---")

    # ── TABS ──────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🚫 Fără Părinte", "✅ Cu Părinte", "📋 Toate CAWB-urile"])

    def afiseaza_tabel(data, key_suffix):
        # Filtre
        with st.expander("🔍 Filtre", expanded=False):
            col_a, col_b, col_c = st.columns(3)
            origini = ["Toate"] + sorted(data["Origine"].dropna().unique().tolist())
            dest = ["Toate"] + sorted(data["Destinatie"].dropna().unique().tolist())

            origine_sel = col_a.selectbox("Origine", origini, key=f"orig_{key_suffix}")
            dest_sel = col_b.selectbox("Destinație", dest, key=f"dest_{key_suffix}")
            search = col_c.text_input("🔎 Caută CAWB", key=f"search_{key_suffix}")

        filtered = data.copy()
        if origine_sel != "Toate":
            filtered = filtered[filtered["Origine"] == origine_sel]
        if dest_sel != "Toate":
            filtered = filtered[filtered["Destinatie"] == dest_sel]
        if search:
            filtered = filtered[filtered["CAWB"].str.contains(search, case=False, na=False)]

        # Coloane afisate
        cols_show = ["CAWB", "Ruta", "Origine", "Destinatie", "CAWB parinte", "Nr colete", "Total colete descarcate", "Ramas de descarcat"]
        available = [c for c in cols_show if c in filtered.columns]
        display_df = filtered[available].reset_index(drop=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("CAWB-uri filtrate", f"{len(display_df):,}")
        col_m2.metric("Total Colete", f"{display_df['Nr colete'].sum():,}")
        col_m3.metric("Total Descărcate", f"{display_df['Total colete descarcate'].sum():,}")

        st.dataframe(display_df, use_container_width=True, height=450)

        # Download
        buffer = io.BytesIO()
        display_df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Descarcă Excel",
            data=buffer,
            file_name=f"cawb_{key_suffix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{key_suffix}"
        )

    with tab1:
        st.subheader(f"🚫 CAWB-uri Fără Părinte ({len(df_fara_parinte):,})")
        afiseaza_tabel(df_fara_parinte, "fara_parinte")

    with tab2:
        st.subheader(f"✅ CAWB-uri Cu Părinte ({len(df_cu_parinte):,})")
        afiseaza_tabel(df_cu_parinte, "cu_parinte")

    with tab3:
        st.subheader(f"📋 Toate CAWB-urile ({len(df):,})")
        afiseaza_tabel(df, "toate")

else:
    st.info("👆 Te rog încarcă un fișier CSV sau Excel pentru a începe.")
    st.markdown("""
    ### 📌 Coloane necesare în fișier:
    | Coloană | Descriere |
    |---|---|
    | **CAWB** | Codul CAWB |
    | **Ruta** | Origine => Destinație |
    | **CAWB parinte** | Părintele asociat (sau *Fara parinte*) |
    | **Nr colete** | Numărul de colete |
    | **Total colete descarcate** | Colete descărcate |
    | **Ramas de descarcat** | Colete rămase |
    """)
