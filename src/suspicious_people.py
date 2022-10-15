import json
import streamlit as st
from streamlit_timeline import timeline
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Suspicious movements")

# st.write("Location Data")
location_data = pd.read_csv("data/location_data.csv")
# st.write(location_data)

# st.write("People Data")
people_data = pd.read_csv("data/people_data.csv")
# st.write(people_data)

# st.write("Security Data")
security_log_Data = pd.read_csv("data/security_logs.csv")
# st.write(security_log_Data)


def time_not_in_range(start, current, end):
    """Returns whether current is in the range [start, end]"""
    return start > current or current > end


def date_time_parser(i):
    time_list = i[3].split('-')
    opening_time_list = i[5].split('-')

    time_start = datetime(year=2020, month=1, day=1, hour=int(
        time_list[0].lstrip()[:2]), minute=int(time_list[0].lstrip()[2:]))

    if int(time_list[0].lstrip()) == int(time_list[1]):
        day = 3
    elif int(time_list[0].lstrip()) > int(time_list[1]):
        day = 2
    else:
        day = 1

    time_end = datetime(year=2020, month=1, day=day, hour=int(
        time_list[1][:2]), minute=int(time_list[1][2:]))

    ###

    opening_time_start = datetime(year=2020, month=1, day=1, hour=int(
        opening_time_list[0].lstrip()[:2]), minute=int(opening_time_list[0].lstrip()[2:]))

    if int(opening_time_list[0].lstrip()) == int(opening_time_list[1]):
        day = 3
    elif int(opening_time_list[0].lstrip()) >= int(opening_time_list[1]):
        day = 2
    else:
        day = 1

    opening_time_end = datetime(year=2020, month=1, day=day, hour=int(
        opening_time_list[1][:2]), minute=int(opening_time_list[1][2:]))

    return time_start, time_end, opening_time_start, opening_time_end


location_data['Geolocation'] = location_data['Geolocation'].map(
    lambda x: x.lstrip('{').rstrip('}'))
coord_df = pd.DataFrame(location_data.Geolocation.str.split(
    " ").tolist(), columns=['lat', 'lon'])
location_data = location_data.drop(['Geolocation'], axis=1)
location_data["lat"] = coord_df["lat"]
location_data["lon"] = coord_df["lon"]
security_location_data = security_log_Data.merge(
    location_data, right_on="Building Name", left_on="Location")

set_list = set()

for i in security_location_data.values:

    time_start, time_end, opening_time_start, opening_time_end = date_time_parser(
        i)

    if time_not_in_range(opening_time_start, time_start, opening_time_end) or time_not_in_range(opening_time_start, time_end, opening_time_end):
        set_list.add(i[1])
        st.markdown(
            f"**{i[1]}** was at the {i[2]} after closing time from {time_start.time()} to {time_end.time()}. The {i[2]} opening times are {i[3]}.")


for i in set_list:
    st.header(i)

    st.subheader("Testimony")

    st.write("A fire is pretty serious business, so even though I don't like authority or sharing my precious data you can get a pass today. I went to the St Andrews building for my lecture; I chilled in the Wolfson Medical building with some of my medic friends; then last I nipped to the Sir Alwyn Williams Building before ending the day in the Queen Margaret Union.")

    suspicious_person_loc = security_location_data.loc[security_location_data["Name"] == i]

    events = []

    for j in suspicious_person_loc.values:
        time_start, time_end, opening_time_start, opening_time_end = date_time_parser(
            j)

        color = "lightgreen"
        addit_text = ""
        if time_not_in_range(opening_time_start, time_start, opening_time_end) or time_not_in_range(opening_time_start, time_end, opening_time_end):
            color = "lightcoral"
            addit_text = "(In building after closing time)"
        # st.write(time_start, time_end, opening_time_start, opening_time_end)
        events.append(
            {
                "start_date": {
                    "year": "2022",
                    "hour": time_start.hour,
                    "minute": time_start.minute
                },
                "end_date": {
                    "year": "2022",
                    "hour": time_end.hour,
                    "minute": time_end.minute
                },
                "text": {
                    "headline": f"{j[2]} {addit_text}",
                    "text": j[6]
                },
                "background": {
                    "color": color
                }
            }
        )

    data = json.dumps({
        "events": events
    })
    timeline(data, height=800)
