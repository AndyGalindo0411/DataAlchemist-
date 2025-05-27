import streamlit as st # type: ignore

st.set_page_config(page_title="Dashboard Principal", layout="wide")

st.sidebar.header("⚙️ Settings")
st.sidebar.date_input("Start date")
st.sidebar.date_input("End date")
st.sidebar.selectbox("Select time frame", ["Daily", "Weekly", "Monthly"])
st.sidebar.selectbox("Select a chart type", ["Bar", "Line", "Area"])

st.title("📊 YouTube Channel Dashboard")

st.header("All-Time Statistics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Subscribers", "141,036", "+2.41%")
with col2:
    st.metric("Total Views", "10,935,596", "-6.72%")
with col3:
    st.metric("Watch Hours", "1,060,225", "-2.21%")
with col4:
    st.metric("Total Likes", "543,761", "-15.25%")

st.header("Selected Duration")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric("Subscribers", "49,745", "+2.41%")
with col6:
    st.metric("Views", "3,870,516", "-6.72%")
with col7:
    st.metric("Hours", "379,235", "-2.21%")
with col8:
    st.metric("Likes", "193,675", "-15.25%")
