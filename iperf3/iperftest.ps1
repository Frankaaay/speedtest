param (
    [string]$c,
    [int]$t,
    [int]$n
)

 echo "下载 Mb/s"; 
 1..$n | ForEach-Object {
    .\iperf3.exe  -c $c -t $t -P 12 -R -J | ConvertFrom-Json | ForEach-Object { $_.end.sum_received.bits_per_second / 1000000 }
 };

 echo "上传 Mb/s";
 1..$n | ForEach-Object {
    .\iperf3.exe  -c $c -t $t -P 12 -J | ConvertFrom-Json | ForEach-Object { $_.end.sum_received.bits_per_second / 1000000 }
 };