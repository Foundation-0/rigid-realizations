#!/usr/bin/env python3
"""Check explicit planar input graphs for every Laman sparsity inequality."""
import argparse,itertools,json

def check(d):
 n=d['n'];edges=[tuple(sorted(e))for e in d['edges']]
 if type(n)is not int or not 2<=n<=13:raise ValueError('n must be 2 through 13')
 if any(len(e)!=2 or e[0]==e[1]or any(type(x)is not int or x not in range(n)for x in e)for e in edges)or len(set(edges))!=len(edges):raise ValueError('invalid zero-based edges')
 if len(edges)!=2*n-3:raise ValueError('total edge count differs from 2n-3')
 for size in range(2,n+1):
  for vertices in itertools.combinations(range(n),size):
   V=set(vertices);count=sum(a in V and b in V for a,b in edges)
   if count>2*size-3:raise ValueError(f'sparsity violation on {vertices}')
 return {'n':n,'edges':len(edges),'laman_sparsity':True,'real_count':None}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('graph');a=p.parse_args();print(json.dumps(check(json.load(open(a.graph))),indent=2))
