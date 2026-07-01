#!/usr/bin/env python3
"""T2a-core-calibrate: derive token-ratio thresholds per section archetype from translated chapters.
Reads manifest (source prose tokens) + translated MDX (KO prose tokens), computes ratio,
stratifies by code_ratio (>=0.30 code-heavy), applies sigma floors + prior seed for sparse strata (W5-H1/H3, W6-M1).
Usage: python3 scripts/calibrate_ratio.py ch01 [ch02 ...]"""
import tiktoken, re, json, sys, os
enc = tiktoken.get_encoding("cl100k_base")
def strip(t):
    t = re.sub(r'```.*?```','',t,flags=re.S); t = re.sub(r'^---.*?---','',t,flags=re.S)
    t = re.sub(r'<[^>]+>','',t); t = re.sub(r'import .*','',t); return t
man = {s['id']:s for s in json.load(open('assets/manifest.json'))['sections']}
prose, code = [], []
for sid in sys.argv[1:]:
    p=f'site/docs'; mdx=None
    for root,_,fs in os.walk('site/docs'):
        if f'{sid}.mdx' in fs: mdx=open(os.path.join(root,f'{sid}.mdx')).read()
    if not mdx or sid not in man: continue
    r = len(enc.encode(strip(mdx)))/man[sid]['token_count']
    (code if man[sid]['code_ratio']>=0.30 else prose).append(r)
def stratum(vals, floor):
    import statistics as st
    if not vals: return None
    mu=st.mean(vals); sg=max(floor, st.pstdev(vals) if len(vals)>1 else mu*0.15)
    return {"mu":round(mu,3),"sigma":round(sg,3),"lower":round(mu-2*sg,3),"upper":round(mu+3*sg,3),"n":len(vals)}
thr={"tokenizer":"cl100k_base","para_ratio_min":0.85,"code_ratio_threshold":0.30,
     "strata":{"prose":stratum(prose,0.286) or {}, "code-heavy":stratum(code,0.477) or {}}}
json.dump(thr,open('scripts/gates/ratio_thresholds.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(thr,ensure_ascii=False))
