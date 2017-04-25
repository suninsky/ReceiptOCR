f=open('result','r')
result=f.read()
print ','.join(result.split('\n')[0:3])[0]