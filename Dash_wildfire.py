import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
from dash.exceptions import PreventUpdate

# --- Data Loading and Column Fixing ---
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"
df = pd.read_csv(URL)

# Force the column name to match the code's expectation
df.columns = [col.lower().replace(' ', '_') for col in df.columns] 
# Now all columns are lowercase (e.g., 'unemployment_rate', 'vehicle_type')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(id='dropdown-statistics',
                     options=[{'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                              {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}],
                     value='Yearly Statistics'),
        dcc.Dropdown(id='select-year', 
                     options=[{'label': i, 'value': i} for i in range(1980, 2024)],
                     value=2010)
    ]),
    html.Div(id='output-container', style={'display': 'flex', 'flex-wrap': 'wrap'})
])

@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'), Input('select-year', 'value')]
)
def update_output_container(selected_statistics, input_year):
    if not selected_statistics: raise PreventUpdate

    try:
        if selected_statistics == 'Recession Period Statistics':
            recession_data = df[df['recession'] == 1]
            
            # Use lowercase names to match our cleaning step above
            sales_by_type = recession_data.groupby('vehicle_type')['automobile_sales'].mean().reset_index()
            R_chart1 = dcc.Graph(figure=px.line(sales_by_type, x='vehicle_type', y='automobile_sales', title="Avg Sales"))
            R_chart2 = dcc.Graph(figure=px.bar(sales_by_type, x='vehicle_type', y='automobile_sales', title="Total Sold"))

            exp_rec = recession_data.groupby('vehicle_type')['advertising_expenditure'].sum().reset_index()
            R_chart3 = dcc.Graph(figure=px.pie(exp_rec, values='advertising_expenditure', names='vehicle_type'))

            # FIXED: Using 'unemployment_rate' (lowercase)
            unemp_data = recession_data.groupby(['vehicle_type', 'unemployment_rate'])['automobile_sales'].mean().reset_index()
            R_chart4 = dcc.Graph(figure=px.bar(unemp_data, x='unemployment_rate', y='automobile_sales', color='vehicle_type'))

            return [html.Div([R_chart1, R_chart2], style={'display':'flex'}),
                    html.Div([R_chart3, R_chart4], style={'display':'flex'})]

        elif (input_year and selected_statistics == 'Yearly Statistics'):
            yearly_data = df[df['year'] == input_year]
            yas = df.groupby('year')['automobile_sales'].mean().reset_index()
            Y_chart1 = dcc.Graph(figure=px.line(yas, x='year', y='automobile_sales'))
            
            # Monthly sales
            ms = yearly_data.groupby('month')['automobile_sales'].sum().reset_index()
            Y_chart2 = dcc.Graph(figure=px.line(ms, x='month', y='automobile_sales'))
            
            return [html.Div([Y_chart1, Y_chart2], style={'display':'flex'})]

    except Exception as e:
        return html.Div([f"Error: {e}"], style={'color': 'red'})

if __name__ == '__main__':
    app.run(debug=True, port=8060)