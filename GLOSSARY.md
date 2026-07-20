# Glossary

Rýchly referenčný zoznam pojmov. Glossary nenahrádza plné kapitoly; obsahuje krátke definície a odkazy na širší kontext.

## Artifact

Výstup build procesu určený na ďalšie testovanie, distribúciu alebo deployment, napríklad binárny súbor, balík, container image alebo Helm chart.

## Declarative configuration

Konfigurácia opisujúca požadovaný výsledný stav systému, nie presnú sekvenciu krokov potrebných na jeho dosiahnutie.

## Deployment

Proces sprístupnenia konkrétnej verzie aplikácie alebo konfigurácie v cieľovom prostredí. Deployment nie je automaticky release; nasadená zmena môže zostať používateľom skrytá.

## Desired state

Požadovaný stav systému deklarovaný používateľom alebo automatizačným nástrojom. Controller alebo reconciliation mechanizmus porovnáva desired state s aktuálnym stavom a vykonáva korekcie.

## Drift

Rozdiel medzi deklarovaným alebo evidovaným stavom a skutočným stavom systému, často spôsobený manuálnymi zmenami mimo riadeného procesu.

## Idempotencia

Vlastnosť operácie, pri ktorej opakované vykonanie s rovnakým vstupom vedie k rovnakému výslednému stavu bez neželaných vedľajších účinkov.

## Immutable infrastructure

Prevádzkový model, v ktorom sa existujúce inštancie zásadne neupravujú. Nová konfigurácia alebo verzia sa nasadí vytvorením nových inštancií a nahradením starých.

## Lead time

Čas od vzniku požiadavky alebo potvrdenia zmeny po jej dostupnosť v cieľovom prostredí. Presná definícia musí byť v organizácii konzistentná.

## Reconciliation

Opakovaný proces porovnávania desired state so skutočným stavom a vykonávania krokov, ktoré odchýlku zmenšujú.

## Release

Obchodné alebo produktové rozhodnutie sprístupniť funkcionalitu používateľom. Release môže byť oddelený od deploymentu napríklad feature flagom.

## Rollback

Návrat k predchádzajúcej verzii aplikácie alebo konfigurácie. Nie vždy je bezpečný, najmä po nekompatibilnej databázovej migrácii.

## Roll-forward

Náprava zlyhania nasadením novej opravnej verzie namiesto návratu na starú verziu.

## Toil

Manuálna, opakujúca sa, automatizovateľná a nízko hodnotná prevádzková práca, ktorá rastie spolu so systémom.

## T-shaped engineer

Inžinier so širokou orientáciou naprieč viacerými oblasťami a hlbokou expertízou aspoň v jednej z nich.
