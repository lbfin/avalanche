# import packages
import streamlit as st
import pandas as pd
import re
import os
import plotly.express as px


# Helper function to clean text
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text


st.title("Hello, GenAI!")
st.write("This is your GenAI-powered data processing app.")

# File uploader (add-on to hardcoded path)
col_uploader, col_reset = st.columns([4, 1])
with col_uploader:
    uploaded_file = st.file_uploader("📁 Upload a CSV file (or use default)", type=["csv"])
with col_reset:
    #st.write("")  # Vertical padding to align with uploader
    st.empty()
    if st.button("🔄 Reset", help="Clear all data and start fresh"):
        st.session_state.clear()
        st.rerun()  # Refresh to reflect cleared state

# Dynamic path for default dataset
default_csv_path = os.path.join(os.path.dirname(__file__), "customer_reviews.csv")

# Layout two buttons side by side
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Ingest Dataset"):
        try:
            with st.spinner("🔄 Loading dataset..."):
                if uploaded_file:
                    st.session_state["df"] = pd.read_csv(uploaded_file)
                else:
                    st.session_state["df"] = pd.read_csv(default_csv_path)
            # Validate required columns (dynamic from original CSV)
            try:
                original_df = pd.read_csv(default_csv_path)
                required_columns = list(original_df.columns)
            except:
                required_columns = ["Product", "Date", "Summary", "Sentiment_Score", "Order_id"]
            missing_columns = [col for col in required_columns if col not in st.session_state["df"].columns]
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
            else:
                st.success("Dataset loaded successfully!")
        except FileNotFoundError:
            st.error("Dataset not found. Please check the file path.")
        except Exception as e:
            st.error(f"Error loading dataset: {str(e)}")

with col2:
    if st.button("🧹 Parse Reviews"):
        if "df" in st.session_state:
            st.session_state["df"]["CLEANED_SUMMARY"] = st.session_state["df"]["SUMMARY"].apply(clean_text)
            st.success("Reviews parsed and cleaned!")
        else:
            st.warning("Please ingest the dataset first.")

# Display the dataset if it exists
if "df" in st.session_state:
    # Product filter dropdown
    st.subheader("🔍 Filter by Product")
    sorted_products = sorted(st.session_state["df"]["PRODUCT"].unique())
    product = st.selectbox("Choose a product", ["All Products"] + sorted_products)
    st.subheader(f"📁 Reviews for {product}")

    if product != "All Products":
        filtered_df = st.session_state["df"][st.session_state["df"]["PRODUCT"] == product]
    else:
        filtered_df = st.session_state["df"]
    st.write(f"Showing {len(filtered_df)} reviews")
    st.dataframe(filtered_df.reset_index(drop=True))
    
    # Pie chart: Show share of selected product vs. all others
    if product != "All Products":
        total_reviews = len(st.session_state["df"])
        product_count = len(filtered_df)
        other_count = total_reviews - product_count
        pie_data = pd.DataFrame({
            "Category": [product, "Other Products"],
            "Count": [product_count, other_count]
        })
        st.subheader("📊 Distribution of Reviews")
        fig = px.pie(pie_data, values="Count", names="Category", title="Share of Reviews")
        st.plotly_chart(fig)
    
    st.subheader("Sentiment Score by Product")
    grouped = st.session_state["df"].groupby(["PRODUCT"])["SENTIMENT_SCORE"].mean()
    st.bar_chart(grouped)

