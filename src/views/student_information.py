import json
import streamlit as st
from streamlit_timeline import timeline
import pandas as pd
from datetime import datetime
import numpy as np
import replicate
from annotated_text import annotated_text
import webcolors
from sklearn.metrics import mean_squared_error
import string
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from io import BytesIO

def get_student_statements():
    coldata = ["Statement:", "Student Number:", "Name:", "Testimony:"]
    statementdata = []
    studentnumberdata = []
    namedata = []
    testimonydata = []
    with open("student_statement/student_statements.txt") as f:
        for line in f:
            if "Statement" in line:
                statementdata.append(line[10:-1])
            if "Student Number:" in line:
                studentnumberdata.append(line[16:-1])
            if ("Name:") in line:
                namedata.append(line[6:-1])
            if ("Testimony:") in line:
                testimonydata.append(line[11:-1])

    statements = pd.DataFrame(np.array(
        [statementdata, studentnumberdata, namedata, testimonydata]).T, columns=coldata)

    return statements, namedata


def time_not_in_range(start, current, end):
    """Returns whether current is in the range [start, end]"""
    return start > current or current > end


def date_time_parser(i):
    time_list = i[3].split('-')
    opening_time_list = i[5].split('-')

    time_start = datetime(year=2022, month=11, day=1, hour=int(
        time_list[0].lstrip()[:2]), minute=int(time_list[0].lstrip()[2:]))

    if int(time_list[0].lstrip()) == int(time_list[1]):
        day = 3
    elif int(time_list[0].lstrip()) > int(time_list[1]):
        day = 2
    else:
        day = 1

    time_end = datetime(year=2022, month=11, day=day, hour=int(
        time_list[1][:2]), minute=int(time_list[1][2:]))

    ###

    opening_time_start = datetime(year=2022, month=11, day=1, hour=int(
        opening_time_list[0].lstrip()[:2]), minute=int(opening_time_list[0].lstrip()[2:]))

    if int(opening_time_list[0].lstrip()) == int(opening_time_list[1]):
        day = 3
    elif int(opening_time_list[0].lstrip()) >= int(opening_time_list[1]):
        day = 2
    else:
        day = 1

    opening_time_end = datetime(year=2022, month=11, day=day, hour=int(
        opening_time_list[1][:2]), minute=int(opening_time_list[1][2:]))

    return time_start, time_end, opening_time_start, opening_time_end


def generate_security_location_data(location_data, security_log_Data):
    location_data['Geolocation'] = location_data['Geolocation'].map(
        lambda x: x.lstrip('{').rstrip('}'))
    coord_df = pd.DataFrame(location_data.Geolocation.str.split(
        " ").tolist(), columns=['lat', 'lon'])
    location_data = location_data.drop(['Geolocation'], axis=1)
    location_data["lat"] = coord_df["lat"]
    location_data["lon"] = coord_df["lon"]
    security_location_data = security_log_Data.merge(
        location_data, right_on="Building Name", left_on="Location")
    return security_location_data


def check_past_closing(security_location_data):
    set_list = set()

    for i in security_location_data.values:

        time_start, time_end, opening_time_start, opening_time_end = date_time_parser(
            i)

        if time_not_in_range(opening_time_start, time_start, opening_time_end) or time_not_in_range(opening_time_start, time_end, opening_time_end):
            set_list.add(i[1])
            st.markdown(
                f"**{i[1]}** was at the {i[2]} after closing time from {time_start.time()} to {time_end.time()}. The {i[2]} opening times are {i[3]}.")

    return set_list


def hex2name(c):
    h_color = '#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2]))
    try:
        nm = webcolors.hex_to_name(h_color, spec='css3')
    except ValueError as v_error:
        print("{}".format(v_error))
        rms_lst = []
        for img_clr, img_hex in webcolors.CSS3_NAMES_TO_HEX.items():
            cur_clr = webcolors.hex_to_rgb(img_hex)
            rmse = np.sqrt(mean_squared_error(c, cur_clr))
            rms_lst.append(rmse)

        closest_color = rms_lst.index(min(rms_lst))

        nm = list(webcolors.CSS3_NAMES_TO_HEX.items())[closest_color][0]
    return nm


def info_about_student(name, people_data, hair_data):
    attrs = ["Student ID", "Name", "Age", "Sex",
             "Year of Study", "Subject", "Hair colour", "Societies"]
    info = {}
    rowinfo = people_data.loc[people_data["Name"] == name]
    for attr in attrs:
        info[attr] = rowinfo[attr].iloc[0]
    firstpersonpronoun = "He" if info["Sex"] == "Male" else "She"
    thirdpersonpronoun = "his" if info["Sex"] == "Male" else "her"
    print(info["Societies"])
    # st.write("societylist = " + info["Societies"])
    # st.write(societylist)
    is_string = type(info["Societies"]) == type("")
    societydesc = "not in any societies" if not is_string else "in the "
    if is_string:
        societydesc += info["Societies"].replace(
            "[", "").replace("]", "").replace("'", "")

    # hairdesc=webcolors.hex_to_name(info["Hair colour"])
    # hairdesc = hex2name(info["Hair colour"][1:])
    hairdesc = str(hair_data.loc[hair_data['Name'] == info['Name']]['Hair colour'].values[0]).lower()
    description = st.markdown(
        f"**{info['Name']}** (Student ID: {info['Student ID']}) is a {info['Age']} year old {info['Sex'].lower()}. {firstpersonpronoun} is in year {info['Year of Study']}, studying {info['Subject'].lower()}. {firstpersonpronoun} has {hairdesc} hair. {firstpersonpronoun} is {societydesc}.    "
    )

    return description, info


def add_sidebar(name):
    section = "#about-"+name.replace(" ", "-").lower()
    st.subheader(f"About {name}")
    st.sidebar.markdown(f"[{name}]({section})")
    return


def add_header_sidebar(name):
    st.header(f"{name}")
    st.sidebar.markdown(f"**{name}**")


def check_testimony(testimony, location_data_nickname):
    location_in_testimony = set()
    split_testimony = testimony.split(' ')
    testimony_annotated = []

    for index, value_i in enumerate(split_testimony):
        value = value_i.strip().lower().translate(
            str.maketrans('', '', string.punctuation))

        if index != len(split_testimony)-1:
            value_2 = split_testimony[index+1].strip().lower().translate(
                str.maketrans('', '', string.punctuation))
            if value_2 != "but":
                value_full = value + " " + value_2
            else:
                continue
        else:
            value_full = value

        loc_found = False
        for j in location_data_nickname.keys():
            loc_nickname = location_data_nickname[j]
            if (value_full == "union" or value == "union") and "Queen Margaret Union" in location_in_testimony and value_full != "union rather":
                break
            if value_full in loc_nickname:
                location_in_testimony.add(j)
                testimony_annotated.append(
                    (value_i+" ", j)
                )

                loc_found = True
                break
            elif value in loc_nickname:
                location_in_testimony.add(j)
                testimony_annotated.append((value_i+" ", j))
                loc_found = True
                break

        if loc_found is False:
            testimony_annotated.append(value_i+" ")

    annotated_text(
        *testimony_annotated
    )

    return location_in_testimony


def main(location_data, people_data, security_log_Data, location_data_nickname):
    statements, namedata = get_student_statements()

    security_location_data = generate_security_location_data(
        location_data, security_log_Data)

    hair_data = pd.read_csv("data/ai_prompt/folk_data")

    add_header_sidebar("Students with Testimonies")
    for i in namedata:
        add_sidebar(i)
        _, info = info_about_student(i, people_data, hair_data)
        st.subheader("Testimony")

        locations_in_testimony = check_testimony(statements.loc[statements["Name:"] == i]
                                                 ["Testimony:"].iloc[0], location_data_nickname)

        person_loc = security_location_data.loc[security_location_data["Name"] == i]

        person_loc_set = set(person_loc["Location"].values.tolist())

        loc_only_testimony = locations_in_testimony-person_loc_set

        loc_only_log = person_loc_set - locations_in_testimony

        unusual_behaviours = []

        persons_age = info["Age"]

        if persons_age >= 30:
            unusual_behaviours.append(
                f"**{info['Name']}** is a mature student as their age is **{info['Age']}**.")
        elif persons_age < 18:
            unusual_behaviours.append(
                f"**{info['Name']}** is a young student as their age is **{info['Age']}**.")

            age_restrictive_venues = [
                "Queen Margaret Union", "Glasgow University Union", "The Hive"]
            for venue in age_restrictive_venues:
                if venue in locations_in_testimony or venue in person_loc_set:
                    unusual_behaviours.append(
                        f"**{info['Name']}** has gone to the **{venue}** which is a age restrictive venue.")

        if len(unusual_behaviours) != 0:
            st.subheader("Unusual behaviours")
            for i in unusual_behaviours:
                st.markdown(f"- {i}")

        if len(loc_only_testimony) != 0 or len(loc_only_log) != 0:
            st.subheader("Discrepancies between location data")

            fig, ax = plt.subplots(figsize=(6, 7))

            venn = venn2([locations_in_testimony, person_loc_set],
                         ('Testimony', 'Security logs'))
            ax.legend(
                labels=["Testimony", "Security logs", "Appears in both"])

            try:
                venn.get_label_by_id('100').set_text(
                    '\n'.join(map(str, loc_only_testimony)))
            except:
                pass
            try:
                venn.get_label_by_id('110').set_text(
                    '\n'.join(map(str, locations_in_testimony & person_loc_set)))
            except:
                pass
            try:
                venn.get_label_by_id('010').set_text(
                    '\n'.join(map(str, loc_only_log)))
            except:
                pass

            buf = BytesIO()
            fig.savefig(buf, format="png")
            st.image(buf, width=600)

        events = []

        for j in person_loc.values:
            time_start, time_end, opening_time_start, opening_time_end = date_time_parser(
                j)

            color = "darkgreen"
            addit_text = ""
            if time_not_in_range(opening_time_start, time_start, opening_time_end) or time_not_in_range(opening_time_start, time_end, opening_time_end):
                color = "darkred"
                addit_text += "(In building after closing time) "

            if j[2] in loc_only_log:
                color = "darkred"
                addit_text = "(Location discrepancy)"

            events.append(
                {
                    "start_date": {
                        "year": "2022",
                        "month": "11",
                        "hour": time_start.hour,
                        "minute": time_start.minute
                    },
                    "end_date": {
                        "year": "2022",
                        "month": "11",
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

        st.subheader("Timeline of security log")
        timeline(data, height=600)
    add_header_sidebar("All Other Students")
    namedate_other = people_data[~people_data['Name'].isin(
        namedata)].Name.tolist()

    for i in namedate_other:
        add_sidebar(i)
        _, info = info_about_student(i, people_data, hair_data)

        person_loc = security_location_data.loc[security_location_data["Name"] == i]

        person_loc_set = set(person_loc["Location"].values.tolist())

        unusual_behaviours = []

        persons_age = info["Age"]

        if persons_age >= 30:
            unusual_behaviours.append(
                f"**{info['Name']}** is a mature student as their age is **{info['Age']}**.")
        elif persons_age < 18:
            unusual_behaviours.append(
                f"**{info['Name']}** is a young student as their age is **{info['Age']}**.")

            age_restrictive_venues = [
                "Queen Margaret Union", "Glasgow University Union", "The Hive"]
            for venue in age_restrictive_venues:
                if venue in locations_in_testimony or venue in person_loc_set:
                    unusual_behaviours.append(
                        f"**{info['Name']}** has gone to the **{venue}** which is a age restrictive venue.")

        if len(unusual_behaviours) != 0:
            st.subheader("Unusual behaviours")
            for i in unusual_behaviours:
                st.markdown(f"- {i}")

        events = []

        for j in person_loc.values:
            time_start, time_end, opening_time_start, opening_time_end = date_time_parser(
                j)

            color = "darkgreen"
            addit_text = ""
            if time_not_in_range(opening_time_start, time_start, opening_time_end) or time_not_in_range(opening_time_start, time_end, opening_time_end):
                color = "darkred"
                addit_text += "(In building after closing time) "

            events.append(
                {
                    "start_date": {
                        "year": "2022",
                        "month": "11",
                        "hour": time_start.hour,
                        "minute": time_start.minute
                    },
                    "end_date": {
                        "year": "2022",
                        "month": "11",
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

        st.subheader("Timeline of security log")
        timeline(data, height=600)


@st.cache(allow_output_mutation=True)
def read_csv():
    location_data = pd.read_csv("data/location_data.csv")

    people_data = pd.read_csv("data/people_data.csv")

    security_log_Data = pd.read_csv("data/security_logs.csv")
    return location_data, people_data, security_log_Data


def load_view():

    st.title("Student Information")

    location_data_nickname = {
        "Boyd Orr Building": ["boyd orr", "boydy", "bob"],
        "James Watt Building": ["james watt", "jwb"],
        "Adam Smith Building": ["adam smith", "asb"],
        "Main Building": ["main building"],
        "Wolfson Medical Building": ["wolfson", "medicine", "medical" "medical"],
        "The Hive": ["hive", "nightclub"],
        "Sir Alwyn Williams Building": ["alwyn williams", "sawb", "alwyn"],
        "Library": ["library"],
        "Queen Margaret Union": ["union which", "union rather", "union i", "queen margaret", "qmu"],
        "St Andrews Building": ["st andrews", "education"],
        "Kelvingrove Park": ["kelvingrove", "kelvin grove", "park", "KG"],
        "Joseph Black Building": ["joseph black", "chemistry"],
        "Kelvin Building": ["kelvin", "physics"],
        "Glasgow University Union": ["glasgow university union", "guu", "union", "of fun"]
    }
    location_data, people_data, security_log_Data = read_csv()

    main(location_data, people_data, security_log_Data, location_data_nickname)
