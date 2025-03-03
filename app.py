import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# Page Configuration
st.set_page_config(page_title="Growth Mindset Tracker", layout="wide")

# App Title
st.title("📈 Growth Mindset Tracker")
st.write("Track and improve your mindset through structured steps and visual insights!")

# Authentication (Basic Admin Login)
st.sidebar.subheader("🔑 Admin Login")
admin_password = "admin123"  # Change this for security
password = st.sidebar.text_input("Enter Password", type="password")

if password != admin_password:
    st.sidebar.error("Incorrect password! Access restricted.")
    st.stop()

# Define Growth Mindset Steps
growth_steps = [
    "Embrace Challenges",
    "Persist Through Obstacles",
    "See Effort as a Path to Mastery",
    "Learn from Criticism",
    "Find Inspiration in Others"
]

expected_columns = ["Date", "Day"] + growth_steps

# File Upload Feature with Multiple Formats
st.subheader("📂 Upload Any File (CSV, Excel, JSON) and Convert to CSV")
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "xls", "json"])

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_extension == "csv":
            data = pd.read_csv(uploaded_file)
        elif file_extension in ["xlsx", "xls"]:
            data = pd.read_excel(uploaded_file)
        elif file_extension == "json":
            data = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format!")
            st.stop()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
    
    data.columns = [col.strip() for col in data.columns]  # Clean column names

    # Identify Missing Columns
    missing_cols = set(expected_columns) - set(data.columns)
    
    for col in missing_cols:
        if col == "Day":
            data[col] = pd.to_datetime(data["Date"]).dt.strftime("%A")
        else:
            data[col] = 5  # Default score

    st.session_state.data = data
    st.success("✅ File uploaded successfully!")

    # Convert to CSV for download
    csv = data.to_csv(index=False).encode("utf-8")
    st.download_button(label="⬇️ Download as CSV", data=csv, file_name="converted_data.csv", mime="text/csv")
else:
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=expected_columns)

data = st.session_state.data.copy()

# User Data Input
st.subheader("📝 Track Your Mindset Progress")
st.write("Rate yourself on each mindset factor (1-10 scale):")

with st.form("mindset_form"):
    date = st.date_input("Select Date", value=datetime.date.today())
    day_of_week = date.strftime("%A")  # Get day name
    ratings = {step: st.slider(step, 1, 10, 5) for step in growth_steps}
    submitted = st.form_submit_button("Add Entry")
    
    if submitted:
        new_entry = {"Date": date.strftime("%Y-%m-%d"), "Day": day_of_week, **ratings}
        data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
        st.session_state.data = data
        st.success("✅ Entry Added Successfully!")

# Display Data
st.subheader("📊 Your Growth Mindset Data")
st.dataframe(data)

# Convert Data Columns to Numeric
for step in growth_steps:
    if step in data.columns:
        data[step] = pd.to_numeric(data[step], errors="coerce")

# Visualization
st.subheader("📈 Mindset Progress Over Time")
if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")
    fig = px.line(data, x="Date", y=growth_steps, markers=True, title="Mindset Growth Over Time")
    st.plotly_chart(fig)
else:
    st.write("⚠️ No data yet. Add your first mindset assessment above!")

# Download Feature
st.subheader("📥 Download Your Progress")
if not data.empty:
    csv = data.to_csv(index=False).encode("utf-8")
    st.download_button(label="⬇️ Download CSV", data=csv, file_name="growth_mindset_data.csv", mime="text/csv")

st.success("🚀 Keep tracking your growth mindset and improving!")
