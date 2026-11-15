import re
s = open('game.c', encoding='latin-1').read()
strs = re.findall(r'"([^"]*)"', s)
total = sum(len(x) + 1 for x in strs)
print('num strings', len(strs), 'total incl NUL', total)
for x in sorted(set(strs), key=len, reverse=True):
    print(len(x), repr(x))
