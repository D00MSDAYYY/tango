from observer_app import observer_app
import streamlit as st

if __name__ == "__main__":
    if 'observer_app' not in st.session_state:
        st.session_state.observer_app = observer_app()
        st.session_state.observer_app()
    else:
        st.session_state.observer_app()