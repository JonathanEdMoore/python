numList = list(range(1, 30))

i = len(numList) - 1
numOdd = 0

while (i >= 0) and (numOdd < 2):
    if numList[i] % 2 != 0:
        print(numList[i])
        i -= 1
        numOdd += 1
    else:
        i -= 1