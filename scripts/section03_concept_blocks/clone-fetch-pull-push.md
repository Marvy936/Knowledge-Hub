## Čo znamenajú clone, fetch, pull a push

Git je distribuovaný systém: každá plnohodnotná clone má vlastnú object database, refs a históriu. Remote nie je centrálna pracovná kópia, ale iné repository dostupné cez transport. Názov `origin` je iba lokálny alias URL.

**Clone** vytvorí nové lokálne repository, stiahne dostupné objekty a refs, nastaví remote a checkoutne úvodnú branch. **Fetch** prenesie nové objekty a aktualizuje remote-tracking refs, napríklad `origin/main`. Nemení automaticky working tree ani lokálny `main`.

**Pull** nie je samostatný synchronizačný primitív. Je to skratka pre fetch a následnú integráciu do aktuálnej branch, typicky merge alebo rebase podľa konfigurácie. Preto je predvídateľnejšie vedieť, ktorú integračnú stratégiu pull použije.

**Push** navrhuje aktualizáciu refu v inom repository a odosiela chýbajúce objekty. Remote prijme update iba ak spĺňa ref policy. Bežný fast-forward push je povolený, keď starý remote tip je ancestor nového tipu. Non-fast-forward update zahadzuje z pohľadu refu časť dostupnej histórie a vyžaduje force policy.

Neutrálny stav:

```text
lokálne:
main        → C3
origin/main → C2

remote:
main        → C2
```

`origin/main` nie je živý query na server. Je to lokálny ref z posledného fetchu. Po úspešnom `git fetch origin` sa aktualizuje podľa remote advertisement. Lokálny `main` zostane na `C3`, kým ho vedome neposunieš.

Refspec určuje mapovanie source a destination refs. Typický fetch refspec mapuje `refs/heads/*` na `refs/remotes/origin/*`. Push môže explicitne poslať `HEAD:refs/heads/main`. Upstream configuration iba určuje predvolený vzťah branch–remote branch pre commands ako `pull` alebo `push`.

`--force-with-lease` je bezpečnejší než slepý `--force`, pretože remote ref prepíše iba ak stále zodpovedá očakávanému tipu. Chráni pred nevedomým zahodením práce, ktorú remote získal po tvojom poslednom observation pointe; stále však ide o history rewrite a potrebuje collaboration contract.