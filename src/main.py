import streamlit as st
import pandas as pd 

st.write("Hello WOrld")

location_data = pd.read_csv("../data/location_data.csv")
st.write(location_data)

people_data = pd.read_csv("../data/people_data.csv")
st.write(people_data)

security_log_Data = pd.read_csv("../data/security_logs.csv")
st.write(security_log_Data)

