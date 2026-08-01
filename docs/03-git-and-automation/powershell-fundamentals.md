# PowerShell fundamentals

<!-- CONCEPT-FIRST:START -->
## Čo je PowerShell

PowerShell je shell a automatizačný jazyk postavený nad .NET. Jeho pipeline neprenáša iba textové riadky; prenáša objekty s properties a methods. Formatting je oddelená prezentačná vrstva, preto to, čo vidíš v tabuľke, nemusí byť celý objekt ani jeho serialization.

```powershell
Get-Process | Where-Object CPU -gt 10 | Select-Object Name, Id, CPU
```

`Where-Object` pracuje s property `CPU`, nie s pozíciou textového stĺpca. To znižuje potrebu parsovať ľudský output, ale iba pri cmdletoch a nástrojoch, ktoré skutočne vracajú objekty.

PowerShell má viac streams: success output, errors, warnings, verbose, debug a information. Machine-readable output sa nemá miešať s diagnostickými správami. `Write-Host` je prezentačný výstup, nie návratová hodnota funkcie.

Errors môžu byť terminating alebo non-terminating. `try/catch` zachytí terminating error. Parameter `-ErrorAction Stop` môže pre konkrétny cmdlet zmeniť non-terminating error na terminating. Native process má samostatný exit code v `$LASTEXITCODE`; vznik error recordu a native failure nie sú totožné.

Advanced function definuje typed parametre, validation a common parameters. `SupportsShouldProcess` umožní `-WhatIf` a `-Confirm`, ale mutation sa musí skutočne nachádzať za volaním `$PSCmdlet.ShouldProcess(...)`. Samotná deklarácia parameteru nič nechráni.

```powershell
if ($PSCmdlet.ShouldProcess($Target, 'Apply configuration')) {
    # mutation
}
```

PowerShell objekty sa pri prechode cez external process alebo JSON serialization menia na text/serialized representation. Type fidelity sa môže stratiť. Dates, enums, large integers a nested objects preto potrebujú explicitný contract.

Pri cross-platform automation treba rozlišovať PowerShell language behavior od platformových APIs, filesystem semantics a dostupnosti native commands. Rovnaký `.ps1` môže syntakticky fungovať na Linuxe aj Windows, ale jeho mutation a locking semantics sa môžu líšiť.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Atlas Windows operátori potrebujú rovnaký release contract ako Linux tím. PowerShell nie je Bash so syntaxou `$env:`. Jeho pipeline prenáša .NET objekty, cmdlets používajú parameter binding a errors majú viac streams a terminating semantics. Bez tejto hranice skript môže zobraziť červenú chybu a napriek tomu pokračovať alebo môže úspešne spracovať text, ktorý už stratil objektovú štruktúru.

## Object pipeline

```powershell
Get-ChildItem -Path . -File |
    Where-Object Length -gt 1MB |
    Select-Object Name, Length
```

Pipeline neposúva formatted columns, ale objects s properties. Formatting cmdlets patria až na presentation koniec:

```powershell
Get-Process | Format-Table
```

Výstup `Format-Table` už nie je vhodný ako input pre business processing. Automation má pracovať s objects a serializovať ich až na boundary.

## Parameter contract

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$ConfigPath,

    [Parameter(Mandatory)]
    [string]$StatePath,

    [switch]$Force
)
```

Advanced function alebo script dostane common parameters, validation a `ShouldProcess`. Parameter validation je input gate, no runtime precondition sa musí overiť neskôr nad effective state-om.

## Success output a ďalšie streams

PowerShell rozlišuje success, error, warning, verbose, debug, information a progress streams. `Write-Output` posiela data do success pipeline. `Write-Host` je presentation/information output a nemá byť machine-readable API.

```powershell
[pscustomobject]@{
    Status = 'Verified'
    Commit = $commit
    Changed = $false
}
```

Caller môže object ďalej filtrovať alebo serializovať:

```powershell
$result | ConvertTo-Json -Depth 5
```

Ak function mieša progress strings a objects do success streamu, consumer dostane heterogénne pole.

## Terminating a non-terminating errors

Mnohé cmdlets vytvoria non-terminating error a pokračujú. Pre kritický krok:

```powershell
Get-Content -LiteralPath $ConfigPath -ErrorAction Stop
```

Potom `try/catch/finally`:

```powershell
try {
    $content = Get-Content -LiteralPath $ConfigPath -Raw -ErrorAction Stop
}
catch {
    Write-Error "Unable to read config: $($_.Exception.Message)"
    exit 2
}
finally {
    # bounded cleanup
}
```

Globálne `$ErrorActionPreference = 'Stop'` môže byť vhodné, ale script musí rozumieť cmdlets, ktoré stále pracujú inak, a native processes, ktoré sa riadia exit codeom.

## Native processes

```powershell
& git diff --quiet
$gitExit = $LASTEXITCODE
```

`$?` a `$LASTEXITCODE` nie sú to isté. Pri native command je authoritative exit code `$LASTEXITCODE`. PowerShell 7 má ďalšie preference pre native error behavior, ale portable automation má exit code zachytiť bezprostredne po command-e.

```powershell
if ($gitExit -eq 1) {
    throw 'Working tree is dirty.'
}
elseif ($gitExit -ne 0) {
    throw "git diff failed with exit code $gitExit"
}
```

## `ShouldProcess`, `-WhatIf` a dry-run hranica

```powershell
if ($PSCmdlet.ShouldProcess($StatePath, 'Apply Atlas desired state')) {
    # mutation
}
```

`-WhatIf` preukazuje, že mutation branch nebola vykonaná. Nepreukazuje, že plan je validný alebo že všetky nested functions rešpektujú ShouldProcess. Každá mutating helper musí mať contract alebo byť volaná iba za gate-om.

Dry-run output má obsahovať resolved inputs a proposed delta, nie iba vetu „would update file“.

## LiteralPath a wildcardy

`-Path` môže interpretovať wildcardy. Pre user-provided file identity je bezpečnejšie:

```powershell
Get-Content -LiteralPath $ConfigPath
```

Rovnako pri remove/copy operáciách. Path canonicalization a allowed-root check sú security boundary, najmä pri elevated scripts.

## Serialization

```powershell
$config = Get-Content -LiteralPath $ConfigPath -Raw |
    ConvertFrom-Json -AsHashtable
```

PowerShell objects a JSON majú rozdielne type semantics. Default depth pri `ConvertTo-Json` môže orezať nested data, preto sa depth volí explicitne a output sa round-trip testuje.

YAML nie je built-in vo všetkých podporovaných PowerShell versions. Automation má pinned module alebo external parser contract, nie implicitný dependency na developer profile.

## Remoting a serialization boundary

PowerShell remoting posiela serialized representations, nie živé objects s plnými methods. Type names môžu dostať prefix `Deserialized.`. Skript, ktorý lokálne volá method, môže remote zlyhať.

Remote mutation potrebuje target identity, authentication, session configuration, timeout a verification na remote hoste. Successful command submission nepreukazuje desired runtime state.

## Incident: native tool zlyhá, script vráti success

PowerShell wrapper spustí Python CLI, potom vypíše success object bez kontroly `$LASTEXITCODE`:

```powershell
& python tools/atlasctl.py apply ...
[pscustomobject]@{ Status = 'Applied' }
```

Python vráti 3 pre stale plan, no PowerShell process skončí 0. CI je false-green. Oprava zachytí exit code okamžite, mapuje ho na terminating error a success object vytvorí až po samostatnom verify kroku.

## Zhrnutie

PowerShell automation stojí na object pipeline, parameter contracte, oddelených streams, explicitnom error behavior a native exit code handlingu. `ShouldProcess` poskytuje mutation gate, nie automatickú correctness. Machine-readable output má byť object, nie formatted text, a remote alebo serialization boundary sa musí overiť samostatne.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Bash automation](bash-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Python for automation →](python-for-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
