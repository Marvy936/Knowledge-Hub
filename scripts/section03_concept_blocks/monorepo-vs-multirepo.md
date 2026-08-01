## Čo znamenajú monorepo a multirepo

Repository topology určuje, ktoré source subjects, ownership boundaries a changes sa verzujú spolu. **Monorepo** ukladá viac komponentov alebo služieb v jednom repository a commit graph-e. **Multirepo** ich rozdeľuje do viacerých repositories. Hybrid kombinuje obe podľa change a governance boundaries.

Monorepo neznamená automaticky jeden build alebo jeden deploy. Multirepo neznamená automaticky nezávislé služby. Skutočná nezávislosť závisí od contracts, build graphu, release procesu a runtime coupling.

Pri monorepe môže jeden atomic commit zmeniť library, consumer a tests naraz. Ref transition poskytne spoločný source snapshot. Cena je väčší repository scale, zložitejšie ownership rules, selective build a potreba presného dependency graphu.

Pri multirepe má každý komponent vlastný ref lifecycle, permissions a release cadence. Cross-repository change však nie je atomic. Potrebuje kompatibilné poradie, dočasné expand/contract obdobie, versioned contracts alebo koordinovaný rollout.

Neutrálny príklad zmeny API:

```text
producer pridá nový optional field
→ publikuje kompatibilný contract
→ consumers sa postupne aktualizujú
→ producer začne field vyžadovať až po migrácii
```

V monorepe možno source changes commitnúť spolu, ale production deployments stále nemusia byť simultánne. V multirepe sa source changes prirodzene delia, preto je compatibility contract ešte viditeľnejší.

Rozhodovanie má vychádzať z **change coupling**: ktoré súbory, komponenty a tímy sa často menia ako jedna business zmena. Ďalšie faktory sú ownership, security boundaries, build scale, tooling, artifact promotion, dependency update automation a compliance.

Repository boundary nie je service boundary ani team boundary. Jedno repository môže obsahovať mnoho tímov a jedna služba môže závisieť od viacerých repositories. Topology je optimalizácia toku zmien a governance, nie architektonická pravda sama o sebe.