import numpy as np,pandas as pd
from datos import semanal
def sim(t,desde,zd,s=None,lvl=None,cap=52,hasta='2026-10-30'):
    w=semanal(t,desde); w=w[w.index<=hasta]
    c=w.Close.values; e=w.Close.ewm(span=50,adjust=False).mean().values; idx=w.index
    dist=c/e-1; slope=np.r_[[False]*4,e[4:]>e[:-4]]
    res=[];i=50
    while i<len(c):
        if dist[i]>=0.10 and slope[i]:
            pk=i;j=i
            while j<len(c)-1 and c[j+1]>=c[pk]*0.97:
                j+=1
                if c[j]>c[pk]: pk=j
            k=pk+1;ent=None
            while k<len(c) and k<=pk+26 and c[k]<=c[pk]:
                if c[k]<=c[pk]*(1-zd) and c[k]>e[k]: ent=k;break   # en zona y aún sobre la EMA (filtro de tendencia)
                k+=1
            if ent is not None:
                E=c[ent]; d=s if s else (E-c[pk]*(1-lvl))/E   # distancia del stop en %
                stop=E*(1-d); mx=E; out=None
                for m in range(ent+1,min(len(c),ent+1+cap)):
                    if c[m]<stop or c[m]<e[m]: out=(m,'stop' if c[m]<stop else 'EMA');break
                    mx=max(mx,c[m]); stop=max(stop,mx*(1-d))
                if out is None:
                    if ent+cap>=len(c): i=k+1; continue   # sin un año completo: fuera
                    out=(ent+cap,'1 año')
                X=c[out[0]]; R=(X/E-1)/d
                res.append((idx[ent].date(),round(E,2),idx[out[0]].date(),out[1],round((X/E-1)*100,1),round(R,2)))
            i=max(k,pk+1)
        else: i+=1
    return pd.DataFrame(res,columns=['entrada','precio','salida','motivo','%','R'])
casos=[('XLE',915148800,0.107,0.12,None,'stop 12%'),('EXXY.DE',1104537600,0.071,0.10,None,'stop 10%'),
       ('XLV',915148800,0.124,0.10,None,'stop 10%'),('XLV',915148800,0.124,None,0.18,'stop nivel -18% del pico'),
       ('CIBR',1420070400,0.127,None,0.155,'control: stop nivel -15,5%')]
for t,dd,zd,s,lvl,lab in casos:
    r=sim(t,dd,zd,s,lvl)
    g=r[r.R>0]; p=r[r.R<=0]
    pay=(g.R.mean()/abs(p.R.mean())) if len(p) and len(g) else float('nan')
    print(f"\n== {t} ({lab}) — {len(r)} entradas | mediana R {r.R.median():.2f} | media R {r.R.mean():.2f} | ganadoras {len(g)}/{len(r)} | ganancia media {g.R.mean():.2f}R, pérdida media {p.R.mean() if len(p) else 0:.2f}R | payoff {pay:.2f}")
    print(r.to_string(index=False))
