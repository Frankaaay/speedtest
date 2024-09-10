import multi3
from common import *

obj = multi3.ProxySpeed('127.0.0.1:6210', '0.0.0.0')
for _ in range(10):
   obj.update()
   sleep(0.5)
   print(obj.res)
obj.stop()
pass