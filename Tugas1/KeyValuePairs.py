N = int(input())
pair = {}

for _ in range(N):
    key, value = input().split()
    pair[key] = int(value)

K = input()

print(pair[K])
