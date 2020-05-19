import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as ex
import plotly.graph_objects as go

import pandas as pd

from RV import ReverseNormalize

smallest_index = 0
# get clean plant data
df = pd.read_excel("ultratech_data_clean.xlsx")
df = df.iloc[0:,0:19]
df = df.drop(["A", "B", "a", "group","resnorm"], 1)
df = df.dropna()
df = df[((df.Q_f>100))]
df = df[((df.Q_p < 100))]
df = df[((df.Q_p > 50))]
df = df[((df.index < 4000))]
df["C_f"] = df["C_f"]*0.64
df["C_p"] = df["C_p"]*0.64
df["Cond. At ERT to RWST [AIT - 005] [µS/cm]"] = df["Cond. At ERT to RWST [AIT - 005] [µS/cm]"]*.64
df["SP"] = df["C_p"]/df["C_f"]*100
df = df.reset_index()
#Q_p, Q_f, Temp, Conc_f, Conc_p, P_f, P_p, dp
#datetime,feed_flow,product_flow,reject_flow,temperature,feed_cond,reject_cond,product_cond,feed_ph,orp,reject_ph,product_ph,pressure_drop,feed_pressure,hpp_pressure,cf_pressure
RV = ReverseNormalize()
RV.set_reference(df.at[smallest_index,"Q_p"],df.at[smallest_index,"Q_f"],df.at[smallest_index,"T_f"],df.at[smallest_index,"C_f"],df.at[smallest_index,"C_p"],
                    df.at[smallest_index,"P_f"],1,df.at[smallest_index,"dp"])
df["Qpress"],df["QNM"],df["Qt"] = RV.Flow(df["Q_p"],df["Q_f"], df["T_f"],df["C_f"],df["C_p"],df["P_f"],1,df["dp"])
df["SP"], df["SPtemp"], df["SPNM"] = RV.SP(df["C_f"], df["C_p"], df["Q_f"], df["Q_p"], df["T_f"])
df["DPNM"] = RV.DP(df.Q_p, df.Q_f, df.T_f)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(style={"width":"70vw", "height":"93vh","padding":0,"margin":"auto", "float":"center"},children=[
    dcc.Graph(style={"width":"70vw", "height":"33%","padding":"0px","margin":0},
                id="graph-with-slider1"),
    dcc.Graph(style={"width":"70vw", "height":"33%","padding":0,"margin":0},id="graph-with-slider2"),
    dcc.Graph(style={"width":"70vw", "height":"33%","padding":0,"margin":0},id="graph-with-slider3"),
    dcc.Slider(
        id="day-slider",
        min=min(df.index),
        max=len(df.Datetime),
            ),
    html.P(id="html-date")
        ])

try:
    @app.callback(
    [Output('graph-with-slider1', 'figure'),
    Output('graph-with-slider2', 'figure'),
    Output('graph-with-slider3', 'figure'),
     Output('html-date', 'children')],
    [Input('day-slider', 'value')])
    def update_barplot(selected_day):
        selected_day = int(selected_day)
        # filtered_df = df[df.datetime = selected_day]
        return  [{"data":[{"x":[df.at[selected_day,"Q_p"]], "y":["Flow"], "type":"bar", "orientation":"h","name":"Flow"},
                {"x":[df.at[selected_day,"QNM"]-df.at[selected_day,"Q_p"]], "y":["Flow"], "type":"bar", "orientation":"h","name":"New Membrane"},
                {"x":[df.at[selected_day,"Qpress"]-df.at[selected_day,"Q_p"]], "y":["Flow"], "type":"bar", "orientation":"h","name":"Reference Pressure"}],
                "layout": go.Layout(barmode="relative",title="Flow/Time",
                yaxis=dict(
                autorange=True,
                showgrid=False,
                ticks='',
                showticklabels=False
                ))},
                {"data":[{"x":[df.at[selected_day,"SP"]], "y":["SP"], "type":"bar", "orientation":"h","name":"SP"},
                {"x":[df.at[selected_day,"SPNM"]-df.at[selected_day,"SP"]], "y":["SP"], "type":"bar", "orientation":"h","name":"New Membrane"},
                {"x":[df.at[selected_day,"SPtemp"]-df.at[selected_day,"SP"]], "y":["SP"], "type":"bar", "orientation":"h","name":"Reference Temp"}],
                "layout": go.Layout(barmode="relative",title="Salt Passage/Time",
                yaxis=dict(
                autorange=True,
                showgrid=False,
                ticks='',
                showticklabels=False
                ))},
                {"data":[{"x":[df.at[selected_day,"dp"]], "y":["DP"], "type":"bar", "orientation":"h","name":"DP"},
                {"x":[df.at[selected_day,"DPNM"]-df.at[selected_day,"dp"]], "y":["DP"], "type":"bar", "orientation":"h","name":"New Membrane"}],
                "layout": go.Layout(barmode="relative", title="Pressure Drop/Time",
                yaxis=dict(
                autorange=True,
                showgrid=False,
                ticks='',
                showticklabels=False
                ))},
                df.at[selected_day, "Datetime"]]



# fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", title="A Plotly Express Figure")

# # If you print fig, you'll see that it's just a regular figure with data and layout
# # print(fig)

# fig.show()



# @app.callback(
#     Output('graph-with-slider', 'figure'),
#     [Input('year-slider', 'value')])
# def update_figure(selected_year):
#     filtered_df = df[df.year == selected_year]
#     traces = []
#     for i in filtered_df.continent.unique():
#         df_by_continent = filtered_df[filtered_df['continent'] == i]
#         traces.append(dict(
#             x=df_by_continent['gdpPercap'],
#             y=df_by_continent['lifeExp'],
#             text=df_by_continent['country'],
#             mode='markers',
#             opacity=0.7,
#             marker={
#                 'size': 15,
#                 'line': {'width': 0.5, 'color': 'white'}
#             },
#             name=i
#         ))

#     return {
#         'data': traces,
#         'layout': dict(
#             xaxis={'type': 'log', 'title': 'GDP Per Capita',
#                    'range':[2.3, 4.8]},
#             yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
#             margin={['l': 40, 'b': 40, 't': 10, 'r': 10},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest',
#             transition = {'duration': 500},
#         )
#     }

except:
    pass

if __name__ == '__main__':
    app.run_server(debug=False)