import pandas as pd

from RV import ReverseNormalize
from posm import osmotic_pressure_TX
import plotly.express as ex
import plotly.graph_objects as go

df = pd.read_excel("ultratech_data_clean.xlsx")
df = df.iloc[0:,0:19]
df = df.drop(["A", "B", "a", "group","resnorm"], 1)
df = df.dropna()
df = df[((df.Q_f>100))]
df = df[((df.Q_p < 100))]
df = df[((df.Q_p > 50))]
df = df[((df.index < 4000 ))]
df["C_f"] = df["C_f"]*0.64
df["C_p"] = df["C_p"]*0.64
df["Cond. At ERT to RWST [AIT - 005] [µS/cm]"] = df["Cond. At ERT to RWST [AIT - 005] [µS/cm]"]*.64
df["SP"] = df["C_p"]/df["C_f"]*100
rv = ReverseNormalize()

df1 = pd.DataFrame()
df1["product_flow"],df1["feed_flow"],df1["temperature"],df1["feed_cond"],df1["product_cond"],df1["feed_pressure"],df1["pressure_drop"] = df["Q_p"],df["Q_f"],df["T_f"],df["C_f"],df["C_p"],df["P_f"],df["dp"]

rv = ReverseNormalize()

firstRow = df1.iloc[515]

#Q_p, Q_f, Temp, Conc_f, Conc_p, P_f, P_p, dp
#datetime,feed_flow,product_flow,reject_flow,temperature,feed_cond,reject_cond,product_cond,feed_ph,orp,reject_ph,product_ph,pressure_drop,feed_pressure,hpp_pressure,cf_pressure

rv.set_reference(firstRow["product_flow"],firstRow["feed_flow"],firstRow["temperature"],
                            firstRow["feed_cond"],firstRow["product_cond"],firstRow["feed_pressure"],1,
                            firstRow["pressure_drop"])
                    
df1["DP_change"] = rv.DP(df1.product_flow, df1.feed_flow, df1.temperature)
df1["SP"], df1["SPTemp"], df1["SPNM"] = rv.SP(df1.feed_cond, df1.product_cond, df1.feed_flow, df1.product_flow, df1.temperature)
#self,Qp, Qf, Temp, Cf, Cp, Pf, Pp, dp
df1["Qrefpress"], df1["QNM"], df1["Qtemp"] = rv.Flow(df1.product_flow, df1.feed_flow, df1.temperature, df1.feed_cond, df1.product_cond, df1.feed_pressure, 1,  df1.pressure_drop)

fig = go.Figure()
fig.add_trace(go.Bar(
    y = ["Flow"],
    x = [1,2,3],
    name = "QrefPress",
    orientation="h"
))
fig.add_trace(go.Bar(
    y = ["SP"],
    x = [1,2,15],
    name = "QNM",
    orientation="h"
))

fig.update_layout(barmode='relative')
fig.show()

# fig = go.Figure()
# fig.add_trace(go.Bar(
#     y=['giraffes', 'orangutans', 'monkeys'],
#     x=[20, 14, 23],
#     name='SF Zoo',
#     orientation='h',
#     marker=dict(
#         color='rgba(246, 78, 139, 0.6)',
#         line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
#     )
# ))
# fig.add_trace(go.Bar(
#     y=['giraffes', 'orangutans', 'monkeys'],
#     x=[12, 18, 29],
#     name='LA Zoo',
#     orientation='h',
#     marker=dict(
#         color='rgba(58, 71, 80, 0.6)',
#         line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
#     )
# ))

# fig.update_layout(barmode='stack')
# fig.show()

