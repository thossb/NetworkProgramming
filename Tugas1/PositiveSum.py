N = int(input())

positive_sum = 0

for _ in range(N):
    number = int(input())
    if number > 0:
        positive_sum += number

print(positive_sum)