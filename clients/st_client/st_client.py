import streamlit as st
import pages.pages as pgs
from tinydb import TinyDB, Query
import os 

if 'db' not in st.session_state:
    @st.dialog("Connect to DB", dismissible=False)
    def connect_to_db():
        st.write("Enter DB name")
        db_name = st.text_input("Database name", "my_database")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", type="primary"):
                st.session_state.db = TinyDB(db_name + ".json")
                st.rerun() 
        with col2:
            if st.button("Cancel"):
                st.error("Cannot proceed without database connection")
                st.stop()  
    connect_to_db()

nav = st.navigation({"Work": [pgs.charts_page]})
nav.run()