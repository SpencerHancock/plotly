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


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(style={"margin":"auto", "text-align":"center"},children=[
    #==================================== Bullet Graph ============================================
    html.Div(style={"height":"100vh"}, children=[
    html.Div(style = {"height":"80%"}, className="row", children=[
        html.Div(style={"height":"90%"}, className="col-sm-1"),
        dcc.Graph(style={"height":"90%","padding":"0px","margin":0},
                    id="graph-with-slider4", className="col-10"),
        html.Div(style={"height":"90%"}, className="col-sm-1")
    ]),
    html.Div(style = {"font-size":"15px"},className="row", children=[
        html.B("Select Date: ", className="col-2"),
        dcc.Slider(
        id="day-slider2",
        min=min(df.index),
        max=len(df.Datetime),
        value=2,
        className="col-8"
            ),
        html.B(id="html-date2", className="col-2")

    ]),

    html.P("""The Bullet graph listed above represents real time changes in pressure drop, 
            salt passage and product flow rate. On the Flow Rate Graph the grey indicates 
            the current flow rate at reference pressure, the blue is current product flow rate, 
            and the red line is what the flow rate could be given a new membrane. For Salt Passage which is 
            affected differently by conditions and fouling, the blue once again represents real-time Salt Passage, 
            the grey is Salt Passage as reference temp but otherwise current conditions and the red line is salt 
            passage with a new membrane at the current conditions. For Differential Pressure or Pressure Drop, the blue is real-
            time and again the red line is pressure drop with a new membrane at the current conditions.""", style = {"font-size":"15px", "margin":"auto"}, className="col-10"),]),
    #======================================= Bar Graph =============================================

    html.Div(className="row", style={"height":"100vh"}, children=[

        html.Div(style={"height":"90%"}, className="col-sm-1"),

        html.Div([
        dcc.Graph(style={"height":"30%"},id="graph-with-slider1"),
        dcc.Graph(style={"height":"30%"},id="graph-with-slider2"),
        dcc.Graph(style={"height":"30%"},id="graph-with-slider3")
        ], className="col-10", style={"height":"100%"}),

        html.Div(style={"height":"90%"}, className="col-sm-1"),
    ]),
    html.Div(style = {"font-size":"15px"},className="row", children=[
        html.B("Select Date: ", className="col-2"),
        dcc.Slider(
        id="day-slider",
        min=min(df.index),
        max=len(df.Datetime),
        value=2,
        className="col-8"
            ),
        html.B(id="html-date", className="col-2")

    ]),
    html.P("""The bar graphs show all of the same information just differently. These Graphs are horizontal bar graphs set to be 'relative', 
    that means that the changes due to reference pressure or a new membrane are the additive portion. 
    Each smaller section indicates how much you would gain or lose given that change. They Do Not sum to an overall ideal value.""", style = {"font-size":"15px", "margin":"auto"}, className="col-10")
    ])

# def MakeBarPlot(X,Y, names):
#     data = []
#     for x, y, name in zip(X,Y, names):
#         data.append({"x":[x], "y":[y], "type":"bar", "orientation":"h","name":name})


#     return {"data":data,
#                 "layout": go.Layout(barmode="relative",title="Flow/Time",
#                 yaxis=dict(
#                 autorange=True,
#                 showgrid=False,
#                 ticks='',
#                 showticklabels=False
# #                 ))}

# def MakeBulletPlot(X,Y,Names):
#     graph = go.Indicator(
#     mode = "number+gauge+delta", value = 180,
#     delta = {'reference': 200},
#     domain = {'x': [0, 1], 'y': [0, 1]},
#     title = {'text': "Revenue"},
#     gauge = {
#         'shape': "bullet",
#         'axis': {'range': [None, 300]},
#         'threshold': {
#             'line': {'color': "black", 'width': 2},
#             'thickness': 0.75,
#             'value': [170, 160]},
#         'steps': [
#             {'range': [0, 150], 'color': "gray"},
#             {'range': [150, 250], 'color': "lightgray"}],
#         'bar': {'color': "black"}})
#     return graph

    # return {"data":[{"x":[1], "y":["DP"], "type":"bar", "orientation":"h","name":"DP"},
    #             {"x":[2-1], "y":["DP"], "type":"bar", "orientation":"h","name":"New Membrane"}],
    #             "layout": go.Layout(barmode="relative",title="Flow/Time",
    #             yaxis=dict(
    #             autorange=True,
    #             showgrid=False,
    #             ticks='',
    #             showticklabels=False
    #             ))}


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
@app.callback(
    [Output('graph-with-slider4', 'figure'),
    Output('html-date2', 'children')],
    [Input('day-slider2', 'value')])
def update_bulletplot(selected_day):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
    mode = "number+gauge+delta", value = df.at[selected_day, "Q_p"],
    delta = {'reference': df.at[selected_day, "QNM"]},
    domain = {'x': [0, 1], 'y': [.05, .25]},
    title = {'text': "Flow"},
    gauge = {
        'shape': "bullet",
        'axis': {'range': [None, max(df.QNM)]},
        'threshold': {
            'line': {'color': "green", 'width': 2},
            'thickness': 0.75,
            'value': df.at[selected_day, "QNM"]},
        'steps': [
            {'range': [0, df.at[selected_day, "Qpress"]], 'color': "gray"},
            {'range': [df.at[selected_day, "Qpress"], max(df.QNM)], 'color': "white"}],
        'bar': {'color': "blue"}}))
    fig.add_trace(go.Indicator(
                mode = "number+gauge+delta", value = df.at[selected_day, "SP"],
                delta = {'reference': df.at[selected_day, "SPNM"]},
                domain = {'x': [0, 1], 'y': [0.4, .6]},
                title = {'text': "SP"},
                gauge = {
                    'shape': "bullet",
                    'axis': {'range': [None, 2]},
                    'threshold': {
                        'line': {'color': "red", 'width': 2},
                        'thickness': 0.75,
                        'value': df.at[selected_day, "SPNM"]},
                    'steps': [
                        {'range': [0, df.at[selected_day, "SPtemp"]], 'color': "gray"},
                        {'range': [df.at[selected_day, "SPtemp"], max(df.SPNM)], 'color': "white"}],
                    'bar': {'color': "blue"}}))
    fig.add_trace(go.Indicator(
    mode = "number+gauge+delta", value = df.at[selected_day, "dp"],
    delta = {'reference': df.at[selected_day, "DPNM"]},
    domain = {'x': [0, 1], 'y': [.7,.9 ]},
    title = {'text': "DP"},
    gauge = {
        'shape': "bullet",
        'axis': {'range': [None, max(df.dp)]},
        'threshold': {
            'line': {'color': "red", 'width': 2},
            'thickness': 0.75,
            'value': df.at[selected_day, "DPNM"]},
        'bar': {'color': "blue"}}))
    
    fig.update_layout(
        title={
        'text': "Normalized Performance Breakdown",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        xaxis_title="Time",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"))
    return fig, df.at[selected_day, "Datetime"]



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

if __name__ == '__main__':
    app.run_server(debug=True)