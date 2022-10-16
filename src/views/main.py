import streamlit as st
import pydeck as pdk
from pydeck.types import String
import pandas as pd
from datetime import datetime, timedelta, time
from random import random
from math import cos, sin

def load_view():
    start_time = datetime(2022, 11, 1, 3, 0)

    @st.cache(persist=True)
    def load_data():
        location_data = pd.read_csv("data/location_data.csv")
        people_data = pd.read_csv("data/people_data.csv")
        security_log_data = pd.read_csv("data/security_logs.csv")
        return location_data, people_data, security_log_data

    location_data, people_data, security_log_data = load_data()

    building_closed = {"url": "https://i.imgur.com/Rzbdb5k.png",
                       "width": 50,
                       "height": 82,
                       "anchorY": 82}

    building_open = {"url": "https://i.imgur.com/OV4ImX1.png",
                     "width": 50,
                     "height": 82,
                     "anchorY": 82}

    coords = location_data.Geolocation.str.strip(
        '{}').str.split(expand=True).astype(float)
    opening_times = location_data["Opening Times"].str.split(
        '-', expand=True).astype(int)
    coords = pd.concat(
        [coords, location_data["Building Name"], opening_times], axis=1)
    coords.columns = ['lat', 'lon', 'name', 'open', 'closed']

    def update_icons(curr_time=None):
        if curr_time is None:
            curr_time = st.session_state.map_slider_key

        curr_time = curr_time.hour * 100 + curr_time.minute

        icons = []
        for i in coords.index:
            time_open = coords['open'][i]
            time_closed = coords['closed'][i]
            if time_open > time_closed:
                icons.append(building_closed
                             if (time_closed < curr_time < time_open)
                             else building_open)
            elif time_open == time_closed:
                icons.append(building_open)
            else:
                icons.append(building_open
                             if (time_open < curr_time < time_closed)
                             else building_closed)

        coords['icon_data'] = icons

    update_icons(st.session_state.get("map_slider_key", start_time))

    joined = security_log_data.join(
        location_data.set_index('Building Name'), on='Location')

    joined = joined[["Name", "Time", "Geolocation"]]

    joined[['start', 'end']] = joined.Time.str.split(
        '-', expand=True).astype(int)
    joined[['lat', 'lon']] = joined.Geolocation.str.strip(
        '{}').str.split(expand=True).astype(float)
    joined = joined.drop(columns=['Time', 'Geolocation'])

    timelines = {}
    for _, person in people_data.iterrows():
        timelines[person['Name']] = joined.loc[joined["Name"]
                                               == person["Name"]].drop(columns=['Name'])

    def hextorgb(s):
        return [int(s[i:i+2], 16) for i in (1, 3, 5)]
        
    students = people_data.loc[:, ['Name']]
    students.columns = ['name']
    students['color'] = list(map(hextorgb, people_data['Hair colour']))
    students[['lat', 'lon']] = 0
    students['size'] = 12

    def curr_loc(name, time):
        timeline = timelines[name]
        last_lat = -55
        last_lon = 176
        last_endtime = datetime(2022, 11, 1, 0, 0)

        start = datetime(2022, 11, 1, int(timeline['start'].iloc[0])//100, int(timeline['start'].iloc[0]) % 100)
        if start > time:
            return (0, 0, 0)

        for _, loc in timeline.iterrows():
            start, end, lat, lon = loc

            start = datetime(2022, 11, 1, int(start)//100, int(start) % 100)
            end = datetime(2022, 11, 1, int(end)//100, int(end) % 100)

            if start > end:
                end = end.replace(day=2) 
                
            if time < start:
                t = 0
                if (start - last_endtime) != timedelta(0):
                    t = (time - last_endtime) / (start - last_endtime)
                return (last_lat * (1 - t) + lat * t, last_lon * (1 - t) + lon * t, 12)

            if start <= time < end:
                r = random() * 0.0001
                theta = random() * 6.28
                return (lat + r * sin(theta), lon + r * cos(theta), 6)

            last_lat = lat
            last_lon = lon
            last_endtime = end

        return (0, 0, 0)

    def update_locs(curr_time=None):
        if curr_time is None:
            curr_time = st.session_state.map_slider_key

        locs = []
        for i in students.index:
            locs.append(curr_loc(students['name'][i], curr_time))
        
        lats, lons, sizes = map(list, zip(*locs))
        students['lat'] = lats
        students['lon'] = lons
        students['size'] = sizes

    update_locs(st.session_state.get("map_slider_key", start_time))

    building_layer = pdk.Layer(
        'IconLayer',
        data=coords,
        pickable=True,
        get_icon='icon_data',
        get_position='[lon, lat]',
        get_size=6,
        size_scale=15,
    )

    building_label_layer = pdk.Layer(
        "TextLayer",
        data=coords,
        get_position='[lon, lat]',
        get_text='name',
        get_size=24,
        get_color=[255, 255, 255],
        font_settings={'sdf': True},
        outline_width=1,
        outline_color=[0, 0, 0],
        get_angle=0,
        get_text_anchor=String("middle"),
        get_alignment_baseline=String("top"),
    )

    student_layer = pdk.Layer(
        "ScatterplotLayer",
        data=students,
        pickable=True,
        radius_units=String('pixels'),
        opacity=0.3,
        filled=True,
        get_position='[lon, lat]',
        get_radius='size',
        get_fill_color='color',
    )

    deck = pdk.Deck(
        map_style='dark_no_labels',
        initial_view_state=pdk.ViewState(
            latitude=55.8714864,
            longitude=-4.2869478,
            zoom=14.5,
            min_zoom=10,
            pitch=0,
        ),
        layers=[building_layer, building_label_layer, student_layer],
        tooltip={"text": "{name}"})

    st.pydeck_chart(deck)

    map_timeline = st.slider(
        "Time:",
        value=start_time,
        min_value=start_time,
        max_value=start_time + timedelta(hours=25),
        step=timedelta(minutes=5),
        format="hh:mm, MMM Do",
        key="map_slider_key"
    )
