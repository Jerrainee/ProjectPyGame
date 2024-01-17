lst = []

for X in range(2):
    for Y in range(2):
        for Z in range(2):
            result = not((X and Y) and (not(X) or X)) and (Z == Y)
            print(X, Y, Z, int(result))
