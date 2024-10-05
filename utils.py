import streamlit as st
import pandas as pd

@st.cache_data(persist=True)
def load_data(path, number_rows):
    df = pd.read_csv(path, nrows=number_rows)
    df.rename(str.lower, axis="columns", inplace=True)
    return df