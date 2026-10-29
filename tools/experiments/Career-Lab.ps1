[CmdletBinding()]
param(
    [ValidateSet('Install','CheckGitHub','Stage','List','Status','Observe','Run','OpenRun','Watch','PrepareParallel','ParallelStatus','RunParallel','OpenParallel')]
    [string]$Action = 'Status',
    [string]$Candidate,
    [string]$Source,
    [string]$Name,
    [string]$Provenance,
    [string]$Repo = 'Artepace/slopathone_winningteam',
    [string]$Ref,
    [string]$BatchId,
    [string]$Version = 'V4',
    [ValidateRange(2,3)][int]$Count = 3,
    [string]$Distro = 'Debian',
    [string]$LinuxWorkspace = '/home/gulebi/career-team',
    [switch]$Approved,
    [switch]$Download
)
$ErrorActionPreference = 'Stop'
$LinuxSystem = "$LinuxWorkspace/experiment_system"
$LinuxPython = "$LinuxWorkspace/.venv/bin/python"

function Invoke-Linux {
    param([string[]]$CommandArgs)
    & wsl.exe -d $Distro -- @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "Debian command failed (exit $LASTEXITCODE)." }
}

# --cd belongs to wsl itself, not to the Linux command.
function Invoke-Controller {
    param([string[]]$ControllerArgs)
    & wsl.exe -d $Distro --cd $LinuxWorkspace -- $LinuxPython "$LinuxSystem/controller.py" --workspace $LinuxWorkspace @ControllerArgs
    if ($LASTEXITCODE -ne 0) { throw "Experiment command failed (exit $LASTEXITCODE)." }
}

function Invoke-Parallel {
    param([string[]]$ParallelArgs)
    & wsl.exe -d $Distro --cd $LinuxWorkspace -- $LinuxPython "$LinuxSystem/parallel.py" --workspace $LinuxWorkspace @ParallelArgs
    if ($LASTEXITCODE -ne 0) { throw "Parallel experiment command failed (exit $LASTEXITCODE)." }
}

switch ($Action) {
    'Install' {
        $MappedOutput = & wsl.exe -d $Distro -- wslpath -a ($PSScriptRoot.Replace('\','/'))
        if ($LASTEXITCODE -ne 0) { throw 'Could not map the Windows source path into Debian.' }
        $MappedSource = ([string]$MappedOutput).Trim()
        Invoke-Linux -CommandArgs @('test', '-d', $LinuxWorkspace)
        Invoke-Linux -CommandArgs @('mkdir', '-p', $LinuxSystem)
        Invoke-Linux -CommandArgs @('cp', '-r', "$MappedSource/.", "$LinuxSystem/")
        Invoke-Controller -ControllerArgs @('init')
        Write-Host 'Installed the experiment tools only. No game or service was started.'
    }
    'CheckGitHub' {
        $GithubArgs = @("$LinuxSystem/github_sources.py", '--inbox', "$LinuxSystem/inbox", '--repo', $Repo)
        if ($Ref) { $GithubArgs += @('--ref', $Ref) }
        if ($Download) { $GithubArgs += '--download' }
        & wsl.exe -d $Distro --cd $LinuxWorkspace -- $LinuxPython @GithubArgs
        if ($LASTEXITCODE -ne 0) { throw 'GitHub check failed. Local solutions were not changed.' }
    }
    'Stage' {
        if (-not $Source) { throw 'Stage requires -Source with a ZIP or solution directory.' }
        if ($Source.StartsWith('/')) { $MappedSource = $Source }
        else {
            $AbsoluteSource = (Resolve-Path -LiteralPath $Source).Path
            $MappedOutput = & wsl.exe -d $Distro -- wslpath -a ($AbsoluteSource.Replace('\','/'))
            if ($LASTEXITCODE -ne 0) { throw 'Could not map source path.' }
            $MappedSource = ([string]$MappedOutput).Trim()
        }
        $SourceLabel = if ($Provenance) { $Provenance } else { $MappedSource }
        $StageArgs = @('stage', $MappedSource, '--source', $SourceLabel)
        if ($Name) { $StageArgs += @('--name', $Name) }
        Invoke-Controller -ControllerArgs $StageArgs
    }
    'List' { Invoke-Controller -ControllerArgs @('list') }
    'Status' { Invoke-Controller -ControllerArgs @('status', '--json') }
    'Observe' { Invoke-Controller -ControllerArgs @('observe', '--json') }
    'Watch' { Invoke-Controller -ControllerArgs @('status', '--watch') }
    'PrepareParallel' {
        if (-not $Candidate) { throw 'Specify a staged candidate.' }
        Invoke-Parallel -ParallelArgs @('prepare', $Candidate, '--version', $Version, '--count', [string]$Count)
    }
    'ParallelStatus' {
        $ArgsToPass = @('status')
        if ($BatchId) { $ArgsToPass += $BatchId }
        Invoke-Parallel -ParallelArgs $ArgsToPass
    }
    'RunParallel' {
        if (-not $Approved -or -not $BatchId) { throw 'Explicit approval for the whole batch and a batch ID are required.' }
        Invoke-Parallel -ParallelArgs @('run',$BatchId,'--approved')
    }
    'OpenParallel' {
        if (-not $Approved -or $BatchId -notmatch '^[A-Za-z0-9-]+$') { throw 'Specify an approved batch ID.' }
        foreach ($Value in @($PSCommandPath,$Distro,$LinuxWorkspace)) {
            if ($Value.Contains('"')) { throw 'Double quotes are not supported in launch paths.' }
        }
        $ParallelLaunchArgs = @('-NoExit','-NoProfile','-ExecutionPolicy','Bypass','-File',('"{0}"' -f $PSCommandPath),
            '-Action','RunParallel','-BatchId',$BatchId,'-Approved','-Distro',('"{0}"' -f $Distro),'-LinuxWorkspace',('"{0}"' -f $LinuxWorkspace))
        Start-Process -FilePath 'powershell.exe' -ArgumentList $ParallelLaunchArgs -WorkingDirectory $PSScriptRoot -WindowStyle Normal
    }
    'Run' {
        if (-not $Approved) { throw 'No run started. Use -Approved only after authorizing this run.' }
        if (-not $Candidate -or $Candidate -notmatch '^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$') { throw 'Specify a valid candidate ID from List.' }
        Invoke-Controller -ControllerArgs @('run', $Candidate, '--approved')
    }
    'OpenRun' {
        if (-not $Approved) { throw 'No run started. Explicit approval is required.' }
        if (-not $Candidate -or $Candidate -notmatch '^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$') { throw 'Specify a valid candidate ID from List.' }
        foreach ($Value in @($PSCommandPath, $Distro, $LinuxWorkspace)) {
            if ($Value.Contains('"')) { throw 'Double quotes are not supported in launch paths.' }
        }
        $LaunchArgs = @('-NoExit','-NoProfile','-ExecutionPolicy','Bypass','-File',('"{0}"' -f $PSCommandPath),
            '-Action','Run','-Candidate',$Candidate,'-Approved','-Distro',('"{0}"' -f $Distro),'-LinuxWorkspace',('"{0}"' -f $LinuxWorkspace))
        Start-Process -FilePath 'powershell.exe' -ArgumentList $LaunchArgs -WorkingDirectory $PSScriptRoot -WindowStyle Normal
    }
}
