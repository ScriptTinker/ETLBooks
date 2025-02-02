import pandas as pd
import tensorflow as tf
from transformers import TFAutoModelForCausalLM, AutoTokenizer
from plotly_graphs import df_composition,df_avg_review,df_avg_price,df_price_review

# Load text generation model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
model = TFAutoModelForCausalLM.from_pretrained("distilgpt2")


def generate_comment(prompt):
    """Generates textual comment using the AI model with better constraints"""
    try:
        inputs = tokenizer(
            prompt, 
            return_tensors='tf', 
            max_length=256,
            truncation=True
        )
        
        outputs = model.generate(
            inputs['input_ids'],
            max_new_tokens=100,  
            num_return_sequences=1,
            temperature=0.3,     
            top_k=30,            
            top_p=0.9,           
            repetition_penalty=1.5, 
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        comment = tokenizer.decode(
            outputs[0], 
            skip_special_tokens=True
        ).replace(prompt, "").strip()
        
        return comment
    
    except Exception as e:
        return f"Comment generation failed: {str(e)}"


def generate_composition_comment(df_composition):
    """Generates focused category analysis"""
    if df_composition.empty or 'category' not in df_composition.columns:
        return "No category data available for analysis."

    try:
        category_counts = df_composition['category'].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]
        top_categories = category_counts.head(6)
        
        # Structured prompt template
        prompt = """Analyze book category distribution from this data:
        Top Categories:
        {}
        
        1. Identify the dominant category with its percentage
        2. Note any surprising omissions from expected categories
        3. Suggest potential reasons for the distribution
        Answer in 3 concise bullet points:""".format(
            "\n".join([f"- {row['Category']}: {row['Count']} books" 
                      for _, row in top_categories.iterrows()])
        )
        
        return generate_comment(prompt)
    
    except Exception as e:
        return f"Analysis error: {str(e)}"

def generate_avg_price_comment(df_avg_price):
    """Generates a comment for the average price per category visualization."""
    if df_avg_price.empty:
        return "No data available for average price analysis."
    
    df_avg_price['price'] = pd.to_numeric(df_avg_price['price'], errors='coerce')
    valid_prices = df_avg_price.dropna(subset=['price'])
    
    if valid_prices.empty:
        return "No valid price data available for analysis."
    
    avg_price_per_category = valid_prices.groupby('category', observed=True)['price'].mean().reset_index()
    avg_price_per_category.columns = ["Category", "Average Price"]
    
    prompt = f"""Analyze the average price of books across categories:
    {avg_price_per_category.to_string(index=False)}
    Provide insights on the most and least expensive categories:"""
    
    return generate_comment(prompt)

def generate_price_review_comment(df_price_review):
    """Generates a comment for the price vs. review visualization."""
    if df_price_review.empty:
        return "No data available for price-review analysis."
    
    review_mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    df_price_review['review'] = df_price_review['review'].replace(review_mapping).astype(float)
    
    prompt = f"""Analyze the relationship between book prices and review scores:
    - Average Price: {df_price_review['price'].mean():.2f}
    - Average Review: {df_price_review['review'].mean():.2f}
    Provide insights on whether higher-priced books tend to have better reviews:"""
    
    return generate_comment(prompt)

def generate_avg_review_comment(df_avg_review):
    """Generates a comment for the average review per category visualization."""
    if df_avg_review.empty:
        return "No data available for review analysis."
    
    review_mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    df_avg_review['review'] = df_avg_review['review'].replace(review_mapping).astype(float)
    valid_reviews = df_avg_review.dropna(subset=['review'])
    
    if valid_reviews.empty:
        return "No valid review data available for analysis."
    
    avg_review_per_category = valid_reviews.groupby('category', observed=True)['review'].mean().reset_index()
    avg_review_per_category.columns = ["Category", "Average Review"]
    
    prompt = f"""Analyze the average review scores across categories:
    {avg_review_per_category.to_string(index=False)}
    Provide insights on which categories have the highest and lowest customer satisfaction:"""
    
    return generate_comment(prompt)

composition_comment=generate_composition_comment(df_composition)
