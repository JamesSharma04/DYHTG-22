import streamlit as st
import pandas as pd
import numpy as np
st.write("Hello WOrld")

people_data = pd.read_csv("data/people_data.csv")
st.write(people_data)
st.write(people_data['Age'])
Age_Data = pd.DataFrame(people_data['Age'], columns=people_data['Name'])
st.bar_chart(Age_Data)
