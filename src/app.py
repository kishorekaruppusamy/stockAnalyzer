import streamlit as st
import sys
from tavily import TavilyClient
import os
from utils.helpers import search_news, analyze_news

print("Starting Stock Market News Analyzer...")

st.set_page_config(
    page_title="Stock Market News Analyzer",
    page_icon="📈",
    layout="wide"
)

os.environ["OPENAI_API_KEY"] = st.secrets.API_SECRETS.OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = st.secrets.API_SECRETS.TAVILY_API_KEY

# Initialize clients
tavily_client = TavilyClient(os.getenv('TAVILY_API_KEY'))

# Add custom CSS
print("Setting up UI components...")
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 18px;
        padding: 15px;
    }
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 10px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📈 Stock Market News Analyzer")

# Input form
with st.form("news_form"):
    prompt = st.text_input(
        "Enter your stock news query",
        placeholder="e.g., today's stock market news about tata motors",
        key="prompt"
    )
    submitted = st.form_submit_button("Get Analysis")

if submitted and prompt:
    print(f"\nProcessing query: {prompt}")
    try:
        with st.spinner('Searching for latest news...'):
            print("Fetching news from Tavily API...")
            search_results = search_news(tavily_client, prompt)
            print(f"Found {len(search_results.get('results', []))} news articles")

            # Extract relevant information from search results
            news_context = "\n".join([
                f"📰 {result.get('title', '')}\n" +
                f"Key Points: {result.get('content', '')}\n" 
                for result in search_results.get('results', [])[:5]
            ])

        with st.spinner('Analyzing news...'):
            print("Sending to OpenAI for analysis...")
            analysis = analyze_news(prompt, news_context)
            print("Analysis received from OpenAI")

        # Display results
        print("Displaying results to user...")
        st.success("Analysis Complete!")
        
        # Show sources
        with st.expander("View News Sources"):
            for idx, result in enumerate(search_results.get('results', [])[:5], 1):
                st.markdown(f"""
                    **Article {idx}:** [{result.get('title', '')}]({result.get('url', '')})  
                    {result.get('content', '')}
                    ---
                """)

        # Show analysis
        st.markdown("### Analysis")
        st.markdown(analysis)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        st.error(f"An error occurred: {str(e)}") 