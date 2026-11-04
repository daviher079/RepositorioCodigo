import sys,pandas as pd
from datos import semanal
def episodios(w,hasta='2026-10-30'):
    w=w[w.index<=hasta]; c=w.Close; e=c.ewm(span=50,adjust=False).mean()
    out=[]; P=c.iloc[0]; pi=c.index[0]; mn=P; mi=pi; up=False
    for i,(d,x) in enumerate(c.items()):
        if x>P:
            if mn<P: out.append((pi.date(),round(P,2),mi.date(),round(mn/P-1,4),up))
            P=x; pi=d; mn=x; mi=d; up=bool(x>e.iloc[i] and e.iloc[i]>e.iloc[max(0,i-4)])
        elif x<mn: mn=x; mi=d
    if mn<P: out.append((pi.date(),round(P,2),mi.date(),round(mn/P-1,4),up,'(en curso)'))
    return out
if __name__=='__main__':
    t=sys.argv[1]; desde=int(sys.argv[2]); prof=float(sys.argv[3])
    w=semanal(t,desde)
    ep=[x for x in episodios(w) if x[4] and x[3]<=-prof]
    print(t,'desde',w.index[0].date(),'| retrocesos en tendencia que llegaron a',f'-{prof:.1%}',':',len(ep))
    for x in sorted(ep,key=lambda y:y[3],reverse=True): print('  ',x)
