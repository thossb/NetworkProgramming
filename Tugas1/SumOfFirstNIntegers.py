N = int(input())

if N >= 0:
    sum_N = N * (N + 1) // 2
else:
    N = -N
    sum_N = -(N * (N + 1) // 2)

# Output
print(sum_N)