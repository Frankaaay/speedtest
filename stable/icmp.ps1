# ����Ŀ�������Ͳ��Դ���
$target = "www.baidu.com"
$count = 10

# ��ʼ����ʱ�б�
$latencies = @()

# ѭ�����͵���ping����
for ($i = 1; $i -le $count; $i++) {
    $result = Test-Connection $target -Count 1
    $latencies += [int]$result.ResponseTime
    # Start-Sleep -Milliseconds 10  # ��ѡ����Ӷ��ݵ���ʱ�Ա������Ƶ��������
}

Write-Output $latencies

# ����ƽ����ʱ
$averageLatency = ($latencies | Measure-Object -Average).Average
Write-Output "Average Latency to $target : $averageLatency ms"

# ���㶶������ʱ�ı�׼�
$jitter = ($latencies | Measure-Object -StandardDeviation).StandardDeviation
Write-Output "Jitter to $target : $jitter ms"
