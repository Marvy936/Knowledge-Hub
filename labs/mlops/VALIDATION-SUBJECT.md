# MLOps Registry validation subject

> **Status: Pending**

Tento súbor vytvára samostatný `labs/mlops/**` pull-request subject po tom, ako hosted Registry workflow prešiel na štandardný `pull_request` event.

Jeho existencia sama osebe nepreukazuje runtime úspech. Autoritatívny dôkaz vznikne iba vtedy, keď exact commit tejto vetvy prejde hosted Python 3.12 jobom, ktorý vykoná 16 contract testov, MLflow Registry round-trip, artifact SHA-256 read-back, exact-version verification, server restart a cleanup.

Aktuálna revision je samostatný `synchronize` trigger vytvorený po úplnom načítaní workflowu v base vetve. Aj tento stav zostáva `Pending`, kým GitHub nepriradí exact workflow run a jeho výsledok.

Po runtime closeoute sa tento dočasný validation marker odstráni alebo nahradí odkazom na exact evidence record.
