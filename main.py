from pytrends.request import TrendReq

from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI

from bs4 import BeautifulSoup
from wordpress import post

import dotenv
import random
import re

dotenv.load_dotenv()

def is_html(text):
    html_pattern = re.compile(r'<[^>]+>')
    return bool(html_pattern.search(text))

pytrends = TrendReq(hl='en-US', tz=300, retries=3)
trends = pytrends.realtime_trending_searches(pn='US', cat='t')

llm = ChatOpenAI(model='gpt-4')

humanMessage = "{trendsUrl} Read This post and rewrite in new form as a proper SEO optimized article with headings and subheadings, containing a minimum of 3000 words of human-written content, while bypassing AI detector. Please output the results in HTML format including head title, description, keywords."

prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(humanMessage),
    ]
)

conversation_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

posted = False

while not posted and trends:
    trend = random.choice(trends)
    trends.remove(trend)

    articles = trend['articles']
    for article in articles:
        news_url = article['url']
        result = conversation_chain({"trendsUrl": news_url})
        html = result['text'].replace('<p>', '<span>').replace('</p>', '</span>')

        if is_html(html):
            soup = BeautifulSoup(html, 'html.parser')

            title = soup.title.text.strip()

            description = soup.find('meta', attrs={'name': 'description'})
            if description:
                description = description['content'].strip()

            keywords = soup.find('meta', attrs={'name': 'keywords'})
            if keywords:
                keywords = keywords['content'].strip()

            post(title, description, keywords, html)
            
            posted = True
            break