import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from ETLBooks_flask import app,db
from ETLBooks_flask.models import Book
import base64
from io import BytesIO

composition_thumbnail = None
avg_price_per_category_thumbnail = None
price_review_thumbnail = None

with app.app_context():
    def graph_thumbnail(graph):
        img_bytes = graph.to_image(format="png") 
        thumbnail = base64.b64encode(img_bytes).decode("utf-8")
        return thumbnail
    
    def create_error_layout(message):
            return html.Div([
                html.H1("Error", style={'color': 'red'}),
                html.P(message)
            ])    

    dash_composition = dash.Dash(__name__, server=app, url_base_pathname='/dash/pie_chart/')

    #Cleaning Data!
    try:
        books_composition = Book.query.distinct(Book.name).all() 
        books_composition_data = [book.__dict__ for book in books_composition]
    except Exception as e:
        print(f"Database error: {str(e)}")    
    #Cleaning Data!

    if books_composition_data:
        df_composition = pd.DataFrame(books_composition_data)
    else:
        df_composition = pd.DataFrame()

    if df_composition.empty:
        dash_composition.layout = create_error_layout("No data available for category composition")
    else:
        try:
            if 'category' not in df_composition.columns:
                raise KeyError("Category column missing in dataset")
                
            category_counts = df_composition['category'].value_counts().reset_index()
            category_counts.columns = ["Category", "Book Count"]

            threshold = 13
            small_categories = category_counts[category_counts['Book Count'] < threshold]
            
            if not small_categories.empty:
                others_count = small_categories['Book Count'].sum()
                category_counts = category_counts[category_counts['Book Count'] >= threshold]
                category_counts = pd.concat([  # Changed from deprecated _append()
                    category_counts,
                    pd.DataFrame({'Category': ['Others'], 'Book Count': [others_count]})
                ])

            fig_composition = px.pie(
                category_counts,
                names="Category",
                values="Book Count",
                title="Category Composition",
            ).update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='white', width=1))
            )
            
            dash_composition.layout = html.Div(
                children=[
                    dcc.Graph(
                        figure=fig_composition,
                        style={'margin-left': '10px'}
                    )
                ],
                style={'width': '100%', 'display': 'flex', 'justify-content': 'left'}
            )
            composition_thumbnail = graph_thumbnail(fig_composition)
        except KeyError as ke:
            dash_composition.layout = create_error_layout(f"Data validation error: {str(ke)}")
        except Exception as e:
            dash_composition.layout = create_error_layout(f"Error generating composition chart: {str(e)}")

    """
    The second graph will be a simple bar chart that shows the avarage price of each category
    This one would be simplier than the first one because we don't need to remove duplicates
    and we don't need to count the number of books per category just the avarage price
    """

    dash_avg_price = dash.Dash(__name__, server=app, url_base_pathname='/dash/avg_price_chart/')

    #Cleaning Data!
    try:
        books_avg_price = Book.query.all() 
        books_avg_price_data = [book.__dict__ for book in books_avg_price]
    except Exception as e:
        print(f"Database error: {str(e)}")
    #Cleaning Data!
    
    try:
        if books_avg_price_data:
            df_avg_price = pd.DataFrame(books_avg_price_data)
        else:
            df_avg_price = pd.DataFrame()
    except Exception as e:
        print(f"Database error: {str(e)}")        

    if df_avg_price.empty:
        dash_avg_price.layout = create_error_layout("No data available for price analysis")
    else:
        try:
            df_avg_price['price'] = pd.to_numeric(df_avg_price['price'], errors='coerce')
            valid_prices = df_avg_price.dropna(subset=['price'])
            
            if valid_prices.empty:
                raise ValueError("No valid price data available")
                
            avg_price_per_category = valid_prices.groupby('category', observed=True)['price'].mean().reset_index()
            avg_price_per_category.columns = ["Category", "Average Price"]

            fig_average_price = px.bar( 
                avg_price_per_category,
                x="Category",
                y="Average Price",
                title="Average Price per Category"
            )
            
            dash_avg_price.layout = html.Div([
                html.H1("Average Price by Category"),
                dcc.Graph(figure=fig_average_price)
            ])
            avg_price_per_category_thumbnail = graph_thumbnail(fig_average_price)
        except Exception as e:
            dash_avg_price.layout = create_error_layout(f"Error generating price chart: {str(e)}")

    """
    Our third graph will be a scatter plot that compares the price of each book with the review
    to determine if there is a correlation between the two such as "do more expensive books have better reviews?"
    or the impact the prices has in the review
    """

    dash_price_review = dash.Dash(__name__, server=app, url_base_pathname='/dash/price_review_chart/')

    try:
        books_price_review = Book.query.all()
        df_price_review = pd.DataFrame([book.__dict__ for book in books_price_review]) if books_price_review else pd.DataFrame()
    except Exception as e:
        df_price_review = pd.DataFrame()
        print(f"Database error: {str(e)}")

    if df_price_review.empty:
        dash_price_review.layout = create_error_layout("No data available for price-review analysis") 
    else:
        try:
            review_mapping = {
                "One": 1, "Two": 2, "Three": 3, 
                "Four": 4, "Five": 5
            }
            df_price_review['review'] = df_price_review['review'].replace(review_mapping)
            
            df_price_review['date_extracted'] = pd.to_datetime(df_price_review['date_extracted'], errors='coerce')
            
            dash_price_review.layout = html.Div([
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=df_price_review['date_extracted'].min(),
                    max_date_allowed=df_price_review['date_extracted'].max(),
                    start_date=df_price_review['date_extracted'].min(),
                    end_date=df_price_review['date_extracted'].max(),
                    display_format='YYYY-MM-DD',
                ),
                html.Br(),
                dcc.Graph(id='price-review-scatter'),
            ])

            @dash_price_review.callback(
                Output('price-review-scatter', 'figure'),
                Input('date-picker-range', 'start_date'),
                Input('date-picker-range', 'end_date')
            )
            def update_scatter_plot(start_date, end_date):
                try:
                    df_filtered = df_price_review[
                        (df_price_review['date_extracted'] >= pd.to_datetime(start_date)) & 
                        (df_price_review['date_extracted'] <= pd.to_datetime(end_date))
                    ]
                    
                    if df_filtered.empty:
                        return px.scatter(title="No data available for selected dates")
                        
                    return px.scatter(
                        df_filtered,
                        x='price',
                        y='review',
                        title="Price vs Review Score",
                        labels={'price': 'Price', 'review': 'Review Score'},
                        trendline="lowess"
                    )
                except Exception as e:
                    return px.scatter(title=f"Error: {str(e)}")
                
            # Making a default thumbnail using the lastest extracted date:
            latest_date = df_price_review['date_extracted'].max()
            df_latest = df_price_review[df_price_review['date_extracted'] == latest_date]
            default_price_review_fig = px.scatter(
                        df_latest,
                        x='price',
                        y='review',
                        title="Price vs Review Score",
                        labels={'price': 'Price', 'review': 'Review Score'},
                        trendline="lowess"
                    )
            
            price_review_thumbnail = graph_thumbnail(default_price_review_fig)
            # Making a default thumbnail using the lastest extracted date:
        except Exception as e:
            dash_price_review.layout = create_error_layout(f"Error setting up price-review analysis: {str(e)}")

"""
Our fourth graph would be a line chart of every
"""            
