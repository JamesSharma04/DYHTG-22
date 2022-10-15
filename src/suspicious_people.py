import json
import streamlit as st
from streamlit_timeline import timeline
import pandas as pd
from datetime import datetime
import numpy as np 
import replicate
import webcolors

st.set_page_config(layout="wide")
st.title("Student Information")

# st.write("Location Data")
location_data = pd.read_csv("data/location_data.csv")
# st.write(location_data)

# st.write("People Data")
people_data = pd.read_csv("data/people_data.csv")
# st.write(people_data)

# st.write("Security Data")
security_log_Data = pd.read_csv("data/security_logs.csv")
# st.write(security_log_Data)

def get_student_statement_df():
    coldata = ["Statement:","Student Number:","Name:","Testimony:"]
    statementdata=[]
    studentnumberdata=[]
    namedata=[]
    testimonydata=[]
    with open ("student_statement/student_statements.txt") as f:
        for line in f:
            if "Statement" in line:
                statementdata.append(line[10:-1])
            if "Student Number:" in line:
                studentnumberdata.append(line[16:-1])
            if ("Name:") in line:
                namedata.append(line[6:-1])
            if ("Testimony:") in line:
                testimonydata.append(line[11:-1])
    return pd.DataFrame(np.array([statementdata,studentnumberdata,namedata,testimonydata]).T, columns = coldata)




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

statements=get_student_statement_df()


@st.cache
def get_image(prompt):
    client = replicate.Client(api_token='d21eac06fcdbe3eb35c4d22453c018ad623a493f')
    model = client.models.get("stability-ai/stable-diffusion")
    type(model)
    output = model.predict(prompt="prompt")
    return output

#st.image(get_image(prompt="25 year old male with #e079db hair colour"))

def info_about_student(name):
    attrs = ["Student ID","Name", "Age", "Sex", "Year of Study", "Subject", "Hair colour", "Societies"]
    info = {}
    rowinfo = people_data.loc[people_data["Name"]==name]
    for attr in attrs:
        info[attr] = rowinfo[attr].iloc[0]
    firstpersonpronoun = "He" if info["Sex"]=="Male" else "She"
    thirdpersonpronoun = "his" if info["Sex"]=="Male" else "her"
    societylist = info["Societies"].replace("[","").replace("]","").replace("'","")
    #st.write("societylist = " + info["Societies"])
    #st.write(societylist)
    societydesc = "not in any societies" if info["Societies"]=="N/A" else "in the " + societylist
    
    #hairdesc=webcolors.hex_to_name(info["Hair colour"])
    hairdesc='brown'
    description = st.markdown(
        f"**{info['Name']}** (Student ID: {info['Student ID']}) is a {info['Age']} year old {info['Sex'].lower()}. {firstpersonpronoun} is in year {info['Year of Study']}, studying {info['Subject'].lower()}. {firstpersonpronoun} has {hairdesc} hair. {firstpersonpronoun} is {societydesc}.    "
    )

    return description


for i in set_list:
    st.header(f"{i}")
    with st.sidebar:
        st.markdown(f"[{i}](#section-1)")
        #for i in namedata:
            #   st.write(i)

    
    #replace with natural language desc
    info_about_student(i)
    st.subheader("Testimony")
    st.write(statements.loc[statements["Name:"]==i]["Testimony:"].iloc[0])

    suspicious_person_loc = security_location_data.loc[security_location_data["Name"] == i]

    events = []

    for j in suspicious_person_loc.values:
        time_start, time_end, opening_time_start, opening_time_end = date_time_parser(
            j)

        color = "darkgreen"
        addit_text = ""
        if time_not_in_range(opening_time_start, time_start, opening_time_end) or time_not_in_range(opening_time_start, time_end, opening_time_end):
            color = "darkred"
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
