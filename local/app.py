import pandas as pd
pd.set_option('display.max_colwidth', -1)
import datetime as dt
import plotly as py
import plotly.graph_objs as go
import plotly.express as px
py.offline.init_notebook_mode(connected = True)
from flask import Flask, request, render_template, session, redirect, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    df0 = pd.DataFrame()
    df0["title"] = ["/earthquake"]
    df0["title"]=df0["title"].apply(lambda x: '<a href="{0}">{0}</a>'.format(x))
    df0["content"] = ["Will geo plot location and intensity within the range of input in time animation"]
    
    df = pd.DataFrame()
    df["title"] =[
        "hello",
        "환영",
        "/us",
        "/kr"
    ]
    df["title"]=df["title"].apply(lambda x: '<a href="{0}">{0}</a>'.format(x))
    
    df["content"]=[
        "welcome to DQ's stock plot, app scrapes Yahoo Finace and plots closing values(with repect to day 1 for comparison) of last 100 days to compare",
        "DQ의 주식 그래프 어플입니다, 네이버 금융에서 최근 100일의 종가를 웹스크랩 하여 그래프합니다",
        "Utilize input spaces in first line to enter stock symbols, app recognizes comma as speration of multiple inputs(eg: AMZN,NFLX,GOOGL)",
        "두번째 줄의 입력칸에 주식명 입력, 어플은 쉼표(',')로 다수의 검색어를 구분할 수 있습니다(예: 삼성전자, naver, 카카오)"
    ]
    
    print("Server received request for 'Home' page...")
    n = pd.DataFrame().to_html()
    return (
        df0.to_html(escape=False) + n + n + n +        
        df.to_html(escape=False))

@app.route("/us", methods=["GET", "POST"])
def us():
    if request.method == "POST":
        mains = ["^GSPC","^DJI","^IXIC","^RUT","TVIX"]
        main_names = ["S&P500","DOW30","NASDAQ","Russel2000","Velocity Shares Daily"]
        dfs = []
        for main in mains:
            url = f'https://finance.yahoo.com/quote/{main}/history?p={main}'
            df = pd.read_html(url)[0]#[0:100]
            df["Date"]=pd.to_datetime(df["Date"],errors = "coerce")
            df.dropna(inplace = True)
            for n in range(1,7):
                df.iloc[:,n] = pd.to_numeric(df.iloc[:,n],errors = "coerce")
            df.dropna(inplace = True)
            base = df.iloc[:,4][len(df)-1]
            df["c_base"] = df["Close*"]/base
            dfs.append(df)
        traces = []
        for n in range(len(main_names)):
            x = dfs[n]["Date"]
            y = dfs[n]["c_base"]
            trace = go.Scatter(x=x,y=y,
                           mode = 'lines',
                           name = main_names[n])
            traces.append(trace)
            
        stocks = request.form["symbols"]
        stocks = stocks.upper()
        stocks = str(stocks).replace(" ","").split(",")
        dfs = []
        for stock in stocks:
            url = f'https://finance.yahoo.com/quote/{stock}/history?p={stock}'
            df = pd.read_html(url)[0]#[0:100]
            df["Date"]=pd.to_datetime(df["Date"],errors = "coerce")
            df.dropna(inplace = True)
            for n in range(1,7):
                df.iloc[:,n] = pd.to_numeric(df.iloc[:,n],errors = "coerce")
            df.dropna(inplace = True)
            base = df.iloc[:,4][len(df)-1]
            df["c_base"] = df["Close*"]/base
            dfs.append(df)

#         traces = []
        for n in range(len(stocks)):
            x = dfs[n]["Date"]
            y = dfs[n]["c_base"]
            trace = go.Scatter(x=x,y=y,
                           mode = 'lines',
                           name = stocks[n])
            traces.append(trace)
        fig = go.Figure(data=traces)
        return(py.offline.plot(fig,output_type='div'))

    return render_template("form.html")

@app.route("/kr", methods=["GET", "POST"])
def kr():
    symbols = pd.read_html("http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13",encoding="euc_kr")
    
    if request.method == "POST":
        stocks = request.form["symbols"]
        stocks = stocks.upper()
        stocks = str(stocks).replace(" ","").split(",")

        symbols = symbols[0]
        stocks_df = pd.DataFrame({"회사명": stocks})
        stocks_symbols = pd.merge(stocks_df,symbols)
        codes = stocks_symbols["종목코드"]
        results = 30

        dfs = []
        kos_name = ["코스피","코스피200","코스닥"]
        kos = ["KOSPI", "KPI200", "KOSDAQ"]
        for code in kos:
            for pg in range(1,int(results/6)+2):
                url = f"https://finance.naver.com/sise/sise_index_day.nhn?code={code}&page={pg}"
#                 return(url)
                if pg == 1:
                    df = pd.read_html(url)[0].dropna()
                else:
                    apnd = pd.read_html(url)[0].dropna()
                    df = df.append(apnd)
            df.reset_index(drop=True,inplace=True)
            df = df[0:results]
            df["날짜"] = pd.to_datetime(df["날짜"])
            df["비율"] = df["체결가"]/(df["체결가"][len(df)-1])
            dfs.append(df)

        traces = []
        for n in range(len(kos_name)):
            x = dfs[n]["날짜"]
            y = dfs[n]["비율"]
            trace = go.Scatter(x=x,y=y,
                           mode = 'lines',
                           name = kos_name[n])
            traces.append(trace)


        dfs=[]
        for code in codes:
            code = str(code).zfill(6)
            for pg in range(1,int(results/10)+2):
                url = f"https://finance.naver.com/item/sise_day.nhn?code={code}&page={pg}"
                if pg == 1:
                    df = pd.read_html(url)[0].dropna()
                else:
                    apnd = pd.read_html(url)[0].dropna()
                    df = df.append(apnd)
            df.reset_index(drop=True,inplace=True)
            df = df[0:results]
            df["날짜"] = pd.to_datetime(df["날짜"])
            df["비율"] = df["종가"]/(df["종가"][len(df)-1])
            dfs.append(df)

        for n in range(len(stocks)):
            x = dfs[n]["날짜"]
            y = dfs[n]["비율"]
            trace = go.Scatter(x=x,y=y,
                           mode = 'lines',
                           name = stocks[n])
            traces.append(trace)

        fig = go.Figure(data=traces)
        return(py.offline.plot(fig, output_type = 'div'))

    return render_template("form1.html")
    

@app.route("/earthquake", methods=["GET", "POST"])
def earthquake():
    if request.method == "POST":
        dtype = request.form["dtype"]
        if dtype == "hr":
            data = pd.read_csv("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.csv")
        
        if dtype == "day":
            data = pd.read_csv("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.csv")
        
        if dtype == "7days":
            data = pd.read_csv("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.csv")
        
        if dtype == "30days":
            data = pd.read_csv("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv")

        data["updated"] = pd.to_datetime(data["updated"])
        data["updated"] = pd.DatetimeIndex(data["updated"]).normalize()
        data["updated"] = data["updated"].astype(str)

        data = data[data["mag"]>0]
        data.sort_values("updated",inplace = True)
        px.set_mapbox_access_token("pk.eyJ1IjoidGl2bWU3IiwiYSI6ImNrMWEwZDVtNDI4Zm4zYm1vY3o3Z25zejEifQ._yTPkj3nXTzor72zIevLCQ")
        fig = px.scatter_mapbox(data, lat="latitude", lon="longitude", size="mag", color = "mag",
                          color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=3,animation_frame="updated")
        fig.update_layout(autosize=True,width=1500,height=750)
#                           ,margin=go.layout.Margin(l=50,r=50,b=100,t=100,pad=4))
        
        return(py.offline.plot(fig,output_type="div"))
        
    return render_template("earthquake.html")    

if __name__ == "__main__":
    app.run(debug=True)