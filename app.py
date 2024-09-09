import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pickle

# Load data
df_dim_date = pd.read_pickle(r"df_dim_date.pkl")
df_dim_hotels = pd.read_pickle(r"df_dim_hotels.pkl")
df_dim_rooms = pd.read_pickle(r"df_dim_rooms.pkl")
df_fact_aggregated_bookings = pd.read_pickle(r"df_fact_aggregated_bookings.pkl")
df_fact_bookings = pd.read_pickle(r"df_fact_bookings.pkl")

# Data preprocessing
df_dim_date["date"] = pd.to_datetime(df_dim_date["date"])
df_fact_bookings["check_in_date"] = pd.to_datetime(df_fact_bookings["check_in_date"])

df_fact_aggregated_bookings["occ_pct"] = round((df_fact_aggregated_bookings["successful_bookings"] / df_fact_aggregated_bookings["capacity"]) * 100, 2)

df_fact_bookings_with_property_id = df_fact_bookings.merge(df_dim_hotels, how="left", on="property_id")
df_fact_bookings_with_room_class = df_fact_bookings.merge(df_dim_rooms, how="left", left_on="room_category", right_on="room_id")
df_fact_bookings_full = df_fact_bookings_with_property_id.merge(df_fact_bookings_with_room_class[["booking_id", "room_class"]], how="left", on="booking_id")
df = df_fact_bookings_full.merge(df_dim_date, how="left", left_on="check_in_date", right_on="date")

# Streamlit app
st.set_page_config(page_title="Hotel Booking Analysis Dashboard", layout="wide")
st.title("🏨 Hotel Booking Analysis Dashboard")

# Sidebar for chart selection
st.sidebar.title("🔍 Select a View")
chart_option = st.sidebar.selectbox(
    "Choose Chart",
    [
        "Revenue by Room Category",
        "Revenue by City",
        "Revenue by Day Type",
        "Revenue by Booking Status",
        "Revenue by Room Class",
        "Revenue by Booking Platform",
        "Guests by Room Category",
        "Average Occupancy by Room Category"
    ]
)

# Sidebar for view type (chart or table)
view_option = st.sidebar.selectbox(
    "Choose View Type",
    ["Chart", "Table"]
)

# Set seaborn theme for all plots
sns.set_theme(style="whitegrid")

# Function to add bar labels
def add_bar_labels(ax):
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 5), 
                    textcoords='offset points')

# Plot or display table for selected option
if chart_option == "Revenue by Room Category":
    st.header("💰 Revenue by Room Category")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="room_category", y="revenue_generated", data=df, ax=ax, palette="viridis")
        ax.set_title("Revenue by Room Category", fontsize=16)
        ax.set_xlabel("Room Category", fontsize=12)
        ax.set_ylabel("Revenue Generated", fontsize=12)
        plt.xticks(rotation=45)
        add_bar_labels(ax)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("room_category")["revenue_generated"].sum().reset_index())

elif chart_option == "Revenue by City":
    st.header("💸 Revenue by City")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x="city", y="revenue_generated", data=df, ax=ax, marker='o', color="magenta")
        ax.set_title("Revenue by City", fontsize=16)
        ax.set_xlabel("City", fontsize=12)
        ax.set_ylabel("Revenue Generated", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("city")["revenue_generated"].sum().reset_index())

elif chart_option == "Revenue by Day Type":
    st.header("📅 Revenue by Day Type")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="day_type", y="revenue_generated", data=df, ax=ax, palette="coolwarm")
        ax.set_title("Revenue by Day Type", fontsize=16)
        ax.set_xlabel("Day Type", fontsize=12)
        ax.set_ylabel("Revenue Generated", fontsize=12)
        add_bar_labels(ax)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("day_type")["revenue_generated"].sum().reset_index())

elif chart_option == "Revenue by Booking Status":
    st.header("💼 Revenue by Booking Status")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x="booking_status", y="revenue_realized", data=df, ax=ax, marker='o', color="dodgerblue")
        ax.set_title("Revenue by Booking Status", fontsize=16)
        ax.set_xlabel("Booking Status", fontsize=12)
        ax.set_ylabel("Revenue Realized", fontsize=12)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("booking_status")["revenue_realized"].sum().reset_index())

elif chart_option == "Revenue by Room Class":
    st.header("🏷️ Revenue by Room Class")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="room_class", y="revenue_realized", data=df, ax=ax, palette="YlGnBu")
        ax.set_title("Revenue by Room Class", fontsize=16)
        ax.set_xlabel("Room Class", fontsize=12)
        ax.set_ylabel("Revenue Realized", fontsize=12)
        add_bar_labels(ax)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("room_class")["revenue_realized"].sum().reset_index())

elif chart_option == "Revenue by Booking Platform":
    st.header("📲 Revenue by Booking Platform")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(8, 8))
        df_platform_revenue = df.groupby("booking_platform")["revenue_realized"].sum().reset_index()
        ax.pie(df_platform_revenue["revenue_realized"], labels=df_platform_revenue["booking_platform"], autopct="%1.1f%%", colors=sns.color_palette("pastel"))
        ax.set_title("Revenue by Booking Platform", fontsize=16)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("booking_platform")["revenue_realized"].sum().reset_index())

elif chart_option == "Guests by Room Category":
    st.header("👥 Number of Guests by Room Category")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="room_category", y="no_guests", data=df, ax=ax, palette="inferno")
        ax.set_title("Number of Guests by Room Category", fontsize=16)
        ax.set_xlabel("Room Category", fontsize=12)
        ax.set_ylabel("Number of Guests", fontsize=12)
        add_bar_labels(ax)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df.groupby("room_category")["no_guests"].sum().reset_index())

elif chart_option == "Average Occupancy by Room Category":
    st.header("🏨 Average Occupancy by Room Category")
    if view_option == "Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x="room_category", y="occ_pct", data=df_fact_aggregated_bookings, ax=ax, palette="cubehelix")
        ax.set_title("Average Occupancy by Room Category", fontsize=16)
        ax.set_xlabel("Room Category", fontsize=12)
        ax.set_ylabel("Occupancy Percentage", fontsize=12)
        add_bar_labels(ax)
        st.pyplot(fig)
    elif view_option == "Table":
        st.dataframe(df_fact_aggregated_bookings.groupby("room_category")["occ_pct"].mean().reset_index())