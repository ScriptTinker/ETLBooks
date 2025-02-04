import pandas as pd
from transformers import pipeline
import logging
import os
from plotly_graphs import df_composition

composition_comment=None

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logging.getLogger("transformers").setLevel(logging.ERROR)

from transformers import pipeline

ai_model = pipeline(
    "text-generation",
    model="HuggingFaceH4/zephyr-7b-beta",
    device_map="cpu")


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

composition_comment = generate_composition_comment(df_composition)