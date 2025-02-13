from typing import Dict, List
from openai import OpenAI
from tavily import TavilyClient


def search_news(client: TavilyClient, query: str) -> Dict:
    """
    Search for news using Tavily API
    """
    print(f"\nSearching news for query: {query}")
    try:
        results = client.search(
            query=query,
            search_depth="advanced",
            include_domains=["moneycontrol.com", "economictimes.indiatimes.com", "reuters.com", "bloomberg.com",
                             "business-standard.com", "financialexpress.com", "thehindu.com",
                             "theeconomicstimes.indiatimes.com", "timesofindia.indiatimes.com", "livemint.com",
                             "businessinsider.com", "businessinsider.in", "business-standard.com",
                             "business-standard.in", "business-standard.com.in"]
        )

        # Filter and process the results
        processed_results = []
        for article in results.get('results', []):
            # Extract key information
            title = article.get('title', '').strip()
            content = article.get('content', '').strip()

            # Skip articles with no meaningful content
            if not title or not content or len(content) < 50:
                continue

            # Extract the most relevant part of the content (first 2-3 sentences)
            sentences = content.split('.')[:3]
            key_content = '. '.join(sentences) + '.'

            processed_results.append({
                'title': title,
                'content': key_content,
                'url': article.get('url', '')
            })

        # Sort by relevance (assuming first results are most relevant)
        processed_results = processed_results[:5]

        print(f"Search successful - Processing {len(processed_results)} most relevant articles")
        for idx, article in enumerate(processed_results, 1):
            print(f"\nArticle {idx}:")
            print(f"Title: {article['title']}")
            print(f"Key Points: {article['content'][:200]}...")

        return {'results': processed_results}
    except Exception as e:
        print(f"Error in search_news: {str(e)}")
        raise


def get_system_prompt(query: str) -> str:
    """
    Get appropriate system prompt based on query type
    """
    query = query.lower()

    if 'technical analysis' in query or 'chart' in query:
        return """You are a technical analyst specializing in stock market analysis. 
               Focus on technical indicators, price patterns, and chart analysis. 
               Provide insights on support/resistance levels, trends, and potential trading signals."""

    elif 'fundamental' in query or 'financials' in query or 'balance sheet' in query:
        return """You are a fundamental analyst specializing in company financials. 
               Focus on financial metrics, company performance, balance sheet analysis, 
               and key performance indicators. Provide insights on company's financial health and valuation."""

    elif 'news' in query or 'latest' in query:
        return """You are a financial news analyst specializing in real-time market updates. 
               Focus on recent developments, market sentiment, and potential impact on stock prices. 
               Provide a comprehensive analysis of news events and their market implications."""

    elif 'competitor' in query or 'industry' in query or 'sector' in query:
        return """You are an industry analyst specializing in competitive analysis. 
               Focus on industry trends, competitive positioning, market share analysis, 
               and sector-wide developments. Compare the company with its peers."""

    else:
        return """You are a comprehensive financial analyst. Analyze the stock market information 
               considering both technical and fundamental factors. Provide a balanced view of 
               market conditions, company performance, and potential investment implications."""


def analyze_news(prompt: str, news_context: str) -> str:
    """
    Analyze news using OpenAI's GPT model
    """
    print("\nInitializing OpenAI client...")
    client = OpenAI()
    print(f"Determining analysis type for query: {prompt}")
    system_prompt = get_system_prompt(prompt)
    print(f"Using specialized system prompt for analysis")

    print("Sending request to OpenAI...")
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Based on the following news about {prompt}, provide a comprehensive analysis:\n\n{news_context}"
                }
            ]
        )
        print("Successfully received analysis from OpenAI")
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error in analyze_news: {str(e)}")
        raise
