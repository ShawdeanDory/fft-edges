param([int]$Workers=4)
$taskRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$taskRun = Join-Path $taskRoot 'results/course_rgb_main200/run_20261027_01'
if ($Workers -lt 1 -or $Workers -gt 4) { throw 'Workers must be1..4' }
$taskLock = Get-Content -LiteralPath (Join-Path $taskRun 'parameters_locked.json') -Raw | ConvertFrom-Json
if ($taskLock.methods.Count -ne 6 -or $taskLock.parameterSearch) { throw 'Invalid lock' }
$taskJobs = @()
for ($taskWorker = 1; $taskWorker -le $Workers; $taskWorker++) {
    $taskLog = 'results/course_rgb_main200/run_20261027_01/worker_{0}.log' -f $taskWorker
    $taskExpression = '"addpath(''matlab'');run_course_rgb_main200({0}:{1}:200);"' -f $taskWorker,$Workers
    $taskArgs = @('-nojvm','-singleCompThread','-logfile',$taskLog,'-batch',$taskExpression)
    $taskProcess = Start-Process -FilePath 'C:\Program Files\MATLAB\R2026b\bin\matlab.exe' -ArgumentList $taskArgs -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru
    $taskJobs += [pscustomobject]@{worker=$taskWorker;pid=$taskProcess.Id;log=$taskLog;started=(Get-Date).ToString('o')}
}
$taskJobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRun 'processes.json') -Encoding UTF8
$taskJobs | Format-Table worker,pid,log
