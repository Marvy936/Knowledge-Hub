# PowerShell fundamentals

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

Parameter contract je prvá boundary medzi callerom a automatizáciou. PowerShell binding priradí named alebo positional values, vykoná deklarované type conversions a validation attributes a až potom vstúpi do body skriptu. Táto fáza môže odmietnuť chýbajúci alebo syntakticky neplatný input, ale nepreukazuje, že file, remote subject alebo runtime precondition zostanú platné v okamihu mutation.

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

Native executable nevytvára PowerShell error record rovnakým mechanizmom ako cmdlet. PowerShell spustí process, prepojí jeho standard streams a po ukončení sprístupní process exit code cez `$LASTEXITCODE`. Wrapper preto musí bezprostredne zachytiť command-specific code a samostatne rozhodnúť, či znamená success, očakávaný rozdiel alebo tool failure.

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

## Mechanický rozbor kľúčových PowerShell vzorov

Nasledujúce rozbory sledujú každý vzor od parameter bindingu alebo object emission cez pipeline, error a serialization boundary až po mutation a read-back. Cieľom nie je zopakovať syntax, ale ukázať, ktorý runtime objekt alebo stream vznikne, čo môže ďalší krok skutočne použiť a kde sa úspešný PowerShell command ešte nesmie zameniť za verified outcome.

### Object pipeline nie je vizuálna tabuľka

```powershell
Get-ChildItem -Path . -File |
    Where-Object Length -gt 1MB |
    Select-Object Name, Length
```

`Get-ChildItem` zapisuje do success streamu `FileInfo` objekty. Pipeline enumeruje každý object. Skrátená syntax `Where-Object Length -gt 1MB` bindne property `Length`, porovná integer bytes s hodnotou `1MB` a prepustí matching objects. `Select-Object` vytvorí nové projected objects iba s properties `Name` a `Length`.

Ak na koniec pridáš `Format-Table`, pipeline dostane formatting instruction objects určené hostu. Už nejde o pôvodné `FileInfo` a ďalšie `Where-Object Length` nebude mať očakávaný property. Formatting preto patrí až za machine-processing boundary.

Over type:

```powershell
$item = Get-ChildItem -Path . -File | Select-Object -First 1
$item.GetType().FullName
$item | Get-Member
```

Po remoting alebo JSON round-tripe môže type a methods zmiznúť. Consumer má používať explicitný serialization contract, nie predpoklad živého .NET objectu.

### Advanced parameter binding

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string]$ConfigPath
)
```

`CmdletBinding` mení script/function na advanced command a pridáva common parameters. `Mandatory` rieši prítomnosť inputu, nie jeho business platnosť. `ValidateScript` sa vykoná počas bindingu; `$_` je candidate value. Použitie `-LiteralPath` zabráni wildcard interpretácii.

Validation môže byť subjectom TOCTOU race: file existuje pri bindingu a zmení sa pred readom. Kritický apply musí po získaní locku znovu otvoriť/canonicalizovať file a overiť fingerprint.

### Streams a návratová hodnota

PowerShell automaticky zapisuje neassignnutý expression output do success streamu:

```powershell
function Get-Result {
    'starting'                       # toto je tiež success output
    [pscustomobject]@{ Status='OK' } # a toto tiež
}
```

Caller dostane array dvoch objects, nie jeden result. Progress používaj cez `Write-Verbose`, `Write-Information` alebo `Write-Host` podľa contractu a success stream nechaj iba pre data.

```powershell
function Get-Result {
    [CmdletBinding()]
    param()
    Write-Verbose 'Starting calculation'
    [pscustomobject]@{ Status='OK' }
}
```

Pri redirectoch poznaj stream numbers; napríklad `2>` je error stream a `*>` všetky streams. Zlúčenie všetkého do stdout môže zničiť JSON API rovnako ako v Bash.

### Terminating a non-terminating error

```powershell
try {
    $content = Get-Content -LiteralPath $ConfigPath -Raw -ErrorAction Stop
}
catch {
    Write-Error "Unable to read config: $($_.Exception.Message)"
    exit 2
}
```

`-ErrorAction Stop` zmení error record tohto cmdletu na terminating error, takže execution preskočí do `catch`. `catch` premenná `$_` je `ErrorRecord`, nie iba Exception. Obsahuje category, target object, invocation info a stack information.

`Write-Error` v catch môže samo vytvoriť non-terminating error podľa preference. Na CLI boundary je často čitateľnejšie zapísať bounded diagnostic na error stream a `return` stabilný code z `main`, než volať `exit` hlboko vo function.

```powershell
function Invoke-Main {
    try { ...; return 0 }
    catch [System.IO.IOException] { Write-Error $_; return 2 }
}
exit (Invoke-Main)
```

`finally` sa vykoná pri success aj exception. Cleanup nesmie prepísať primary error bez explicitnej policy.

### Native process a `$LASTEXITCODE`

```powershell
& git diff --quiet
$gitExit = $LASTEXITCODE
```

Call operator `&` spustí native executable alebo command path. `$LASTEXITCODE` musíš skopírovať okamžite, pretože ďalší native command ho zmení. `$?` je boolean success poslednej PowerShell pipeline a jeho správanie sa v rôznych versions/native preference nastaveniach môže líšiť.

Git contract:

```powershell
switch ($gitExit) {
    0 { $dirty = $false }
    1 { $dirty = $true }
    default { throw "git diff failed with exit code $gitExit" }
}
```

Exit 1 nie je tool crash; je „differences exist“. Mapovanie command-specific statuses je súčasť wrappera.

### `ShouldProcess` a nested mutations

```powershell
if ($PSCmdlet.ShouldProcess($StatePath, 'Apply Atlas desired state')) {
    Set-Content -LiteralPath $StatePath -Value $payload
}
```

Pri `-WhatIf` vráti `ShouldProcess` false a body sa nevykoná. Ak však helper pred gate-om už vytvoril directory, získal cloud token alebo zmenil temp state, dry-run nie je side-effect free. Najprv resolve/observe/plan, potom všetky mutácie umiestni za gate.

Nested function môže sama deklarovať `SupportsShouldProcess` a caller má forwardovať `-WhatIf:$WhatIfPreference`. Alternatívne nech iba top-level function vlastní mutation gate a helpers nemutujú mimo nej. Mixed model často vytvára dvojité prompts alebo neúplný WhatIf.

### JSON serialization a depth

```powershell
$json = $result | ConvertTo-Json -Depth 10 -Compress
$roundTrip = $json | ConvertFrom-Json
```

`-Depth` určuje, ako hlboko sa nested objects serializujú; príliš malá hodnota môže orezať data a vydať warning. `-Compress` mení whitespace, nie semantics. PowerShell numbers, DateTime, enums, hashtables a ordered dictionaries sa mapujú do JSON s možnou stratou type fidelity.

Pre fingerprint nepoužívaj náhodný property order z ľubovoľného object graphu. Vytvor explicitný ordered DTO a definuj string/date/number representation. Po serialization over schema alebo round-trip values.

### Atomic file mutation

`Set-Content` priamo na production path môže pri process crashi nechať partial alebo truncated file. Bezpečnejší local pattern:

```powershell
$directory = Split-Path -Parent $StatePath
$temp = Join-Path $directory ('.' + [IO.Path]::GetRandomFileName())
try {
    [IO.File]::WriteAllText($temp, $json, [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temp, $StatePath, $true)
}
finally {
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
}
```

Temporary file je na rovnakom filesysteme, aby rename/replace mal platformovo čo najsilnejšiu atomicitu. Windows file-sharing handles, ACL inheritance a antivirus môžu operation ovplyvniť. Po Move stále potrebuješ content fingerprint a runtime verify.

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
