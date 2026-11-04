import sys,numpy as np,pandas as pd
from datos import semanal
def retro(t,desde,hasta='2026-10-30'):
    w=semanal(t,desde); w=w[w.index<=hasta].rename(columns={'Close':'c','Low':'l'})
    w['ema']=w.c.ewm(span=50,adjust=False).mean(); w['dist']=w.c/w.ema-1; w['slope']=w.ema.diff(4)>0
    w=w.iloc[50:]; c,l,e=w.c.values,w.l.values,w.ema.values
    i=0;rows=[]
    while i<len(w):
        if w.dist.iloc[i]>=0.10 and w.slope.iloc[i]:
            pk=i;j=i
            while j<len(w)-1 and c[j+1]>=c[pk]*0.97:
                j+=1
                if c[j]>c[pk]: pk=j
            k=pk+1;lo=np.inf;lo_i=None
            while k<len(w) and k<=pk+26 and c[k]<=c[pk]:
                if l[k]<lo: lo=l[k];lo_i=k
                k+=1
            if lo_i is not None and k<len(w):
                rows.append((w.index[pk].date(),round(c[pk],2),w.index[lo_i].date(),round(lo,2),round((lo/c[pk]-1)*100,1)))
            i=max(k,pk+1)
        else: i+=1
    return pd.DataFrame(rows,columns=['pico','cierre_pico','fecha_min','minimo','caida%'])
if __name__=='__main__':
    t,desde,prof=sys.argv[1],int(sys.argv[2]),float(sys.argv[3])
    r=retro(t,desde); print(t,'retrocesos totales',len(r))
    s=r[r['caida%']<=-prof].sort_values('caida%',ascending=False)
    print(f'tan profundos como -{prof}%: {len(s)}'); print(s.to_string(index=False))
