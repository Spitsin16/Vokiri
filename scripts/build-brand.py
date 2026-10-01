from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
b=Path('dist/brand');ink='#262c20';paper='#f3f3ed'
shape='M12 12h16v16h-8l12 20-8 5-12-22Z M36 12h16v19L40 53l-8-5 12-20h-8Z'
for name,color in [('mark',ink),('mark-inverse',paper)]:
 (b/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="{shape}" fill="{color}"/></svg>')
icon=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#d6f477"/><path d="{shape}" transform="translate(8 8) scale(.75)" fill="{ink}"/></svg>'
(b/'icon.svg').write_text(icon);Path('dist/icon.svg').write_text(icon)
f=TTFont('/System/Library/Fonts/Avenir Next.ttc',fontNumber=0);gs=f.getGlyphSet();cm=f.getBestCmap();pen=BoundsPen(gs);gs[cm[ord('o')]].draw(pen)
scale=100/f['head'].unitsPerEm;xheight=pen.bounds[3]*scale;factor=xheight/41
start=40*factor+5;cursor=0;parts=[]
for ch in 'okiri':
 name=cm[ord(ch)];p=SVGPathPen(gs);gs[name].draw(p)
 parts.append(f'<path transform="translate({cursor} 0)" d="{p.getCommands()}"/>');cursor+=f['hmtx'].metrics[name][0]-28
width=start+cursor*scale+2
for name,color in [('wordmark',ink),('wordmark-inverse',paper)]:
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.3f} 112"><g transform="translate({-12*factor:.3f} {100-53*factor:.3f}) scale({factor:.6f})"><path d="{shape}" fill="{color}"/></g><g transform="translate({start:.3f} 100) scale({scale} {-scale})" fill="{color}">'+''.join(parts)+'</g></svg>'
 (b/(name+'.svg')).write_text(svg)
