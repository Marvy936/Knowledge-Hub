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