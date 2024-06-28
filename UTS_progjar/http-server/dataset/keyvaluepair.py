n = int(input())
dict = {}

for i in range(n):
    key, value = input().split()
    dict[key] = int(value)
    
keyfind = input()

print(dict[keyfind])