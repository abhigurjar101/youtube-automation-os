import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
from wordcloud import WordCloud
from collections import Counter

# --- PAGE CONFIG ---
st.set_page_config(page_title="YouTube Automation OS", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff0000; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Automation OS")
    api_key = st.text_input("🔑 API Key", type="password")
    st.divider()
    country_code = st.selectbox("Target Region", ["US", "IN", "GB", "CA", "AU"], index=0)
    rpm = st.slider("Est. RPM ($)", 0.5, 10.0, 2.5)

# --- FUNCTIONS ---
def get_data(api_key, query, max_results=50):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    search_req = youtube.search().list(
        part="snippet", q=query, type="video", 
        regionCode=country_code, maxResults=max_results, order="viewCount"
    )
    search_res = search_req.execute()
    
    video_ids = [item['id']['videoId'] for item in search_res.get('items', [])]
    
    stats_req = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids))
    stats_res = stats_req.execute()
    
    data = []
    all_tags = []
    
    for item in stats_res.get('items', []):
        stats = item['statistics']
        snippet = item['snippet']
        
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        title = snippet['title']
        tags = snippet.get('tags', [])
        all_tags.extend(tags)
        
        engagement = ((likes + comments) / views * 100) if views > 0 else 0
        revenue = (views / 1000) * rpm
        
        blob = TextBlob(title)
        sentiment = "Positive" if blob.sentiment.polarity > 0 else "Neutral"
        
        raw_score = (views * 0.7) + (likes * 50) + (comments * 100)
        
        data.append({
            'Thumbnail': snippet['thumbnails']['high']['url'],
            'Title': title,
            'Views': views,
            'Likes': likes,
            'Engagement': round(engagement, 2),
            'Est. Earnings ($)': round(revenue, 2),
            'Sentiment': sentiment,
            'Title Len': len(title),
            'Published': snippet['publishedAt'],
            'Raw_Score': raw_score
        })
    
    df = pd.DataFrame(data)
    if not df.empty:
        df['Virality Score'] = (df['Raw_Score'] / df['Raw_Score'].max()) * 100
        df['Virality Score'] = df['Virality Score'].round(1)
    
    return df, all_tags

# --- MAIN UI ---
st.title("⚡ YouTube Automation OS")

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Enter Niche / Topic")
with col2:
    st.write("") 
    st.write("") 
    search_btn = st.button("🚀 Launch", use_container_width=True, type="primary")

if search_btn and api_key:
    with st.spinner('Analyzing...'):
        try:
            df, all_tags = get_data(api_key, query)
            
            # METRICS
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Views", f"{df['Views'].sum():,}")
            m2.metric("Total Earnings", f"${df['Est. Earnings ($)'].sum():,.0f}")
            m3.metric("Avg Virality", f"{df['Virality Score'].mean():.0f}/100")
            m4.metric("Title Len", f"{int(df['Title Len'].mean())}")
            
            st.divider()
            
            # TABS
            t1, t2, t3 = st.tabs(["Tag Spy", "Top Videos", "Analytics"])
            
            with t1:
                tag_counts = Counter(all_tags).most_common(15)
                st.text_area("📋 Copy Tags", ", ".join([t[0] for t in tag_counts]))
                
                wc = WordCloud(width=600, height=300, background_color='white').generate_from_frequencies(dict(tag_counts))
                fig, ax = plt.subplots()
                plt.imshow(wc, interpolation='bilinear')
                plt.axis("off")
                st.pyplot(fig)
                
            with t2:
                st.dataframe(
                    df[['Thumbnail', 'Title', 'Views', 'Virality Score']].sort_values('Virality Score', ascending=False),
                    column_config={"Thumbnail": st.column_config.ImageColumn("Preview"), "Virality Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100)},
                    use_container_width=True
                )
                
            with t3:
                fig, ax = plt.subplots()
                sns.scatterplot(data=df, x='Views', y='Est. Earnings ($)', hue='Sentiment', size='Virality Score', ax=ax)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")
elif search_btn and not api_key:
    st.error("⚠️ Please enter your API Key in the sidebar first.")
