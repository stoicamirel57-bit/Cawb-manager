import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CAWB Manager", page_icon="📦", layout="wide")
st.title("📦 CAWB Manager")
st.markdown("---")

uploaded_file = st.file_uploader("📂 Incarca fisierul CSV / Excel", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df["Nr colete"] = pd.to_numeric(df["Nr colete"], errors="coerce").fillna(0).astype(int)
    df["Total colete descarcate"] = pd.to_numeric(df["Total colete descarcate"], errors="coerce").fillna(0).astype(int)
    df["Ramas de descarcat"] = pd.to_numeric(df["Ramas de descarcat"], errors="coerce").fillna(0).astype(int)

    split_ruta = df["Ruta"].str.split(" => ", expand=True, n=1)
    df["Origine"] = split_ruta[0]
    df["Destinatie"] = split_ruta[1] if 1 in split_ruta.columns else ""

    df_fara_parinte = df[df["CAWB parinte"] == "Fara parinte"].copy()
    df_cu_parinte = df[df["CAWB parinte"] != "Fara parinte"].copy()

    st.subheader("Statistici Generale")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total CAWB-uri", f"{len(df):,}")
    col2.metric("Fara Parinte", f"{len(df_fara_parinte):,}")
    col3.metric("Cu Parinte", f"{len(df_cu_parinte):,}")
    col4.metric("Total Colete", f"{df['Nr colete'].sum():,}")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Fara Parinte", "Cu Parinte", "Toate CAWB-urile"])

    def afiseaza_tabel(data, key_suffix):
        st.markdown("### 🔍 Filtre")
        col_a, col_b = st.columns(2)
        col_c, col_d = st.columns(2)
        col_e, col_f = st.columns(2)

        origini = ["Toate"] + sorted(data["Origine"].dropna().unique().tolist())
        dest = ["Toate"] + sorted(data["Destinatie"].dropna().unique().tolist())
        tipuri = sorted(data["Tip"].dropna().unique().tolist())

        origine_sel = col_a.selectbox("Origine", origini, key="orig_" + key_suffix)
        dest_sel = col_b.selectbox("Destinatie", dest, key="dest_" + key_suffix)

        tipuri_sel = col_c.multiselect("Tip CAWB", options=tipuri, default=tipuri, key="tip_" + key_suffix)

        search = col_d.text_input("Cauta CAWB", key="search_" + key_suffix)

        min_c = int(data["Nr colete"].min())
        max_c = int(data["Nr colete"].max())
        if min_c < max_c:
            colete_range = col_e.slider("Nr Colete (interval)", min_value=min_c, max_value=max_c, value=(1, max_c), key="colete_" + key_suffix)
        else:
            colete_range = (min_c, max_c)

        ascunde_zero = col_f.checkbox("Ascunde CAWB-urile cu 0 colete", value=True, key="zero_" + key_suffix)

        st.markdown("---")

        filtered = data.copy()
        if ascunde_zero:
            filtered = filtered[filtered["Nr colete"] > 0]
        if origine_sel != "Toate":
            filtered = filtered[filtered["Origine"] == origine_sel]
        if dest_sel != "Toate":
            filtered = filtered[filtered["Destinatie"] == dest_sel]
        if tipuri_sel:
            filtered = filtered[filtered["Tip"].isin(tipuri_sel)]
        if search:
            filtered = filtered[filtered["CAWB"].str.contains(search, case=False, na=False)]
        filtered = filtered[(filtered["Nr colete"] >= colete_range[0]) & (filtered["Nr colete"] <= colete_range[1])]

        cols_show = ["CAWB", "Tip", "Ruta", "Origine", "Destinatie", "CAWB parinte", "Nr colete", "Total colete descarcate", "Ramas de descarcat"]
        available = [c for c in cols_show if c in filtered.columns]
        display_df = filtered[available].reset_index(drop=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("CAWB-uri filtrate", f"{len(display_df):,}")
        c2.metric("Total Colete", f"{display_df['Nr colete'].sum():,}")
        c3.metric("Total Descarcate", f"{display_df['Total colete descarcate'].sum():,}")

        st.dataframe(display_df, use_container_width=True, height=450)

        buffer = io.BytesIO()
        display_df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button("📥 Descarca Excel", data=buffer, file_name="cawb_" + key_suffix + ".xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_" + key_suffix)

    with tab1:
        st.subheader("CAWB-uri Fara Parinte (" + str(len(df_fara_parinte)) + ")")
        afiseaza_tabel(df_fara_parinte, "fara_parinte")
    with tab2:
        st.subheader("CAWB-uri Cu Parinte (" + str(len(df_cu_parinte)) + ")")
        afiseaza_tabel(df_cu_parinte, "cu_parinte")
    with tab3:
        st.subheader("Toate CAWB-urile (" + str(len(df)) + ")")
        afiseaza_tabel(df, "toate")

else:
    st.info("Te rog incarca un fisier CSV sau Excel pentru a incepe.")
