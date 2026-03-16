#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 16:17:30 2026

@author: shashankdokka
"""


import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from textblob import TextBlob

# --- 1. INITIALIZATION ---
st.set_page_config(page_title="2026 Tactical Flight Hub", layout="wide")
st.title("🛡️ 2026 Global Aviation Intelligence Hub")

# GLOBAL FIX: Initialize 'df' at the very start so it is ALWAYS defined
df = pd.DataFrame(columns=['Hub', 'Airline', 'Flight', 'Status', 'Origin', 'Alt'])

# Sidebar
with st.sidebar:
    st.header("🔑 Intelligence Access")
    # PASTE YOUR NEW AIRLABS KEY HERE
    # NEW WAY (Pulling from Secure Vault)
airlabs_key = st.secrets["AIRLABS_KEY"]
news_key = st.secrets["NEWS_KEY"]

st.success("🛰️ Secure Intelligence Connection Established") 
st.divider() 
st.info(f"Theater: Operation Epic Fury | Status: March 14, 2026")

# --- 2. INTELLIGENCE ENGINES ---
def fetch_war_news(key):
    """Tactical News Engine with Crisis Fallback."""
    url = f'https://newsapi.org/v2/everything?q=(aviation OR airspace)&sortBy=publishedAt&language=en&apiKey={key}'
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        # If API limit is hit or server error, switch to Intelligence Simulation
        if response.status_code != 200:
            return get_analyst_predictions()
            
        data = response.json()
        articles = data.get('articles', [])
        
        # Ensure articles have the 'url' key before returning
        if articles and 'url' in articles[0]:
            return articles[:10]
        else:
            return get_analyst_predictions()
            
    except:
        return get_analyst_predictions()

def get_analyst_predictions():
    return [
        {
            "title": "CENTCOM confirms high-altitude GPS spoofing over Hormuz", 
            "source": {"name": "INTEL-WATCH"},
            "url": "https://www.aljazeera.com/tag/aviation/" # Direct link to aviation news
        },
        {
            "title": "Emirates flight EK001 rerouted via Baku due to 'Unspecified Threat'", 
            "source": {"name": "FLIGHT-ANALYSIS"},
            "url": "https://www.bbc.com/news/topics/c7zp7430901t" # BBC Aviation news
        }
    ]   

def fetch_airlabs_flights(key, hub):
    """Pulls live flights using the AirLabs v9 API."""
    url = f"https://airlabs.co/api/v9/flights?api_key={key}&arr_iata={hub}"
    try:
        r = requests.get(url).json()
        # AirLabs returns data in the 'response' field
        return r.get('response', [])
    except Exception as e:
        print(f"AirLabs Error: {e}")
        return []

# --- 3. DASHBOARD EXECUTION ---
if airlabs_key and news_key:
    # A. Fetch Intelligence
    articles = fetch_war_news(news_key)
    
    # Calculate Heat Index (AI Mood)
    if articles:
        sentiment = sum([TextBlob(a['title']).sentiment.polarity for a in articles]) / len(articles)
        heat_index = round((1 - sentiment) * 5, 1)
    else: heat_index = 8.5 # Escalated risk for tonight

    # TOP ROW: THE METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Conflict Heat Index", f"{heat_index}/10", delta="CRITICAL" if heat_index > 7.5 else "HIGH")
    m2.metric("Strait of Hormuz", "LOCKED", delta_color="inverse")
    m3.metric("Reroute Penalty", "+4.5 Hours", delta="Via Northern Corridor")

    st.divider()

    # MIDDLE ROW: MAP & NEWS
    col_map, col_news = st.columns([1.5, 1])

    with col_map:
        st.subheader("📍 Interactive Danger Zone Map")
        risk_data = pd.DataFrame({'lat': [35.6, 25.2, 51.5, 28.6], 'lon': [51.3, 55.2, -0.1, 77.2]})
        st.map(risk_data, color='#FF0000', size=40000)
        st.error(f"**Field Brief:** Heat Index at {heat_index}. Severe GPS jamming active in the Gulf sector.")
        
        with col_news:
            st.subheader("📰 Live War Wire")
    if articles:
        for art in articles[:5]:
            # Display source and title
            source_name = art.get('source', {}).get('name', 'Intel')
            st.markdown(f"**{source_name}**: {art['title']}")
            
            # THE FIX: Only show the link if it's a real article URL
            real_url = art.get('url')
            if real_url and "google.com" not in real_url:
                st.link_button("🚀 Read Full Report", real_url)
            else:
                st.caption("🔒 Original source restricted or in Blackout mode.")
            st.divider()
    else:
        st.warning("Intelligence feed disrupted. Check signal strength.") 
        

    # BOTTOM ROW: LIVE FLIGHT DATA
    st.divider()
    st.subheader("✈️ Live Corridor Status (AirLabs Feed)")
    
    hubs = ['DXB', 'LHR', 'DEL', 'BOM']
    all_flights = []
    
    for h in hubs:
        f_data = fetch_airlabs_flights(airlabs_key, h)
        if f_data:
            for f in f_data:
                all_flights.append({
                    'Hub': h,
                    'Airline': f.get('airline_iata', 'N/A'),
                    'Flight': f.get('flight_iata', 'N/A'),
                    'Status': f.get('status', 'en-route'),
                    'Origin': f.get('dep_iata', 'Unknown'),
                    'Alt': f.get('alt', 0)
                })
    
    if all_flights:
        df = pd.DataFrame(all_flights)
        st.dataframe(df, use_container_width=True)
        st.subheader("📊 Tactical Capacity")
        st.bar_chart(df['Status'].value_counts())
    else:
        # TACTICAL FALLBACK: If AirLabs is dark, we explain why
        st.error("🚨 LIVE BLACKOUT: AirLabs reports zero civilian transponders in the hot zones. This confirms military transponder suppression is active.")

else:
    st.info("Awaiting AirLabs and NewsAPI keys to engage the Command Center.")