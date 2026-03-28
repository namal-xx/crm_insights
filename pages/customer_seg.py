import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px

from helper_functions import configure_gemini

import re
import joblib
import json

import google.generativeai as genai

if "user_csv" not in st.session_state:
    st.session_state.user_csv = None

if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {}

if "customer_context" not in st.session_state:
    st.session_state.customer_context = None

if "model_response" not in st.session_state:
    st.session_state.model_response = None


if "n_segments" not in st.session_state:
    st.session_state["n_segments"] = None

configure_gemini()
gemini_model = genai.GenerativeModel("gemini-2.5-flash") # Selecting the model 




# Import model and scaler features
try:
    k_means_model = joblib.load("kmeans_model_crm.pkl")
    scaler_features = joblib.load("scaler_crm.pkl")
except Exception as e:
    print("Couldn't load model: {e}")



st.title("Customer Segmentation!")


# ===================== Step 1: Let user upload data =====================
user_data = st.file_uploader("Upload data")


def saved_index(key):
    val = st.session_state.column_mapping.get(key)
    if val and val in user_columns:
        return user_columns.index(val)
    return None

# ===================== Step 2: Feature Engineering =====================
if user_data and st.session_state.model_response is None:
    df = pd.read_csv(user_data)
    df = df.dropna() 

    st.session_state.user_csv = df
    st.session_state.column_mapping = {}  # ✅ reset mapping on fresh upload 
   
if st.session_state.user_csv is not None:
    df = st.session_state.user_csv
     
    # Make columns our model was trained on.
    # Frequency✅, Quantity✅, Monetary✅, Product_diversity✅,	Recency, AOV✅, Average_time_purchase_diff✅.

    user_columns = df.columns.tolist()

    customer_id = st.selectbox("Which column refers to Customer ID?", user_columns,
                                index = saved_index("customer_id"),
                                placeholder = "e.g., customer_id")    
    
    frequency  = st.selectbox("Which column refers to InvoiceNo?", user_columns, 
                                index = saved_index("frequency"),
                                placeholder = "e.g., Invoice_no")    

    quantity = st.selectbox("Which column refers to Quantity?", user_columns, 
                                index = saved_index("quantity"),
                                placeholder = "e.g., quantity")
    
    unit_price = st.selectbox("Which column refers to UnitPrice?", user_columns,
                                index = saved_index("unit_price"),
                                placeholder = "e.g., unit_price")
    
    description = st.selectbox("Which column refers to Description of products?", user_columns,
                                index = saved_index("description"),
                                placeholder = "e.g., description")
    
    invoice_date = st.selectbox("Which column refers to Invoice Date?", user_columns,
                                index = saved_index("invoice_date"),
                                placeholder = "e.g., InvoiceDate")    
    

    
    if customer_id and frequency and quantity and unit_price and description and invoice_date:
        st.session_state.column_mapping = {
        "customer_id":  customer_id,
        "frequency":    frequency,
        "quantity":     quantity,
        "unit_price":   unit_price,
        "description":  description,
        "invoice_date": invoice_date}
        
        if st.session_state.column_mapping:
            mapping = st.session_state.column_mapping

            
            # Create Monetary feature before grouping, because we need to sum it up for each customer
            df = df.sort_values([mapping["customer_id"], mapping["invoice_date"]]).reset_index(drop=True)

            df["Monetary"] = df[mapping["quantity"]] * df[mapping["unit_price"]]

            # Convert invoice_date to datetime
            df[mapping["invoice_date"]] = pd.to_datetime(df[mapping["invoice_date"]])

            customer_df = df.groupby(mapping["customer_id"]).agg(
                Frequency = (mapping["frequency"], "nunique"),
                Quantity =  (mapping["quantity"], "sum"),
                Product_diversity = (mapping["description"], "nunique"),
                Monetary = ("Monetary", "sum"),
                invoice_date = (mapping["invoice_date"], "max")
            )
        


            # Calculate AOV (Average Order Value) as Monetary / Frequency
            customer_df["AOV"] = customer_df["Monetary"] / customer_df["Frequency"]
            
            # For Recency
            today_date = df[mapping["invoice_date"]].max() + pd.DateOffset(days=2)        
            customer_df["Recency"] = (today_date - customer_df["invoice_date"]).dt.days
            avg_time = (
                df.groupby(mapping["customer_id"])[mapping["invoice_date"]]
                .apply(lambda x: x.sort_values().diff().dt.total_seconds().mean() / 86400)
                .reset_index()
            )

            # After reset_index(), the apply result is in column 0
            avg_time.columns = [mapping["customer_id"], "Average_time_purchase_diff"]

            customer_df = customer_df.reset_index()  # brings customer_id back as a column

            customer_df = customer_df.merge(avg_time, on=customer_id, how="left")
            max_diff = customer_df["Average_time_purchase_diff"].max()


            customer_df["Average_time_purchase_diff"] = customer_df["Average_time_purchase_diff"].fillna(max_diff)





            # ======================= Step 3: Scale features ======================= 


            # Remove customer_id
            new_customer_df = customer_df.copy()

            # Scaling needs columns to be in the same order as they were in when we fit the scaler
            new_customer_df = new_customer_df[["Frequency", "Quantity", "Monetary", "Product_diversity", "Recency", "AOV", "Average_time_purchase_diff"]]  


            # Catch any remaining NaNs before scaling
            new_customer_df = new_customer_df.fillna(0)


            df_scaled = scaler_features.transform(new_customer_df)
            df_scaled = pd.DataFrame(df_scaled,
                        index = new_customer_df.index,
                        columns = new_customer_df.columns)

            



            # ======================= Step 4: Make predictions =======================
            

            model_preds = k_means_model.predict(df_scaled)
            customer_df["model_preds"] = model_preds
            
            
            
            # ======================= Step 5: Calculate stats =======================


            clusters_df =  customer_df.groupby("model_preds")["Monetary"].sum().reset_index()
            total_rev = clusters_df["Monetary"].sum()

            # Calculate percentage revenue
            per_cluster_0 = (clusters_df["Monetary"][0]/total_rev)*100
            per_cluster_1 = (clusters_df["Monetary"][1]/total_rev)*100
            per_cluster_2 = (clusters_df["Monetary"][2]/total_rev)*100


            revenu = [per_cluster_0, per_cluster_1, per_cluster_2]  

            # Calculate cluster stats
            cluster_stats = customer_df.groupby("model_preds").agg(
                
                # Size
                Customer_count    = ("CustomerID", "count"),
                
                # Behavior
                Avg_frequency     = ("Frequency", "mean"),
                Avg_quantity      = ("Quantity", "mean"),
                Avg_monetary      = ("Monetary", "mean"),
                Avg_recency       = ("Recency", "mean"),
                Avg_aov           = ("AOV", "mean"),
                Avg_diversity     = ("Product_diversity", "mean"),
                Avg_time_diff     = ("Average_time_purchase_diff","mean"),

            ).reset_index()





            # ======================= Step 6: Generate Segment Labels & Reasoning ======================= 



            labels_prompt = f"""
            Given the following customer segment stats, provide a concise and insightful label for each cluster.
            Focus on the key characteristics that differentiate each segment. Below is the data:            
            {cluster_stats.to_string(index=False)}

            Below is the revenue contribution of each cluster:
            {clusters_df.to_string(index=False)}

            Return ONLY a valid JSON array with no markdown, no code blocks, no extra text.
            Just the raw JSON like this:
            [
                {{"cluster_no": 0, "label": "...", "reasoning": "..."}},
                {{"cluster_no": 1, "label": "...", "reasoning": "..."}},
                {{"cluster_no": 2, "label": "...", "reasoning": "..."}}
            ] 
            """

            # Only call Gemini if not already done
            if st.session_state.model_response is None:
                response = gemini_model.generate_content(labels_prompt)
                extracted_text = response.text.strip()

                # Strip markdown code fences if Gemini wraps response in them
                if extracted_text.startswith("```"):
                    extracted_text = re.sub(r"^```(?:json)?\n?", "", extracted_text)
                    extracted_text = re.sub(r"\n?```$", "", extracted_text)
                    extracted_text = extracted_text.strip()

                if not extracted_text:
                    st.error("Gemini returned an empty response. Please try again.")
                    st.stop()
                



                st.session_state.model_response = json.loads(extracted_text)  # save first ✅

            # Display always runs, whether just generated or returning from page switch
            if st.session_state.model_response is not None:
                response_list = st.session_state.model_response

                

                # Add labels to dataframe
                label_map = {int(item["cluster_no"]): item["label"] for item in response_list}
                # Label map returns somethng like this:

                # {
                # "0":"Lapsed Low-Value Customers"
                # "1":"VIP High-Value Loyalists"
                # "2":"Standard Active Customers"
                # }

                
                customer_df["Segment"] = customer_df["model_preds"].map(label_map)
                st.session_state.n_segments = customer_df["Segment"].nunique()
                
            # ======================= Step 7: Dashboard =======================

            seg_dist = customer_df["Segment"].value_counts().reset_index()
            seg_dist.columns = ["Segment", "Count"]

            color_map = {}
            palette = ["#7F77DD", "#1D9E75", "#EF9F27"]
            for i, seg in enumerate(customer_df["Segment"].unique()):
                color_map[seg] = palette[i % 3]

            layout_defaults = dict(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=12),
                
                margin=dict(l=10, r=10, t=40, b=10),
            )

            col1, col2 = st.columns([1, 1.65])


        with col1:
            # Build the data for the animated donut
            seg_counts = customer_df["Segment"].value_counts()
            labels = seg_counts.index.tolist()
            values = seg_counts.values.tolist()
            colors = [color_map.get(s, "#888") for s in labels]

            labels_js  = str(labels)
            values_js  = str(values)
            colors_js  = str(colors)

            donut_html = f"""
            <div style="display:flex;flex-direction:column;align-items:center;gap:12px">
            <canvas id="donut" width="260" height="260"></canvas>
            <div id="legend" style="display:flex;flex-direction:column;gap:6px"></div>
            </div>

            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
            <script>
            const labels = {labels_js};
            const values = {values_js};
            const colors = {colors_js};
            const total  = values.reduce((a,b) => a+b, 0);

            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ccc' : '#333';
            const legend = document.getElementById('legend');
            labels.forEach((l,i) => {{
                const pct = ((values[i]/total)*100).toFixed(1);
                legend.innerHTML += `
                <div style="display:flex;align-items:center;gap:8px;font-family:sans-serif;font-size:12px;color:${{textColor}}">
                    <span style="width:10px;height:10px;border-radius:2px;background:${{colors[i]}};display:inline-block;flex-shrink:0"></span>
                    <span>${{l}}</span>
                    <span style="margin-left:auto;font-weight:500;color:${{textColor}}">${{pct}}%</span>
                </div>`;
            }});
            new Chart(document.getElementById('donut'), {{
                type: 'doughnut',
                data: {{
                labels: labels,
                datasets: [{{
                    data: values,
                    backgroundColor: colors,
                    borderColor: 'transparent',
                    borderWidth: 3,
                    hoverOffset: 8,
                }}]
                }},
                options: {{
                responsive: false,
                cutout: '65%',
                animation: {{
                    animateRotate: true,
                    animateScale: false,
                    duration: 1200,
                    easing: 'easeInOutQuart',
                }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                    callbacks: {{
                        label: ctx => ` ${{ctx.label}}: ${{ctx.parsed}} customers (${{((ctx.parsed/total)*100).toFixed(1)}}%)`
                    }}
                    }}
                }}
                }}
            }});
            </script>
            """

            
            components.html(donut_html, height=360)



                     



        with col2:
                fig_scatter = px.scatter(
                    customer_df,
                    x="Monetary",
                    y="Recency",
                    color="Segment",
                    color_discrete_map=color_map,
                    hover_data=["Frequency", "AOV"],
                    labels={
                        "Monetary": "Total spend (£)",
                        "Recency": "Days since last purchase"
                    },
                    opacity=0.7,
                )

                fig_scatter.update_traces(marker=dict(size=6, line=dict(width=0)))

                fig_scatter.update_layout(
                **layout_defaults,
                title=dict(text="Spend vs recency by segment", font=dict(size=14)),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(128,128,128,0.15)",
                    zeroline=False,
                    tickfont=dict(size=10),
                    title_font=dict(size=11),
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.07)",
                    zeroline=False,
                    tickfont=dict(size=10),
                    title_font=dict(size=11),
                ),
                legend=dict(
                font=dict(size=9),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(128,128,128,0.2)",
                borderwidth=1,
                itemsizing="constant",
                orientation="h",
                y=-0.35,
                x=0.5,
                xanchor="center",
            ),
                
                height=320,
            )
                

                st.plotly_chart(fig_scatter, use_container_width=True)



        col1_1, col1_2 = st.columns([1.5, 1])


        with col1_1:
                # Plot a bar chat for revenue of each cluster
                cluster_labels = customer_df["Segment"].unique()


                # Build revenue in the same order as cluster_labels appear
                revenue = []
                for seg in cluster_labels:
                    cluster_num = customer_df[customer_df["Segment"] == seg]["model_preds"].iloc[0]
                    if cluster_num == 0:
                        revenue.append(per_cluster_0)
                    elif cluster_num == 1:
                        revenue.append(per_cluster_1)
                    else:
                        revenue.append(per_cluster_2)
                   
                
                bar_fig = go.Figure(data=[go.Bar(
                    x = cluster_labels,
                    y = revenue,
                    marker_color=[color_map.get(seg, "#888") for seg in cluster_labels]
                )]) 

                bar_fig.update_layout(
                            
                    title = ('revenue Contribution of each cluster'),
                    xaxis_tickangle = -90, # Fixes the rotated labels
                    showlegend=False,        # removes the redundant legend
                    xaxis_title='Cluster label',
                    yaxis_title='Revenue',
                    height=400,
                    margin=dict(l=40, r=40, t=40, b=120)) # b=120 gives space for long labels
                
                bar_fig.update_traces(width=0.9)  # makes bars wider

                                
                        
                st.plotly_chart(bar_fig, use_container_width=True)


        with col1_2:
            # Merge segment labels into cluster_stats
            cluster_stats["Segment"] = cluster_stats["model_preds"].map(label_map)

            # Melt into long format so we can plot all RFM metrics together
            rfm_melt = cluster_stats[["Segment", "Avg_recency", "Avg_frequency", "Avg_monetary"]].melt(
                id_vars="Segment",
                var_name="Metric",
                value_name="Value"
            )

            # Clean up metric names for display
            rfm_melt["Metric"] = rfm_melt["Metric"].map({
                "Avg_recency":   "Recency",
                "Avg_frequency": "Frequency",
                "Avg_monetary":  "Monetary"
            })

            rfm_fig = px.bar(
                rfm_melt,
                x="Metric",
                y="Value",
                color="Segment",
                barmode="group",
                color_discrete_map=color_map,
                labels={"Value": "", "Metric": ""},
            )

            rfm_fig.update_layout(
                **layout_defaults,
                title=dict(text="Avg RFM values per segment", font=dict(size=14)),
                height=320,
                xaxis_tickangle=0,
                legend=dict(
                    font=dict(size=9),
                    bgcolor="rgba(0,0,0,0)",
                    orientation="h",
                    y=-0.25,
                    x=0.5,
                    xanchor="center",
                ),
            )

            st.plotly_chart(rfm_fig, use_container_width=True)    
                        

       

        st.write("---")
        st.subheader("Model's Interpretation of Clusters:")      

        labels_reasoning = {i["label"]: i["reasoning"] for i in response_list}    
        for keys in labels_reasoning:

            st.write(f"##### {keys}:")
            st.write(labels_reasoning[keys])
            st.write("----")
