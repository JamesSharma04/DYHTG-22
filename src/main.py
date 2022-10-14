import streamlit as st
import pandas as pd 

st.write("Hello WOrld")

location = pd.read_csv("../data/location_data.csv")
st.write(location)