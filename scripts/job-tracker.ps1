<#
.SYNOPSIS
  Job application tracker helper. Works on tracker.csv in the JobSearch folder.

.EXAMPLES
  .\scripts\job-tracker.ps1 add -Company "Acme" -Role "QA Engineer" -Location "Pune" -Link "https://..."
  .\scripts\job-tracker.ps1 followups     # applications needing a nudge today
  .\scripts\job-tracker.ps1 stats         # pipeline overview
  .\scripts\job-tracker.ps1 list          # all rows, compact
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('add', 'followups', 'stats', 'list')]
    [string]$Command = 'stats',

    [string]$Company,
    [string]$Role,
    [string]$Location,
    [string]$Link,
    [string]$Source = 'LinkedIn',
    [string]$Status = 'Applied',
    [string]$Notes = '',
    [int]$FollowUpDays = 6
)

$ErrorActionPreference = 'Stop'
$csvPath = Join-Path $PSScriptRoot '..\tracker.csv'
$csvPath = (Resolve-Path $csvPath).Path

function Get-Rows { Import-Csv -Path $csvPath }

switch ($Command) {

    'add' {
        if (-not $Company -or -not $Role) {
            Write-Host "Need at least -Company and -Role." -ForegroundColor Red
            Write-Host 'Example: .\scripts\job-tracker.ps1 add -Company "Acme" -Role "QA Engineer" -Location "Pune" -Link "https://..."'
            break
        }
        $rows = @(Get-Rows)
        $nextId = 1
        if ($rows.Count -gt 0) {
            $nextId = ([int]($rows[-1].ID)) + 1
        }
        $today = Get-Date -Format 'yyyy-MM-dd'
        # Leads (e.g. link-sent) have no applied/follow-up date; applied rows do.
        $isApplied = $Status -eq 'Applied'
        $dateApplied = if ($isApplied) { $today } else { '' }
        $followUp = if ($isApplied) { (Get-Date).AddDays($FollowUpDays).ToString('yyyy-MM-dd') } else { '' }
        $new = [PSCustomObject]@{
            'ID'            = $nextId
            'Date Added'    = $today
            'Company'       = $Company
            'Role'          = $Role
            'Location'      = $Location
            'Source'        = $Source
            'Job Link'      = $Link
            'Status'        = $Status
            'Date Applied'  = $dateApplied
            'Follow-up Date' = $followUp
            'Contact Name'  = ''
            'Contact Email' = ''
            'Resume Used'   = ''
            'Notes'         = $Notes
        }
        $all = $rows + $new
        $all | Export-Csv -Path $csvPath -NoTypeInformation
        Write-Host "Added #$nextId : $Role @ $Company [$Status]" -ForegroundColor Green
    }

    'followups' {
        $today = Get-Date
        $due = Get-Rows | Where-Object {
            $_.Status -eq 'Applied' -and $_.'Follow-up Date' -and
            ([datetime]::ParseExact($_.'Follow-up Date', 'yyyy-MM-dd', $null) -le $today)
        }
        if (-not $due) {
            Write-Host "No follow-ups due today. Nice." -ForegroundColor Green
            break
        }
        Write-Host "`nFollow-ups DUE:" -ForegroundColor Yellow
        $due | Format-Table ID, Company, Role, 'Date Applied', 'Follow-up Date' -AutoSize
    }

    'stats' {
        $rows = @(Get-Rows | Where-Object { $_.Company -and $_.Company -ne 'EXAMPLE Corp' })
        if ($rows.Count -eq 0) {
            Write-Host "No applications logged yet. Add one with the 'add' command." -ForegroundColor Cyan
            break
        }
        Write-Host "`n=== Pipeline ($($rows.Count) total) ===" -ForegroundColor Cyan
        $rows | Group-Object Status | Sort-Object Count -Descending |
            ForEach-Object { "{0,-12} {1}" -f $_.Name, $_.Count }
        $applied = ($rows | Where-Object { $_.Status -ne 'Lead' }).Count
        $responded = ($rows | Where-Object { $_.Status -in 'Screening', 'Interview', 'Offer' }).Count
        if ($applied -gt 0) {
            $rate = [math]::Round(($responded / $applied) * 100, 1)
            Write-Host "`nResponse rate: $responded / $applied = $rate%" -ForegroundColor Cyan
        }
    }

    'list' {
        Get-Rows | Where-Object { $_.Company -and $_.Company -ne 'EXAMPLE Corp' } |
            Format-Table ID, Company, Role, Status, 'Date Applied', 'Follow-up Date' -AutoSize
    }
}
