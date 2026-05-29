# AI driven CRM Insights 

This is an AI powered CRM dashboard that scores leads and segments customers using Machine learning and Gemini's LLM. You can get follow-up recommendations and ask questions about your leads by using AI chat interface 

![Image of home page](home-page.png)


## Links:

- Check out the [Live App](https://crminsights-byeryl6xnrmrnm728amppf.streamlit.app/).
- Watch the full demo video on [my YouTube channel](https://www.youtube.com/watch?v=v3zBEEgcmqU)
- Read the full article on [Medium](https://medium.com/@namalrizwan4/raw-sales-data-to-smart-decisions-an-ai-ml-powered-crm-dashboard-da52e84eac06)
 
## Overview:

**What problem does this app solves?**

Slow lead scoring silently drains business revenue, yet most companies don't realize it until the damage is done. The numbers tell a brutal story: businesses lose 70–80% of potential revenue due to delayed responses, and 78% of customers simply go with whoever reaches out first. Leads contacted within 5 minutes are 100x more likely to convert compared to those reached after 30 minutes, and every minute beyond that window makes qualification 21 times less likely. For sales teams, this translates to over $75,000 lost per rep annually in missed opportunities.

This app was built to solve exactly that - giving businesses AI-powered lead scoring, automated follow-up recommendations, and behavioral customer segmentation so they can identify and act on high-value leads before the window closes.


 ## Features:
 
 - Upload CSV data to score leads using the lead scoring model.
 - AI-powered chatbot to query and explore your lead data.
 - Automated AI-generated recommendations for follow-ups.
 - Customer segmentation using clustering techniques.
 - Interactive dashboard to visualize customer segments.


## Tech Stack:

- **Pandas** - data preprocessing
- **Scikit-learn** - machine learning models
- **Gemini (gemini-2.5-flash)** - LLM-powered insights and chat
- **Plotly** - interactive data visualizations
- **Streamlit** - web application framework
- **HTML & CSS** - for customization


## Machine learning details:

- **Models used:** 
    - Logistic Regression - Lead scoring.
    - KMeans - Customer segmentation  

- **Feature Engineering:**    

    - **Customer Segmentation:**
       - AOV (Average Order Value)
       - RFM (Recency, Frequency, Monetary)
       - Product Diversity
       - Average purchase interval
           
    - **Lead Scoring:** 
        - Recency
        - Frequency
           
              
## How it works:

1. Upload CRM data (CSV format)
2. Data is preprocessed and features are engineered
3. Leads are scored using a trained Logistic Regression model
4. Customers are segmented using KMeans clustering
5. Results are visualized in an interactive dashboard
6. Users can interact with data using an AI chatbot for insights and recommendations
       

## Project Structure:

```
.streamlit/
pages/
    customer_seg.py
    lead_scoring.py
sample_data/
    crm_segmentation_data.csv
    lead_scoring.csv    
README.md
.gitignore
requirements.txt
crm_logo.png
app.py
home.py
about.py
helper_functions.py
kmeans_model_crm.pkl
leads_scoring_model_pipeline.pkl
scaler_crm.pkl
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Clone the Repository
```bash
git clone https://github.com/namal-xx/crm_insights.git
cd crm-insights
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the root directory and add your Gemini API key: 
```
GEMINI_API_KEY=your_api_key_here
```

### Run the App
```bash
streamlit run app.py
```


## Usage

*Note: This repository includes sample data in the sample_data/ directory. No external dataset is required to run the app.*

### Lead Scoring
1. Navigate to the **Lead Scoring** page and upload your leads CSV
2. Get scored leads and AI-powered follow-up recommendations
3. Use the **AI Chat** to ask questions about your leads

### Customer Segmentation
1. Navigate to the **Customer Segmentation** page and upload your customer CSV
2. View segments and AI-generated cluster labels along with their reasoning


## License

This project is licensed under the MIT License.

