n = input()
n = int(n)

if(n >= 0):
    hasil = (n * (n + 1))/2
    print(int(hasil))
    
else:
    sum = 0
    for x in range(n, 0):
        sum = sum + x
    print(sum)