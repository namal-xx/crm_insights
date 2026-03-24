# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import google.generativeai as genai
import PIL.Image
import io
import math


from helper_functions import make_categories, suggestion_prompt_image, image_prompt, suggestion_promt_csv 
from helper_functions import get_ai_response, create_custom_cards_html, show_chat, configure_gemini

# Make our chatbot more likley to chatgpt, so a user can ask follow-up questions, rather than chatbot just stops after
# giving suggestions for the leads.



# Gemini API setup
configure_gemini()
gemini_model = genai.GenerativeModel("gemini-2.5-flash") # Selecting the model 


# We'll use per se these variables  later in the app to store the conversation history and the lead context. 
if "messages" not in st.session_state: 
    st.session_state.messages = []

if "lead_context" not in st.session_state:
    st.session_state.lead_context = "" 

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "uploaded_csv" not in st.session_state:
    st.session_state.uploaded_csv = None

if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

if "user_input" not in st.session_state:
    st.session_state.user_input = "Image (screenshot of lead)"

if "output_format" not in st.session_state:
    st.session_state.output_format = None

if "csv_format" not in st.session_state:
    st.session_state.csv_format = None

if "image_response" not in st.session_state:
    st.session_state.image_response = None

if "csv_response" not in st.session_state:
    st.session_state.csv_response = None







# Write the title of the app
st.title("AI Lead Scoring App")

# Load the trained model
try:
    model = joblib.load("leads_scoring_model_pipeline.pkl")
except Exception as e: 
    st.error(f"Error loading model: {e}")

  


# Step 2: For user input
user_input = st.selectbox("Upload type", 
                          ["Image (screenshot of lead)", "CSV (multiple leads)"],

                          # By default, it selects the first option (image upload) when the app loads for the first time.
                          # But if user has already made a selection, then show that selection instead of default one.
                          index = ["Image (screenshot of lead)", "CSV (multiple leads)"].index(st.session_state.user_input)
)
st.session_state.user_input = user_input  # save selection to session state so it persists across interactions)


# ============= Below code is for images =================


if user_input == "Image (screenshot of lead)":
    uploaded_image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"]) 

    if uploaded_image:
        new_file = uploaded_image.getvalue()
    
        # Only reset if it's a different image than before
        if new_file != st.session_state.get("uploaded_image"):
            st.session_state.uploaded_image = new_file
            st.session_state.image_response = None
            st.session_state.messages = []
            st.session_state.suggestion_added = False

    if st.session_state.uploaded_image:
        st.write("Processing image.....")

        image = PIL.Image.open(io.BytesIO(st.session_state.uploaded_image))


        # Extract recency and frequency using OpenAI vision
        st.write("Extracting details from image...")



 

        if st.session_state.image_response is None: 
            IMAGE_PROMPT =  image_prompt()
            response = gemini_model.generate_content([IMAGE_PROMPT, image])
            st.session_state.image_response = response.text.strip()
             
        extracted_text  = st.session_state.image_response
        

        # Parse the text 
        try:
           # Creates a list of features with their values in a single line.. (E.g., "Recency": .., "Frequency":..., ...) 
           lines = extracted_text.strip().split("\n")  
           data = {}
           for line in lines:
               if ":" in line:
                   key, value = line.split(":")
                   data[key.strip()] = value.strip() # this is same as data["Recency"] = 23.. this how we add things to a dictionary 
                   customer_id = data.get("CustomerID", "Not found")
                   recency = int(data.get("Recency", 0))
                   frequency = int(data.get("Frequency", 0))

        except Exception as e:
            st.error(f"Could not parse extracted text: {e}")
            st.stop() # stop the execution of the app if json is not valid    


        
        # Make prediction using the loaded model
        input_features = np.array([[recency, frequency]])
        model_probs = model.predict_proba(input_features)[0, 1] # Take the probability of the first (and only) sample belonging to class 1

        # Get LLM suggestions
        Category = make_categories(model_probs)


       # Only call Gemini if suggestion not already generated
        if st.session_state.get("suggestion_text") is None:
            SUGGESTION_PROMPT_IMAGE = suggestion_prompt_image(model_probs, recency, frequency, Category, customer_id)
            st.session_state.suggestion_text = get_ai_response(
                prompt=SUGGESTION_PROMPT_IMAGE,
                model=gemini_model
            )

        suggestion_text = st.session_state.suggestion_text

        

        st.write("#### Lead information:")
        st.write("**Category:**", Category)
        st.write("**Probability:**", f"{model_probs:.2f}")
        st.write(suggestion_text)         

        # Store context of leads for follow-up questions  
        st.session_state.lead_context = f"""
        Lead info: CustomerID={customer_id},
        Recency={recency} days, 
        Frequency={frequency},
        Category={Category},
        Probability={model_probs:.2f}
        Suggestion given: {suggestion_text}
        """

        # avoid adding the suggestion to the chat history more than once
        if "suggestion_added" not in st.session_state:
            st.session_state.messages.append({
                "role": "assistant",
                "content": suggestion_text
            })
            st.session_state.suggestion_added = True  # ← flag so it never runs again

        if st.session_state.lead_context:
            show_chat(ai_model = gemini_model)



# =============== Below code is for CSV files ==============



# If user uploads CSV then:
elif user_input ==  "CSV (multiple leads)":
        uploaded_csv = st.file_uploader("Upload CSV")

        if uploaded_csv:
            file_name = uploaded_csv.name
            if file_name != st.session_state.get("uploaded_csv_name"):
                st.session_state.uploaded_csv_name = file_name
                st.session_state.messages = []
   
            df = pd.read_csv(uploaded_csv)

            # Normalize column names to title case
            df.columns = [col.strip().title() for col in df.columns]

            if "Frequency" not in df.columns or "Recency" not in df.columns:
                st.error("CSV must have 'Recency' and 'Frequency' columns") 
                st.stop()

            else:             
                    
                # Make predictions
                model_probs = model.predict_proba(df[["Frequency", "Recency"]])[:, 1] # get the probabilites for postive class
                df["Probs"] = model_probs
                df["Category"] =  df["Probs"].apply(make_categories)

                target_df = df.copy()

                SUGGESTION_PROMPT_CSV = suggestion_promt_csv(target_df=target_df)
                defined_max_tokens = min(500 * len(target_df), 8192) 


                if st.session_state.csv_response is None:
                    suggestion_text = get_ai_response(prompt=SUGGESTION_PROMPT_CSV,
                                                    model=gemini_model,
                                                    max_tokens=defined_max_tokens)
                    st.session_state.csv_response = suggestion_text

            suggestions = st.session_state.csv_response.split("\n\n")

            # Pad or trim to match the dataframe length
            if len(suggestions) < len(target_df):
                suggestions += ["No suggestion available."] * (len(target_df) - len(suggestions))
            else:
                suggestions = suggestions[:len(target_df)]

                              
            target_df["Suggestions"] = suggestions
            st.session_state.uploaded_csv = target_df # STORE IN SESSION_STATE     
                
        if  st.session_state.uploaded_csv is not None:
                    
            target_df = st.session_state.uploaded_csv # STORE THAT TO LOCAL VARIABLE FOR FURTHER USE.    

            # Prepare sorted version once (most common order)
            scored_sorted = target_df.sort_values("Probs", ascending=False).copy()

            # Prepare context once (used by chat & can be shown in CSV mode too)
            context_csv = scored_sorted.to_csv(index=False)
            
            st.session_state.lead_context = f"""
            You are a helpful CRM / sales assistant.
            Here are the recently scored leads (highest probability first):

            {context_csv}
            """

            selection = st.radio("**Output format**",
                                 ["📊 Dashboard", "📄 Downloadable CSV"],
                                 index = None if st.session_state.output_format is None 
                                 else ["📊 Dashboard", "📄 Downloadable CSV"].index(st.session_state.output_format),

                                 horizontal=True,
                                 key = "csv_output_mode" )
            if selection is not None:
                st.session_state.output_format = selection  # save selection to session state so it persists across interactions


            if selection is None:
                st.info("Please select an output format above.")
                # st.stop()                     
            


            if selection == "📄 Downloadable CSV":                   
                
                # Ask user what they want
                suggestion_scope = st.radio("**Generate suggestions for:**",
                                        ["Top 10 Hot leads only", "All leads"],
                                        index = None if st.session_state.csv_format is None
                                        else ["Top 10 Hot leads only", "All leads"].index(st.session_state.csv_format),

                                        horizontal=True,
                                        key = "csv_scope")
                
                if suggestion_scope is not None:
                    st.session_state.csv_format = suggestion_scope  # save selection to session state so it persists across interactions
                
                if suggestion_scope is None:
                    st.info("Please select the scope for suggestions above.")
                    st.stop()   
                
                if suggestion_scope == "Top 10 Hot leads only":
                    
                    # Check if a user csv has even hot leads or not  
                    if target_df["Category"].eq("Hot").sum() == 0:
                        st.info("No Hot leads found in the uploaded CSV.")  

                    else:                
                            target_df = target_df[target_df['Category'] == 'Hot'].sort_values('Probs', ascending=False).head(10)
                    
                # If user selects "ALL_LEADS"
                elif suggestion_scope == "All leads":
                    target_df = target_df.sort_values('Probs', ascending=False)
                    
                    
                    id_col = next((col for col in df.columns if "id" in col.lower()), None)
                    cols = [id_col, 'Recency', 'Frequency', 'Category', 'Probs', "Suggestions"]
                    target_df = target_df[cols] if id_col in target_df.columns else target_df[cols[1:]]
                    
                    
                    # Show table
                    st.subheader("Scored Leads Table")
                                    
                    # show the table in the app 
                    if st.session_state.lead_context: # only show chat if there's context
                        st.dataframe(target_df,
                        use_container_width=True,
                        height=400,                # or None / auto
                        hide_index=True,) 
                        
                        st.divider() 
                        st.subheader("💬 Ask Questions About Leads")
                        show_chat(ai_model = gemini_model)

            
          # ======================== for dashboard ==========================
            

            elif selection == "📊 Dashboard":

                id_col = next((col for col in df.columns if "id" in col.lower()), None)
                cols = [id_col, 'Recency', 'Frequency', 'Category', 'Probs', "Suggestions"]
                target_df = target_df[cols] if id_col in target_df.columns else target_df[cols[1:]]
   
                
                st.subheader("Scored Leads")

                col1, col2, col3, col4 = st.columns(4)

                if "filter_cat" not in st.session_state:
                    st.session_state.filter_cat = "All"

                    # Other way to do the same.
                    # st.session_state["filter_cat"] = "All"

                if col1.button("All"): st.session_state.filter_cat = "All"
                if col2.button("🔴 Hot"): st.session_state.filter_cat = "Hot"
                if col3.button("🟡 Warm"): st.session_state.filter_cat = "Warm"
                if col4.button("🔵 Cold"): st.session_state.filter_cat = "Cold"

                if st.session_state.filter_cat == "All":
                    filtered = target_df
                else:
                    filtered = target_df[target_df["Category"] == st.session_state.filter_cat]



                # Pagination   
                CARDS_PER_PAGE = 6
                total_pages = max(1, math.ceil(len(filtered) / CARDS_PER_PAGE))

                if "page" not in st.session_state:
                    st.session_state.page = 1

                page = st.session_state.page # at first, it is assigned to 1. 

                col1, col2 = st.columns(2)

                # Index the dataframe based on current page 
                start = (page - 1) * CARDS_PER_PAGE # e.g. at first we're on page 1.. so (1 - 1) * cards per page = 0 .. starting index is 0       
                end = start + CARDS_PER_PAGE # 0 + 3 = 3, means from 0 to 3 cards will be shown on page 1 and maths goes on for other pages.
                page_df = filtered.iloc[start:end]

                # Cards
                with col1:
                    for _, row in page_df.iloc[:3].iterrows():               
                        create_custom_cards_html(row)

                with col2:
                    for _, row in page_df.iloc[3:6].iterrows():               
                            create_custom_cards_html(row)


                # Pagination controls
                st.write(f"Page {page} of {total_pages}")
                p1, p2, p3 = st.columns([1, 2, 1])

                if p1.button("◀ Prev") and page > 1:
                    st.session_state.page -= 1
                    st.rerun()
                if p3.button("Next ▶") and page < total_pages:
                    st.session_state.page += 1
                    st.rerun()

                # ============= Follow-up questions interface ===============

                if st.session_state.lead_context: # only show chat if there's context
                    st.divider()
                    st.subheader("💬 Ask Questions About Leads") 
                    show_chat(ai_model = gemini_model)    






