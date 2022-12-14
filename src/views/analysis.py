import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

location_data = pd.read_csv("data/location_data.csv")
people_data = pd.read_csv("data/people_data.csv")
security_log_Data = pd.read_csv("data/security_logs.csv")


def age_histogram(bin_size):
    data = people_data['Age'].values

    st.subheader("People under 18")
    people_under_18 = str(
        people_data.loc[people_data['Age'] < 18]['Name'].values).replace('[\'', '') .replace('\']', '').replace('\' \'', ', ')

    for i in people_under_18.split(', '):
        st.markdown(f"- {i}")

    st.subheader("People over 30")
    people_over_30 = str(
        people_data.loc[people_data['Age'] > 30]['Name'].values).replace('[\'', '').replace('\']', '').replace('\' \'', ', ')

    for i in people_over_30.split(', '):
        st.markdown(f"- {i}")

    st.subheader("Histogram of ages")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.hist(data, bins=bin_size, color='c', alpha=0.65)
    ax.vlines(18, 0, 30, color='k', label="18")
    ax.vlines(30, 0, 30, color='k', label="30")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)

def height_histogram(bin_size):
    data = people_data['Height'].values


    st.subheader("Histogram of Heights")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.hist(data, bins=bin_size, color='c', alpha=0.65)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)

def load_view():
    st.title('Analysis Page')
    age_histogram(20)
    height_histogram(20)


    
