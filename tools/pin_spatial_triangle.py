#!/usr/bin/env python3
"""Enclose a pinned spatial triangle in exact rational coordinates."""
from fractions import Fraction as Q
from math import isqrt
import argparse,json

def frame(l01,l02,l12,bits=80):
 a,b,c=map(Q,(l01,l02,l12))
 if min(a,b,c)<=0 or a+b<=c or a+c<=b or b+c<=a:raise ValueError('nondegenerate triangle required')
 if type(bits)is not int or not 1<=bits<=4096:raise ValueError('invalid precision')
 x=(a*a+b*b-c*c)/(2*a);y2=b*b-x*x;scale=1<<bits
 lo=Q(isqrt((y2.numerator*scale*scale)//y2.denominator),scale);hi=lo if lo*lo==y2 else lo+Q(1,scale)
 assert lo*lo<=y2<=hi*hi
 return {'p0':['0','0','0'],'p1':[str(a),'0','0'],'p2':[[str(x),str(x)],[str(lo),str(hi)],['0','0']],'status':'frame enclosure only; no realization count'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('lengths',nargs=3);a=p.parse_args();print(json.dumps(frame(*a.lengths),indent=2))
