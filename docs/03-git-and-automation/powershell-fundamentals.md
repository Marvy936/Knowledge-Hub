# PowerShell fundamentals

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Processes, threads, PID a signals](../01-linux-and-systems/processes-threads-pid-signals.md), [Environment variables](../01-linux-and-systems/environment-variables.md)
- Súvisiace témy: object pipeline, .NET, modules, remoting, native processes, CI automation

## 1. Cieľ kapitoly

PowerShell je shell a automatizačný jazyk postavený nad .NET object modelom. Jeho hlavná výhoda nie je farebná konzola ani množstvo cmdletov, ale možnosť niesť typované objekty cez celý automation lifecycle:

```text
parameter binding
→ input a dependency validation
→ current-state objects
→ change-plan objects
→ ShouldProcess / WhatIf boundary
→ bounded mutations
→ postcondition objects
→ structured result
→ process exit code
```

Object pipeline, output streams, error records, native exit codes, remoting a modules majú význam iba vtedy, keď podporujú tento lifecycle. Produkčný script nesmie zamieňať zobrazený text za dáta ani úspešné vykonanie commandu za overený výsledok.

## 2. Nosný scenár: Atlas service configuration

Atlas prevádzkuje `orders-api` na Windows aj Linux hostoch. Potrebuje PowerShell nástroj:

```powershell
Invoke-AtlasConfigDeployment `
    -Environment prod `
    -TargetHost orders-01 `
    -Version '3.8.1' `
    -WhatIf
```

Workflow má:

1. bindnúť a validovať parameters,
2. zistiť aktuálnu config version a service state,
3. vytvoriť typed change plan,
4. pri `-WhatIf` plán iba zobraziť,
5. pri apply vykonať idempotentnú mutation,
6. spustiť native validator,
7. reštartovať alebo reloadnúť službu,
8. overiť readiness a config version,
9. vrátiť jeden stabilný result object,
10. na top-level hranici mapovať failure na process exit code.

Rovnaký nástroj môže neskôr používať remoting a parallel fan-out. Najprv však musí byť správny pre jeden target.

## 3. Kedy je PowerShell vhodný

PowerShell je prirodzený pre:

- Windows administráciu,
- cross-platform .NET automation,
- filesystem, registry, certificate a service orchestration,
- Azure, Microsoft 365 a ďalšie object-oriented modules,
- JSON, XML a CSV transformácie,
- CI/CD entrypoints,
- reusable automation modules,
- remoting s explicitným serialization modelom.

Je slabšia voľba, keď workflow potrebuje rozsiahly aplikačný domain model, high-throughput processing alebo dlhodobý daemon. Vtedy má byť PowerShell tenká orchestration vrstva nad vhodnejším programom alebo API.

## 4. Runtime verzia je súčasť contractu

Treba rozlišovať:

```text
Windows PowerShell 5.1  Windows-only, .NET Framework, powershell.exe
PowerShell 7+           cross-platform, moderný .NET, pwsh
```

Rozdiely zasahujú:

- dostupné modules a providers,
- .NET API,
- default encoding,
- native argument passing,
- remoting transport,
- parallel features,
- command a filesystem case semantics.

Atlas script deklaruje runtime:

```powershell
#requires -Version 7.4
```

A required module:

```powershell
#requires -Modules @{ ModuleName = 'Atlas.Automation'; ModuleVersion = '2.0.0' }
```

CI má testovať explicitnú runtime matrix. Náhodné opravy compatibility incidentov nie sú version policy.

## 5. Object pipeline verzus text pipeline

Cmdlet typicky posiela objects:

```powershell
Get-Process |
    Where-Object CPU -gt 10 |
    Sort-Object CPU -Descending |
    Select-Object -First 5 Name, Id, CPU
```

`Where-Object` číta property `CPU`; neparsuje stĺpec z tabuľky.

Inspection:

```powershell
$item = Get-Process | Select-Object -First 1
$item.GetType().FullName
$item | Get-Member
```

Native executable však môže produkovať text alebo bytes. Serialization, formatting a remoting môžu object semantics zmeniť. Pipeline nie je „vždy objektová“ bez ohľadu na boundary.

## 6. Formatting je posledná hranica

`Format-Table` nevytvára business objects. Vytvára formatting instructions pre host.

Nesprávne:

```powershell
Get-Service |
    Format-Table Name, Status |
    ConvertTo-Json
```

Správne:

```powershell
$data = Get-Service | Select-Object Name, Status
$data | ConvertTo-Json -Depth 3
$data | Format-Table
```

Atlas module vracia objects. Až top-level interactive caller rozhodne, či ich zobrazí ako table, JSON alebo iný formát.

## 7. Parameter binding je vstupná state transition

Advanced function:

```powershell
function Invoke-AtlasConfigDeployment {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('dev', 'test', 'prod')]
        [string]$Environment,

        [Parameter(Mandatory)]
        [ValidatePattern('^[a-z][a-z0-9-]+$')]
        [string]$TargetHost,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$Version,

        [ValidateRange(1, 300)]
        [int]$TimeoutSeconds = 30
    )
}
```

Binding môže vykonať type conversion pred vstupom do function body. Preto:

```powershell
[int]$Port = '8080'
```

môže uspieť, ale stále treba range a business validation.

Rozlišuj:

- syntax/type validation cez attributes,
- environment-dependent preconditions v explicitnej validation fáze,
- mutation až po vytvorení plánu.

`ValidateScript` nemá robiť side effects. Existence check tiež neodstraňuje race medzi kontrolou a použitím.

## 8. `$null`, scalar a collection sú odlišné states

Command result môže byť:

```text
0 objektov  → $null
1 objekt    → scalar
N objektov  → collection
```

Pre stabilný collection contract:

```powershell
$targets = @(Get-AtlasTarget -Environment $Environment)
```

Porovnávaj `$null` na ľavej strane:

```powershell
if ($null -eq $currentState) {
    throw 'Current state was not returned.'
}
```

Rozlišuj:

- `$null`,
- empty string,
- whitespace-only string,
- empty array,
- chýbajúcu property,
- existujúcu property s hodnotou `$null`,
- command bez success outputu.

Schema-critical object contract má pomenovať nullability a cardinality.

## 9. Function vracia celý success stream

PowerShell function nevracia iba posledný expression. Každý neodchytený object v success stream-e sa stane outputom.

Problematické:

```powershell
function Get-DeploymentState {
    'Reading state'
    Get-Item -LiteralPath $ConfigPath
    [pscustomobject]@{ Version = '3.8.1' }
}
```

Caller dostane string, `FileInfo` aj result object.

Správne:

```powershell
function Get-DeploymentState {
    [CmdletBinding()]
    param([string]$ConfigPath)

    Write-Verbose 'Reading state'
    $item = Get-Item -LiteralPath $ConfigPath -ErrorAction Stop

    [pscustomobject]@{
        PSTypeName = 'Atlas.DeploymentState'
        Path       = $item.FullName
        Version    = Get-AtlasVersion -LiteralPath $item.FullName
    }
}
```

Unwanted cmdlet output potlač zámerne:

```powershell
$null = New-Item -ItemType Directory -Path $Directory -Force
```

Output pollution je API bug, nie iba vizuálny problém.

## 10. Output streams majú rozdielne kontrakty

PowerShell používa samostatné streams:

```text
1 Success
2 Error
3 Warning
4 Verbose
5 Debug
6 Information
```

Použitie:

```powershell
Write-Verbose 'Reading current state.'
Write-Warning 'Using compatibility fallback.'
Write-Information 'phase=apply target=orders-01'
Write-Error 'Deployment failed.'
```

Library function má:

- vracať typed objects cez success stream,
- používať verbose/debug/information na diagnostics,
- nevypisovať secret values,
- neukončovať hosting process cez `exit`.

Top-level script môže výsledok serializovať a rozhodnúť o exit code.

## 11. Error nie je automaticky exception

PowerShell rozlišuje:

### Terminating error

Preruší current statement alebo pipeline scope a vstúpi do `catch`.

### Non-terminating error

Vytvorí `ErrorRecord`, ale command môže pokračovať.

Pre operation, ktorá musí byť atomická z pohľadu workflowu:

```powershell
try {
    $item = Get-Item -LiteralPath $ConfigPath -ErrorAction Stop
}
catch [System.Management.Automation.ItemNotFoundException] {
    throw [System.InvalidOperationException]::new(
        "Required config does not exist: $ConfigPath",
        $_.Exception
    )
}
```

Bez `-ErrorAction Stop` sa `catch` nemusí spustiť.

Globálne:

```powershell
$ErrorActionPreference = 'Stop'
```

je užitočný top-level default, ale script musí stále poznať commands, ktoré používajú non-terminating semantics zámerne.

## 12. `ErrorRecord` je diagnostický object

V `catch` je `$_` typicky `ErrorRecord` s:

- `Exception`,
- `CategoryInfo`,
- `FullyQualifiedErrorId`,
- `TargetObject`,
- `InvocationInfo`,
- `ScriptStackTrace`.

Rethrow:

```powershell
catch {
    Write-Verbose "Failure category: $($_.CategoryInfo.Category)"
    throw
}
```

Holé `throw` zachová pôvodný context. Pri pridávaní správy zachovaj inner exception.

Diagnostics nemajú automaticky serializovať celý target object alebo invocation arguments, pretože môžu obsahovať credentials.

## 13. Strict mode a cleanup

```powershell
Set-StrictMode -Version Latest
```

pomáha odhaliť nenastavené variables a niektoré neplatné property accesses. Nie je to static type system ani náhrada tests.

Cleanup:

```powershell
$tempPath = $null
try {
    $tempPath = New-AtlasTemporaryFile
    # work
}
catch {
    throw
}
finally {
    if ($null -ne $tempPath -and (Test-Path -LiteralPath $tempPath)) {
        Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
    }
}
```

`finally` sa vykoná v bežnom success/error flowe. Hard process termination môže cleanup znemožniť. Cleanup má byť idempotentný a nesmie zakryť primárny error.

## 14. Current state má byť typed object

Atlas observation function:

```powershell
function Get-AtlasCurrentState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TargetHost
    )

    $service = Get-Service -Name 'orders-api' -ErrorAction Stop
    $version = Get-Content `
        -LiteralPath 'C:\ProgramData\Atlas\orders.version' `
        -Raw `
        -Encoding utf8 `
        -ErrorAction Stop

    [pscustomobject]@{
        PSTypeName    = 'Atlas.CurrentState'
        TargetHost    = $TargetHost
        ServiceStatus = $service.Status.ToString()
        Version       = $version.Trim()
        ObservedAtUtc = [datetime]::UtcNow
    }
}
```

Object contract určuje property names, types, units, timezone a nullability. Human-formatted table nie je current-state API.

## 15. Plan je object graph bez mutations

Desired state:

```powershell
$desiredState = [pscustomobject]@{
    PSTypeName = 'Atlas.DesiredState'
    TargetHost = $TargetHost
    Version    = $Version
    Service    = 'Running'
}
```

Plan:

```powershell
function Get-AtlasChangePlan {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$CurrentState,
        [Parameter(Mandatory)]$DesiredState
    )

    if ($CurrentState.Version -ne $DesiredState.Version) {
        [pscustomobject]@{
            PSTypeName = 'Atlas.PlanItem'
            Target     = $CurrentState.TargetHost
            Action     = 'UpdateConfiguration'
            Current    = $CurrentState.Version
            Desired    = $DesiredState.Version
        }
    }

    if ($CurrentState.ServiceStatus -ne $DesiredState.Service) {
        [pscustomobject]@{
            PSTypeName = 'Atlas.PlanItem'
            Target     = $CurrentState.TargetHost
            Action     = 'StartService'
            Current    = $CurrentState.ServiceStatus
            Desired    = $DesiredState.Service
        }
    }
}
```

Caller stabilizuje cardinality:

```powershell
$plan = @(Get-AtlasChangePlan -CurrentState $currentState -DesiredState $desiredState)
```

Plan sa dá zobraziť, serializovať, schváliť a testovať bez side effects.

## 16. `ShouldProcess` je mutation gate

```powershell
function Invoke-AtlasPlanItem {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)]
        [psobject]$PlanItem
    )

    if ($PSCmdlet.ShouldProcess($PlanItem.Target, $PlanItem.Action)) {
        switch ($PlanItem.Action) {
            'UpdateConfiguration' {
                Set-AtlasConfiguration -Version $PlanItem.Desired
            }
            'StartService' {
                Start-Service -Name 'orders-api'
            }
            default {
                throw "Unsupported plan action: $($PlanItem.Action)"
            }
        }
    }
}
```

`SupportsShouldProcess` poskytuje `-WhatIf` a `-Confirm`, ale iba code pod `ShouldProcess` je chránený.

Limity:

- nested function môže vykonať ďalšiu mutation,
- native executable nevie automaticky o `WhatIf`,
- read-only planning sa má vykonať aj pri `-WhatIf`,
- top-level `WhatIf` flag bez pokrytia všetkých mutation calls vytvára falošný safety contract.

## 17. Native process má vlastný result contract

Atlas config validator je native executable:

```powershell
$arguments = @(
    '--config'
    $ConfigPath
    '--environment'
    $Environment
)

& 'atlas-config-validator' @arguments
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    throw "Validator failed with exit code $exitCode"
}
```

Rozlišuj:

```text
PowerShell command execution
≠ native process exit code
```

`$?` je Boolean úspech poslednej PowerShell operation. `$LASTEXITCODE` je integer contract native procesu. Zachyť ho okamžite.

Argumenty drž v array alebo splatting štruktúre. Nevytváraj command string a nepoužívaj `Invoke-Expression`.

## 18. Native wrapper musí poznať success codes

```powershell
function Invoke-AtlasNativeCommand {
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
        throw [System.ComponentModel.Win32Exception]::new(
            "Native command '$FilePath' failed with exit code $exitCode"
        )
    }
}
```

Niektoré tools používajú viac success-like statuses. Wrapper nesmie predpokladať, že každý non-zero znamená rovnakú chybu.

Binary output alebo presný byte stream nevedieme cez line-oriented string pipeline. Použije sa .NET `Process` API alebo file redirection.

## 19. Atomic file update a encoding

PowerShell 5.1 a 7+ sa historicky líšia v encoding defaults. Atlas používa explicitné UTF-8 bez BOM:

```powershell
$targetDirectory = Split-Path -Parent $TargetPath
$tempPath = Join-Path $targetDirectory ('.orders.tmp.{0}' -f [guid]::NewGuid())

try {
    [System.IO.File]::WriteAllText(
        $tempPath,
        $Content,
        [System.Text.UTF8Encoding]::new($false)
    )

    Invoke-AtlasNativeCommand `
        -FilePath 'atlas-config-validator' `
        -ArgumentList @('--config', $tempPath)

    Move-Item -LiteralPath $tempPath -Destination $TargetPath -Force
    $tempPath = $null
}
finally {
    if ($null -ne $tempPath -and (Test-Path -LiteralPath $tempPath)) {
        Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
    }
}
```

Treba overiť:

- same-filesystem replace semantics,
- ACL a ownership,
- existing-target behavior na platforme,
- antivirus/file-lock interference,
- crash durability požiadavky.

`Move-Item` nie je automaticky transakčný deployment primitive pre každý provider a filesystem.

## 20. Idempotencia a no-change result

Idempotentná mutation smeruje current state k desired state bez akumulácie side effects.

Slabé:

```powershell
Add-Content -LiteralPath $Profile -Value '$env:APP_ENV = ''prod'''
```

Lepší model:

```text
observe current content
→ compare with desired content
→ no change alebo atomic replace
→ verify final content
```

Result object:

```powershell
[pscustomobject]@{
    PSTypeName = 'Atlas.AutomationResult'
    Target     = $TargetHost
    Changed    = $false
    Action     = 'None'
    Verified   = $true
}
```

Druhý run s rovnakým desired inputom musí skončiť s rovnakým state a `Changed = $false`.

## 21. Postcondition verification

Mutation command môže uspieť a služba môže byť stále nepoužiteľná.

```powershell
$service = Get-Service -Name 'orders-api' -ErrorAction Stop
$service.WaitForStatus(
    [System.ServiceProcess.ServiceControllerStatus]::Running,
    [timespan]::FromSeconds($TimeoutSeconds)
)

$response = Invoke-RestMethod `
    -Uri 'http://127.0.0.1:8080/ready' `
    -Method Get `
    -TimeoutSec 5 `
    -ErrorAction Stop

if ($response.version -ne $Version) {
    throw "Readiness reports version '$($response.version)', expected '$Version'."
}
```

Verification má kontrolovať:

- desired config version,
- service state,
- readiness semantics,
- parser/schema validity,
- target identity,
- neprítomnosť neočakávaného driftu.

`ServiceStatus = Running` nemusí znamenať, že aplikácia prijíma requesty.

## 22. Timeouts, retries a neistý výsledok

Timeout policy musí zohľadniť partial side effects.

Pri native process-e možno použiť .NET process lifecycle:

```powershell
$process = Start-Process `
    -FilePath $FilePath `
    -ArgumentList $ArgumentList `
    -PassThru

try {
    if (-not $process.WaitForExit($TimeoutMilliseconds)) {
        $process.Kill($true)
        throw "Process timed out after $TimeoutMilliseconds ms."
    }

    if ($process.ExitCode -ne 0) {
        throw "Process failed with exit code $($process.ExitCode)."
    }
}
finally {
    $process.Dispose()
}
```

Safe retry potrebuje:

- retryable failure class,
- bounded attempts,
- total time budget,
- backoff a jitter,
- idempotent operation alebo idempotency key,
- operation-status lookup po nejasnom timeout-e.

Slepý retry `POST` môže vytvoriť duplicate order alebo deployment.

## 23. Remoting mení object aj trust boundary

```powershell
$session = New-PSSession -ComputerName $TargetHost
try {
    $result = Invoke-Command -Session $session -ScriptBlock {
        Get-Service -Name 'orders-api'
    }
}
finally {
    Remove-PSSession -Session $session
}
```

Remoting pridáva:

```text
authentication/authorization
+ network timeout
+ session lifecycle
+ remote runtime/modules
+ serialization
+ credential delegation
```

Remote object býva deserialized representation:

```text
Deserialized.System.ServiceProcess.ServiceController
```

Properties môžu zostať, methods nie. Live operation vykonaj na remote strane a vráť explicitný DTO/result object.

`$using:` prenesie hodnotu do remote alebo parallel contextu. Nevytvára shared mutable reference.

## 24. Parallelism až po definovaní side effects

PowerShell 7:

```powershell
$results = $targets | ForEach-Object -Parallel {
    Invoke-AtlasTargetDeployment -TargetHost $_
} -ThrottleLimit 5
```

Riziká:

- oddelené runspaces,
- module/function availability,
- output ordering,
- secret duplication,
- spoločné files a APIs,
- rate limits,
- partial success,
- cancellation a cleanup.

Najprv musí existovať bezpečný single-target operation contract. Potom sa definuje:

- throttle,
- per-target result,
- fail-fast alebo continue policy,
- retry a dead-letter handling,
- central aggregation,
- concurrency-safe side effects.

Parallelism nie je default optimalizácia.

## 25. Module je versionovaný automation API

Reusable functions patria do module:

```text
Atlas.Automation/
├── Atlas.Automation.psd1
├── Atlas.Automation.psm1
├── Public/
├── Private/
└── Tests/
```

Explicitný export:

```powershell
Export-ModuleMember -Function Invoke-AtlasConfigDeployment, Get-AtlasCurrentState
```

Module contract zahŕňa:

- function names a approved verbs,
- parameters a defaults,
- pipeline binding,
- output types a cardinality,
- error categories,
- `ShouldProcess` behavior,
- supported PowerShell editions,
- dependency versions.

Auto-loading môže zakryť, ktorú module version command používa:

```powershell
Get-Command Invoke-AtlasConfigDeployment |
    Format-List Name, Source, Version, ModuleName
```

CI má dependencies pinovať alebo kontrolovať. Mutable machine-wide module state znižuje reprodukovateľnosť.

## 26. Worked failure: function vrátila tri objekty

Pipeline očakávala jeden `Atlas.AutomationResult`, ale dostala tri values.

Pôvodná function:

```powershell
function Invoke-Deployment {
    'Starting deployment'
    New-Item -ItemType Directory -Path $WorkDirectory -Force
    [pscustomobject]@{ Changed = $true }
}
```

Mechanizmus:

```text
string expression
→ success stream

New-Item output
→ DirectoryInfo v success stream-e

result object
→ tretí success object
```

Caller:

```powershell
$result = Invoke-Deployment
$result.Changed
```

pracoval nad collection a vytvoril nejasný contract.

Diagnostika:

```powershell
$output = @(Invoke-Deployment)
$output | ForEach-Object { $_.GetType().FullName }
```

Náprava:

```powershell
Write-Verbose 'Starting deployment'
$null = New-Item -ItemType Directory -Path $WorkDirectory -Force
[pscustomobject]@{ PSTypeName = 'Atlas.AutomationResult'; Changed = $true }
```

Problém nevyrieši `return` na poslednom riadku. Treba kontrolovať celý success stream.

## 27. Worked failure: validator zlyhal, script bol green

Pôvodný code:

```powershell
& atlas-config-validator --config $ConfigPath
Write-Information 'Configuration valid.'
```

Native validator vrátil `3`, ale PowerShell nevytvoril terminating error podľa použitého runtime/preferences. Script pokračoval a CI dostalo exit code `0`.

Mechanizmus:

```text
native process exit 3
→ $LASTEXITCODE = 3
→ exit code sa nevyhodnotil
→ success message
→ top-level script skončil 0
→ false green
```

Náprava:

```powershell
& atlas-config-validator --config $ConfigPath
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "Validator failed with exit code $exitCode"
}
```

`$ErrorActionPreference = 'Stop'` sama nemusí nahradiť explicitný native-process contract.

## 28. Worked failure: `-WhatIf` zmenil target

Top-level function deklarovala `SupportsShouldProcess`, ale helper zapisoval file mimo gate-u:

```powershell
Set-AtlasConfiguration -Content $content

if ($PSCmdlet.ShouldProcess($TargetHost, 'Restart service')) {
    Restart-Service orders-api
}
```

Pri `-WhatIf` sa service nereštartovala, ale configuration file sa zmenil.

Príčina:

```text
ShouldProcess pokrýval iba restart
→ file mutation bola mimo gate-u
→ falošný dry-run contract
```

Náprava je vytvoriť plan a všetky mutations vykonávať cez jednu kontrolovanú apply boundary. Integration test musí porovnať target state pred a po `-WhatIf`.

## 29. Top-level process boundary

Reusable module functions používajú `throw`, nie `exit`.

Top-level script:

```powershell
try {
    $result = Invoke-AtlasConfigDeployment @PSBoundParameters
    $result
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
```

Podrobnejší contract môže mapovať input, transient, verification a internal failures na odlišné stable exit codes. Mapping patrí na process boundary, nie do každej helper function.

## 30. Produkčný skeleton

```powershell
#requires -Version 7.4

[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateSet('dev', 'test', 'prod')]
    [string]$Environment,

    [Parameter(Mandatory)]
    [ValidatePattern('^[a-z][a-z0-9-]+$')]
    [string]$TargetHost,

    [Parameter(Mandatory)]
    [string]$Version,

    [ValidateRange(1, 300)]
    [int]$TimeoutSeconds = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-CurrentState {
    [CmdletBinding()]
    param([string]$TargetHost)

    # Return one Atlas.CurrentState object.
}

function Get-DesiredState {
    [CmdletBinding()]
    param(
        [string]$TargetHost,
        [string]$Version
    )

    [pscustomobject]@{
        PSTypeName = 'Atlas.DesiredState'
        TargetHost = $TargetHost
        Version    = $Version
        Service    = 'Running'
    }
}

function Get-ChangePlan {
    [CmdletBinding()]
    param($CurrentState, $DesiredState)

    # Return zero or more Atlas.PlanItem objects, no mutations.
}

function Invoke-PlanItem {
    [CmdletBinding(SupportsShouldProcess)]
    param($PlanItem)

    if ($PSCmdlet.ShouldProcess($PlanItem.Target, $PlanItem.Action)) {
        # Perform one bounded idempotent mutation.
    }
}

function Test-Postcondition {
    [CmdletBinding()]
    param($DesiredState, [int]$TimeoutSeconds)

    # Throw if actual state does not satisfy desired state.
}

function Invoke-Main {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string]$Environment,
        [string]$TargetHost,
        [string]$Version,
        [int]$TimeoutSeconds
    )

    $current = Get-CurrentState -TargetHost $TargetHost
    $desired = Get-DesiredState -TargetHost $TargetHost -Version $Version
    $plan = @(Get-ChangePlan -CurrentState $current -DesiredState $desired)

    foreach ($item in $plan) {
        Invoke-PlanItem `
            -PlanItem $item `
            -WhatIf:$WhatIfPreference `
            -Confirm:$false
    }

    if (-not $WhatIfPreference) {
        Test-Postcondition -DesiredState $desired -TimeoutSeconds $TimeoutSeconds
    }

    [pscustomobject]@{
        PSTypeName  = 'Atlas.AutomationResult'
        TargetHost  = $TargetHost
        Changed     = ($plan.Count -gt 0)
        PlanCount   = $plan.Count
        Verified    = -not $WhatIfPreference
        CompletedAt = [datetime]::UtcNow
    }
}

try {
    Invoke-Main `
        -Environment $Environment `
        -TargetHost $TargetHost `
        -Version $Version `
        -TimeoutSeconds $TimeoutSeconds `
        -WhatIf:$WhatIfPreference `
        -Confirm:$false

    exit 0
}
catch {
    Write-Error $_
    exit 1
}
```

Skeleton je lifecycle, nie hotová knižnica. Reálny nástroj ešte potrebuje lock/concurrency policy, credential provider, retry classification, rollback alebo compensation a konkrétnu result schema.

## 31. Testing podľa contractu

Pester tests majú pokrývať:

### Inputs a outputs

- parameter validation,
- zero/one/many cardinality,
- stable output type,
- output pollution,
- null a missing properties.

### Error boundaries

- terminating a non-terminating errors,
- native success a failure exit codes,
- cleanup bez zakrytia primary failure,
- timeout a cancellation,
- partial-success policy.

### State lifecycle

- no-change run,
- idempotent second run,
- `-WhatIf` bez mutations,
- apply failure,
- verify failure,
- rollback alebo compensation evidence.

### Environment boundaries

- PowerShell 5.1/7 compatibility podľa support policy,
- Windows/Linux path a encoding semantics,
- module version drift,
- remoting serialization,
- concurrency throttle a result aggregation.

Príklad:

```powershell
Describe 'Invoke-AtlasConfigDeployment' {
    It 'returns one typed result on no-change' {
        $result = @(Invoke-AtlasConfigDeployment `
            -Environment test `
            -TargetHost orders-01 `
            -Version 3.8.1)

        $result.Count | Should -Be 1
        $result[0].PSTypeNames | Should -Contain 'Atlas.AutomationResult'
        $result[0].Changed | Should -BeFalse
        $result[0].Verified | Should -BeTrue
    }
}
```

PSScriptAnalyzer a formatter kontrolujú patterns a štýl. Nenahrádzajú native-process, remoting ani state-transition integration tests.

## 32. Referenčné pravidlá

- Formátuj až na display boundary.
- Stabilizuj collection cardinality pomocou `@(...)`, keď contract vyžaduje array.
- Success stream drž čistý od logs a incidental cmdlet outputs.
- Použi `-LiteralPath` pre user-provided paths bez wildcard semantics.
- Očakávané cmdlet errors konvertuj na terminating cez `-ErrorAction Stop`.
- Native exit code čítaj z `$LASTEXITCODE` okamžite.
- Arguments odovzdávaj cez arrays alebo splatting, nie `Invoke-Expression`.
- Mutation umiestni pod `ShouldProcess` a testuj `-WhatIf` na reálnom state.
- Remote objects považuj za serialized data, nie live local instances.
- Functions vracajú objects; top-level script mapuje process exit code.
- Secrets nevypisuj do verbose, debug, transcript ani error serialization.
- Parallelism pridaj až po definovaní idempotency a partial-success contractu.

## 33. Časté omyly

### „PowerShell function vracia posledný expression“

Vracia všetok success output vytvorený počas vykonania.

### „Každá chyba vstúpi do `catch`“

Non-terminating error potrebuje `-ErrorAction Stop` alebo zodpovedajúcu preference.

### „`$?` je native exit code“

Integer status native procesu je v `$LASTEXITCODE`.

### „Object pipeline prežije `Format-Table`“

Formatting cmdlets vytvárajú display records, nie pôvodné business objects.

### „`-WhatIf` automaticky zastaví všetky side effects“

Chráni iba správne implementované `ShouldProcess` paths.

### „SecureString je secret vault“

Je to API representation s platform-dependent ochranou, nie kompletný secret lifecycle.

### „Remote object má rovnaké methods ako lokálny object“

Po serialization typicky zostanú properties, nie live methods.

### „PowerShell 5.1 a 7 sa líšia iba executable menom“

Líšia sa runtime, modules, encoding, native invocation a platform semantics.

## 34. Kontrolné otázky

1. Aký lifecycle má produkčná PowerShell automatizácia?
2. Aký je rozdiel medzi object pipeline a formatting boundary?
3. Prečo function môže vrátiť viac objektov, než autor očakával?
4. Ako stabilizuješ zero/one/many output contract?
5. Aký je rozdiel medzi terminating a non-terminating error?
6. Kedy treba použiť `-ErrorAction Stop`?
7. Prečo `$LASTEXITCODE` treba zachytiť okamžite?
8. Ako `ShouldProcess` podporuje plan/apply boundary a kde sú jeho limity?
9. Prečo úspešný service command neznamená úspešnú postcondition?
10. Ako remoting mení type a trust model výsledku?
11. Prečo module versioning patrí do automation API contractu?
12. Ktoré testy dokazujú, že `-WhatIf` je skutočne bez side effects?

## Glossary impact

Relevantné pojmy: object pipeline, formatting boundary, pipeline enumeration, scalar, collection, advanced function, parameter binding, success stream, information stream, terminating error, non-terminating error, ErrorRecord, `$LASTEXITCODE`, splatting, native process, `ShouldProcess`, `WhatIf`, current state, desired state, plan object, postcondition, remoting serialization, runspace, module contract, Pester.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Bash automation](bash-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Python for automation →](python-for-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->