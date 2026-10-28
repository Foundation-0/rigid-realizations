#!/usr/bin/env python3
"""Numerical diagnostics for candidate roots; never classifies a root as certified."""
import argparse,cmath,json,math

def diagnose(records):
 if len({r['id']for r in records})!=len(records):raise ValueError('duplicate candidate IDs')
 points=[]
 for r in records:
  coords=[complex(*z)for z in r['coordinates']]
  if not coords or any(not math.isfinite(z.real)or not math.isfinite(z.imag)for z in coords):raise ValueError('invalid coordinates')
  points.append(coords)
 if points and len({len(x)for x in points})!=1:raise ValueError('inconsistent coordinate dimensions')
 out=[]
 for i,(r,p)in enumerate(zip(records,points)):
  near=min((max(abs(x-y)for x,y in zip(p,q))for j,q in enumerate(points)if i!=j),default=None)
  out.append({'id':r['id'],'max_absolute_imaginary_coordinate':max(abs(z.imag)for z in p),'nearest_candidate_sup_distance':near,'classification':'unresolved; independent interval proof required'})
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('candidates');a=p.parse_args();print(json.dumps(diagnose(json.load(open(a.candidates))),indent=2))
