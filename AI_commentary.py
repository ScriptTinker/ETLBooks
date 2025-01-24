"""
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from plotly_graphs import books_composition_data



model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

def generate_comment(data):
    prompt = f"Based on the following data write a comprehensive report: {data}"
    inputs = tokenizer.encode(prompt, return_tensors="tf")

    # Explicitly set the device to CPU (already handled by disabling GPUs)
    output = model.generate(inputs, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2, temperature=0.7)

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text

composition_comment = generate_comment(books_composition_data)
"""