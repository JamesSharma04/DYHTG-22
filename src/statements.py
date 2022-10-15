import streamlit as st
import pandas as pd
import numpy as np
import csv 

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
    st.write(statementdata)
    st.write(studentnumberdata)
    st.write(namedata)
    st.write(testimonydata)

statements = pd.DataFrame(np.array([statementdata,studentnumberdata,namedata,testimonydata]).T, columns = coldata)
st.write(pd.DataFrame(statements))
st.write(statements.loc[statements["Name:"]=="Abdul Murphy"])

people_data = pd.read_csv("data/people_data.csv")
st.write(people_data)

box = st.selectbox(label = 'Which Student would you like to view information about?',options = aaaa["Name:"])
box
st.write(box, "\n Societies: ", people_data.loc[people_data["Name"]==box]["Societies"])

def info_about_student(name):
    attrs = ["Student ID","Name", "Age", "Sex", "Year of Study", "Subject", "Hair Color", "Societies"]
    info = {}
    rowinfo = people_data.loc[people_data["Name"]==name]


    return info

def textual_representation_of_info(info):
    desc = "HI"
    return desc

def is_outlier(name,info):
    outlier = False



    if outlier:

        def detect_outliers(name, info):
            outliers = "example"
            return outliers
    return False

def display_plots(visualisations):
    return
    #void 

#show each statement on the sidebar 

# use AI generated image of suspect given age, sex, hair colour
# hex to natural language desc of hair colour 
# might be useful to cache results as statements fixed
# ask if statement people more important/main thing to visualise 

# sus: oscar brown, Barry robinson, 