from subprocess import PIPE,Popen
from statistics import stdev,mean
def pings(target,n):
    # Use powershell Test-Connection
    run = Popen(["pwsh","-Command",f"0..{n}|Foreach-Object","{(Test-Connection",str(target),"-Count","1",").Latency}",],stdout=PIPE,stderr=PIPE)
    run.c
    out, err= run.communicate()
    print(out,err)
    res = list(map(int,out.decode().split()))
    return res

def ping_and_jit(target,n):
    data = pings(target,n)
    return (round(mean(data),2),round(stdev(data),2))

def main():
    print(ping_and_jit("www.baidu.com",2))

if __name__ == '__main__':
    main()