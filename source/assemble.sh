#!/bin/bash
set -e
cd /home/claude/build
python3 build.py
python3 - <<'PY'
t=open('/home/claude/build/template.html',encoding='utf-8').read()
d=open('/home/claude/build/data.json',encoding='utf-8').read()
out=t.replace('/*__DATA__*/', d)
open('/home/claude/build/kit.html','w',encoding='utf-8').write(out)
print('kit.html bytes', len(out.encode()))
PY
python3 - <<'PY'
SK='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
h=open('/home/claude/build/kit.html',encoding='utf-8').read()
open('/home/claude/build/preview.html','w',encoding='utf-8').write(SK+h+'</body></html>')
PY
