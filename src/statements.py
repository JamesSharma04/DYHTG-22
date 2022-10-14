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

aaaa = pd.DataFrame(np.array([statementdata,studentnumberdata,namedata,testimonydata]).T, columns = coldata)
st.write(pd.DataFrame(aaaa))

people_data = pd.read_csv("data/people_data.csv")
st.write(people_data)

box = st.selectbox(label = 'Which Student would you like to view information about?',options = aaaa["Name:"])
box
st.write(people_data.loc[people_data["Name"]==box])
