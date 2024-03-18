import streamlit as st
import getpass, os
st.set_page_config(layout="wide")

username = getpass.getuser()
domain_username = os.getenv('USERDOMAIN')+ "\\" + username
if "" in domain_username.lower():
    st.title("SQL Automation For Client Analysis")
    st.subheader("\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699\u2699")
    st.write("\n")
    st.write("\n")
    st.write("\n")

    st.subheader("\U0001F448Select the tool of your choice from the side bar.")
