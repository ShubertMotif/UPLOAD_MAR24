#import BGC
import numpy as np
import math as mt
import random as rd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import requests
import json
import zipfile
import os

print('$$$$$>>>>>>>>>>>>>>>>>>>>>>>>>>$$$$$$$$$$$$$$$$$$$$$$$$$')
print('####  Welcome to NEURO_II_v2.1 by SShow ################')
print('$$$$>>>>>>>>>>>>>>>>>>>>>>>>>>>$$$$$$$$$$$$$$$$$$$$$$$$$')
#DEFINISCO FUNZIONI DI BASE
############################################

def sigmoide(t):
    return 1/(1+mt.exp(-t))
################################################

#definiamo la derivata
def sigmoide_p(t):
    return sigmoide(t)*(1-sigmoide(t))

#################################################

def area(m,q,l,w1,w2):
	def y(x):
		y=m*(1+w1)*x + q*(1+w2)
		return y
	yi=y(1)
	yf=y(1+l)
	h=yf-yi
	area=((1+l)*h)/2
	
	return area
################################################
#DEFINISCO VARIABILI DI AMBIENTE
rd.seed(1)

direct='/home/linuz/RN_BTC_1H/'

archivio=zipfile.ZipFile(direct+'Data_base.zip')

indice=archivio.namelist()

archivio.extractall(direct+'h2')

DB1=[]
date_modifica=[]
for i in range(len(indice)):
	data=np.load(direct+'h2/'+indice[i])
	m1=data[0]
	q1=data[1]
	l1=data[2]
	w11=data[3]
	w12=data[4]
	
	
	m2=data[6]
	q2=data[7]
	l2=data[8]
	w21=data[9]
	w22=data[10]
	
	aree=[area(m1,q1,l1,w11,w12),area(m2,q2,l2,w21,w22)]
	DB1.append(aree)

print('DATABASE AREE')
print(DB1)

def prezzo_ora():
	query={'symbol':'BTCUSDT'}
	r=requests.get('https://api.binance.com/api/v3/avgPrice', params=query)
	response=json.loads(r.text)
	p=response["price"]
	return float(p)

p=prezzo_ora()

seconds=time.time()
print('Data e ora>',time.ctime(seconds))
print('>>>>>>>>>>>Prezzo ora>>>>>>>>>>>>', p)

w1,w2,b=rd.random(),rd.random(),rd.random()

x=5

def A3(A1,A2):
	
	area3=w1*A1+w2*A2+b
	
	return area3

def m3_q3(A3,elle3):
	h=(A3*2)/elle3
	xi=0
	xf=elle3
	yi=0.5
	yf=h
	#print('Area 3',A3,'Yf',yf)
	m3=(yf-yi)/(xf-xi)
	q3=0.5-m3*elle3
	return m3,q3,h

aree3=[]	
for i in range(len(DB1)):
	print('\n Coppia A1 A2 n_',i)
	area3=A3(DB1[i][0],DB1[i][1])
	print('\n A3',area3)
	aree3.append(area3)
	m3=m3_q3(aree3[i],0.5)[0]
	q3=m3_q3(aree3[i],0.5)[1]
	print('m3>',m3,'\n q3>',q3)
	for i in range(x):
		y=m3*i+q3
		#print(y)
		
		
lastA3=aree3[-1]		
print('\n Ultima Area3',lastA3)

err_A3=[]
for i in range(len(DB1)-1):
	err=np.abs(aree3[i]-lastA3)
	err_A3.append(err)
	minore=np.amin(err_A3)
	point=err_A3.index(minore)
	print('###################')
	print('Point \n',point,' \n min_', minore)
	print('Iterazione n_',i,'\n Errore_',err,'\n Best coppia A1 A2 n_',point)
	#print('m',\n DB1[point][0],'\n q',\n DB1[point][1],\n'A3',\n area3 )




risultato=np.load(direct+'h2/'+indice[point])

print('###################')
print('###################')
print('###################')


print('Risultato Migliore n_',point, '\n m1_',risultato[0],'\n q1_',risultato[1], '\n l1_',risultato[2],'\n m2_',risultato[6], '\n q2_',risultato[7],'\n l2_',risultato[8])


### STAMPO RETTE


X1=[]
Y1=[]
for i in range(int(risultato[2])):
	x=i
	y=risultato[0]*x + risultato[1]
	X1.append(x)
	Y1.append(y)
	
X2=[]
Y2=[]
X2.append(X1[-1])
Y2.append(Y1[-1])

for i in range(int(risultato[8]-1)):
	x=i+risultato[2]
	y=risultato[6]*x + risultato[7]
	X2.append(x)
	Y2.append(y)
	
plt.plot(X1,Y1, label='Prima retta')
plt.plot(X2,Y2, label='Seconda retta')

plt.show()

	
input('Procedo??')
	
print('$$$$$>>>>>>>>>>>>>>>>>>>>>>>>>>$$$$$$$$$$$$$$$$$$$$$$$$$')
print('####  Goodbye to NEURO_II_v2.1 by SShow ################')
print('$$$$>>>>>>>>>>>>>>>>>>>>>>>>>>>$$$$$$$$$$$$$$$$$$$$$$$$$')


