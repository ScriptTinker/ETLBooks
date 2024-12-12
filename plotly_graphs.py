import plotly.graph_objects as go
from ETLBooks_flask import app, db
from ETLBooks_flask.models import Book
import pandas as pd

with app.app_context():
    categories = db.session.query(Book.category).all()
    category_counts = pd.Series([cat[0] for cat in categories]).value_counts()

# Combine the last 5% into 'Other'
threshold = int(len(category_counts) * 0.45)
if threshold > 0:
    other_count = category_counts.iloc[-threshold:].sum()
    category_counts = category_counts[:-threshold]
    category_counts['Other'] = other_count

# Create pie chart using graph objects
fig = go.Figure(data=[go.Pie(labels=category_counts.index, values=category_counts.values, 
                               pull=[0.1] * (len(category_counts) - 1) + [0.2])])
fig.update_layout(title_text='Book Categories Distribution', showlegend=True)
fig.show()