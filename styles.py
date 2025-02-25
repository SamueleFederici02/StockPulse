import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stTable {
            width: 100%;
        }
        .metric-card {
            background-color: #ffffff;
            padding: 1.2rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border: 1px solid #e1e4e8;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .metric-card h4 {
            color: #1f2937;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        .metric-card p {
            color: #111827;
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
        }
        .stock-header {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        /* Custom styles for search bar */
        .stTextInput > div > div > input {
            font-size: 1.1rem;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        /* Style for tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            font-size: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)