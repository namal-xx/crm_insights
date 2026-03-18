import base64
import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai


genai.configure(api_key = st.secrets["GEMINI_API_KEY"]) # telling the google that i've acces to your api by providing api key





st.set_page_config(page_title="CRM Insights", page_icon="📊")

page_options = ["Home", "Lead Scoring", "Customer Segmentation", "About"]

# Handle nav_target from home.py buttons
nav_target = st.session_state.pop("nav_target", None)

if nav_target in page_options:
    st.session_state["selected_page"] = nav_target

# Restore saved page on every rerun
default_index = page_options.index(st.session_state.get("selected_page", "Home"))



def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = get_image_base64("crm_logo.png")

with st.sidebar:
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding: 4px 0 20px 0; 
                    border-bottom: 0.5px solid rgba(255,255,255,0.1); margin-bottom: 12px;">
             <img src="data:image/png;base64,{logo_b64}" 
                  style="width:100px; height:100px; border-radius:70%; object-fit:cover; object-position:center;">
             <span style="font-size:20px; font-weight:500;">CRM Insights</span>


        </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=page_options,
        icons=["house", "bar-chart", "people", "info-circle"],
        default_index=default_index,
        styles={
            "container":{"padding": "0", "background-color": "transparent"},
            "icon":     {"color": "rgba(180,180,180,0.8)", "font-size": "15px"},
            "nav-link": {
                "font-size": "14px",
                "color": "rgba(180,180,180,0.9)",
                "padding": "9px 16px",
                "border-radius": "6px",
                "margin": "2px 0",
            },
            "nav-link-selected": {
                "background-color": "rgba(79,142,247,0.15)",
                
                "border-left": "2px solid #4f8ef7",
                "font-weight": "400",
            },
        }
    )

# Save currently selected page
if st.session_state.get("selected_page") != selected:
    st.session_state["selected_page"] = selected
    st.rerun()


# ── Route pages ───────────────────────────────────────────────────
home_page         = st.Page("home.py",                 title="Home")
lead_scoring_page = st.Page("pages/lead_scoring.py",   title="Lead Scoring")
customer_seg_page = st.Page("pages/customer_seg.py",   title="Customer Segmentation")
about_page        = st.Page("about.py",                title="About")

if selected == "Home":
    pg = st.navigation([home_page], position="hidden")
elif selected == "Lead Scoring":
    pg = st.navigation([lead_scoring_page], position="hidden")
elif selected == "Customer Segmentation":
    pg = st.navigation([customer_seg_page], position="hidden")
elif selected == "About":
    pg = st.navigation([about_page], position="hidden")

pg.run()