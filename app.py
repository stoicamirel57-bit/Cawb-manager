import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CAWB Manager", page_icon="parcels", layout="wide")
st.title("CAWB Manager")
st.markdown("---")

MIJLOACE_TRANSPORT = sorted([
    'IF32YAC', 'CL27ABS', 'IF69AMS', 'IF19TEX', 'IF07SNA', 'IF87MGV', 'IF21MGW',
    'IF35TEX', 'GR21TEX', 'IF57STM', 'IF90SNA', 'IF96STM', 'B125MLK', 'IL51DOD',
    'BR78CEH', 'IF68SMA', 'CL30ABS', 'B150MLK', 'IF43MGV', 'IF15ANS', 'IF42STT',
    'IF41MGV', 'IF92STM', 'IF20MGW', 'IF19SNA', 'IF93STM', 'B724SMA', 'BR73CEH',
    'IF54MGV', 'IF15YAC', 'GR20ALR', 'IF98SNA', 'BR71CEH', 'IF38AMS', 'IF41AMS',
    'IF20SNA', 'IF11YAC', 'IF94STM', 'IF51ASM', 'IF28AMS', 'B165MLK', 'IF98STM',
    'IF78MGV', 'BR75CEH', 'IF29SNA', 'IL16DOD', 'B151TKT', 'GR26MNU', 'IF78STM',
    'IF39ASM', 'B163MLK', 'IL64BMG', 'IF64SMA', 'B168MLK', 'IF53MGV', 'BR77CEH',
    'IL19DOD', 'GR24ZZI', 'IF32MGV', 'IF30YAC', 'IF36MGV', 'IL44DOD', 'IF42YAC',
    'IF96SNA', 'IF44ANS', 'IL94DOD', 'BR72CEH', 'IF18VXX', 'IF86SMA', 'IF67MGV',
    'IL23BGM', 'IF93ANS', 'IF02MGW', 'IF70MGV', 'IF31TEX', 'IF26MGW', 'GR14TEX',
    'IF42SSA', 'IF47YAC', 'IF94MGV', 'TR20DEN', 'IF93AMS', 'IF52STM', 'IF89MGV',
    'CL25ABS', 'IF28YAC', 'GR11CXB', 'TR10TEN', 'IF26ANS', 'IF32MGW', 'IF71MGV',
    'IF19MGW', 'TR97TEN', 'MH92TOX', 'IF20DTI', 'IF29MGW', 'IF79MGV', 'IF72MGV'
])

def get_zona(dest):
    if not isinstance(dest, str):
        return "Alta", "#FFFFFF"
    d = dest.strip()
    exact_mov = ['DC2_R30_OCT_H01', 'DC1_R30_OTC_H01']
    if d in exact_mov:
        return "Mov", "#C27BA0"
    exact_rosu = ['SOF_SOFIAHUB_H01']
    if d in exact_rosu:
        return "Rosu", "#FF4444"
    exact_verde = ['CV_SFGHEORGHE_A01', 'CT_MEGIDIA_A05', 'GR_GIURGIU_A02', 'CL_CALARASI_A01']
    if d in exact_verde:
        return "Verde", "#C6EFCE"
    mov_patterns = ['B_A0', 'B_PO', 'B_ST', 'B_MO', 'B_HUB', 'B_BRAG', 'B_STEF', 'LOCKERE', 'SB_SIBIU_H']
    for p in mov_patterns:
        if d.startswith(p):
            return "Mov", "#C27BA0"
    prefix2 = d[:2]
    verde = ['BZ', 'DJ', 'OT', 'BR', 'DB', 'PH', 'IL', 'AG', 'TR']
    if prefix2 in verde:
        return "Verde", "#C6EFCE"
    rosu = ['IS', 'CJ', 'MM', 'BN', 'CS', 'SV', 'BH', 'TM', 'SM', 'SJ', 'BT', 'AR', 'SD']
    if prefix2 in rosu:
        return "Rosu", "#FF4444"
    if d.startswith('MS_TGM') or d.startswith('MS_TGMURES'):
        return "Rosu", "#FF4444"
    galben = ['SB', 'BC', 'CT', 'TL', 'HD', 'VL', 'NT', 'VN', 'MS', 'HR', 'GJ', 'MH', 'GL', 'BV', 'AB', 'VS']
    if prefix2 in galben:
        return "Galben", "#FFEB9C"
    return "Alta", "#FFFFFF"

def coloreaza(row):
    _, culoare = get_zona(row.get("Destinatie", ""))
    return ["background-color: " + culoare] * len(row)

uploaded_files = st.file_uploader(
    "Incarca unul sau mai multe fisiere CSV / Excel",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    dfs = []
    for f in uploaded_files:
        try:
            if f.name.endswith(".csv"):
                temp = pd.read_csv(f)
            else:
                temp = pd.read_excel(f)
            temp["Fisier sursa"] = f.name
            dfs.append(temp)
            st.success("Fisier incarcat cu succes: " + f.name + " (" + str(len(temp)) + " randuri)")
        except Exception as e:
            st.error("Eroare la fisierul " + f.name + ": " + str(e))

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df["Nr colete"] = pd.to_numeric(df["Nr colete"], errors="coerce").fillna(0).astype(int)
        df["Total colete descarcate"] = pd.to_numeric(df["Total colete descarcate"], errors="coerce").fillna(0).astype(int)
        df["Ramas de descarcat"] = pd.to_numeric(df["Ramas de descarcat"], errors="coerce").fillna(0).astype(int)
        split_ruta = df["Ruta"].str.split(" => ", expand=True, n=1)
        df["Origine"] = split_ruta[0]
        df["Destinatie"] = split_ruta[1] if 1 in split_ruta.columns else ""
        df["Culoare"] = df["Destinatie"].apply(lambda x: get_zona(x)[0])
        df_fara_parinte = df[df["CAWB parinte"] == "Fara parinte"].copy()
        df_cu_parinte = df[df["CAWB parinte"] != "Fara parinte"].copy()

        st.markdown("---")
        st.subheader("Statistici Generale")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Fisiere incarcate", str(len(dfs)))
        col2.metric("Total CAWB-uri", f"{len(df):,}")
        col3.metric("Fara Parinte", f"{len(df_fara_parinte):,}")
        col4.metric("Cu Parinte", f"{len(df_cu_parinte):,}")
        col5.metric("Total Colete", f"{df['Nr colete'].sum():,}")

        st.markdown("---")
        st.markdown("**Legenda culori:**")
        lc1, lc2, lc3, lc4 = st.columns(4)
        lc1.markdown('<div style="background-color:#C6EFCE;padding:8px;border-radius:5px;text-align:center"><b>Verde - Sud</b></div>', unsafe_allow_html=True)
        lc2.markdown('<div style="background-color:#FF4444;padding:8px;border-radius:5px;text-align:center;color:white"><b>Rosu - Nord / Vest / International</b></div>', unsafe_allow_html=True)
        lc3.markdown('<div style="background-color:#C27BA0;padding:8px;border-radius:5px;text-align:center;color:white"><b>Mov - Bucuresti / Hub-uri</b></div>', unsafe_allow_html=True)
        lc4.markdown('<div style="background-color:#FFEB9C;padding:8px;border-radius:5px;text-align:center"><b>Galben - Alte zone</b></div>', unsafe_allow_html=True)
        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["Fara Parinte", "Cu Parinte", "Toate CAWB-urile", "Mijloace Transport"])

        def afiseaza_tabel(data, key_suffix, include_transport=False):
            st.markdown("### Filtre")
            col_a, col_b = st.columns(2)
            col_c, col_d = st.columns(2)
            col_e, col_f = st.columns(2)

            origini = ["Toate"] + sorted(data["Origine"].dropna().unique().tolist())
            dest = ["Toate"] + sorted(data["Destinatie"].dropna().unique().tolist())
            tipuri = sorted(data["Tip"].dropna().unique().tolist())
            culori_disponibile = ["Toate"] + sorted(data["Culoare"].dropna().unique().tolist())

            origine_sel = col_a.selectbox("Origine", origini, key="orig_" + key_suffix)
            dest_sel = col_b.selectbox("Destinatie", dest, key="dest_" + key_suffix)
            tipuri_sel = col_c.multiselect("Tip CAWB", options=tipuri, default=tipuri, key="tip_" + key_suffix)
            culoare_sel = col_d.selectbox("Culoare", culori_disponibile, key="culoare_" + key_suffix)

            min_c = int(data["Nr colete"].min())
            max_c = int(data["Nr colete"].max())
            if min_c < max_c:
                colete_range = col_e.slider("Nr Colete (interval)", min_value=min_c, max_value=max_c, value=(1, max_c), key="colete_" + key_suffix)
            else:
                colete_range = (min_c, max_c)

            col_f1, col_f2 = col_f.columns(2)
            ascunde_zero = col_f1.checkbox("Ascunde 0 colete", value=True, key="zero_" + key_suffix)
            search = col_f2.text_input("Cauta CAWB", key="search_" + key_suffix)

            masini_selectate = []
            if include_transport:
                st.markdown("**Filtru Mijloc de Transport:**")
                btn1, btn2, _ = st.columns([1, 1, 4])
                if btn1.button("Selecteaza toate", key="sel_" + key_suffix):
                    st.session_state["masini_" + key_suffix] = MIJLOACE_TRANSPORT
                if btn2.button("Deselecteaza toate", key="desel_" + key_suffix):
                    st.session_state["masini_" + key_suffix] = []
                if "masini_" + key_suffix not in st.session_state:
                    st.session_state["masini_" + key_suffix] = []
                masini_selectate = st.multiselect(
                    "Selecteaza mijloacele de transport",
                    options=MIJLOACE_TRANSPORT,
                    default=st.session_state["masini_" + key_suffix],
                    key="masini_multi_" + key_suffix
                )

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
            if culoare_sel != "Toate":
                filtered = filtered[filtered["Culoare"] == culoare_sel]
            if search:
                filtered = filtered[filtered["CAWB"].str.contains(search, case=False, na=False)]
            if include_transport and masini_selectate:
                filtered = filtered[filtered["Mijloc transport"].isin(masini_selectate)]
            filtered = filtered[
                (filtered["Nr colete"] >= colete_range[0]) &
                (filtered["Nr colete"] <= colete_range[1])
            ]

            if include_transport:
                cols_show = ["CAWB", "Tip", "Culoare", "Ruta", "Origine", "Destinatie", "CAWB parinte",
                             "Mijloc transport", "Nr colete", "Total colete descarcate", "Ramas de descarcat", "Fisier sursa"]
            else:
                cols_show = ["CAWB", "Tip", "Culoare", "Ruta", "Origine", "Destinatie", "CAWB parinte",
                             "Nr colete", "Total colete descarcate", "Ramas de descarcat", "Fisier sursa"]

            available = [c for c in cols_show if c in filtered.columns]
            display_df = filtered[available].reset_index(drop=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("CAWB-uri filtrate", f"{len(display_df):,}")
            c2.metric("Total Colete", f"{display_df['Nr colete'].sum():,}")
            c3.metric("Total Descarcate", f"{display_df['Total colete descarcate'].sum():,}")

            styled_df = display_df.style.apply(coloreaza, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=450)

            buffer = io.BytesIO()
            display_df.to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                "Descarca Excel",
                data=buffer,
                file_name="cawb_" + key_suffix + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_" + key_suffix
            )

        with tab1:
            st.subheader("CAWB-uri Fara Parinte (" + str(len(df_fara_parinte)) + ")")
            afiseaza_tabel(df_fara_parinte, "fara_parinte", include_transport=False)

        with tab2:
            st.subheader("CAWB-uri Cu Parinte (" + str(len(df_cu_parinte)) + ")")
            afiseaza_tabel(df_cu_parinte, "cu_parinte", include_transport=True)

        with tab3:
            st.subheader("Toate CAWB-urile (" + str(len(df)) + ")")
            afiseaza_tabel(df, "toate", include_transport=False)

        with tab4:
            st.subheader("Filtrare dupa Mijloc de Transport")
            st.markdown("Selecteaza una sau mai multe masini:")
            col_sel1, col_sel2 = st.columns([1, 3])
            with col_sel1:
                if st.button("Selecteaza toate", key="sel_toate"):
                    st.session_state["masini_selectate"] = MIJLOACE_TRANSPORT
                if st.button("Deselecteaza toate", key="desel_toate"):
                    st.session_state["masini_selectate"] = []
            if "masini_selectate" not in st.session_state:
                st.session_state["masini_selectate"] = []
            masini_selectate = st.multiselect(
                "Mijloace de transport",
                options=MIJLOACE_TRANSPORT,
                default=st.session_state["masini_selectate"],
                key="masini_multi"
            )
            st.markdown("---")
            if masini_selectate:
                col_t1, col_t2 = st.columns(2)
                ascunde_zero_t = col_t1.checkbox("Ascunde 0 colete", value=True, key="zero_transport")
                search_t = col_t2.text_input("Cauta CAWB", key="search_transport")
                filtered_t = df.copy()
                if "Mijloc transport" in filtered_t.columns:
                    filtered_t = filtered_t[filtered_t["Mijloc transport"].isin(masini_selectate)]
                if ascunde_zero_t:
                    filtered_t = filtered_t[filtered_t["Nr colete"] > 0]
                if search_t:
                    filtered_t = filtered_t[filtered_t["CAWB"].str.contains(search_t, case=False, na=False)]
                cols_show_t = ["CAWB", "Tip", "Culoare", "Ruta", "Origine", "Destinatie",
                               "CAWB parinte", "Mijloc transport", "Nr colete",
                               "Total colete descarcate", "Ramas de descarcat", "Fisier sursa"]
                available_t = [c for c in cols_show_t if c in filtered_t.columns]
                display_t = filtered_t[available_t].reset_index(drop=True)
                ct1, ct2, ct3 = st.columns(3)
                ct1.metric("CAWB-uri gasite", f"{len(display_t):,}")
                ct2.metric("Total Colete", f"{display_t['Nr colete'].sum():,}")
                ct3.metric("Total Descarcate", f"{display_t['Total colete descarcate'].sum():,}")
                styled_t = display_t.style.apply(coloreaza, axis=1)
                st.dataframe(styled_t, use_container_width=True, height=450)
                buffer_t = io.BytesIO()
                display_t.to_excel(buffer_t, index=False)
                buffer_t.seek(0)
                st.download_button(
                    "Descarca Excel",
                    data=buffer_t,
                    file_name="cawb_transport.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_transport"
                )
            else:
                st.info("Selecteaza cel putin o masina pentru a vedea rezultatele.")

else:
    st.info("Te rog incarca unul sau mai multe fisiere CSV sau Excel pentru a incepe.")
