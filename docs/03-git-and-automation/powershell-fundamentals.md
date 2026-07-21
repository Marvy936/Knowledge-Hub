# PowerShell fundamentals

PowerShell je shell a automatizačný jazyk postavený na .NET object modeli. Jeho hlavný rozdiel oproti tradičným textovým shellom je, že pipeline prenáša objekty s vlastnosťami a metódami, nie iba riadky textu. To umožňuje stabilnejšie filtrovanie a transformáciu dát, ale iba vtedy, keď skript nezničí object semantics predčasným formátovaním.

## 1. Kedy je PowerShell vhodný

PowerShell je vhodný najmä pre:

- Windows administráciu,
- cross-platform .NET automation,
- prácu s objektovými API a management vrstvami,
- Azure, Microsoft 365 a Active Directory tooling,
- CI/CD skripty na Windows aj Linux runneroch,
- transformáciu JSON, XML, CSV a structured command outputu,
- orchestration procesov, služieb, filesystému a registry.

Na jednoduchý POSIX shell glue môže byť Bash kratší. Na komplexný aplikačný model, väčšie knižnice alebo vysokovýkonné spracovanie môže byť vhodnejší Python alebo C#.

## 2. Object pipeline

```powershell
Get-Process |
    Where-Object CPU -gt 10 |
    Sort-Object CPU -Descending |
    Select-Object -First 5 Name, Id, CPU
```

Pipeline prenáša process objects. `Where-Object` číta property `CPU`; nemusí parsovať stĺpec textovej tabuľky.

Kritický rozdiel:

```powershell
Get-Process | Format-Table Name, Id
```

`Format-Table` vytvára formatting instructions určené na display. Nemá byť uprostred dátovej pipeline.

Správne:

```powershell
$data = Get-Process | Select-Object Name, Id
$data | ConvertTo-Json
$data | Format-Table
```

## 3. Cmdlet naming a discoverability

PowerShell používa convention `Verb-Noun`:

```powershell
Get-Command -Verb Get
Get-Command -Noun Service
Get-Help Get-Service -Full
Get-Member -InputObject (Get-Service | Select-Object -First 1)
```

Používaj schválené verbs pre vlastné functions:

```powershell
Get-Verb
```

Konzistentné názvy zlepšujú discoverability a tooling.

## 4. Premenné a typy

```powershell
$name = 'api'
$count = 3
$enabled = $true
$items = @('a', 'b', 'c')
```

Explicitný typ môže validovať kontrakt:

```powershell
[int]$port = 8080
[datetime]$startedAt = Get-Date
[string[]]$services = 'api', 'worker'
```

PowerShell vykonáva type conversion. Pri hraniciach skriptu je vhodné validovať, čo presne sa akceptuje.

## 5. Arrays a enumerácia

PowerShell často automaticky enumeruje kolekcie v pipeline.

```powershell
1..5 | ForEach-Object { $_ * 2 }
```

Unary comma vytvorí single-element array obsahujúci objekt:

```powershell
,$object
```

Vynútenie array výsledku:

```powershell
$results = @(Get-ChildItem -File)
```

Bez `@(...)` môže premenná obsahovať `$null`, scalar alebo array podľa počtu výsledkov. To môže meniť správanie `.Count` a downstream logiky.

## 6. `$null`

Porovnávaj s `$null` na ľavej strane:

```powershell
if ($null -eq $value) {
    # missing
}
```

Pri kolekcii môže `$value -eq $null` vykonať collection filtering namiesto scalar comparison.

Rozlišuj:

- `$null`,
- empty string `''`,
- whitespace string,
- empty array `@()`,
- missing property.

## 7. Strings a quoting

Single-quoted string neexpanduje premenné:

```powershell
'$name'
```

Double-quoted string expanduje:

```powershell
"service=$name"
"count=$($items.Count)"
```

Here-string:

```powershell
$json = @'
{
  "environment": "prod"
}
'@
```

Pri generovaní JSON alebo XML preferuj serializer pred ručným skladaním stringov.

## 8. Splatting

Splatting zlepšuje čitateľnosť a bezpečnú prácu s argumentmi:

```powershell
$params = @{
    Path        = 'output.json'
    Encoding    = 'utf8'
    NoNewline   = $true
}

Set-Content @params -Value $json
```

Pre native executable je potrebné chápať argument passing konkrétnej PowerShell verzie a platformy. Nepredpokladaj, že shell quoting funguje rovnako ako v Bash.

## 9. Functions a advanced functions

```powershell
function Get-ServiceHealth {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$Name,

        [ValidateRange(1, 300)]
        [int]$TimeoutSeconds = 10
    )

    [pscustomobject]@{
        Name      = $Name
        Healthy   = $true
        CheckedAt = Get-Date
        Timeout   = $TimeoutSeconds
    }
}
```

`[CmdletBinding()]` zapína common parameters ako `-Verbose`, `-Debug`, `-ErrorAction` a podporuje cmdlet-like správanie.

## 10. Parameter validation

Použiteľné atribúty:

```powershell
[ValidateSet('dev', 'test', 'prod')]
[string]$Environment

[ValidatePattern('^[a-z][a-z0-9-]+$')]
[string]$ServiceName

[ValidateScript({ Test-Path $_ -PathType Leaf })]
[string]$ConfigPath
```

Validácia má prebehnúť čo najbližšie k vstupnej hranici. Runtime failure hlboko v skripte je ťažšie diagnostikovateľný.

## 11. Output contract

PowerShell posiela do success streamu každý neodchytený expression result.

Problematické:

```powershell
function Get-Result {
    'starting'
    [pscustomobject]@{ Status = 'ok' }
}
```

Function vráti dva objekty. Logovanie má ísť cez správny stream:

```powershell
Write-Verbose 'starting'
[pscustomobject]@{ Status = 'ok' }
```

Používaj:

- success output pre dátový kontrakt,
- `Write-Verbose` pre detail,
- `Write-Warning` pre varovanie,
- `Write-Error` pre error record,
- `Write-Information` pre informačný stream.

`Write-Host` je vhodný najmä pre explicitný host display, nie ako univerzálny dátový výstup.

## 12. Error model

PowerShell rozlišuje terminating a non-terminating errors.

```powershell
try {
    Get-Item -Path $path -ErrorAction Stop
}
catch [System.Management.Automation.ItemNotFoundException] {
    Write-Error "Missing path: $path"
    throw
}
finally {
    # cleanup
}
```

Bez `-ErrorAction Stop` nemusí `catch` zachytiť non-terminating error.

Globálny default v automation skripte:

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
```

Používaj vedome; niektoré cmdlets legitímne produkujú non-terminating errors pre časť inputu.

## 13. Native commands a exit codes

PowerShell error stream a native process exit code sú rozdielne mechanizmy.

```powershell
& git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE"
}
```

`$?` hovorí, či posledná operácia uspela z pohľadu PowerShellu. Pri native commands je pre presný kontrakt dôležitý `$LASTEXITCODE`.

V PowerShell 7 možno podľa potreby používať novšie native argument a error správanie, ale skript má deklarovať minimálnu verziu.

## 14. Pipeline error handling

```powershell
$results = Get-Content $Path |
    ForEach-Object {
        try {
            ConvertFrom-Json $_ -ErrorAction Stop
        }
        catch {
            Write-Error "Invalid JSON line: $_"
        }
    }
```

Definuj, či má chyba jednej položky:

- zastaviť celý batch,
- zaznamenať failure a pokračovať,
- vytvoriť dead-letter výstup,
- spustiť retry.

## 15. Structured objects

```powershell
$result = [pscustomobject]@{
    Service     = 'api'
    Environment = 'prod'
    Version     = '1.4.2'
    Healthy     = $true
    CheckedAt   = [datetime]::UtcNow
}
```

Custom objects sú stabilnejší automation contract než formátovaný text.

Export:

```powershell
$result | ConvertTo-Json -Depth 10
$result | Export-Csv -Path results.csv -NoTypeInformation
```

Pri JSON sleduj `-Depth`; príliš malá hodnota môže nested štruktúru skrátiť.

## 16. Providers

PowerShell používa provider abstraction:

```powershell
Get-PSDrive
Get-ChildItem Env:
Get-ChildItem Cert:
Get-ChildItem HKLM:\Software
```

Rovnaké cmdlet verbs môžu pracovať s filesystemom, registry, certificates alebo environmentom. Provider semantics sa však môžu líšiť; nejde o identické datasources.

## 17. Files a encoding

PowerShell verzie a platformy sa historicky líšili v default encodingu. V automatizácii používaj explicitný encoding:

```powershell
Set-Content -Path config.json -Value $json -Encoding utf8
Get-Content -Path config.json -Raw -Encoding utf8
```

`-Raw` vráti celý súbor ako jeden string namiesto array riadkov.

Pre atomic update:

```powershell
$temp = New-TemporaryFile
try {
    $content | Set-Content -Path $temp -Encoding utf8
    Test-Configuration -Path $temp
    Move-Item -Path $temp -Destination $Target -Force
}
finally {
    if (Test-Path $temp) {
        Remove-Item $temp -Force
    }
}
```

Over, či rename prebieha na rovnakom filesysteme a aké semantics má cieľová platforma.

## 18. Paths

Používaj path cmdlets:

```powershell
$path = Join-Path $BaseDirectory 'config/app.json'
$resolved = Resolve-Path $path
$leaf = Split-Path $path -Leaf
```

Neskladaj paths ručne cez platform-specific separator, ak skript má byť cross-platform.

## 19. Remoting

PowerShell Remoting používa sessions a serializáciu objektov.

```powershell
$session = New-PSSession -ComputerName server01
try {
    Invoke-Command -Session $session -ScriptBlock {
        Get-Service -Name sshd
    }
}
finally {
    Remove-PSSession $session
}
```

Remote object môže byť deserialized representation bez pôvodných methods. Nespoliehaj sa, že vzdialený objekt sa po prenose správa identicky ako lokálny live object.

## 20. Credentials a secrets

```powershell
$credential = Get-Credential
```

`SecureString` nie je univerzálne bezpečné úložisko a jeho vlastnosti sa líšia podľa platformy. Preferuj:

- secret manager,
- managed identity alebo workload identity,
- krátkodobé tokens,
- environment-specific credential provider,
- explicitné redaction pravidlá.

Nevypisuj credential objects ani tokeny cez verbose/debug logy.

## 21. Idempotencia a `ShouldProcess`

Advanced function môže podporovať `-WhatIf` a `-Confirm`:

```powershell
function Remove-StaleArtifact {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if ($PSCmdlet.ShouldProcess($Path, 'Remove stale artifact')) {
        Remove-Item -Path $Path -Recurse -Force
    }
}
```

`-WhatIf` nie je automaticky bezpečný pre external commands alebo vlastný kód mimo `ShouldProcess`. Všetky mutations musia byť pod kontrolou plánovacieho mechanizmu.

## 22. Parallelism

PowerShell 7 podporuje napríklad:

```powershell
$results = $items | ForEach-Object -Parallel {
    Invoke-Work -InputObject $_
} -ThrottleLimit 5
```

Paralelný script block má oddelený runspace. Stav, modules a variables sa neprenášajú automaticky ako shared memory.

Riziká:

- rate limits,
- thread-unsafe dependencies,
- output ordering,
- shared file writes,
- secret duplication,
- príliš vysoká concurrency.

## 23. Modules

Opakovateľné functions patria do modulu:

```text
MyAutomation/
├── MyAutomation.psd1
├── MyAutomation.psm1
├── Public/
├── Private/
└── Tests/
```

Module manifest definuje version, exports, dependencies a metadata. Explicitne exportuj iba public commands.

## 24. Testing s Pester

```powershell
Describe 'Get-ServiceHealth' {
    It 'returns a structured healthy result' {
        $result = Get-ServiceHealth -Name 'api'
        $result.Name | Should -Be 'api'
        $result.Healthy | Should -BeTrue
    }
}
```

Pester podporuje mocks, assertions a test discovery. Testuj aj:

- invalid parameters,
- non-terminating errors,
- native exit codes,
- `-WhatIf`,
- serialization,
- cross-platform paths,
- prázdne a viacprvkové výsledky.

## 25. Static analysis a formatting

```powershell
Invoke-ScriptAnalyzer -Path . -Recurse
Invoke-Formatter -ScriptDefinition (Get-Content script.ps1 -Raw)
```

PSScriptAnalyzer môže kontrolovať conventions, security-sensitive patterns a compatibility pravidlá.

## 26. Produkčný skeleton

```powershell
#requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('dev', 'test', 'prod')]
    [string]$Environment,

    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Main {
    [CmdletBinding()]
    param()

    Write-Verbose "Planning changes for $Environment"

    $plan = Get-ChangePlan -Environment $Environment
    $plan | ForEach-Object {
        if ($PSCmdlet.ShouldProcess($_.Target, $_.Action)) {
            Invoke-Change -PlanItem $_
        }
    }

    Test-Postcondition -Environment $Environment
}

try {
    Invoke-Main
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
```

Pri top-level skripte je vhodné explicitne mapovať výsledok na process exit code pre CI alebo scheduler.

## 27. Troubleshooting

### Pipeline vracia formatting objects

Odstráň `Format-*` z dátovej pipeline. Formátuj až na display boundary.

### `catch` sa nespustil

Príkaz pravdepodobne vytvoril non-terminating error. Použi `-ErrorAction Stop` alebo vhodne nastav `$ErrorActionPreference`.

### Function vrátila viac objektov

Skontroluj neodchytené expressions, command output a `Write-Output`. Logy presuň na verbose/information stream.

### Skript funguje vo Windows PowerShell, ale nie v PowerShell 7

Skontroluj:

- module compatibility,
- .NET API rozdiely,
- default encoding,
- native argument passing,
- Windows-only providers,
- remoting transport.

## 28. Časté omyly

### „PowerShell pipeline je iba textová pipeline“

Nie. Prenáša .NET objects, pokiaľ sa output predčasne nezmení na text.

### „Každá chyba je exception“

Nie. Non-terminating error môže pokračovať bez vstupu do `catch`.

### „`Write-Host` je správny výstup funkcie“

Nie pre composable automation. Dátový output má zostať v success streame.

### „`-WhatIf` automaticky zastaví všetky mutations“

Iba tie, ktoré sú správne implementované cez `ShouldProcess` alebo vlastný dry-run kontrakt.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi object pipeline a text pipeline?
2. Prečo `Format-Table` nemá byť uprostred automation pipeline?
3. Aký je rozdiel medzi terminating a non-terminating error?
4. Kedy potrebuješ `-ErrorAction Stop`?
5. Ako rozlíšiš success output, verbose log a error stream?
6. Prečo môže výsledok commandu meniť typ medzi `$null`, scalar a array?
7. Čo robí `SupportsShouldProcess`?
8. Ako kontroluješ native process exit code?
9. Aké riziká má PowerShell remoting serialization?
10. Ako navrhneš module s testovateľným public API?

## Glossary impact

Relevantné pojmy: object pipeline, cmdlet, advanced function, common parameters, terminating error, non-terminating error, error record, PowerShell provider, splatting, runspace, `ShouldProcess`, Pester, PSScriptAnalyzer a deserialized object.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Bash automation](bash-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Python for automation →](python-for-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
