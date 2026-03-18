import streamlit as st


# Optional badge!
st.markdown("""
    <p style="display:inline-block;background:rgba(55,138,221,0.15);color:#378ADD;font-size:11px;font-weight:500;padding:4px 10px;border-radius:20px;margin-bottom:12px">
        About
    </p>
""", unsafe_allow_html=True)
st.markdown("## CRM Insights")
st.markdown("**An AI-powered CRM tool that helps businesses score leads, segment customers, and generate actionable sales strategies, built with Streamlit and Gemini AI.**")

st.divider()



# --------------------------------------------------WHAT IT DOES? -------------------------------------



st.markdown("""
    <p style="font-size:20px;font-weight:500;color:gray;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">
        What it does
    </p>
""", unsafe_allow_html=True)

with st.container(border=True):

    # For icons
    st.markdown("""
            <div style="width:32px;height:32px;border-radius:8px;background:#EEEDFE;display:flex;align-items:center;justify-content:center;margin-bottom:10px">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <rect x="2" y="8" width="3" height="6" rx="1" fill="#7F77DD"/>
                    <rect x="6.5" y="5" width="3" height="9" rx="1" fill="#7F77DD"/>
                    <rect x="11" y="2" width="3" height="12" rx="1" fill="#7F77DD"/>
                </svg>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("**Lead Scoring**")
    st.markdown("Upload a screenshot or CSV of leads. The app extracts recency and frequency from your data, "
"runs it through a trained ML model, and uses Gemini AI to generate personalized sales suggestions for each lead. "
"Use the Dashboard for a quick overview, or download the results as a CSV after uploading. "
"You can also ask follow-up questions about your leads through an AI chat interface.")

with st.container(border=True):
    st.markdown("""
            <div style="width:32px;height:32px;border-radius:8px;background:#E1F5EE;display:flex;align-items:center;justify-content:center;margin-bottom:10px">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="5" cy="5" r="3" fill="#1D9E75"/>
                    <circle cx="11" cy="5" r="3" fill="#1D9E75" opacity="0.5"/>
                    <circle cx="8" cy="11" r="3" fill="#1D9E75" opacity="0.75"/>
                </svg>
            </div>
        """, unsafe_allow_html=True)    
    
    st.markdown("**Customer Segmentation**")
    st.markdown("Upload transaction data. The app engineers RFM-style features," \
    " runs KMeans clustering (with cluster numbers 3), and uses Gemini AI to label each segment with a" \
    " human-readable name and reasoning.")

# ---------------------------------------------------------------------------------------------------------


st.divider()
 
# ----------------------------------- TECH STACK ---------------------------------------------------------------

# For title 
st.markdown("""
    <div style="font-size:20px;font-weight:500;color:gray;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">
        Built with
    </div>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0">
                <div style="font-size:16px;font-weight:500;margin-bottom:4px"> Streamlit </div>  
                <div style="font-size:14px;color:gray">UI Framework</div>
            </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0">
                <div style="font-size:16px;font-weight:500;margin-bottom:4px">Plotly</div>
                <div style="font-size:14px;color:gray">Charts</div>
            </div>
        """, unsafe_allow_html=True)


with col2:
    with st.container(border=True):
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0">
                <div style="font-size:16px;font-weight:500;margin-bottom:4px"> Gemini AI </div>  
                <div style="font-size:14px;color:gray"> LLM suggestions </div>
            </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0">
                <div style="font-size:16px;font-weight:500;margin-bottom:4px"> Pandas </div>
                <div style="font-size:14px;color:gray"> Data preprocessing </div>
            </div>
        """, unsafe_allow_html=True)



with col3: 
    with st.container(border=True):
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0">
                <div style="font-size:16px;font-weight:500;margin-bottom:4px"> Scikit-learn </div>  
                <div style="font-size:14px;color:gray"> ML models  </div>
            </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
            <div style="text-align:center;padding:0.5rem 0">
                <div style="font-size:16px;font-weight:500;margin-bottom:4px"> Chart.js </div>
                <div style="font-size:14px;color:gray"> Donut animation </div>
            </div>
        """, unsafe_allow_html=True)



# -------------------------------------------------------------------------------------------------------------


st.divider()

# -------------------------------------------------- BUILT BY ------------------------------------------------


st.markdown("""
    <p style="font-size:20px;font-weight:500;color:gray;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">
        Built by
    </p>
""", unsafe_allow_html=True)


st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;background:rgba(128,128,128,0.08);border:0.5px solid rgba(128,128,128,0.15);border-radius:12px;padding:1rem 1.25rem">
        <div style="width:44px;height:44px;border-radius:50%;background:rgba(127,119,221,0.2);color:#7F77DD;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:500;flex-shrink:0">N</div>
        <div>
            <div style="font-size:16px;font-weight:500;margin-bottom:2px">Namal</div>
            <div style="font-size:12px;color:gray"> Junior ML Engineer </div>
        </div>
    </div>

    <div style="border-top:0.5px solid rgba(128,128,128,0.15);padding-top:12px;display:flex;flex-direction:column;gap:8px">
            <span style="display:flex;align-items:center;gap:8px;font-size:15px;color:gray">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="1" y="3" width="14" height="10" rx="2" stroke="gray" stroke-width="1"/><path d="M1 5l7 5 7-5" stroke="gray" stroke-width="1"/></svg>
            namalrizwan4@gmail.com
        </span>
            <a href="https://namal-xx.github.io/" target="_blank" style="display:flex;align-items:center;gap:8px;font-size:15px;color:gray;text-decoration:none">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="gray" stroke-width="1"/><path d="M8 4v4l3 2" stroke="gray" stroke-width="1" stroke-linecap="round"/></svg>
                My personal blog
            </a>
            <a href="https://medium.com/@namalrizwan4" target="_blank" style="display:flex;align-items:center;gap:8px;font-size:15px;color:gray;text-decoration:none">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="14" height="14" rx="3" stroke="gray" stroke-width="1"/><path d="M5 8h6M5 5h6M5 11h4" stroke="gray" stroke-width="1" stroke-linecap="round"/></svg>
               Medium blog
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)
