import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from ETLBooks_flask import app,db
from ETLBooks_flask.models import Book

with app.app_context():

    #Cleaning Data!
    books = Book.query.distinct(Book.name).all()
    books_data = [book.__dict__ for book in books]
    for book in books_data:
        book.pop('_sa_instance_state')#Removes internal attributes that affects data accuracy 
    #Cleaning Data!
    """
    The standard SQLAlchemy query made a single instance of data meaning that it
    was somewhat hard to filter in pandas....

    """

    if books_data is None:
        df_composition = {}
    else:
        df_composition = pd.DataFrame(books_data)
        print (df_composition)

    """
    The first Graph rappresents the composition of each category 
    to see which one is more popular with authors(<< example) so
    we count the number of books per category, devide them by the 
    total all easy thanks to plotly/dash
    """

    dash_composition = dash.Dash(__name__, server=app, url_base_pathname='/dash/pie_chart/')

    category_counts = df_composition.value_counts().reset_index()
    category_counts.columns=["Category","Book Count"]

    #Define "Other Category!"
    threshold = 13#<< is the perfect number for a good looking graph
    small_categories = category_counts[category_counts['Book Count'] < threshold]
    others_count = small_categories['Book Count'].sum()
    category_counts = category_counts[category_counts['Book Count'] >= threshold]
    category_counts = category_counts._append(pd.DataFrame({'Category': ['Others'],
                                                             'Book Count': [others_count]}))
    #Define "Other Category!"

    """
    Because of the high number of categories the graph is a bit of a mess
    So we clean it up with an "other" category
    The last line means: Cat.counts is = to Cat.count plus an appended 
                         new column called Other! 
    """

    fig_composition = px.pie(category_counts,names="Category",values="Book Count", title="Category composition")

    dash_composition.layout= html.Div(
        children=[ 
        dcc.Graph(figure=fig_composition)
    ], 
        style={'margin-left': '20px'}
    )