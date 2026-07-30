#!/usr/bin/env python3
import base64,hashlib,json,zlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/"scripts"
h0=["f8c3443336585cd216771307a1c5c161cd220272b0d415b866f0289f73fac7a6","3373cfb77639d23a3258b9c2127ebc38f4db9301cbb8dc40a29bb9e5faa63537","25a9032c2ac52e9e2c4a1ff326c5ee2f860b4df406d837a91bddbac59e938380","630ea8593b1052e81a05995dc7b94b23cbd9294607d0625e62982e44cec7e173","bbe2d1d12b5198b3d92815b762032f33c727e24e3d4e2d8ba38d549f45af6fd9","75ce4fdb5e95aafb5ce6989b5318d1aeefdebb6addf442e3c955eef86fbbf65b","4719a41590cb8e49018205542fe6469cb3b3906833fc090c4ad814864c7ea4c6"]
h1=["239649e07d4b21693b979b222e6c8d46e68ff6809218bb321871ec4883de71be","8c7eb68bc9882f50f3c0e6e2c4e33466ad7b25487c06c8f64a66fac5743459e8","dbc40c489166e14eb36e38dc4c16c3cc9d1172c15023a1e8cedeceab4ae11c80","a2bf59031c95513649218059aaffde3ecd73f06766d901d61d3ffdfc6f1e516f","078c2f7ed1da13b7ee5daccf46ad296cc2b6f3dfd193ebc21363d20e5805a80f","9224578caddf9f3481518e9cac593006a982a317af853f8d229c98d41ff82250","b9b85041bd0e49c3e46799c81ece521213964cdf14083a79c704b015ae419aa9","2f3c3813984b340ed5eebe5dea59d340d5d4f1ec6f680d7565a29d051a9ffd0d","445438ed1280688a8c3aac5c6d765913e71abfc329aaaddd89be72b6ffabd6ad","af36375ea7dd386675de797934bac3b0c3070a335742a590b20a6fd97b9016c6","3dc6d2d9086c679cc23717f30aaea4add6368291860017174b2a51dd5c1aa62e","8d15e4071a7814abd56ba5a248445d367cdf051e10e3ede3f8decde68ff325c8"]
P=[(f".gitops_block4_{i:03d}.txt",h) for i,h in enumerate(h0)]+[(f".gitops_block4_pair_{i:03d}.txt",h) for i,h in enumerate(h1)]
C=[]
for n,e in P:
 p=S/n
 if not p.is_file(): raise SystemExit(f"Missing payload part: {n}")
 b=p.read_bytes(); a=hashlib.sha256(b).hexdigest()
 if a!=e: raise SystemExit(f"Integrity failure {n}: length={len(b)} expected={e} actual={a}")
 C.append(b.decode("ascii"))
x="".join(C); d=hashlib.sha256(x.encode()).hexdigest()
if len(x)!=59808 or d!="581389fd3c1d8dfe320e76242d122eae9795840749ebe42eaa284769e92601aa": raise SystemExit(f"Assembled integrity failure: length={len(x)} sha256={d}")
try: raw=zlib.decompress(base64.b64decode(x,validate=True)); data=json.loads(raw.decode())
except Exception as e: raise SystemExit(f"Decode failure: {e}") from e
E={"docs/16-gitops-and-platform-engineering/service-catalog.md","docs/16-gitops-and-platform-engineering/guardrails.md","docs/16-gitops-and-platform-engineering/multi-tenancy.md","glossary/16d-service-catalog-guardrails-multitenancy-lifecycles.md","scripts/integrate_gitops_block4.py"}
if not isinstance(data,dict) or set(data)!=E: raise SystemExit(f"Unexpected output inventory: {sorted(data) if isinstance(data,dict) else type(data).__name__}")
for n,c in data.items():
 if not isinstance(c,str): raise SystemExit(f"Non-text content: {n}")
 p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(c,encoding="utf-8",newline="\n")
for n,_ in P:(S/n).unlink()
for p in S.glob(".gitops_block4_rest_*.txt"):p.unlink()
Path(__file__).unlink()
print(f"Assembled GitOps block 4: chars={len(x)} json={len(raw)} outputs={len(data)} sha256={d}")
