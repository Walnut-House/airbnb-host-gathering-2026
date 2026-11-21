import json, subprocess, sys, os
T=os.path.expanduser("~/Library/Application Support/Tesseract/bin/tsrct")
FONT="/System/Library/Fonts/AppleSDGothicNeo.ttc"
W,H=1920,1080
BG=(0.972,0.965,0.950); INK=(0.11,0.11,0.12); SEC=(0.36,0.35,0.34); MUT=(0.42,0.41,0.40)
LINE=(0.86,0.85,0.83); CARD=(1,1,1); ACC=(0.80,0.24,0.25); ACC_SOFT=(0.97,0.90,0.89)
class Doc:
    def __init__(s): s.layers=[]; s.n=0
    def _id(s): s.n+=1; return s.n
    def rect(s,x,y,w,h,c,r=0,stroke=None):
        L={"type":"Rect","id":s._id(),"name":f"rect{s.n}","blendMode":"normal","activeRange":{"start":0,"duration":3000},
           "transform":{"anchorPoint":[0,0],"position":[x,y],"scale":[100,100],"rotation":0,"opacity":100},
           "rect":{"size":[w,h],"fillColor":[*c,1],"roundness":r}}
        if stroke: L["rect"].update(strokeEnabled=True,strokeColor=[*stroke,1],strokeWidth=2)
        s.layers.append(L)
    def text(s,x,y,w,h,t,size,style="Regular",c=INK,just="left",lead=None,track=0):
        d={"text":t,"fontFamily":"Apple SD Gothic Neo","fontStyle":style,"fontSize":size,"fillColor":[*c,1],
           "strokeWidth":0,"justification":just,"boxText":True,"boxSize":[w,h],"boxPosition":[0,0],"tracking":track}
        if lead: d["leading"]=lead
        s.layers.append({"type":"Text","id":s._id(),"name":t[:20],"blendMode":"normal","activeRange":{"start":0,"duration":3000},
           "transform":{"anchorPoint":[0,0],"position":[x,y],"scale":[100,100],"rotation":0,"opacity":100},"sourceText":d})
def build(name, fn):
    proj=f"{name}.tsrct"; work=f".tesseract-work/{name}.json"
    if not os.path.exists(proj):
        subprocess.run([T,"project","create","--project",proj],check=True,capture_output=True)
        subprocess.run([T,"project","import-font","--project",proj,"--file",FONT],check=True,capture_output=True)
    subprocess.run([T,"project","checkout","--project",proj,"--output",work],check=True,capture_output=True)
    doc=json.load(open(work)); d=Doc(); fn(d)
    doc["dimensions"]={"width":W,"height":H}; doc["backgroundColor"]=[*BG,1] if "backgroundColor" in doc else None
    doc.pop("backgroundColor",None)
    doc["composition"]["layers"]=list(reversed(d.layers))  # first drawn = back
    json.dump(doc,open(work,"w"),ensure_ascii=False)
    r=subprocess.run([T,"project","commit","--project",proj,"--file",work],capture_output=True,text=True)
    if r.returncode: print(r.stdout,r.stderr); sys.exit(1)
    r=subprocess.run([T,"preview","--project",proj,"--time","1","--output",f"{name}.png"],capture_output=True,text=True)
    if r.returncode: print(r.stdout,r.stderr); sys.exit(1)
    print("ok",name)

def header(d,num,title,sub,page=None):
    d.rect(0,0,W,H,BG)
    d.text(120,84,900,40,num,26,"SemiBold",ACC)
    d.text(120,128,1500,90,title,60,"Bold",INK)
    d.text(120,214,1600,50,sub,28,"Regular",SEC)
    d.rect(120,288,W-240,2,LINE)
    d.text(120,1010,1200,30,"호스트, 우리가 만나다 · 2026 대한공유숙박호스트협회 연말 게더링",20,"Regular",MUT)
    if page: d.text(W-320,1010,200,30,str(page),20,"Regular",MUT,just="right")

def stat(d,x,y,w,big,label,acc=False):
    d.text(x,y,w,110,big,92,"Bold",ACC if acc else INK,track=-10)
    d.text(x,y+120,w,80,label,26,"Regular",SEC)


def run(slides):
    """slides: list of (name, fn). Renders into the current directory. CLI args filter names."""
    for name,fn in slides:
        if len(sys.argv)>1 and name not in sys.argv[1:]: continue
        build(name,fn)

# ===== Round-2 shared components (deck-wide spec — use these, do not hand-draw variants) =====
COLHEAD_Y=356          # column/section header baseline row
DIV_X=940              # the only two-column divider x
GREY_BAR=(0.70,0.68,0.65)
def col_head(d,x,w,t,y=COLHEAD_Y):
    d.text(x,y,w,40,t,28,"SemiBold",INK)
def divider(d,y0=340,y1=980,x=DIV_X):
    d.rect(x,y0,2,y1-y0,LINE)
def numlist(d,x,y,w,items,pitch=60,hi=None,size=24,rules=True,sub=None):
    """Numbered list. items: list of str, or (title, detail) tuples (detail on 2nd line, SEC).
    Numbers '1','2'.. (no zero pad) at x in SEC; text at x+40. hi = index of the ONE highlighted item
    (its number turns ACC; text stays INK). Hairline rule above every row and under the last.
    pitch: row height (use 60 for 1-line rows, 96 for 2-line rows). Returns y after the list."""
    for i,it in enumerate(items):
        if rules: d.rect(x,y,w,2,LINE)
        t,det=(it if isinstance(it,tuple) else (it,None))
        d.text(x,y+14,40,size*1.5,str(i+1),size,"SemiBold",ACC if i==hi else SEC)
        d.text(x+40,y+14,w-40,size*1.5,t,size,"Medium" if det else "Regular",INK)
        if det: d.text(x+40,y+14+size*1.5,w-40,size*1.5,det,22,"Regular",SEC)
        y+=pitch
    if rules: d.rect(x,y,w,2,LINE)
    return y
def bars(d,x,y,w,rows,label_w=160,hi=None,maxv=None,unit=""):
    """Horizontal bar chart. rows: (label, value, value_text). Bars 48px, gap 24 (pitch 72).
    Label 24 Regular at x; bar starts at x+label_w; value label 28 Bold, 16px right of bar.
    Longest bar ends 180px before x+w. hi = index of the ONE accent bar (others GREY_BAR)."""
    maxv=maxv or max(r[1] for r in rows); span=w-label_w-180
    for i,(lab,v,vt) in enumerate(rows):
        yy=y+i*72; bw=max(6,span*v/maxv)
        d.text(x,yy+8,label_w-16,36,lab,24,"Regular",INK)
        d.rect(x+label_w,yy,bw,48,ACC if i==hi else GREY_BAR)
        d.text(x+label_w+bw+16,yy+4,200,40,vt,28,"Bold",ACC if i==hi else INK)
    return y+len(rows)*72
def bigstat(d,x,y,w,value,label,hero=True,acc=False):
    """Big number. hero=96px (one per slide region), else 72px. Numbers only — no arrows, no words in the slot."""
    s=96 if hero else 72
    d.text(x,y,w,s*1.2,value,s,"Bold",ACC if acc else INK,track=-10 if hero else -6)
    d.text(x,y+s*1.25,w,72,label,24,"Regular",SEC)
    return y+s*1.25+44
def timeline(d,x,y,steps,pitch,hi=None,body_size=22):
    """Horizontal timeline. steps: (label, body). Dot 24px on a hairline; numbered label '1  제목' 26 SemiBold
    40px under the dot row; body 40px under label. hi = index of the ONE outcome step (red dot)."""
    n=len(steps); d.rect(x+12,y+11,pitch*(n-1),2,LINE)
    for i,(lab,body) in enumerate(steps):
        xx=x+i*pitch
        d.rect(xx,y,24,24,ACC if i==hi else INK,12)
        d.text(xx,y+52,pitch-20,40,f"{i+1} {lab}",26,"SemiBold",INK)
        if body: d.text(xx,y+100,pitch-24,body_size*1.5*3,body,body_size,"Regular",SEC)

# ===== Round-3 additions =====
def takeaway(d,t,y=920,x=120,w=1680):
    """THE takeaway line (max one per slide): hairline above, 26 SemiBold INK. Prefix '호스트가 할 일 — ' when it is an action."""
    d.rect(x,y-24,w,2,LINE); d.text(x,y,w,40,t,26,"SemiBold",INK)
def note(d,x,y,w,t,lines=1):
    """Secondary note/caveat: 22 Regular SEC. Never bold, never red."""
    d.text(x,y,w,int(22*1.5*lines)+6,t,22,"Regular",SEC)
def table_head(d,x,y,w,cols):
    """Table header: labels 22 SemiBold SEC at (x+offset,y), one hairline under at y+40. cols: [(offset,label)]."""
    for off,lab in cols: d.text(x+off,y,400,34,lab,22,"SemiBold",SEC)
    d.rect(x,y+40,w,2,LINE)
