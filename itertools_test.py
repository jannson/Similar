import itertools

list1 = ['a','b','c']
list2 = ['11','22','abc']
for item in itertools.chain(list1, list2):
    print item
print '\n'

i = 0
for item  in itertools.count(100):
    if i > 10:
        break
    print item,
    i = i+1
print '\n'

i = 0
for item in itertools.cycle(list1):
    if i > 10:
        break
    print item,
    i = i+1
print '\n'

def funLargeFive(x):
    if x > 5:
        return True

for item in itertools.ifilter(funLargeFive, xrange(-10,10)):
    print item,
print '\n'

list3 = [1,2,3]
def funAddFive(x):
    return x+5
for item in itertools.imap(funAddFive, list3):
    print item,
print '\n'

list3 = list1+list2
for  item in itertools.islice(list3, 3,5):
    print item,
print '\n'

for item in itertools.repeat(list1,3):
    print item,

