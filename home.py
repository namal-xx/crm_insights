import streamlit as st



# Optional badge!
st.markdown("""
    <div style="display:inline-block;background:rgba(55,138,221,0.15);color:#378ADD;font-size:11px;font-weight:500;padding:4px 10px;border-radius:20px;margin-bottom:12px">
        CRM Insights
    </div>
""", unsafe_allow_html=True)
st.markdown("## Welcome to CRM Insights")
st.markdown("**Your AI-powered CRM dashboard. Score leads, segment customers, and get actionable insights all in one place.**")



# Check if data exists in session state
has_leads    = st.session_state.get("uploaded_csv") is not None and \
               "Category" in st.session_state.uploaded_csv.columns

has_segments = st.session_state.get("n_segments") is not None 

col1, col2, col3 = st.columns(3)

if has_leads:
    total = len(st.session_state.uploaded_csv)
    hot = (st.session_state.uploaded_csv["Category"] == "Hot").sum()

if has_segments:
    segments = int(st.session_state.n_segments)    

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total leads scored", total if has_leads else "—")

with col2:
    st.metric("Hot leads", hot if has_leads else "—")

with col3:
    st.metric("Segments identified", segments if has_segments else "—")

if not has_leads and not has_segments:
    st.info("Upload your data in Lead Scoring or Customer Segmentation to see your stats here.")       


st.divider()



# ── Module cards ──────────────────────────────────────────────────
st.markdown("#### Modules")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
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
        st.markdown("Upload a screenshot or CSV. AI scores each lead and suggests next actions.")

        if st.button("Go to Lead Scoring →", use_container_width=True):
            st.session_state["nav_target"] = "Lead Scoring"
            st.rerun()

with col2:
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
        st.markdown("KMeans clustering with AI-generated labels and revenue breakdown by segment.")

        if st.button("Go to Customer Segmentation →", use_container_width=True):
            st.session_state["nav_target"] = "Customer Segmentation"
            st.rerun()

st.divider()






# ── Recent activity ───────────────────────────────────────────────
st.markdown("#### Recent activity")
if has_leads:
    df = st.session_state.uploaded_csv
    id_col = next((col for col in df.columns if "id" in col.lower()), None)  # ← ADD THIS
    recent = df.sort_values("Probs", ascending=False).head(5)
    
    cols = ["Recency", "Frequency", "Category", "Probs"]
    if id_col:
        cols = [id_col] + cols  # ← prepend whatever ID column exists
    
    st.dataframe(
        recent[cols],  # ← use dynamic cols instead of hardcoded
        use_container_width=True,
        hide_index=True,
    )
else:
    st.markdown(
        """
        <div style="text-align:center;padding:2rem;border:0.5px solid var(--color-border-tertiary, #ddd);border-radius:12px;color:gray;font-size:14px">
            No activity yet. Your scored leads will appear here.
        </div>
        """,
        unsafe_allow_html=True
    )
