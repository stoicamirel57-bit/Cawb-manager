import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CAWB Manager", page_icon="📦", layout="wide")
st.title("📦 CAWB Manager")
st.markdown("---")

uploaded_files = st.file_uploader(
    "📂 Incarca unul sau mai multe fisiere CSV / Excel",
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
            st.success("✅ Fisier incarcat: " + f.name + " (" + str(len(temp)) + " randuri)")
        except Exception as e:
            st.error("❌ Eroare la fisierul " + f.name + ": "
