#!/usr/bin/env python3
"""Exact rational Krawczyk checker for pinned planar distance systems."""
import argparse,json,sys
from fractions import Fraction as Q

def iv(a,b=None):return (Q(a),Q(a if b is None else b))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[1],-a[0]
def sub(a,b):return add(a,neg(b))
def mul(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def scale(c,a):return mul(iv(c),a)
def sumiv(values):
 out=iv(0)
 for v in values:out=add(out,v)
 return out
def inverse(a):
 n=len(a);r=[list(row)+[Q(i==j)for j in range(n)]for i,row in enumerate(a)]
 for c in range(n):
  p=next((i for i in range(c,n)if r[i][c]),None)
  if p is None:raise ValueError('singular centre Jacobian')
  r[c],r[p]=r[p],r[c];v=r[c][c];r[c]=[x/v for x in r[c]]
  for i in range(n):
   if i!=c:
    v=r[i][c];r[i]=[x-v*y for x,y in zip(r[i],r[c])]
 return [row[n:]for row in r]

def check(d):
 n=d['n'];edges=d['edges'];lengths=[Q(x)for x in d['lengths']];pins=d['pinned'];boxes=d['boxes']
 if type(n)is not int or n<3 or d['dimension']!=2:raise ValueError('only planar systems supported')
 if len(edges)!=2*n-3 or len(lengths)!=len(edges)or any(x<=0 for x in lengths):raise ValueError('bad edge/length shape')
 keys=[tuple(sorted(e))for e in edges]
 if any(len(e)!=2 or e[0]==e[1]or any(type(v)is not int or not 1<=v<=n for v in e)for e in edges)or len(set(keys))!=len(keys):raise ValueError('invalid edges')
 if len(pins)!=2 or pins[0]==pins[1]or tuple(sorted(pins))not in keys:raise ValueError('invalid pinned edge')
 pin_index=keys.index(tuple(sorted(pins)));L=lengths[pin_index];free=[i for i in range(1,n+1)if i not in pins];D=2*len(free)
 if d['unknowns']!=[f'{axis}{i}'for i in free for axis in ('x','y')]:raise ValueError('unknown ordering differs')
 constraints=[(e,l)for j,(e,l)in enumerate(zip(edges,lengths))if j!=pin_index]
 def positions(X):return {pins[0]:[iv(0),iv(0)],pins[1]:[iv(L),iv(0)],**{i:[X[2*j],X[2*j+1]]for j,i in enumerate(free)}}
 def system(X):
  p=positions(X);F=[];J=[]
  for (u,v),length in constraints:
   diff=[sub(p[u][k],p[v][k])for k in (0,1)]
   F.append(sub(sumiv(mul(z,z)for z in diff),iv(length*length)))
   J.append([scale((2 if i==u else -2 if i==v else 0),diff[k])for i in free for k in (0,1)])
  return F,J
 parsed=[]
 for box in boxes:
  if len(box)!=D:raise ValueError('wrong box dimension')
  X=[iv(*b)for b in box]
  if any(a>=b for a,b in X):raise ValueError('box must have positive widths')
  centre=[(a+b)/2 for a,b in X];C=[iv(x)for x in centre];F0,J0=system(C);_,J=system(X);A=inverse([[v[0]for v in row]for row in J0])
  B=[[sub(iv(int(i==j)),sumiv(scale(A[i][k],J[k][j])for k in range(D)))for j in range(D)]for i in range(D)]
  if max(sum(max(abs(a),abs(b))for a,b in row)for row in B)>=1:raise ValueError('contraction norm not below one')
  K=[add(sub(iv(centre[i]),sumiv(scale(A[i][k],F0[k])for k in range(D))),sumiv(mul(B[i][j],sub(X[j],C[j]))for j in range(D)))for i in range(D)]
  if any(not (X[i][0]<K[i][0] and K[i][1]<X[i][1])for i in range(D)):raise ValueError('Krawczyk inclusion failed')
  parsed.append(X)
 for i,a in enumerate(parsed):
  for b in parsed[:i]:
   if not any(x[1]<y[0]or y[1]<x[0]for x,y in zip(a,b)):raise ValueError('certificate boxes overlap')
 if type(d['claimed_real_count'])is not int or d['claimed_real_count']!=len(boxes):raise ValueError('claimed count differs')
 return {'certified_non_degenerate_boxes':len(boxes),'status':'lower bound only; independent implementation and source review pending'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('certificate');a=p.parse_args()
 try:print(json.dumps(check(json.load(open(a.certificate)))))
 except (ValueError,KeyError,TypeError,OSError,IndexError,ZeroDivisionError)as e:print(e,file=sys.stderr);return 1
 return 0
if __name__=='__main__':sys.exit(main())
