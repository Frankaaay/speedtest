param (
    [string]$Action = "Enable"  # 默认操作为启用
)

# 检查是否以管理员身份运行
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # 重新启动 PowerShell 并请求管理员权限，并传递参数
    Start-Process powershell.exe -Verb runAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Action $Action"
    exit
}

# 获取所有有线网络适配器
$wiredAdapters = Get-NetAdapter | Where-Object { $_.MediaType -eq "802.3" -and ($_.Name -like "Ethernet*" -or $_.Name -like "以太网*") }

if ($Action -eq "Enable") {
    $wiredAdapters | ForEach-Object {
        Enable-NetAdapter -Name $_.Name -Confirm:$false
        Write-Host "已启用网络适配器: $($_.Name)"
    }
} elseif ($Action -eq "Disable") {
    $wiredAdapters | ForEach-Object {
        Disable-NetAdapter -Name $_.Name -Confirm:$false
        Write-Host "已禁用网络适配器: $($_.Name)"
    }
} else {
    Write-Host "无效的操作参数。请使用 'Enable' 或 'Disable'。"
}

Start-Sleep -Milliseconds 800