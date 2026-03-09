import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Maize Price Forecast", layout="wide")

st.title("Kenya Maize Market Advisory System")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("maize_dataset.xlsx")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

data = load_data()

# ---------------------------
# LOAD MODEL
# ---------------------------
@st.cache_resource
def load_model():
    try:
        model = pickle.load(open("price_prediction_model.pkl","rb"))
        return model
    except:
        return None

model = load_model()

# ---------------------------
# LOGIN SYSTEM
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.subheader("Farmer Registration / Login")

    name = st.text_input("Farmer Name")
    crop = st.selectbox("Crop Produced", ["Maize", "Beans", "Green Grams"])
    password = st.text_input("Password", type="password")

    if st.button("Enter System"):
        if name != "" and password != "":
            st.session_state.logged_in = True
            st.success(f"Welcome {name}")
        else:
            st.warning("Please enter your name and password.")

# ---------------------------
# MAIN SYSTEM
# ---------------------------
else:

    page = st.sidebar.selectbox(
        "Navigation",
        ["Predict Price", "Market Trends"]
    )

# ---------------------------
# PAGE 1: PRICE PREDICTION
# ---------------------------
    if page == "Predict Price":

        st.header("Maize Price Prediction")

        markets = sorted(data["Market"].dropna().unique())

        market = st.selectbox("Select Market", markets)

        duration = st.selectbox(
            "Prediction Timeline",
            ["1 Week","2 Weeks","1 Month","2 Months","3 Months"]
        )

        if st.button("Predict Price"):

            market_data = data[data["Market"] == market]

            avg_price = market_data["Retail"].mean()

            timeline_map = {
                "1 Week":1,
                "2 Weeks":2,
                "1 Month":4,
                "2 Months":8,
                "3 Months":12
            }

            duration_value = timeline_map[duration]

            if model is not None:

                prediction = model.predict([[avg_price, duration_value]])
                price = prediction[0]

            else:
                # fallback if model not loaded
                price = avg_price + duration_value

            st.success(
                f"Estimated maize price in **{market}** after **{duration}** is approximately **{price:.2f} KSh/kg**"
            )

# ---------------------------
# PAGE 2: MARKET TRENDS
# ---------------------------
    if page == "Market Trends":

        st.header("Market Price Trends")

        markets = sorted(data["Market"].dropna().unique())

        market = st.selectbox("Choose Market", markets)

        market_data = data[data["Market"] == market].copy()

        market_data = market_data.sort_values("Date")

        st.subheader("Retail Price Trend")

        fig, ax = plt.subplots()

        ax.plot(
            market_data["Date"],
            market_data["Retail"]
        )

        ax.set_xlabel("Date")
        ax.set_ylabel("Price (KSh/kg)")
        ax.set_title(f"Retail Price Trend - {market}")

        st.pyplot(fig)

        # Seasonal pattern
        st.subheader("Seasonal Price Pattern")

        market_data["Month"] = market_data["Date"].dt.month

        seasonal = market_data.groupby("Month")["Retail"].mean()

        fig2, ax2 = plt.subplots()

        ax2.bar(seasonal.index, seasonal.values)

        ax2.set_xlabel("Month")
        ax2.set_ylabel("Average Price")

        st.pyplot(fig2)

        st.info(
            "Prices often rise before harvest due to low supply and fall during harvest seasons."
        )
