# 定义目标主机和测试次数
$target = "www.baidu.com"
$count = 10

# 初始化延时列表
$latencies = @()

# 循环发送单个ping请求
for ($i = 1; $i -le $count; $i++) {
    $result = Test-Connection $target -Count 1
    $latencies += [int]$result.ResponseTime
    # Start-Sleep -Milliseconds 10  # 可选：添加短暂的延时以避免过于频繁的请求
}

Write-Output $latencies

# 计算平均延时
$averageLatency = ($latencies | Measure-Object -Average).Average
Write-Output "Average Latency to $target : $averageLatency ms"

# 计算抖动（延时的标准差）
$jitter = ($latencies | Measure-Object -StandardDeviation).StandardDeviation
Write-Output "Jitter to $target : $jitter ms"
