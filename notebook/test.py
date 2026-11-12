s = "Python"
# print(s[::-1])

lst = [1,2,3,2,4,1]
seen = set()
duplicate = set()

for item in lst:
    if item in seen:
        duplicate.add(item)
    else:
        seen.add(item)


print("Duplicate",duplicate)

dups = set([x for x in lst if lst.count(x) > 1])

print("New Approach", dups)