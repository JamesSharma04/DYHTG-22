import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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

connections = [i.strip() for i in set(peeps.split(', ')) if i.strip() != str(box)]
st.write(box_socs_l)
st.write(connections)

G = nx.Graph()
G.add_node(str(box))
G.add_nodes_from(connections)
G.add_edges_from([(str(box), i) for i in connections])

st.set_option('deprecation.showPyplotGlobalUse', False)
pos = nx.kamada_kawai_layout(G)
nx.draw(G, pos, node_size=1250, with_labels=True)
st.pyplot()
