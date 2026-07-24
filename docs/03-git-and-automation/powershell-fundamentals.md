# PowerShell fundamentals

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Processes, threads, PID a signals](../01-linux-and-systems/processes-threads-pid-signals.md), [Environment variables](../01-linux-and-systems/environment-variables.md)
- Súvisiace témy: object pipeline, .NET, modules, remoting, native processes, CI automation

## 1. Definícia

PowerShell je shell a automatizačný jazyk postavený nad .NET object modelom. Jeho pipeline štandardne prenáša objekty s typom, properties a methods, nie iba textové riadky.

```text
command
→ objects v success output stream-e
→ parameter binding alebo pipeline processing
→ ďalšie objects
→ display/serialization boundary
```

Object pipeline znižuje potrebu parsovať vizuálne tabuľky, ale sama o sebe nezaručuje bezpečný skript. Produkčná automatizácia potrebuje explicitne riešiť:

- parameter a type contract,
- pipeline enumeration,
- success a diagnostické streams,
- terminating a non-terminating errors,
- native process exit codes,
- side effects a `ShouldProcess`,
- concurrency a remoting,
- serialization a encoding,
- credentials,
- plan, apply a verify lifecycle.

## 2. Kedy je PowerShell vhodný

Silné prípady:

- Windows administrácia,
- cross-platform .NET automation,
- Azure, Microsoft 365, Active Directory a Windows management tooling,
- object-oriented transformácie JSON, XML, CSV a API výsledkov,
- filesystem, registry, certificate a service orchestration,
- CI/CD na Windows aj Linux runneroch,
- remote management cez PowerShell Remoting alebo SSH-based mechanizmy,
- reusable automation modules.

Slabšie prípady:

- veľmi krátky POSIX-only glue script, kde je Bash prirodzenejší,
- high-throughput data processing,
- veľká aplikačná codebase s komplikovaným doménovým modelom,
- dlhodobá service/daemon implementácia,
- knižnica určená primárne pre iné runtime prostredie.

Voľba nemá byť založená iba na OS. PowerShell môže byť výborný cross-platform shell, ak sú podporované modules, native tools a encoding semantics jasne definované.

## 3. Windows PowerShell verzus PowerShell

Dve významné línie:

```text
Windows PowerShell 5.1  → Windows-only, .NET Framework, executable powershell.exe
PowerShell 7+           → cross-platform, moderný .NET, executable pwsh
```

Rozdiely môžu zahŕňať:

- dostupné modules,
- .NET API,
- remoting transport,
- default text encoding,
- native argument passing,
- platform-specific providers,
- parallel execution features,
- language a cmdlet enhancements.

Deklaruj minimálnu verziu:

```powershell
#requires -Version 7.4
```

Ak skript vyžaduje module:

```powershell
#requires -Modules @{ ModuleName = 'Az.Accounts'; ModuleVersion = '3.0.0' }
```

`#requires` sa vyhodnocuje pred vykonaním script body a vytvára čitateľný dependency contract.

## 4. Execution lifecycle

Produkčný script má mať oddelené fázy:

```text
parameter binding
→ input validation
→ dependency/context validation
→ current-state observation
→ change plan
→ WhatIf/dry-run output
→ mutation
→ postcondition verification
→ structured result
→ process exit code
```

PowerShell uľahčuje object handling, ale nemá miešať planning a mutation bez jasnej hranice.

## 5. Object pipeline

```powershell
Get-Process |
    Where-Object CPU -gt 10 |
    Sort-Object CPU -Descending |
    Select-Object -First 5 Name, Id, CPU
```

Pipeline posiela process objects. `Where-Object` pristupuje k property `CPU`; neparsuje stĺpec z formátovanej tabuľky.

Inspect type a members:

```powershell
$process = Get-Process | Select-Object -First 1
$process.GetType().FullName
$process | Get-Member
```

Object semantics sú zachované dovtedy, kým ich explicitne neprevedieš na text, JSON, CSV alebo formatting instructions.

## 6. Formatting boundary

```powershell
Get-Process | Format-Table Name, Id
```

`Format-Table`, `Format-List`, `Format-Wide` a `Format-Custom` vytvárajú formatting objects pre host display.

Nesprávne:

```powershell
Get-Process |
    Format-Table Name, Id |
    ConvertTo-Json
```

Výsledkom nie sú process data, ale interné formatting records.

Správne:

```powershell
$data = Get-Process | Select-Object Name, Id
$data | ConvertTo-Json
$data | Format-Table
```

Formátuj až na prezentačnej hranici.

## 7. Command discovery

PowerShell používa `Verb-Noun` naming:

```powershell
Get-Command -Verb Get
Get-Command -Noun Service
Get-Verb
```

Help:

```powershell
Get-Help Get-Service -Full
Get-Help Get-Service -Examples
Get-Help about_Functions_Advanced
```

Command resolution môže nájsť:

- alias,
- function,
- cmdlet,
- external executable,
- script.

Over skutočný command:

```powershell
Get-Command curl -All
```

Na Windows PowerShell môže názov, ktorý očakávaš ako native executable, kolidovať s aliasom. Pri kritickom skripte používaj explicitný command alebo over `CommandType` a source.

## 8. Variables a types

```powershell
$name = 'api'
$count = 3
$enabled = $true
$items = @('a', 'b', 'c')
```

Explicitné typy:

```powershell
[int]$port = 8080
[datetime]$startedAt = [datetime]::UtcNow
[string[]]$services = 'api', 'worker'
```

PowerShell vykonáva type conversion. To môže byť užitočné aj nebezpečné.

```powershell
[int]$port = '8080'
```

uspeje, ale neznamená, že ľubovoľný string je validný port. Potrebná je range validation.

## 9. Automatic variables

Dôležité automatic variables:

- `$_` alebo `$PSItem` — current pipeline item,
- `$args` — unbound arguments v jednoduchých functions/scripts,
- `$PSBoundParameters` — skutočne bindnuté named parameters,
- `$MyInvocation` — invocation metadata,
- `$PSScriptRoot` — directory aktuálneho scriptu/module,
- `$PSCommandPath` — path aktuálneho scriptu,
- `$LASTEXITCODE` — exit code posledného native procesu,
- `$?` — úspech poslednej operácie z pohľadu PowerShellu,
- `$Error` — error history kolekcia,
- `$PSVersionTable` — runtime informácie.

Automatic variable je runtime state. Nespoliehaj na ňu po množstve ďalších commands, ak potrebuješ presnú hodnotu; zachyť ju okamžite.

## 10. `$null`, empty a missing

Porovnávaj `$null` na ľavej strane:

```powershell
if ($null -eq $value) {
    # missing/null
}
```

Pri kolekcii môže:

```powershell
$value -eq $null
```

vykonať element-wise filtering.

Rozlišuj:

- `$null`,
- `''`,
- whitespace-only string,
- `@()` empty array,
- property s hodnotou `$null`,
- property, ktorá neexistuje,
- command bez outputu.

Príklady:

```powershell
[string]::IsNullOrWhiteSpace($value)
$object.PSObject.Properties.Name -contains 'ExpectedProperty'
```

## 11. Scalar verzus collection output

PowerShell unrolluje kolekcie v pipeline a command result môže byť:

```text
0 objektov → $null
1 objekt   → scalar
N objektov → Object[] alebo iná collection
```

Vynútenie array:

```powershell
$results = @(Get-ChildItem -File)
```

Potom:

```powershell
$results.Count
```

má stabilnejšie semantics.

Ale pozor: niektoré objekty majú vlastnú `Count` property a niektoré command outputs používajú lazy/enumerable model. Typ contract treba poznať.

## 12. Pipeline enumeration

Keď function vypíše collection:

```powershell
function Get-Numbers {
    1, 2, 3
}
```

pipeline dostane tri objects.

Ak potrebuješ poslať collection ako jeden objekt:

```powershell
Write-Output -NoEnumerate (1, 2, 3)
```

alebo unary comma:

```powershell
,(1, 2, 3)
```

Používaj vedome. Väčšina cmdlet-like functions má podporovať bežné pipeline enumeration semantics.

## 13. Strings a interpolation

Single quotes:

```powershell
'$name'
```

neexpandujú premenné.

Double quotes:

```powershell
"service=$name"
"count=$($items.Count)"
```

expandujú variables a subexpressions.

Here-string:

```powershell
$template = @'
Literal $name
multiline content
'@
```

Expandable here-string:

```powershell
$template = @"
Service: $name
Count: $($items.Count)
"@
```

Na JSON/XML/YAML nepoužívaj ručné skladanie stringov, ak existuje serializer.

## 14. Paths

Používaj path cmdlets:

```powershell
$path = Join-Path $BaseDirectory 'config/app.json'
$leaf = Split-Path $path -Leaf
$parent = Split-Path $path -Parent
```

`Resolve-Path` vyžaduje existujúci path a môže pracovať s provider pathom:

```powershell
$resolved = Resolve-Path -LiteralPath $path
```

Pri user-provided path preferuj `-LiteralPath`, aby wildcard characters neboli interpretované.

```powershell
Get-Item -LiteralPath $path
Remove-Item -LiteralPath $path
```

`-Path` podporuje wildcard semantics; `-LiteralPath` nie.

## 15. Provider model

PowerShell providers vystavujú rôzne stores cez path-like interface:

```powershell
Get-PSProvider
Get-PSDrive
Get-ChildItem Env:
Get-ChildItem Cert:
Get-ChildItem HKLM:\Software
```

Rovnaký cmdlet verb môže fungovať nad filesystemom, registry alebo certificates, ale provider semantics nie sú identické.

Napríklad:

- properties a item types sa líšia,
- transakčné a permission semantics sa líšia,
- provider nemusí podporovať všetky parameters,
- cross-platform dostupnosť sa líši.

## 16. Functions

```powershell
function Get-ServiceHealth {
    param(
        [string]$Name
    )

    [pscustomobject]@{
        Name      = $Name
        Healthy   = $true
        CheckedAt = [datetime]::UtcNow
    }
}
```

Function output tvorí každý object poslaný do success output streamu. Explicitný `return` nie je potrebný na bežný output a nefunguje ako v jazykoch, kde je len jedna návratová hodnota.

## 17. Advanced functions

```powershell
function Get-ServiceHealth {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipelineByPropertyName)]
        [Alias('ServiceName')]
        [ValidateNotNullOrEmpty()]
        [string]$Name,

        [ValidateRange(1, 300)]
        [int]$TimeoutSeconds = 10
    )

    process {
        [pscustomobject]@{
            Name           = $Name
            Healthy        = $true
            CheckedAt      = [datetime]::UtcNow
            TimeoutSeconds = $TimeoutSeconds
        }
    }
}
```

`[CmdletBinding()]` poskytuje advanced-function semantics vrátane common parameters:

- `-Verbose`,
- `-Debug`,
- `-ErrorAction`,
- `-WarningAction`,
- `-InformationAction`,
- `-OutVariable`,
- podľa implementácie `-WhatIf` a `-Confirm`.

## 18. Begin, process a end

Pipeline-aware function:

```powershell
function Measure-Item {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline)]
        [object]$InputObject
    )

    begin {
        $count = 0
    }

    process {
        $count++
        # spracovanie jedného pipeline inputu
    }

    end {
        [pscustomobject]@{ Count = $count }
    }
}
```

- `begin` — inicializácia raz,
- `process` — pre každý pipeline input,
- `end` — finalizácia raz.

Bez `process` nemusí function spracovať pipeline input spôsobom, ktorý používateľ očakáva.

## 19. Parameter binding

PowerShell môže bindovať:

- named parameter,
- positional parameter,
- pipeline by value,
- pipeline by property name,
- remaining arguments.

Parameter binding môže vykonať type conversion pred function body.

Pri nejasnosti:

```powershell
Trace-Command -Name ParameterBinding -PSHost -Expression {
    'api' | Get-ServiceHealth
}
```

Použi tracing diagnosticky, pretože output je rozsiahly.

## 20. Parameter validation

```powershell
[ValidateSet('dev', 'test', 'prod')]
[string]$Environment

[ValidateRange(1, 65535)]
[int]$Port

[ValidatePattern('^[a-z][a-z0-9-]+$')]
[string]$ServiceName

[ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
[string]$ConfigPath
```

Nuansy:

- validation exception vznikne počas binding-u,
- `ValidateScript` môže mať side effects, ak je zle navrhnutý,
- existence check nevylučuje neskorší race,
- environment-dependent validation môže znižovať testovateľnosť.

Syntax a jednoduché constraints validuj atribútmi; zložité runtime preconditions validuj explicitne v body.

## 21. Splatting

Named parameters:

```powershell
$params = @{
    LiteralPath = $Path
    Encoding    = 'utf8'
    NoNewline   = $true
}

Set-Content @params -Value $content
```

Positional argument splatting:

```powershell
$arguments = @('status', '--porcelain=v1')
& git @arguments
```

Splatting zachová PowerShell parameter/argument boundaries lepšie než ručné skladanie command stringu.

Nikdy nepoužívaj `Invoke-Expression` na vykonanie command stringu z neovereného vstupu.

## 22. Output streams

PowerShell má viac streams:

```text
1 Success
2 Error
3 Warning
4 Verbose
5 Debug
6 Information
```

Plus progress display, ktorý má osobitné správanie.

Použitie:

```powershell
Write-Output $result
Write-Error 'Operation failed'
Write-Warning 'Using fallback'
Write-Verbose 'Detailed diagnostic'
Write-Debug 'Internal state'
Write-Information 'Lifecycle event'
Write-Progress -Activity 'Processing' -PercentComplete 50
```

Success output má byť dátový contract. Neodchytené expressions a command outputs sa doň pridávajú automaticky.

## 23. Output pollution

Problematické:

```powershell
function Get-Result {
    'Starting operation'
    New-Item -ItemType Directory -Path $Path
    [pscustomobject]@{ Status = 'ok' }
}
```

Function môže vrátiť:

- string,
- DirectoryInfo z `New-Item`,
- result object.

Správne:

```powershell
function Get-Result {
    [CmdletBinding()]
    param([string]$Path)

    Write-Verbose 'Starting operation'
    $null = New-Item -ItemType Directory -Path $Path -Force

    [pscustomobject]@{
        Status = 'ok'
        Path   = $Path
    }
}
```

Použi `$null =`, `[void]` alebo `Out-Null` na zámerné potlačenie success outputu. `$null =` je často efektívnejšie než pipeline do `Out-Null`.

## 24. Host display verzus automation output

`Write-Host` zapisuje do Information streamu s host-oriented semantics v modernom PowerShelli. Je vhodný pre explicitný UI/display, ale nie ako jediný návratový contract composable function.

Library function má vracať objects. Top-level interactive script môže tieto objects formátovať alebo zobrazovať.

## 25. Error model

PowerShell rozlišuje:

### Terminating error

Zastaví current statement/pipeline scope a vstúpi do `catch`.

### Non-terminating error

Vytvorí error record, ale command môže pokračovať s ďalšími inputs.

Príklad:

```powershell
try {
    Get-Item -LiteralPath $Path -ErrorAction Stop
}
catch [System.Management.Automation.ItemNotFoundException] {
    throw "Required path does not exist: $Path"
}
```

Bez `-ErrorAction Stop` môže cmdlet vytvoriť non-terminating error a `catch` sa nespustí.

## 26. ErrorAction a preference

```powershell
$ErrorActionPreference = 'Stop'
```

ovplyvňuje commands, ktoré rešpektujú PowerShell error-action semantics.

Lokálne:

```powershell
Get-Item -LiteralPath $Path -ErrorAction Stop
```

Preferované je explicitne zvoliť správanie na hranici, kde error musí zastaviť transakciu.

Niektoré cmdlets zámerne produkujú non-terminating errors pre jednotlivé pipeline items. Batch workflow musí definovať:

- fail-fast,
- continue and report,
- retry,
- dead-letter output,
- partial-success result.

## 27. ErrorRecord

V `catch` je `$_` `ErrorRecord`.

```powershell
catch {
    Write-Error (
        'Message={0}; Category={1}; Target={2}; Position={3}' -f
        $_.Exception.Message,
        $_.CategoryInfo.Category,
        $_.TargetObject,
        $_.InvocationInfo.PositionMessage
    )
    throw
}
```

Dôležité časti:

- `Exception`,
- `CategoryInfo`,
- `FullyQualifiedErrorId`,
- `TargetObject`,
- `InvocationInfo`,
- `ScriptStackTrace`.

Error log nemá automaticky vypisovať sensitive command arguments alebo objects.

## 28. `throw`, `Write-Error` a rethrow

```powershell
throw 'Fatal failure'
```

vytvorí terminating error.

```powershell
Write-Error 'Failure'
```

je štandardne non-terminating v mnohých contexts, pokiaľ preference/action neurčí inak.

V `catch`:

```powershell
throw
```

zachová pôvodný error context lepšie než vytvorenie úplne novej generic exception.

Ak pridávaš context, zachovaj inner exception:

```powershell
catch {
    throw [System.InvalidOperationException]::new(
        "Unable to update service '$Name'",
        $_.Exception
    )
}
```

## 29. `trap` verzus try/catch/finally

PowerShell podporuje `trap`, ale pre modernú štruktúrovanú automatizáciu je často čitateľnejšie:

```powershell
try {
    # operation
}
catch {
    # error handling
}
finally {
    # cleanup
}
```

`finally` sa vykoná pri úspechu aj chybe v rámci podporovaného flow, ale process termination alebo hard crash môže cleanup znemožniť.

Cleanup má byť idempotentný a nesmie zakryť primárny error.

## 30. Strict mode

```powershell
Set-StrictMode -Version Latest
```

pomáha odhaliť napríklad:

- čítanie nenastavenej premennej,
- neexistujúcu property v niektorých contexts,
- neplatné function call patterns.

Strict mode nie je úplný static type system ani náhrada tests.

Library/module má byť otestovaný s deklarovaným strict mode. Zapnutie globálne v caller session môže ovplyvniť third-party code, preto scope a compatibility treba posúdiť.

## 31. Native commands

Native executable:

```powershell
& git status --porcelain=v1
```

PowerShell spustí process a jeho stdout/stderr spracuje podľa runtime a redirection contextu.

Dôležité sú dve vrstvy:

```text
PowerShell invocation success
native process exit code
```

Kontrola:

```powershell
& git status --porcelain=v1
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "git status failed with exit code $exitCode"
}
```

`$LASTEXITCODE` zachyť okamžite po native command-e.

## 32. `$?` verzus `$LASTEXITCODE`

- `$?` — Boolean úspech poslednej PowerShell operation,
- `$LASTEXITCODE` — integer exit code posledného native executable alebo scriptu, ktorý ho nastaví podľa runtime semantics.

Pre presný native contract používaj `$LASTEXITCODE`.

Nespoliehaj na output text ako jediný dôkaz úspechu.

## 33. Native argument passing

Argument passing sa historicky líšil medzi Windows PowerShell a PowerShell 7, najmä pri quotes, empty strings a Windows executable parsing.

Použi argument array:

```powershell
$args = @(
    '--header'
    "Authorization: Bearer $Token"
    '--connect-timeout'
    '5'
    $Uri
)

& curl @args
```

Nezostavuj jeden command string:

```powershell
$command = "curl --header ..."
Invoke-Expression $command
```

`Invoke-Expression` vykoná ďalšie parsing kolo a vytvára injection boundary.

Pri kritickej cross-version kompatibilite otestuj skutočný argument vector na podporovaných platformách. PowerShell 7 má preference `$PSNativeCommandArgumentPassing`, ktorej dostupnosť a modes závisia od verzie.

## 34. Native stderr a PowerShell errors

Native stderr nie je automaticky to isté ako PowerShell non-terminating error v každej verzii a konfigurácii.

PowerShell 7 poskytuje preference súvisiace s native error handlingom, napríklad `$PSNativeCommandUseErrorActionPreference` v podporovaných verziách.

Skript má aj tak definovať explicitný wrapper:

```powershell
function Invoke-NativeCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,

        [string[]]$ArgumentList = @(),

        [int[]]$SuccessExitCode = @(0)
    )

    & $FilePath @ArgumentList
    $exitCode = $LASTEXITCODE

    if ($SuccessExitCode -notcontains $exitCode) {
        throw "Native command '$FilePath' failed with exit code $exitCode"
    }
}
```

Niektoré tools používajú viac success-like exit codes; wrapper musí poznať ich contract.

## 35. Capturing native output

```powershell
$output = & git status --porcelain=v1
$exitCode = $LASTEXITCODE
```

Output môže byť string alebo array of strings podľa počtu lines.

Vynútenie array:

```powershell
$lines = @(& git status --porcelain=v1)
```

Pri binary output alebo presnom byte stream-e použi .NET process APIs alebo file redirection, nie line-oriented PowerShell string pipeline.

## 36. `Start-Process`

`Start-Process` je vhodný pre process lifecycle, credentials/window options a file redirection, ale štandardne nevracia stdout content.

```powershell
$process = Start-Process \
    -FilePath 'tool' \
    -ArgumentList @('run') \
    -PassThru \
    -Wait

if ($process.ExitCode -ne 0) {
    throw "tool failed: $($process.ExitCode)"
}
```

Na jednoduché composable native invocation je call operator `&` často prirodzenejší. Voľba závisí od potreby streamingu, timeoutu, signal/process-tree kontroly a platformy.

## 37. Timeouts a cancellation

Cmdlet môže podporovať vlastný timeout parameter. Pre .NET async API používaj `CancellationToken`, ak je dostupný.

Pri process timeout-e:

```powershell
$process = Start-Process -FilePath $FilePath -ArgumentList $Arguments -PassThru

if (-not $process.WaitForExit($TimeoutMilliseconds)) {
    try {
        $process.Kill($true)
    }
    finally {
        $process.Dispose()
    }
    throw "Process timed out after $TimeoutMilliseconds ms"
}

$exitCode = $process.ExitCode
$process.Dispose()
```

`Kill($true)` process-tree support závisí od .NET/platformy. Termination môže zanechať partial side effects; timeout policy musí mať recovery model.

## 38. Structured objects

```powershell
$result = [pscustomobject]@{
    PSTypeName  = 'KnowledgeHub.DeploymentResult'
    Service     = 'api'
    Environment = 'prod'
    Version     = '1.4.2'
    Healthy     = $true
    CheckedAt   = [datetime]::UtcNow
}
```

`PSTypeName` môže podporiť custom formatting a type-oriented processing.

Object contract má definovať:

- property names,
- types,
- nullability,
- units a timezone,
- success/failure semantics.

## 39. JSON

```powershell
$json = $result | ConvertTo-Json -Depth 10 -Compress
$parsed = $json | ConvertFrom-Json
```

Pozor na:

- `-Depth`,
- enum/datetime serialization,
- property ordering ako ne-semantic detail,
- duplicate JSON keys v externom inpute,
- large payload memory usage,
- numeric precision a type conversions,
- `null` semantics.

Pre schema-critical API validuj JSON schema alebo explicitný object contract.

## 40. CSV

```powershell
$result | Export-Csv -LiteralPath $Path -NoTypeInformation -Encoding utf8
$data = Import-Csv -LiteralPath $Path -Encoding utf8
```

CSV import vracia string properties, pokiaľ ich explicitne nekonvertuješ.

Delimiter, quoting, culture a encoding musia byť definované pri cross-system exchange.

## 41. XML

PowerShell vie pracovať s XML cez .NET:

```powershell
[xml]$xml = Get-Content -LiteralPath $Path -Raw -Encoding utf8
$xml.DocumentElement.Name
```

Pri untrusted XML inpute posúď parser security settings, external entity behavior a resource limits. Jednoduchý `[xml]` cast nemusí byť vhodný pre všetky threat models.

## 42. Encoding

Default encoding sa líši medzi Windows PowerShell 5.1 a PowerShell 7+ aj medzi cmdlets.

Použi explicitne:

```powershell
Set-Content -LiteralPath $Path -Value $Content -Encoding utf8
Get-Content -LiteralPath $Path -Raw -Encoding utf8
```

Ale aj hodnota `utf8` mala historicky rozdielne BOM semantics medzi verziami. Pri interoperabilite definuj:

- UTF-8 s/bez BOM,
- newline policy,
- serializer,
- consumer expectations.

Pre bytes:

```powershell
[byte[]]$bytes = [System.IO.File]::ReadAllBytes($Path)
```

Nespracúvaj binary data cez text cmdlets.

## 43. Atomic file update

```powershell
$targetDirectory = Split-Path -Parent $Target
$tempPath = Join-Path $targetDirectory ('.config.tmp.{0}' -f [guid]::NewGuid())

try {
    [System.IO.File]::WriteAllText(
        $tempPath,
        $Content,
        [System.Text.UTF8Encoding]::new($false)
    )

    Test-Configuration -LiteralPath $tempPath

    Move-Item -LiteralPath $tempPath -Destination $Target -Force
}
finally {
    if (Test-Path -LiteralPath $tempPath) {
        Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
    }
}
```

Over:

- same-filesystem rename semantics,
- permissions/ACL ownership,
- existing-target replace behavior na platforme,
- antivirus/file-lock interference na Windows,
- crash durability požiadavky.

Pre kritické replace semantics môže byť vhodnejšie konkrétne .NET file API než všeobecný `Move-Item`.

## 44. Scope

PowerShell scopes:

- global,
- script,
- local,
- private,
- module/session state,
- child scopes.

Explicitný scope:

```powershell
$script:Configuration = @{}
$global:DebugMode = $false
```

Globálny mutable state sťažuje tests a concurrency. Preferuj parameters, returned objects a module-private state s jasným lifecycle.

Functions typicky vytvárajú child scope, ale mutácie reference-type objects môžu ovplyvniť zdieľaný object.

## 45. Dot-sourcing

```powershell
. ./Functions.ps1
```

Dot-sourcing vykoná script v aktuálnom scope a importuje variables/functions.

Riziká:

- name collisions,
- zmena preferences,
- zmena working directory alebo state,
- skrytá dependency.

Pre reusable automation preferuj module s explicitnými exports.

## 46. Modules

Štruktúra:

```text
MyAutomation/
├── MyAutomation.psd1
├── MyAutomation.psm1
├── Public/
├── Private/
└── Tests/
```

Manifest môže definovať:

- module version,
- compatible PowerShell editions,
- required modules,
- exported functions/cmdlets/variables/aliases,
- metadata a private data.

Explicitne exportuj public API:

```powershell
Export-ModuleMember -Function Get-ServiceHealth, Invoke-Deployment
```

Module versioning je contract. Breaking parameter/output changes musia mať compatibility policy.

## 47. Module auto-loading a dependency drift

PowerShell môže module auto-loadnúť pri command discovery. To zlepšuje UX, ale môže zakryť dependency source/version.

Diagnostika:

```powershell
Get-Command Invoke-Deployment | Format-List Name, Source, Version, ModuleName
Get-Module -ListAvailable MyAutomation
```

CI má pinovať alebo kontrolovať module versions a registries. Mutable machine-wide module state môže znižovať reprodukovateľnosť runnera.

## 48. Idempotencia

Slabé:

```powershell
Add-Content -LiteralPath $Profile -Value '$env:APP_ENV = ''prod'''
```

Opakované spustenie pridáva duplicate state.

Lepšie:

```powershell
$line = '$env:APP_ENV = ''prod'''
$current = if (Test-Path -LiteralPath $Profile) {
    Get-Content -LiteralPath $Profile -Encoding utf8
}
else {
    @()
}

if ($current -notcontains $line) {
    Add-Content -LiteralPath $Profile -Value $line -Encoding utf8
}
```

Ešte lepšie je spravovať vlastnený configuration fragment alebo použiť desired-state cmdlet/API.

Idempotentná function má vrátiť structured result:

```powershell
[pscustomobject]@{
    Changed = $false
    Target  = $Target
    Action  = 'None'
}
```

## 49. `ShouldProcess`, `-WhatIf` a `-Confirm`

```powershell
function Remove-StaleArtifact {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if ($PSCmdlet.ShouldProcess($Path, 'Remove stale artifact')) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}
```

`ShouldProcess` poskytuje:

- `-WhatIf`,
- `-Confirm`,
- common preference integration.

Limity:

- iba code vo vnútri `ShouldProcess` je chránený,
- nested command môže robiť ďalšie side effects,
- external executable nevie automaticky o `WhatIf`,
- planning musí byť oddelený od mutation.

Dobrá message identifikuje target a action, nie iba generic text.

## 50. Plan, apply a verify

```powershell
$currentState = Get-CurrentState -Environment $Environment
$desiredState = Get-DesiredState -Environment $Environment
$plan = Compare-State -Current $currentState -Desired $desiredState
```

Plan objects:

```powershell
$plan | ForEach-Object {
    [pscustomobject]@{
        Target  = $_.Target
        Action  = $_.Action
        Current = $_.Current
        Desired = $_.Desired
    }
}
```

Apply:

```powershell
foreach ($item in $plan) {
    if ($PSCmdlet.ShouldProcess($item.Target, $item.Action)) {
        Invoke-PlanItem -PlanItem $item
    }
}
```

Verify:

```powershell
Test-Postcondition -DesiredState $desiredState
```

`-WhatIf` má stále vykonať read-only validation a vytvoriť presný plan.

## 51. Credentials a secrets

```powershell
$credential = Get-Credential
```

`PSCredential` a `SecureString` sú API abstractions, nie univerzálne bezpečný secret store.

Preferuj:

- managed/workload identity,
- OS alebo cloud secret manager,
- krátkodobé tokens,
- certificate-based identity,
- credential provider module,
- explicitnú redaction policy.

Nevypisuj:

- credential objects,
- tokens,
- secure-string conversions,
- authentication headers,
- celé environmenty.

`ConvertTo-SecureString -AsPlainText` nevytvára bezpečný storage lifecycle; iba vytvorí object z plaintext inputu.

## 52. Environment variables

```powershell
$env:APP_ENV = 'prod'
$token = $env:API_TOKEN
```

Child process zdedí environment snapshot.

Environment secret môže byť viditeľný v process/debug/CI kontexte podľa platformy. Používaj ho iba podľa threat modelu.

Rozlišuj process, user a machine environment na Windows; zápis do persistent environment store je samostatná mutation a nemusí okamžite meniť už bežiace processes.

## 53. Remoting model

PowerShell Remoting vykonáva script block v remote session:

```powershell
$session = New-PSSession -ComputerName 'server01'
try {
    Invoke-Command -Session $session -ScriptBlock {
        Get-Service -Name 'sshd'
    }
}
finally {
    Remove-PSSession -Session $session
}
```

Transport môže používať WSMan alebo SSH podľa platformy a configuration.

Remoting pridáva:

- authentication a authorization boundary,
- network timeout/failure,
- session lifecycle,
- serialization,
- remote module/version context,
- double-hop/credential delegation problémy.

## 54. Serialization v remoting-u

Remote object sa často vráti ako deserialized representation:

```text
Deserialized.System.ServiceProcess.ServiceController
```

Properties môžu zostať, methods nie.

```powershell
$result = Invoke-Command -ComputerName server01 -ScriptBlock {
    Get-Service -Name sshd
}

$result.PSObject.TypeNames
```

Operáciu vyžadujúcu live object method vykonaj na remote strane, nie až po serializácii.

Type depth a custom serialization rules môžu ovplyvniť výsledok.

## 55. `$using:` a remote/parallel capture

```powershell
$name = 'sshd'
Invoke-Command -ComputerName server01 -ScriptBlock {
    Get-Service -Name $using:name
}
```

`$using:` prenesie hodnotu do remote/parallel contextu podľa mechanizmu. Neznamená shared mutable reference medzi processes/runspaces.

Veľké alebo secret objects môžu byť serializované a kopírované; minimalizuj prenášaný scope.

## 56. Jobs

Background job:

```powershell
$job = Start-Job -ScriptBlock {
    Get-Process
}

try {
    Wait-Job -Job $job | Out-Null
    $result = Receive-Job -Job $job -ErrorAction Stop
}
finally {
    Remove-Job -Job $job -Force
}
```

Job môže bežať v inom process/session context-e a output je serializovaný.

Definuj:

- timeout,
- cancellation,
- error collection,
- cleanup,
- output ordering.

## 57. Parallel runspaces

PowerShell 7:

```powershell
$results = $items | ForEach-Object -Parallel {
    Invoke-Work -InputObject $_
} -ThrottleLimit 5
```

Riziká:

- oddelený runspace state,
- modules/functions nemusia byť dostupné podľa očakávania,
- `$using:` values sa prenášajú s obmedzeniami,
- output order nemusí zodpovedať input order,
- spoločné files/APIs môžu konfliktovať,
- rate limits,
- memory overhead,
- secret duplication.

Parallelism nemá byť default. Najprv zmeraj workload a definuj concurrency-safe side effects.

## 58. Thread-safe collections a shared state

Ak viac runspaces používa shared object, musí byť thread-safe alebo synchronizovaný.

Bežná hashtable nie je automaticky bezpečná pre všetky compound operations.

Preferuj:

- independent work items,
- immutable input,
- concurrent collections,
- central result aggregation,
- external idempotency/locking.

## 59. HTTP automation

```powershell
$response = Invoke-RestMethod \
    -Uri $Uri \
    -Method Get \
    -TimeoutSec 30 \
    -ErrorAction Stop
```

Definuj:

- authentication,
- connection/overall timeout podľa cmdlet capabilities,
- retryable statuses,
- idempotency,
- response schema,
- pagination,
- rate limits,
- TLS trust.

`Invoke-RestMethod` môže automaticky deserializovať JSON; over actual type a missing/null properties.

Neimplementuj slepý retry `POST` po nejasnom timeout-e bez idempotency key alebo operation-status lookupu.

## 60. Registry a Windows-specific automation

```powershell
Get-ItemProperty -LiteralPath 'HKLM:\Software\MyApp'
```

Registry provider umožňuje cmdlet-like operations, ale:

- 32/64-bit registry views sa môžu líšiť,
- elevation a ACL sú významné,
- service/account context môže mať odlišný hive,
- transaction/rollback treba navrhnúť explicitne.

Cross-platform module nemá predpokladať dostupnosť registry provideru.

## 61. Services

```powershell
$service = Get-Service -Name 'MyService' -ErrorAction Stop
```

Service object stav je momentálny snapshot. Po mutation treba čakať a verify-nuť desired state:

```powershell
Start-Service -Name 'MyService'
(Get-Service -Name 'MyService').WaitForStatus(
    [System.ServiceProcess.ServiceControllerStatus]::Running,
    [timespan]::FromSeconds(30)
)
```

API a behavior sa môžu líšiť medzi Windows a Unix service managers. Na Linuxe môže byť vhodnejší `systemctl` wrapper alebo platform-specific module.

## 62. Logging a observability

Library function má používať:

- `Write-Verbose` pre detail,
- `Write-Debug` pre interné state,
- `Write-Warning` pre recoverable problém,
- `Write-Information` pre lifecycle event,
- structured success object pre výsledok.

Top-level log object:

```powershell
[pscustomobject]@{
    Timestamp   = [datetime]::UtcNow
    Level       = 'Information'
    OperationId = $OperationId
    Phase       = 'Apply'
    Target      = $Target
    Message     = 'Configuration updated'
} | ConvertTo-Json -Compress
```

Structured log má mať stabilnú schema a redaction.

## 63. Process exit code

Top-level script pre CI/scheduler má explicitne mapovať výsledok:

```powershell
try {
    $result = Invoke-Main @PSBoundParameters
    $result
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
```

V reusable function/module nepoužívaj `exit`, pretože ukončí hosting process/session. Throwni error a nechaj top-level boundary rozhodnúť o process exit code.

## 64. Testing s Pester

```powershell
Describe 'Get-ServiceHealth' {
    It 'returns a typed healthy result' {
        $result = Get-ServiceHealth -Name 'api'

        $result.Name | Should -Be 'api'
        $result.Healthy | Should -BeTrue
        $result.CheckedAt.Kind | Should -Be 'Utc'
    }
}
```

Testuj:

- parameter validation,
- zero/one/many output shape,
- output pollution,
- terminating aj non-terminating errors,
- native exit codes,
- `-WhatIf` a `ShouldProcess`,
- idempotent second run,
- partial failure,
- cleanup,
- serialization/remoting shape,
- path wildcard safety,
- encoding,
- cross-platform/module compatibility,
- concurrency limits.

Mocks nesmú úplne odstrániť integration contract s native tool/API; doplň integration tests.

## 65. Static analysis a formatting

```powershell
Invoke-ScriptAnalyzer -Path . -Recurse
Invoke-Formatter -ScriptDefinition (Get-Content -LiteralPath script.ps1 -Raw)
```

PSScriptAnalyzer môže kontrolovať:

- naming,
- aliases v script-e,
- unapproved verbs,
- security-sensitive patterns,
- compatibility rules,
- style.

Static analysis nenahrádza runtime, remoting a native-process tests.

## 66. Documentation-based help

Advanced function môže obsahovať comment-based help:

```powershell
function Get-ServiceHealth {
    <#
    .SYNOPSIS
    Returns service health information.

    .PARAMETER Name
    Service name.

    .OUTPUTS
    KnowledgeHub.ServiceHealth
    #>
    [CmdletBinding()]
    param(...)
}
```

Help je súčasť public API contractu spolu s examples, output type a error semantics.

## 67. Produkčný script skeleton

```powershell
#requires -Version 7.4

[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateSet('dev', 'test', 'prod')]
    [string]$Environment,

    [ValidateRange(1, 300)]
    [int]$TimeoutSeconds = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-CurrentState {
    [CmdletBinding()]
    param([string]$Environment)

    # Return structured current-state object.
}

function Get-DesiredState {
    [CmdletBinding()]
    param([string]$Environment)

    # Return structured desired-state object.
}

function Get-ChangePlan {
    [CmdletBinding()]
    param(
        [object]$CurrentState,
        [object]$DesiredState
    )

    # Return plan item objects without mutations.
}

function Invoke-PlanItem {
    [CmdletBinding()]
    param([object]$PlanItem)

    # Apply one bounded idempotent mutation.
}

function Test-Postcondition {
    [CmdletBinding()]
    param([object]$DesiredState)

    # Throw on verification failure.
}

function Invoke-Main {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string]$Environment,
        [int]$TimeoutSeconds
    )

    $currentState = Get-CurrentState -Environment $Environment
    $desiredState = Get-DesiredState -Environment $Environment
    $plan = @(Get-ChangePlan -CurrentState $currentState -DesiredState $desiredState)

    foreach ($item in $plan) {
        if ($PSCmdlet.ShouldProcess($item.Target, $item.Action)) {
            Invoke-PlanItem -PlanItem $item
        }
    }

    if (-not $WhatIfPreference) {
        Test-Postcondition -DesiredState $desiredState
    }

    [pscustomobject]@{
        PSTypeName  = 'KnowledgeHub.AutomationResult'
        Environment = $Environment
        Changed     = ($plan.Count -gt 0)
        PlanCount   = $plan.Count
        Verified    = -not $WhatIfPreference
        CompletedAt = [datetime]::UtcNow
    }
}

try {
    Invoke-Main \
        -Environment $Environment \
        -TimeoutSeconds $TimeoutSeconds \
        -WhatIf:$WhatIfPreference \
        -Confirm:$false

    exit 0
}
catch {
    Write-Error $_
    exit 1
}
```

Skeleton musí byť doplnený o konkrétny:

- timeout/retry model,
- credential provider,
- lock/concurrency policy,
- rollback alebo compensation,
- result schema,
- exit-code mapping.

## 68. Troubleshooting: function vrátila viac objektov

1. Zachyť output do array:

```powershell
$output = @(Invoke-Function)
$output | ForEach-Object { $_.GetType().FullName }
```

2. Hľadaj:

- string expressions,
- cmdlet output, ktorý nebol zachytený,
- `Write-Output`,
- external command output,
- nested function output.

3. Presuň logs do verbose/information streamu a potlač zámerne nepotrebný success output.

## 69. Troubleshooting: `catch` sa nespustil

1. Over, či error bol non-terminating.
2. Použi `-ErrorAction Stop` na konkrétnom cmdlet-e.
3. Skontroluj `$ErrorActionPreference` a scope.
4. Over, či ide o native process failure; ten môže vyžadovať `$LASTEXITCODE`.
5. Skontroluj, či error nebol zachytený vo vzdialenom job/runspace outpute.

## 70. Troubleshooting: funguje v 5.1, nie v 7+

Kontroluj:

- module edition compatibility,
- removed/changed .NET API,
- encoding a BOM,
- native argument passing,
- aliases a command resolution,
- Windows-only providers,
- WSMan verzus SSH remoting,
- type serialization,
- case sensitivity na filesysteme,
- path separators,
- output formatting.

Použi explicitnú test matrix, nie náhodné compatibility fixes.

## 71. Troubleshooting: native command zlyhal bez exception

```powershell
& tool @arguments
$exitCode = $LASTEXITCODE
```

Ak je exit code nenulový, PowerShell nemusí automaticky throw-nuť podľa verzie/preferences.

Wrapper musí:

- zachytiť exit code okamžite,
- vedieť povolené success codes,
- zachovať stdout/stderr podľa contractu,
- pridať context bez leaknutia secrets,
- throw-nuť alebo vrátiť structured failure podľa API.

## 72. Troubleshooting: `WhatIf` aj tak niečo zmenilo

1. Nájdite všetky mutation calls.
2. Over, že sú pod `ShouldProcess`.
3. Skontroluj nested functions a native commands.
4. Oddel state observation od mutation.
5. Testuj `-WhatIf` s mockmi a integration sandboxom.
6. V structured result označ, že verify neprebehol ako real apply.

## 73. Anti-patterny

### `Format-Table` v dátovej pipeline

Ničí object contract a vytvára formatting records.

### `Write-Host` ako jediný function result

Znižuje composability a machine consumption.

### Globálne mutable variables

Komplikujú tests, modules, remoting a parallelism.

### `Invoke-Expression` pre command arguments

Vytvára injection a ďalšie parsing kolo.

### `$ErrorActionPreference = 'SilentlyContinue'` pre celý script

Zakryje failures a môže vytvoriť false success.

### Ignorovanie `$LASTEXITCODE`

Native process môže zlyhať, hoci script pokračuje.

### `-WhatIf` iba na top-level function bez pokrytia mutations

Vytvára falošný safety contract.

### Secret v verbose/debug outpute

Diagnostic streams môžu skončiť v CI logs alebo transcript-e.

### Remote object považovaný za live local object

Deserialized object nemusí mať methods ani plné type semantics.

## 74. Časté omyly

### „PowerShell pipeline je vždy objektová“

Cmdlets typicky posielajú objects, ale native commands posielajú text/bytes podľa host/runtime a formatting/serialization môže object semantics zmeniť.

### „Každá chyba vstúpi do catch“

Nie. Non-terminating error potrebuje `-ErrorAction Stop` alebo príslušnú preference.

### „Function vracia iba posledný expression“

Vracia všetok success output, ktorý počas vykonania vytvorí.

### „`$?` je presný native exit code“

Nie. Na integer contract používaj `$LASTEXITCODE`.

### „`-WhatIf` blokuje všetky side effects automaticky“

Iba správne implementované `ShouldProcess` paths.

### „SecureString je secret vault“

Nie. Je to in-memory/API representation s platform-dependent protection semantics.

### „Monorepo module alebo machine-wide module version je vždy tá správna“

Command discovery môže načítať inú dostupnú version; dependency pinning a test environment musia byť explicitné.

## 75. Kontrolné otázky

1. Aký je rozdiel medzi object pipeline a formatting pipeline?
2. Prečo command result môže byť `$null`, scalar alebo array?
3. Ako sa líši success output od verbose, information a error streamu?
4. Aký je rozdiel medzi terminating a non-terminating error?
5. Kedy treba použiť `-ErrorAction Stop`?
6. Prečo `$LASTEXITCODE` treba zachytiť okamžite po native command-e?
7. Aké riziko vytvára `Invoke-Expression` pri command stringu?
8. Ako `ShouldProcess` podporuje `-WhatIf` a kde sú jeho hranice?
9. Prečo remote object nemusí mať methods pôvodného live objektu?
10. Ako odlíšiš repository/module API od top-level process exit boundary?
11. Ako navrhneš idempotentný plan/apply/verify workflow?
12. Ktoré rozdiely medzi Windows PowerShell 5.1 a PowerShell 7 treba testovať?

## Glossary impact

Relevantné pojmy: object pipeline, pipeline enumeration, cmdlet, advanced function, parameter binding, success stream, error stream, terminating error, non-terminating error, ErrorRecord, common parameters, PowerShell provider, splatting, native command, `$LASTEXITCODE`, `ShouldProcess`, runspace, remoting, deserialized object, module manifest, Pester a PSScriptAnalyzer.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Bash automation](bash-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Python for automation →](python-for-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
