
# coding: utf-8

# In[84]:


import sys 
sys.path.append(r'C:\users\ma303\appdata\local\programs\python\python36-32\lib\site-packages')
import jieba
import jieba.posseg
import jieba.analyse


#string = "台中好玩嗎?"
string =u'我想要去台北101'
stopw = [line.strip().encode('utf-8') for line in open(r'C:\Users\MA303\Desktop\toolong.txt',encoding = 'utf8').readlines()]
# print (str.join(set(default_mode)-set(stopw)))

seg = jieba.posseg.cut(string)

j = []
for i in seg:
    j.append((i.word))
print(j)
aa=len(stopw)
aa1=len(j)
a=0
a1=0
print(aa1)

for a in range(aa1):
    for a1 in range(aa):
        if j[a]==stopw[a1].decode('utf8') :
            j[a]=None
print(j)

string1 = ''
for i in j:
    if i:
        string1+=i
print(string1)
        
#     text.strip(stopw[a].decode('utf8'))
#         if string.find(stopw[a].decode('utf8'))>=0 :
#             print('yes')
#             dle = string.find(stopw[a].decode('utf8'))
#             dle_long=len(stopw[a].decode('utf8'))
#             dle2=dle+dle_long
#             string=string[:dle]+string[dle2:]
# print(string)

# for element in j:
#     print(element[0],element[1])
#     #if element[1] == 'ns':
#     #    print(element[0]+"是地名")
#     #else:
#     #    print('no')


# In[91]:


def hello(string_a, **kwargs):
    if world:
        print(string_a+"Hello World")
    else:
        print(string_a+"Hello")
    
string = "G"
hello(string, world=False)

