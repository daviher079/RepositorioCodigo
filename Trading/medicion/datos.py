import json,subprocess,sys,pandas as pd
def semanal(t,desde=1420070400):
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1={desde}&period2=9999999999&interval=1d"
    r=json.loads(subprocess.run(["curl","-s","-m","30","-A","Mozilla/5.0",url],capture_output=True,text=True).stdout)["chart"]["result"][0]
    q=r["indicators"]["quote"][0]
    d=pd.DataFrame({k:q[k.lower()] for k in ['Open','High','Low','Close','Volume']},index=pd.to_datetime(r["timestamp"],unit='s').normalize()).dropna()
    return d.resample('W-FRI').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
if __name__=='__main__':
    for t in sys.argv[1:]:
        w=semanal(t); w.to_csv(f'{t}.csv')
        c=w['Close']; e=c.ewm(span=50,adjust=False).mean()
        print(t,w.index[-1].date(),'cierre',round(c.iloc[-1],2),'EMA50',round(e.iloc[-1],2),'| máx cierre 1a',round(c[-52:].max(),2),c[-52:].idxmax().date(),'| máx high 1a',round(w.High[-52:].max(),2),'| máx high total',round(w.High.max(),2),w.High.idxmax().date())
