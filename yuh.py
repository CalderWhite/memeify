r = open("WaveListener.py").read()

x = 0
while True:
    r2 = r.replace("pass", "print(%s)" % x, 1)
    if r2 == r:
        break
    
    x += 1
    r = r2

open("WaveListener.py",'w').write(r)
