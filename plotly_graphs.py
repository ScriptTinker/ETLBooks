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
    
    def error_no_data():
        return html.Div([
            html.H1("Error"),
            html.P("No data available to display the graph.")
        ])

    dash_composition = dash.Dash(__name__, server=app, url_base_pathname="/dash/pie_chart/")

    #Cleaning Data!
    books_composition = Book.query.distinct(Book.name).all() 
    books_composition_data = [book.__dict__ for book in books_composition]
    #Cleaning Data!
    """
    The standard SQLAlchemy query made a single instance of data meaning that it
    was somewhat hard to filter in pandas....

    """ 
    if books_composition_data:
        df_composition = pd.DataFrame(books_composition_data)
    else:
        df_composition = pd.DataFrame()

    if df_composition.empty:
        dash_composition.layout = error_no_data()
    else:
        category_counts = df_composition["category"].value_counts().reset_index()
        category_counts.columns=["Category","Book Count"]

        #Define "Other Category!"
        threshold = 13#<< is the perfect number for a good looking graph
        small_categories = category_counts[category_counts["Book Count"] < threshold]
        others_count = small_categories["Book Count"].sum()
        category_counts = category_counts[category_counts["Book Count"] >= threshold]
        category_counts = category_counts._append(pd.DataFrame({"Category": ["Others"],
                                                                "Book Count": [others_count]}))
        #Define "Other Category!"

        """
        Because of the high number of categories the graph is a bit of a mess
        So we clean it up with an "other" category
        The last line means: Cat.counts is = to Cat.count plus an appended 
                            new column called Other! 
        """

        fig_composition = px.pie(
        category_counts,
        names="Category",
        values="Book Count",
        title="Category composition",
        )


        fig_composition.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="white", width=1))
        )
        
        dash_composition.layout = html.Div(
            children=[
                dcc.Graph(
                    figure=fig_composition,
                    style={"margin-left": "10px"}
                )
            ],
            style={"width": "100%", "display": "flex", "justify-content": "left"}
        )

        #Thumbnail
        composition_thumbnail = graph_thumbnail(fig_composition)
        #Thumbnail

    """
    The second graph will be a simple bar chart that shows the avarage price of each category
    This one would be simplier than the first one because we don't need to remove duplicates
    and we don't need to count the number of books per category just the avarage price
    """

    dash_avg_price = dash.Dash(__name__, server=app, url_base_pathname="/dash/avg_price_chart/")

    #Cleaning Data!
    books_avg_price = Book.query.all() 
    books_avg_price_data = [book.__dict__ for book in books_avg_price]
    #Cleaning Data!
 
    if books_avg_price_data:
        df_avg_price = pd.DataFrame(books_avg_price_data)
    else:
        df_avg_price = pd.DataFrame()

    if df_avg_price.empty:
        dash_avg_price.layout= error_no_data()

    else:
        df_avg_price["price"] = pd.to_numeric(df_avg_price["price"], errors="coerce")  # Convert to numeric, invalid values become Null
        df_avg_price = df_avg_price.dropna(subset=["price"])
        avg_price_per_category = df_avg_price.groupby("category")["price"].mean().reset_index()
        avg_price_per_category.columns = ["Category", "Average Price"]

        fig_avarage_price = px.bar(title="Average Price per Category",data_frame=avg_price_per_category,x="Category",y="Average Price")

        dash_avg_price.layout = html.Div([
            html.H1("Average Price by Category"),
            dcc.Graph(figure=fig_avarage_price)
        ])

        #Thumbnail
        avg_price_per_category_thumbnail = graph_thumbnail(fig_avarage_price)
        #Thumbnail
    """
    Our third graph will be a scatter plot that compares the price of each book with the review
    to determine if there is a correlation between the two such as "do more expensive books have better reviews?"
    or the impact the prices has in the review
    """

    dash_price_review = dash.Dash(__name__, server=app, url_base_pathname="/dash/price_review_chart/")

    #Cleaning Data!
    books_price_review = Book.query.all()
    books_price_review_data = [book.__dict__ for book in books_price_review]
    #Cleaning Data!

    if books_price_review_data:
        df_price_review = pd.DataFrame(books_price_review_data)
    else:
        df_price_review = pd.DataFrame()

    if df_price_review.empty:
        dash_price_review.layout = error_no_data

    else:

        review_mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
        }

        df_price_review["review"] = df_price_review["review"].replace(review_mapping)    
            
        @dash_price_review.callback(
            Output("price-review-scatter", "figure"),
            Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date")
        )

        def update_scatter_plot(start_date, end_date):
            if start_date and end_date:
                df_filtered = df_price_review[(df_price_review["date_extracted"] >= start_date) & (df_price_review["date_extracted"] <= end_date)]
            else:
                df_filtered = df_price_review

            if not df_filtered.empty:
                fig = px.scatter(df_filtered, x="price", y="review", title="Price vs Review Score",
                                labels={"price": "Price", "review": "Review Score"})
            else:
                fig = px.scatter(data_frame=pd.DataFrame(), title="No data available for the selected date range")

            return fig
            
        dash_price_review.layout = html.Div([
            dcc.DatePickerRange(
                id="date-picker-range",
                start_date=df_price_review["date_extracted"].min().strftime("%Y-%m-%d") if not df_price_review.empty else "2020-01-01",
                end_date=df_price_review["date_extracted"].max().strftime("%Y-%m-%d") if not df_price_review.empty else "2024-12-31",
                display_format="YYYY-MM-DD",
            ),
            html.Br(),
            dcc.Graph(id="price-review-scatter"),
        ])

    #Creating default state of the graph for a thumbnail!

    default_fig_price_review= px.scatter(df_price_review,x="price",y="review", title="Price vs Review Score",
                                         labels={"price": "Price", "review": "Review Score"})
    price_review_thumbnail = graph_thumbnail(default_fig_price_review)
    
    