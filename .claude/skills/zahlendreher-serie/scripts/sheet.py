import sys; sys.path.insert(0,"tools")
from chars import character, DEFS
items=[("Leo","smirk","point","2.400.000"),("Mia","smile","down","312"),("Chantal","disgust","crossed","48"),("Henri","worried","down","1.250"),("Karl","surprised","notepad","3")]
g="".join(f'<g transform="translate({220+i*420} 1000) scale(1)">{character(n,f"c{i}",pose=p,expr=e,disp_value=v)}</g>' for i,(n,e,p,v) in enumerate(items))
html=f'''<html><head><style>@font-face{{font-family:"DSEG7";src:url("teil-01/assets/fonts/DSEG7Classic-Bold.woff2")}}body{{margin:0;background:#c9b49a}}</style></head><body>
<svg width="2100" height="1050" viewBox="0 0 2100 1050"><defs>{DEFS}</defs>{g}</svg></body></html>'''
open("sheet.html","w").write(html)
