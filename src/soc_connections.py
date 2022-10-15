import streamlit as st
import pandas as pd

location_data = pd.read_csv("data/location_data.csv")
people_data = pd.read_csv("data/people_data.csv")
security_log_Data = pd.read_csv("data/security_logs.csv")
soc_data = pd.read_csv("data/societies.csv")

box = st.selectbox(label = 'Which Student would you like to view information about?', options = people_data['Name'])
box_socs = people_data.loc[people_data['Name'] == box]['Societies'].values[0]
box_socs_l = []
if type(box_socs) == type(""):
    exec("box_socs_l = " + box_socs)

peeps = str(soc_data.loc[soc_data['Soc'].isin(box_socs_l)]['Names'].values)
peeps = peeps.replace('[', '')
peeps = peeps.replace(']', '')
peeps = peeps.replace('"', '')
peeps = peeps.replace('\'', '')
peeps = peeps.replace('\n', ', ')

connections = set(peeps.split(', '))
st.write(box_socs_l)
st.write(list(connections))
