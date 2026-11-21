"""Dependency-free advance-width reader for Apple SD Gothic Neo (.ttc). Used by lib_m to pre-wrap text."""
import struct
_FONT="/System/Library/Fonts/AppleSDGothicNeo.ttc"
_cache={}
def _u16(b,o): return struct.unpack_from(">H",b,o)[0]
def _u32(b,o): return struct.unpack_from(">I",b,o)[0]
def _tables(b,off):
    n=_u16(b,off+4); t={}
    for i in range(n):
        p=off+12+16*i; t[b[p:p+4].decode("latin1")]=(_u32(b,p+8),_u32(b,p+12))
    return t
def _name(b,t,nid):
    o,_=t["name"]; cnt=_u16(b,o+2); so=o+_u16(b,o+4)
    for i in range(cnt):
        p=o+6+12*i; pid,eid,lid,n,ln,lo=struct.unpack_from(">6H",b,p)
        if n==nid and pid==3 and lid==0x409: return b[so+lo:so+lo+ln].decode("utf-16-be")
    return None
def _cmap(b,t):
    o,_=t["cmap"]; n=_u16(b,o+2); best=None
    for i in range(n):
        pid,eid,so=struct.unpack_from(">HHI",b,o+4+8*i)
        fmt=_u16(b,o+so)
        if fmt==12: best=(12,o+so); break
        if fmt==4 and best is None: best=(4,o+so)
    fmt,s=best; m={}
    if fmt==12:
        ng=_u32(b,s+12)
        for g in range(ng):
            a,z,gid=struct.unpack_from(">III",b,s+16+12*g)
            for c in range(a,z+1): m[c]=gid+(c-a)
    else:
        sc=_u16(b,s+6)//2; e=s+14; st=e+2*sc+2; dl=st+2*sc; ro=dl+2*sc
        for k in range(sc):
            end=_u16(b,e+2*k); start=_u16(b,st+2*k); delta=struct.unpack_from(">h",b,dl+2*k)[0]; r=_u16(b,ro+2*k)
            for c in range(start,end+1):
                if c==0xFFFF: continue
                if r==0: g=(c+delta)&0xFFFF
                else:
                    g=_u16(b,ro+2*k+r+2*(c-start))
                    if g: g=(g+delta)&0xFFFF
                m[c]=g
    return m
def _load():
    if _cache: return _cache
    b=open(_FONT,"rb").read(); n=_u32(b,8)
    for i in range(n):
        off=_u32(b,12+4*i); t=_tables(b,off)
        style=_name(b,t,17) or _name(b,t,2)
        upm=_u16(b,t["head"][0]+18)
        nh=_u16(b,t["hhea"][0]+34); ho=t["hmtx"][0]
        adv=[_u16(b,ho+4*g) for g in range(nh)]
        _cache[style]=(upm,_cmap(b,t),adv)
    return _cache
def width(s,size,style="Regular",track=0):
    upm,cm,adv=_load()[style]; tot=0
    for ch in s:
        g=cm.get(ord(ch),0); tot+=adv[min(g,len(adv)-1)]
    return tot*size/upm + track/1000*size*len(s)
def styles(): return list(_load().keys())
