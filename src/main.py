import streamlit as st
import pandas as pd 
import pydeck as pdk

st.write("Hello WOrld")

location_data = pd.read_csv("../data/location_data.csv")
st.write(location_data)

people_data = pd.read_csv("../data/people_data.csv")
st.write(people_data)

security_log_Data = pd.read_csv("../data/security_logs.csv")
st.write(security_log_Data)

coords = location_data.Geolocation.str.strip('{}').str.split(expand=True)
coords.columns = ['lat', 'lon']

coords = coords.astype(float)

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=55.873010,
        longitude=-4.292536,
        zoom=11,
        pitch=60,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=coords,
            get_position='[lon, lat]',
            get_color='[0, 0, 255, 255]',
            get_radius=30,
        ),
    ],
))



