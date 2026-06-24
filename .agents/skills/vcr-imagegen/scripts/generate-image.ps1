#Requires -Version 5.1
<#
.SYNOPSIS
  Generate or edit images via Vans Coding Router POST /v1/images.

.DESCRIPTION
  Thin wrapper around scripts/vcr_image.py. Reads .vans/image.json, supports
  input_references for local reference images, writes PNG/JPEG to project path.

.PARAMETER ImagePrompt
  Prompt text (positional 0). Prefer -PromptFile for Chinese.

.PARAMETER PromptFile
  UTF-8 prompt file path.

.PARAMETER OutputPath
  Relative to -Cwd. Default assets/generated/image.png.

.PARAMETER Cwd
  Project root. Default: current directory.

.PARAMETER Model
  Full openrouter@... model id.

.PARAMETER Preset
  icon | ui_mockup | photo

.PARAMETER AspectRatio
  e.g. 1:1, 16:9

.PARAMETER Resolution
  e.g. 512, 1K

.PARAMETER ReferencePath
  Single reference image (repeatable).

.PARAMETER ReferencePaths
  Comma-separated reference paths.

.PARAMETER DryRun
  Print planned request without calling API.

.PARAMETER TimeoutSec
  HTTP timeout seconds. Default 120 (180 when references present).
#>
param(
    [Parameter(Position = 0)]
    [string] $ImagePrompt,
    [string] $PromptFile = "",
    [string] $OutputPath = "",
    [string] $Cwd = "",
    [string] $Model = "",
    [ValidateSet("", "icon", "ui_mockup", "photo")]
    [string] $Preset = "",
    [string] $AspectRatio = "",
    [string] $Resolution = "",
    [string[]] $ReferencePath = @(),
    [string] $ReferencePaths = "",
    [switch] $DryRun,
    [int] $TimeoutSec = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PyScript = Join-Path $ScriptDir 'vcr_image.py'

if (-not (Test-Path -LiteralPath $PyScript)) {
    throw "Missing vcr_image.py next to generate-image.ps1: $PyScript"
}

if ([string]::IsNullOrWhiteSpace($Cwd)) {
    $Cwd = (Get-Location).Path
}

$pyArgs = @($PyScript, '--cwd', $Cwd)

if (-not [string]::IsNullOrWhiteSpace($PromptFile)) {
    $pyArgs += @('--prompt-file', $PromptFile)
} elseif (-not [string]::IsNullOrWhiteSpace($ImagePrompt)) {
    $pyArgs += @($ImagePrompt)
} else {
    throw "ImagePrompt or PromptFile is required. Prefer -PromptFile for Chinese prompts."
}

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { $pyArgs += @('--output-path', $OutputPath) }
if (-not [string]::IsNullOrWhiteSpace($Model)) { $pyArgs += @('--model', $Model) }
if (-not [string]::IsNullOrWhiteSpace($Preset)) { $pyArgs += @('--preset', $Preset) }
if (-not [string]::IsNullOrWhiteSpace($AspectRatio)) { $pyArgs += @('--aspect-ratio', $AspectRatio) }
if (-not [string]::IsNullOrWhiteSpace($Resolution)) { $pyArgs += @('--resolution', $Resolution) }
foreach ($ref in $ReferencePath) {
    if (-not [string]::IsNullOrWhiteSpace($ref)) {
        $pyArgs += @('--reference-path', $ref)
    }
}
if (-not [string]::IsNullOrWhiteSpace($ReferencePaths)) {
    $pyArgs += @('--reference-paths', $ReferencePaths)
}
if ($DryRun) { $pyArgs += '--dry-run' }
if ($TimeoutSec -gt 0) { $pyArgs += @('--timeout-sec', [string]$TimeoutSec) }

$python = $null
$pythonPrefix = @()
foreach ($candidate in @(
        @{ Exe = 'py'; Prefix = @('-3') },
        @{ Exe = 'python'; Prefix = @() },
        @{ Exe = 'python3'; Prefix = @() }
    )) {
    $cmd = Get-Command $candidate.Exe -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    & $candidate.Exe @($candidate.Prefix + '--version') 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $python = $candidate.Exe
        $pythonPrefix = $candidate.Prefix
        break
    }
}
if (-not $python) {
    throw "Python not found. Install Python 3.10+ or ensure py -3 is on PATH."
}

& $python @($pythonPrefix + $pyArgs)
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
