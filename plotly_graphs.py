import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from ETLBooks_flask import app,db
from ETLBooks_flask.models import Book
import base64
from io import BytesIO

with app.app_context():
    def graph_thumbnail(graph):
        bytes = graph.to_image(format = "png")
        thumbnail = base64.b64encode(bytes).decode("utf-8")
        return thumbnail
    
    def graph_noData(dash_app):
        pass

    dash_composition = dash.Dash(name="Dash Composition", server=app, url_base_pathname='/dash/pie_chart/')

    """
    The first Graph rappresents the composition of each category 
    to see which one is more popular with authors(<< example) so
    we count the number of books per category, devide them by the 
    total all easy thanks to plotly/dash
    """
    
    #Cleaning Data!
    book_composition = Book.query.distinct(Book.name).all()
    book_composition_data = [book.__dict__ for book in book_composition]
    #Cleaning Data!

    """
    The standard SQLAlchemy query made a single instance of data meaning that it
    was somewhat hard to filter in pandas....

    """
    if not book_composition_data:
        dash_composition.layout= html.Div(
        children=[
            html.H2("There seems to be no data available...", style={"color":"red"}),
            html.H2("please scrape some data!", style={"color": "red"})
        ]    
        )

        composition_thumbnail = None
    else:
        df_composition = pd.DataFrame(book_composition_data)

        try:
            category_counts = df_composition["category"].value_counts().reset_index()
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

            composition_thumbnail = graph_thumbnail(fig_composition)

        except Exception as e:
            print(e)

    dash_avg_price = dash.Dash(name="Avarage Price per category", server=app, url_base_pathname="/dash/avg_price/")

    #Cleaning Data!
    book_avg_price = Book.query.all()
    book_avg_price_data = [book.__dict__ for book in book_avg_price]
    #Cleaning Data!

