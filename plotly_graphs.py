import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from ETLBooks_flask import app
from ETLBooks_flask.models import Book

# Funzione per gestire gli errori
def handle_error(e):
    print(f"Si è verificato un errore: {e}")
    return "Si è verificato un errore durante l'elaborazione della richiesta.", 500

# Creazione del DataFrame
with app.app_context():
    try:
        data = Book.query.all()
        if not data:  # Check if there are no books in the database
            df = pd.DataFrame()  # Create an empty DataFrame
        else:
            # Convert SQLAlchemy objects to dicts
            data_dict = [book.__dict__ for book in data]
            # Remove SQLAlchemy internal attributes like _sa_instance_state
            for item in data_dict:
                item.pop('_sa_instance_state', None)
            df = pd.DataFrame(data_dict)
    except Exception as e:
        handle_error(e)


if df.empty:
    empty_data_message = "No books found. Please scrape some data first."
else:
    empty_data_message = None

#First Dash graph about the composition of the books

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/pie-chart/')

# Add a condition to the callback function to handle empty data
@dash_app.callback(
    Output('line-chart', 'figure'),
)
def update_pie_chart(selected_category):
    if df.empty:
        return {}  # Return an empty chart if there's no data

    try:
        categories = [book.category for book in data]
        category_counts = {category: categories.count(category) for category in set(categories)}
        pie_fig = px.pie(category_counts, names='category', values='counts', title='Most prevalent book')
    except Exception as e:
        return handle_error(e)
    
    return  dcc.Graph(figure=pie_fig)