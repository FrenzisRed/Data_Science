import matplotlib
matplotlib.use("Agg")

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from plotly.tools import mpl_to_plotly

from pathlib import Path
import re
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd

lines = []
data = []
list_ips = []
list_dates = []
first_ten = []

direct = Path(__file__).parent
file = Path(direct, "apache_logs")


f = open(file, 'r')

##### line count for debugging / one line per list item
entries = 0
for line in f:
    if line != "\n":
        lines.append(re.split(' \\- - |\\[ |\\] |\\"*" ', str(line))) # a list of items for each list item - each item of the list contain all items of the line of the log
        tempDate = re.split('\\[|\\:|\s',str(lines[entries][1]))
        date = tempDate[1]
        lines[entries][1] = date
        list_dates.append(date)
        entries += 1



i = 0
while entries > i :
    list_ips.append(lines[i][0])
    #tempDate = re.split('\\[|\\:|\s',str(lines[i][1]))   
    #print(tempDate)
    #list_dates.append(tempDate[1])
    #print(list_ips[i])
    i += 1





##dictionary of IPs counts
ips_data = {x:list_ips.count(x) for x in list_ips}
busy_dates = {x:list_dates.count(x) for x in list_dates}
#Sort IPs by number of connections 
ips_data = sorted(ips_data.items(), key=lambda x: x[1], reverse=True)
busy_dates = sorted(busy_dates.items(), key=lambda x: x[1], reverse=True)

######busiest day
#print("the busiest day is : ", busy_dates[0][0], " with :", busy_dates[0][1], "connections")
######average connections

##############First 10 recurrent IPs
x = 0
while x < 10 :
    first_ten.append(ips_data[x])
    x += 1


########################################DATAFRAMES########################################
#GENERAL DATAFRAME
df = pd.DataFrame.from_records(lines)
df.columns = ["IPs", "Time", "Operation", "Reply", "User-Agent"]

#recurrent IPs
df2 = pd.DataFrame(first_ten)
df2.columns = ["IPs", "Connections"]
#days
df3 = pd.DataFrame(busy_dates)
df3.columns = ["Dates", "Connections"]
#print(df3)

######Graphs

df2.plot(kind='bar', x='IPs', y='Connections')
#fig = mpl_to_plotly(fig)
plt.xticks(rotation=45)
df3.plot(kind='bar', x='Dates', y='Connections')
plt.xticks(rotation=45)
#plt.show()

##############################APP DASH

app = dash.Dash(__name__)



def create_IP_graph():
    fig, ax = plt.subplots()
    fig.set_dpi(75)
    #fig.set_size_inches(int(i), int(i))

    ax.bar(df2["IPs"],df2["Connections"])
    plt.xlabel('IPs')
    plt.ylabel('Connections')
    plt.title('Highest 10 IP\'s connections')
    return mpl_to_plotly(fig)


def create_daily_graph():
    fig, ax = plt.subplots()
    fig.set_dpi(75)
    #fig.set_size_inches(int(i), int(i))
    ax.bar(df3["Dates"],df3["Connections"])
    plt.xlabel('days')
    plt.ylabel('Connections')
    plt.title('Logged connections per day ')
    return mpl_to_plotly(fig)

def create_round_graph():
    pass


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('DASH - APACHE LOGS READER'),
                                 html.P('Visualising apache.'),
                                 html.P('Pick filters from the dropdown below.'),
                                 
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 html.H2('Top IP connections:'),
                                 html.P(ips_data[0][0]),
                                 dcc.Graph(figure=create_IP_graph()),
                                 html.P('Busiest day: '),
                                 html.P(busy_dates[0][0]),
                                 dcc.Graph(figure=create_daily_graph()),
                             ]),
                              ])
        ]

)





if __name__ == "__main__":
    app.run_server(debug = True)



#############################################"Debugging" and old part of code############################################

