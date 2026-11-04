import pandas as pd,numpy as np,time
from datos import semanal
U=['SPY','QQQ','IWM','XLV','XLE','XLP','XLU','XLF','XLI','XLB','XLK','XLY','XLRE','GLD','COPX','SMH','CIBR','WCLD','EWL','AWK']
ev=[]
for t in U:
    try: w=semanal(t,1104537600)
    except Exception as ex: print('fallo',t); continue
    w=w[w.index<='2026-10-30']; c=w.Close; v=w.Volume; e=c.ewm(span=50,adjust=False).mean()
    pend=(e/e.shift(13)-1).abs()*100; b26=(c.rolling(26).max()/c.rolling(26).min()-1)*100; med=b26.expanding(104).median()
    raw=((pend<=2)&(b26<=med)).values
    lat=np.zeros(len(c),bool)
    for i in range(3,len(c)): lat[i]=raw[i-3:i+1].all()   # 4 semanas seguidas
    i=0
    while i<len(c)-9:
        if lat[i]:
            j=i
            while j+1<len(c) and lat[j+1]: j+=1
            # banda del lateral: cierres de las 26 semanas hasta j
            lo=c.iloc[max(0,j-25):j+1].min(); hi=c.iloc[max(0,j-25):j+1].max(); vm=v.iloc[max(0,j-25):j+1].mean()
            # primera semana tras el lateral que cierra fuera de la banda (hasta 26 semanas)
            for k in range(j+1,min(len(c)-8,j+27)):
                if c.iloc[k]>hi or c.iloc[k]<lo:
                    up=c.iloc[k]>hi; vr=v.iloc[k]/vm if vm>0 else np.nan
                    after=c.iloc[k+1:k+9]
                    held=(after>hi).iloc[-1] if up else (after<lo).iloc[-1]
                    ev.append((t,c.index[k].date(),'arriba' if up else 'abajo',round(vr,2),bool(held)))
                    break
            i=j+1
        else: i+=1
    time.sleep(0.3)
df=pd.DataFrame(ev,columns=['ticker','semana','rotura','vol_vs_lateral','aguantó_8sem'])
up=df[df.rotura=='arriba']
print('roturas al alza:',len(up),'| aguantan:',up['aguantó_8sem'].mean().round(2))
for th in (0.8,1.0,1.25,1.5,2.0):
    a=up[up.vol_vs_lateral>=th]; b=up[up.vol_vs_lateral<th]
    print(f'vol >= {th}: {len(a)} roturas, aguantan {a["aguantó_8sem"].mean()*100:.0f}% | vol < {th}: {len(b)}, aguantan {b["aguantó_8sem"].mean()*100 if len(b) else float("nan"):.0f}%')
print(up.sort_values('vol_vs_lateral').to_string(index=False))
df.to_csv('finlat.csv',index=False)
