import streamlit as st
import utils as utl
from views import home, student_information, analysis, main

st.set_page_config(layout="wide", page_title='Team 40 SAS challenge')
st.set_option('deprecation.showPyplotGlobalUse', False)
utl.inject_custom_css()
utl.navbar_component()


def navigation():
    route = utl.get_current_route()
    if route == "home":
        home.load_view()
    elif route == "main":
        main.load_view()
    elif route == "student_information":
        student_information.load_view()
    elif route == "analysis":
        analysis.load_view()
    elif route == None:
        home.load_view()


navigation()
