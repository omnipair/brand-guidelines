from html.parser import HTMLParser
from html import escape, unescape
from pathlib import Path
import json, re, zipfile, struct

ROOT=Path(__file__).resolve().parents[1]
class N:
    def __init__(self,tag='',attrs=(),parent=None,raw=None):
        self.tag=tag;self.attrs=dict(attrs);self.children=[];self.parent=parent;self.raw=raw
    def has(self,cls):return cls in self.attrs.get('class','').split()
    def text(self):return unescape(self.raw or '') if not self.tag else ''.join(x.text() for x in self.children)
    def find(self,test):
        out=[]
        for c in self.children:
            if test(c):out.append(c)
            out.extend(c.find(test))
        return out
    def html(self):
        if not self.tag:return self.raw or ''
        attrs=''.join(' '+k+'="'+escape(v or '',quote=True)+'"' for k,v in self.attrs.items())
        if self.tag in VOID:return '<'+self.tag+attrs+'>'
        return '<'+self.tag+attrs+'>'+''.join(c.html() for c in self.children)+'</'+self.tag+'>'
VOID={'img','input','br','meta','link','hr','source','wbr','area','base','col','embed','param','track'}
class Parser(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=False);self.root=N('root');self.current=self.root
    def handle_starttag(self,t,a):
        n=N(t,a,self.current);self.current.children.append(n)
        if t not in VOID:self.current=n
    def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
    def handle_endtag(self,t):
        n=self.current
        while n.parent and n.tag!=t:n=n.parent
        if n.parent:self.current=n.parent
    def handle_data(self,d):self.current.children.append(N(raw=d,parent=self.current))
    def handle_entityref(self,d):self.handle_data('&'+d+';')
    def handle_charref(self,d):self.handle_data('&#'+d+';')

source=(ROOT/'source/simple-original.html').read_text()
def image_size(path):
    try:
        data=path.read_bytes()
        if data[:8]==b'\x89PNG\r\n\x1a\n':return struct.unpack('>II',data[16:24])
        if data[:2]==b'\xff\xd8':
            pos=2
            while pos<len(data):
                while data[pos]==255:pos+=1
                marker=data[pos];pos+=1
                if marker in (0xd8,0xd9):continue
                length=struct.unpack('>H',data[pos:pos+2])[0]
                if marker in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):
                    h,w=struct.unpack('>HH',data[pos+3:pos+7]);return w,h
                pos+=length
        if path.suffix=='.svg':
            vb=re.search(r'viewBox="([\d. -]+)"',data.decode())
            if vb:
                v=vb.group(1).split();return round(float(v[2])),round(float(v[3]))
    except (OSError,IndexError,ValueError):pass
    return None
p=Parser();p.feed(source)
for n in p.root.find(lambda n:n.has('wip-block') or n.has('done-pill')):n.parent.children.remove(n)
for n in p.root.find(lambda n:n.has('wip-pill')):
    if 'sign-off' in n.text():n.attrs['class']='review-note';n.children=[N(raw='Proposed')]
    else:n.parent.children.remove(n)
sections={n.attrs['id']:n for n in p.root.find(lambda n:n.tag=='section' and n.has('sect') and 'id' in n.attrs)}
groups=[
('foundation','Brand foundation','compass','dawn','The belief behind everything we build.',[
 ('what','What is Omnipair?',['hero-enemy','what','narrative','problem','idea']),('purpose','Belief & purpose',['belief','mission','promise']),('positioning','Positioning & audience',['positioning','audience']),('character','Personality & character',['character','stand-against']),('principles','Brand principles',['principles']),('moodboard','Visual territory',['moodboard'])]),
('verbal','Verbal identity','quote','sky','Confident, clear and unmistakably Omnipair.',[
 ('message','Core message',['verbal-intro','core-message','messaging']),('pitch','Pitch & descriptions',['pitch','descriptions']),('tone','Tone of voice',['tone','writing-principles','calibration']),('copy','Copy in practice',['copy-styles','templates']),('terminology','Terminology & naming',['vocabulary','naming']),('phrases','Signature phrases',['phrases','tagline'])]),
('logo','Logo system','asterisk','aqua','One point. Every possibility.',[
 ('lockups','Primary lockups',['lockups','hierarchy']),('symbol','Symbol & wordmark',['symbol','wordmark']),('construction','Construction & alignment',['construction','optical']),('clearspace','Clear space & size',['clearspace','minsize']),('misuse','Logo misuse',['misuse']),('app-icons','App icons',['app-icons'])]),
('colour','Colour','palette','dawn','Sky, Aqua and Dawn. One continuous spectrum.',[
 ('inspiration','Inspiration & the Sky Axis',['inspiration','sky-axis']),('palette-sky','Sky',['palette-sky']),('palette-aqua','Aqua',['palette-aqua']),('palette-dawn','Dawn',['palette-dawn']),('shades','Shades & neutrals',['shades','neutrals']),('palettes-in-use','Palettes in use',['palettes-in-use'])]),
('typography','Typography','type','sky','M Saans. One voice across every touchpoint.',[('type-primary','M Saans',['type-primary'])]),
('photography','Imagery','image','aqua','Painterly worlds. An unmistakable point of view.',[('territory','Open Horizons',['territory']),('environments','Environments',['environments']),('prompt-formula','Prompt formula',['prompt-formula']),('references','References & outputs',['references'])]),
('graphic','Graphic system','grid','dawn','Texture and precision, in the same frame.',[('shader','Dither shader',['shader'])]),
('diagrams','Technical diagrams','layers','sky','Make the mechanism visible.',[('explainers','Explainer graphics',['explainers'])]),
('applications','Applications','shapes','aqua','The identity, out in the world.',[('social','Social media',['social']),('merch','Merchandise & graphics',['merch'])])]

output=[]
for gid,title,icon,color,desc,topics in groups:
    g={'id':gid,'title':title,'icon':icon,'color':color,'description':desc,'topics':[]}
    for tid,label,ids in topics:
        parts=[]
        for sid in ids:
            n=sections[sid]
            for img in n.find(lambda x:x.tag=='img'):
                img.attrs['loading']='lazy';img.attrs['decoding']='async'
                size=image_size(ROOT/'public'/img.attrs.get('src',''))
                if size:img.attrs['width']=str(size[0]);img.attrs['height']=str(size[1])
            for table in n.find(lambda x:x.tag=='table'):
                wrapper=N('div',[('class','table-scroll'),('tabindex','0'),('role','region'),('aria-label',label+' table')],table.parent)
                i=table.parent.children.index(table);table.parent.children[i]=wrapper;wrapper.children=[table];table.parent=wrapper
            for e in n.find(lambda x:x.attrs.get('data-copy')):
                if e.tag not in ('button','a'):e.attrs.update({'role':'button','tabindex':'0','aria-label':'Copy '+e.attrs['data-copy']})
            html=n.html().replace(', alongside Aeonik VF — the display face used for chapter titles and captions in this guideline.','.').replace('M Saans VF and Aeonik VF','M Saans VF').replace('Aeonik','M Saans')
            parts.append(html)
        g['topics'].append({'id':tid,'title':label,'sections':ids,'html':'\n'.join(parts)})
    output.append(g)
glass=(ROOT/'source/engineered-glass.html').read_text()
next(g for g in output if g['id']=='graphic')['topics'].insert(0, {'id':'engineered-glass','title':'Engineered glass','sections':['engineered-glass'],'html':glass})
(ROOT/'content.json').write_text(json.dumps(output,ensure_ascii=False))

# Preserve the existing content components, then theme them in the new stylesheet.
css=re.search(r'<style>([\s\S]*?)</style>',source).group(1)
start=css.index('  /* stance */');end=css.index('  /* brand kit') if '  /* brand kit' in css else css.index('  .kit {')
css=css[start:end]
extra_start=source.index('  .statement-lead {');extra_end=source.index('  footer {',extra_start)
css+='\n'+source[extra_start:extra_end]
css=css.replace("'Aeonik'","'M Saans'").replace("'Saans SemiMono'","'M Saans'")
css=re.sub(r'font-family:[^;}]+;',"font-family: 'M Saans', system-ui, sans-serif;",css)
(ROOT/'content.css').write_text(css)

fonts=ROOT/'public/assets/fonts'
for path in fonts.glob('*Aeonik*'):path.unlink()
with zipfile.ZipFile(ROOT/'public/assets/downloads/Omnipair-Fonts-Pack.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(fonts/'MSaansVF.woff2','MSaansVF.woff2')
print(f'Extracted {len(output)} chapters and {sum(len(g["topics"]) for g in output)} topics.')
