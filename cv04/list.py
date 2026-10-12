def test_fun():
    i = 5
    j = 4
    return i,j


lst = [1, "ahoj", None] #LIst
#indexovatelny
print(lst[0])
print(len(lst))
for item in lst:
    print(item)
    
if 1 in lst:
    pass

lst.append(7) #prida 7 na konec
del lst[1] #smaze vec na prvnim indexu



lst[-1] = 5 #posledni prvek

i, j = test_fun()

tpl = (1,2,3) #Tuple
#indexovatelny
print(tpl[0])
print(len(tpl))
for item in tpl:
    print(item)
    
    
st = {1,2,3,4,5,6} #Set
#neindexovatelny
print(len(st))
for item in st:
    print(item)
    
    
#slovnik - klic => hodnota
dct = {
    "key": "value",
    1   :   5
}
print(dct["key"])