#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md"
text = path.read_text(encoding="utf-8")
old = """Golden path koncentruje authority. Kompromitovaný template, custom action alebo managed module môže zmeniť stovky services. Preto path artifacts potrebujú rovnakú supply-chain disciplínu ako application artifacts.\n\nControls zahŕňajú:\n"""
new = """Golden path koncentruje authority. Kompromitovaný template, custom action alebo managed module môže zmeniť stovky services. Preto path artifacts potrebujú rovnakú supply-chain disciplínu ako application artifacts.\n\nSupply-chain boundary začína pri zdroji path definície a končí až pri effective outpute v cieľových systémoch. Review template-u nestačí, ak template počas execution resolve-ne mutable action image, action získa broad cloud credential alebo output policy neoverí skutočne vytvorenú IAM role. Dôveryhodný chain preto viaže source commit, resolved dependency digests, execution identity, input digest, mutation operation IDs a read-back inventory do jednej provenance línie. Každá transition musí odmietnuť subject, ktorý nevie reprodukovateľne identifikovať alebo ktorého scope prekračuje capability contract.\n\nControls sa presadzujú na odlišných boundaries a navzájom sa nenahrádzajú. Protected review chráni authoring transition, pinning zabraňuje zmene executable bytes po review, least privilege obmedzuje blast radius počas mutation a output read-back odhaľuje confused-deputy alebo provider-defaulting rozdiel. Audit následne umožňuje nájsť všetkých consumers kompromitovanej generation a repair channel vytvorí nový bounded lifecycle namiesto ad-hoc hromadného patchovania. Napríklad podpísaný template stále nie je bezpečný, ak používa `latest` action s cluster-admin credentialom; source authenticity v takom prípade nedokazuje execution integrity ani správny output.\n\nControls zahŕňajú:\n"""
if old not in text:
    raise SystemExit("Golden-path supply-chain remediation marker not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
print("Deepened golden-path supply-chain boundary")
