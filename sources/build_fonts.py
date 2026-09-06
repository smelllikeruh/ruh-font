#!/usr/bin/env python3
"""Build the reviewed fonts from the committed editable UFO, without AI services."""
from pathlib import Path
import json,sys,hashlib
from defcon import Font as UFOFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.ttLib import TTFont,newTable
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
root=Path(__file__).resolve().parent.parent
fontdir=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'fonts'
fontdir.mkdir(parents=True,exist_ok=True)
source=root/'sources/RUH.ufo'
u=UFOFont(source);cfg=json.loads((root/'sources/font-metadata.json').read_text())
family=cfg['family'];version=cfg['version'];basename=cfg['basename'];name=cfg['names']
order=u.lib['public.glyphOrder'];fea=u.features.text;records={};metrics={};cmap={}
for gn in order:
 g=u[gn];p=RecordingPen();g.draw(p);records[gn]=p
 b=BoundsPen(None);p.replay(b);bounds=b.bounds or (0,0,0,0)
 metrics[gn]=(round(g.width),round(bounds[0]))
 for cp in g.unicodes:cmap[cp]=gn
for is_ttf,ext in [(True,'ttf'),(False,'otf')]:
 fb=FontBuilder(1000,isTTF=is_ttf);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap)
 if is_ttf:
  glyphs={}
  for gn,p in records.items():
   pen=TTGlyphPen(None);p.replay(Cu2QuPen(pen,1.0,reverse_direction=False));glyphs[gn]=pen.glyph()
  fb.setupGlyf(glyphs)
 else:
  cs={}
  for gn,p in records.items():
   pen=T2CharStringPen(metrics[gn][0],None);p.replay(pen);cs[gn]=pen.getCharString()
  fb.setupCFF(basename,{'FullName':family+' Regular','FamilyName':family,'Weight':'Regular','version':version,'Notice':name['copyright']},cs,{})
 fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=980,descent=-280,lineGap=0)
 fb.setupNameTable(name,mac=False);fb.setupOS2(version=4,sTypoAscender=980,sTypoDescender=-280,sTypoLineGap=0,
  usWinAscent=980,usWinDescent=280,sxHeight=460,sCapHeight=700,usWeightClass=400,usWidthClass=5,
  fsType=0,fsSelection=0x40|0x80,ulCodePageRange1=3,ulCodePageRange2=0,achVendID='RUH ')
 fb.font['head'].fontRevision=float(version)
 fb.font['head'].created=3871497600;fb.font['head'].modified=3871497600
 fb.font.recalcTimestamp=False
 if is_ttf:
  prep=newTable('prep');prep.program=Program();prep.program.fromBytecode(b'\xb8\x01\xff\x85\xb0\x04\x8d');fb.font['prep']=prep
  gasp=newTable('gasp');gasp.version=1;gasp.gaspRange={65535:15};fb.font['gasp']=gasp
 meta=newTable('meta');meta.data={'dlng':'Latn','slng':'Latn'};fb.font['meta']=meta
 fb.setupPost(underlinePosition=-90,underlineThickness=28);addOpenTypeFeaturesFromString(fb.font,fea)
 target=fontdir/ext;target.mkdir(exist_ok=True)
 fb.save(target/f'{basename}.{ext}')
webdir=fontdir/'webfonts';webdir.mkdir(exist_ok=True)
f=TTFont(fontdir/'ttf'/f'{basename}.ttf',recalcTimestamp=False);f.flavor='woff2';f.save(webdir/f'{basename}.woff2')


print(json.dumps({str(p.relative_to(fontdir)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(fontdir.rglob(basename+".*"))},indent=2))
