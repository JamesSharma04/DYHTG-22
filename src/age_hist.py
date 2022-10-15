import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

location_data = pd.read_csv("data/location_data.csv")
people_data = pd.read_csv("data/people_data.csv")
security_log_Data = pd.read_csv("data/security_logs.csv")

def age_histogram(bin_size):
    data = people_data['Age'].values

    st.write("People under 18")
    st.write(str(people_data.loc[people_data['Age'] < 18]['Name'].values)
                 .replace('[\'', '')
                 .replace('\']', '')
                 .replace('\' \'', ', ')
                 )

    st.write("People over 30")
    st.write(str(people_data.loc[people_data['Age'] > 30]['Name'].values)
                 .replace('[\'', '')
                 .replace('\']', '')
                 .replace('\' \'', ', ')
                 )

    fig, ax = plt.subplots()
    ax.hist(data, bins=bin_size, color='c', alpha=0.65)
    ax.vlines(18, 0, 30, color='k', label="18")
    ax.vlines(30, 0, 30, color='k', label="30")
    st.pyplot(fig)

age_histogram(20)
