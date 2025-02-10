from ETLBooks_flask import app
import pandas as pd
from transformers import pipeline
import os
from plotly_graphs import (cleaning_composition_data,cleaning_avg_price_data,
                           cleaning_price_review_data,cleaning_avg_review_data)
import torch

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from transformers import pipeline

ai_model = pipeline("text-generation", model="HuggingFaceH4/zephyr-7b-beta",
                    torch_dtype=torch.bfloat16)


def ai_response(prompt):
    response = ai_model(
        prompt,
        max_new_tokens=100,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.5,
        top_k=50,
        repetition_penalty=1.5,
        pad_token_id=50256
    )
    
    full_response = response[0]['generated_text'].strip()
    commentary = full_response.split("Commentary:")[-1].split("Commentry:")[-1].strip()

    return commentary

def generate_composition_comment(df_composition):
    if df_composition.empty or 'category' not in df_composition.columns:
        return "No valid data available for category composition analysis."
    try:
        top_categories = df_composition['category'].value_counts().nlargest(7)
        
        prompt = f"""Analyze the book category distribution below and provide a concise commentary.
Avoid URLs or external references. Focus on trends and proportions.

Data:
{top_categories.to_string()}

Commentary:""" 
        
        output = ai_response(prompt)
        return output
    
    except Exception as e:
        print(f"Composition analysis error: {e}")
        return "Failed to generate composition commentary."

def generate_avg_price_comment(df_avg_price):
    if df_avg_price.empty:
        return "No valid data available for category composition analysis."
        
    df_avg_price['price'] = pd.to_numeric(df_avg_price['price'], errors='coerce')
    valid_prices = df_avg_price.dropna(subset=['price'])
                     
    avg_price_per_category = valid_prices.groupby('category', observed=True)['price'].mean().reset_index()
    avg_price_per_category.columns = ["Category", "Average Price"]
    
    prompt=f"""
    Analyse the following average data on book sales and point out any intresting trends or situations:
    {avg_price_per_category}
    """
    
    comment = ai_response(prompt)
    
    return comment

def generate_price_review_comment(df_price_review):
    if df_price_review.empty or 'category' not in df_price_review.columns:
        return "No valid data available for category composition analysis."
    review_mapping = {
            "One": 1, "Two": 2, "Three": 3, 
            "Four": 4, "Five": 5
        }
    df_price_review['review'] = df_price_review['review'].replace(review_mapping)    
    df_price_review['date_extracted'] = pd.to_datetime(df_price_review['date_extracted'], errors='coerce')
    latest_date = df_price_review['date_extracted'].max()
    df_latest = df_price_review[df_price_review['date_extracted'] == latest_date]
    
    prompt=f"""Following the data below can you explain how the lowess line moves at this moment and explain what is the
    trend for reviews and price?: 
    {df_latest}
    """
    comment = ai_response(prompt)
    
    return comment

def generate_avg_review_comment(df_avg_review):
    if df_avg_review.empty or 'category' not in df_avg_review.columns:
        return "No valid data available for category composition analysis."    
    review_mapping = {
            "One": 1, "Two": 2, "Three": 3, 
            "Four": 4, "Five": 5
        }
    df_avg_review['review'] = df_avg_review['review'].replace(review_mapping)    
    df_avg_review['date_extracted'] = pd.to_datetime(df_avg_review['date_extracted'], errors='coerce')
    valid_reviews = df_avg_review.dropna(subset=['review'])
                 
    avg_review_per_category = valid_reviews.groupby('category', observed=True)['review'].mean().reset_index()
    avg_review_per_category.columns = ["Category", "Average review"]

    
    prompt=f"""Following the data below can you explain how the lowess line moves at this moment and explain what is the
    trend for reviews and price?: 
    {avg_review_per_category}
    """
    comment = ai_response(prompt)
    
    return comment

with app.app_context():
    try:
        composition_comment = generate_composition_comment(cleaning_composition_data())
        avg_price_comment= generate_avg_price_comment(cleaning_avg_price_data())
        price_review_comment = generate_price_review_comment(cleaning_price_review_data())
        avg_review_comment = generate_avg_review_comment(cleaning_avg_review_data())
    except:
        pass    