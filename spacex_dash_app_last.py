# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                 dcc.Dropdown(id='site-dropdown',
                                        options=[
                                        {'label': 'ALL Sites', 'value': 'ALL'},    
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                                        value ='ALL',
                                        placeholder='Select a Launch Site here',
                                        searchable = True),
                                        #html.Br(),
                                ]),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                #html.Div([ ], id='success-pie-chart'),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(dcc.RangeSlider(
                                    id='payload-slider',
                                    min = 0,
                                    max = 10000,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={
                                        0: {'label': '0kg', 'style': {'color': '#77b0b1'}},
                                        500: {'label': '500 kg'},
                                        2000:'2000 kg',
                                        3500:'3500 kg',
                                        6500:'6500 kg',
                                        5000:'5000 kg',
                                        8000:'8000 kg',
                                        9550:'9550 kg'
                                    },
                                    updatemode='drag'
                                ), style={'width': '90%', 'padding': '0px 20px 20px 20px'}),    

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'),
               State("success-pie-chart", 'figure')) 
# Add computation to callback function and return graph
def generate_graph(value,chart):
    if value == 'ALL':
        # Group the data by Launch Site and compute success count over class column.
        launch_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()

        fig = px.pie(launch_data, values="class", names="Launch Site", title='Total Successful launches Count')
        return fig
    else:
        #Prepare data to create figure, copy data into distinct varible and don´t touch original data
        df1 = spacex_df
        #Take the two columns we need to generate the Success vs. Failed counts
        df2=df1[['Launch Site','class']]
        #Select records related to the input Launch site selected in Dropdown and reset index
        new_df= df2[df2['Launch Site']== value]   
        new_df.reset_index(drop=True, inplace=True)
        tot= new_df['class'].value_counts()
        df3 = pd.DataFrame(tot)
        df3 = df3.reset_index()
        df3.replace(0,'Fail',inplace = True)
        df3.replace(1,'Success',inplace = True)   
        df3.columns = ['count', 'Launch Site'] 
        fig = px.pie(df3, values="Launch Site", names="count", title='Total Successful launches Count for ' + value + ' Site.')

        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               [Input(component_id = 'site-dropdown', component_property='value'),
               Input(component_id = 'payload-slider', component_property='value')],
               State("success-payload-scatter-chart", 'figure')) 
# Add computation to callback function and return graph
def generate_graph1(value1,slider,chart1):
    if value1 == 'ALL':
        # Creaate scatter plot for all sites in the input range.
        #Payload is a range
        dfa = spacex_df
        dfa[["Payload Mass (kg)"]] = dfa[["Payload Mass (kg)"]].astype("float")
        dfa['class'].replace(0,'Fail',inplace = True)
        dfa['class'].replace(1,'Success',inplace = True)

        #Filter of rows where Payload mass Value is between slider range
        dfar=dfa[(dfa['Payload Mass (kg)'] >= slider[0])&(dfa['Payload Mass (kg)'] <= slider[1])]
        scatFig = px.scatter(data_frame=dfar, x="Payload Mass (kg)", y="class", color="Booster Version Category", height=550,
                title='Correlation between Payload and Sucess for ALL Site(s)') 
        
        return scatFig
    else:
        #Prepare data to create figure, copy data into distinct varible and don´t touch original data
        df_1 = spacex_df

        #Convert Payload mass values from object type to float
        df_1[["Payload Mass (kg)"]] = df_1[["Payload Mass (kg)"]].astype("float")
        
        #Take the four columns we need to generate the Success vs. Failed counts
        dfb=df_1[['Launch Site','class','Payload Mass (kg)','Booster Version Category']]
        #Select records related to the input Launch site selected in Dropdown and reset index
        dfc= dfb[dfb['Launch Site']== value1]   
        dfc.reset_index(drop=True, inplace=True)

        #Filter of rows where Payload mass Value is between slider range
        dfd=dfc[(dfc['Payload Mass (kg)'] >= slider[0])&(dfc['Payload Mass (kg)'] <= slider[1])]

        scatFig = px.scatter(data_frame=dfd, x="Payload Mass (kg)", y="class", color="Booster Version Category", height=550, 
                title='Correlation between Payload and Sucess for ' + value1 + 'Site(s)')  
        
        return scatFig


# Run the app
if __name__ == '__main__':
    app.run_server()
