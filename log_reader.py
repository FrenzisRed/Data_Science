import matplotlib
from pandas.core.indexes.base import Index
matplotlib.use("Agg")

import io
import base64
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

#user agent type
useragent = df.groupby('User-Agent').count()
useragent = useragent.sort_values(by=['IPs'], ascending=False)
total_requests = useragent.sum(axis=1)
totalc = useragent.sum()
totalc = totalc.iloc[0]
#user agent operation
useragent_operation = df.groupby('Operation').count()
useragent_operation = useragent_operation.sort_values(by=['IPs'], ascending=False)
#print(useragent_operation.index[0], 'index')
#print(useragent_operation.loc[useragent_operation.index[0], 'IPs'])
#top 3 user agents
user_agent = [total_requests.index[0], total_requests.index[1], total_requests.index[2]]
user_agent.append('Other')
user_agent_conn = [total_requests.iloc[0], total_requests.iloc[1], total_requests.iloc[2]]
#print(total_requests.loc[total_requests.index[1], 'User-Agent'])
#print(useragent_operation.index[0])
#recurrent IPs
df2 = pd.DataFrame(first_ten)
df2.columns = ["IPs", "Connections"]
#days
df3 = pd.DataFrame(busy_dates)
df3.columns = ["Dates", "Connections"]


######Graphs

df2.plot(kind='bar', x='IPs', y='Connections')
#fig = mpl_to_plotly(fig)
plt.xticks(rotation=45)
df3.plot(kind='bar', x='Dates', y='Connections')
plt.xticks(rotation=45)
#plt.show()

##############################APP DASH

app = dash.Dash(__name__)


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[ 
                     html.Div(className='four columns div-for-charts bg-grey', 
                        children=[  
                                    html.H1('DASH - APACHE LOGS READER'), 
                                    html.P('Visualising apache logs, Pick filters from the dropdown below.'), 
                                    html.P(''), 
                                    html.P('_____________________________________'), 
                                    html.P('Top connections Menu :'),
                                    dcc.Dropdown(id="drop",
                                        options=[
                                            {'label': 'IPs connections', 'value': '0'},
                                            {'label': 'Busiest Day', 'value': '1'},
                                            ],
                                        value='0',
                                        clearable=False,
                                        multi=False
                                    ),

                                    html.P('User Agent Menu :'),
                                    dcc.Dropdown(id="top_3",
                                        options=[
                                            {'label': 'Top User Agents', 'value': '0'},
                                            {'label': 'type of query', 'value': '1'},
                                            ],
                                        value='0',
                                        clearable=False,
                                        multi=False
                                    ),
                                ]
                            ),
                    
                     html.Div(className='four columns div-for-charts ',
                        children=[
                                    html.H2('Top connections:'), 
                                    html.Div(className='two columns div-user-controls', style={'Display': 'flex'}, 
                                        children=[ 
                                                    html.Img(id='example'),
                                                ]
                                        ),
                                        html.P(id='text_one'),
                                        
                               ]
                            ),


                     html.Div(className='four columns div-for-charts', 
                        children=[  
                                    html.H2('User-Agets Stats'), 
                                    html.Div(className='two columns div-user-controls', 
                                        children=[ 
                                                    html.Img(id='example3'),
                                                ]
                                        ), 
                                    html.P('Top 3 user agents:'),
                                    html.P(user_agent[0]),
                                    html.P(user_agent[1]),
                                    html.P(user_agent[2]), 
                                ]
                            ),               

                         ]
            ),
        ]
)

@app.callback(
    dash.dependencies.Output('text_one', 'children'), # src attribute
    [dash.dependencies.Input('drop', 'value')]
)
def text_one(drop):
    if int(drop) == 0 :
        message = 'IPs by connections : \n' + ips_data[0][0] + " - \n" + ips_data[1][0] + " - \n" + ips_data[2][0]
    else:
        message = 'Most busy day : ', busy_dates[0][0]

    return message 

@app.callback(
    dash.dependencies.Output('example', 'src'), # src attribute
    [dash.dependencies.Input('drop', 'value')]
)
def create_IP_graph(drop):
    fig, ax = plt.subplots()
    fig.set_dpi(75)
    #fig.set_size_inches(int(i), int(i))
    if int(drop) == 0 :
        ax.bar(df2["IPs"],df2["Connections"])
        plt.xlabel('IPs')
        plt.ylabel('Connections')
        plt.title('Highest 10 IP\'s connections')
    elif int(drop) == 1:
        ax.bar(df3["Dates"],df3["Connections"])
        plt.xlabel('days')
        plt.ylabel('Connections')
        plt.title('Logged connections per day ')
            
    plt.xticks(rotation=45)

    buf = io.BytesIO() # in-memory files
    fig.savefig(buf, format = "png") # save to the above file object
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    plt.close()
    return "data:image/png;base64,{}".format(data)
    
# @app.callback(
#     dash.dependencies.Output('example2', 'src'), # src attribute
#     [dash.dependencies.Input('n_points', 'value')]
# )
# def create_daily_graph(n_points):
#     fig, ax = plt.subplots()
#     fig.set_dpi(75)
#     #fig.set_size_inches(int(i), int(i))
#     ax.bar(df3["Dates"],df3["Connections"])
#     plt.xlabel('days')
#     plt.ylabel('Connections')
#     plt.title('Logged connections per day ')
#     plt.xticks(rotation=45)

#     buf2 = io.BytesIO() # in-memory files
#     fig.savefig(buf2, format = "png") # save to the above file object
#     data = base64.b64encode(buf2.getbuffer()).decode("utf8") # encode to html elements
#     plt.close()
#     return "data:image/png;base64,{}".format(data)


@app.callback(
    dash.dependencies.Output('example3', 'src'), # src attribute
    [dash.dependencies.Input('top_3', 'value')]
)
def create_round_graph(top_3):
    i=0
    tmpv = 0
    percent = []
    names = []
    if int(top_3) == 0:
        while i < 3:
            percent.append(user_agent_conn[i]/100)
            names.append(total_requests.index[i])
            tmpv += percent[i]
            i += 1

        tmpv = 100 -tmpv
        names.append('Other')
        percent.append(tmpv)
    else:
        while i < 3 :
            temp = int(useragent_operation.loc[useragent_operation.index[i], 'IPs'])
            percent.append(temp/100)
            tmpv += percent[i]
            names.append(total_requests.index[i])
            i += 1
        tmpv = 100 -tmpv
        percent.append(tmpv)
        names.append('Other')

    fig, ax = plt.subplots()
    fig.set_dpi(75)
    explode = (0.1, 0, 0, 0) 
    ax.pie(percent, explode=explode, labels=names, autopct='%1.1f%%', shadow=True, startangle=90)
    ax.axis('equal')
    plt.title("Top 3 User-Agents")
  
    buf = io.BytesIO() # in-memory files
    fig.savefig(buf, format = "png") # save to the above file object
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    plt.close()
    return "data:image/png;base64,{}".format(data)



if __name__ == "__main__":
    app.run_server(debug = True)



#############################################"Debugging" and old part of code############################################

