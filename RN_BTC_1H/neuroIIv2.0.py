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
print('####  Welcome to NEURO_II_v2.0 by SShow ################')
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
	



input('pulisco temp?')
for i in range(len(DB1)):
	os.remove(direct+'h2/h1/N1_log_'+str(i)+'.npy')













	
	
	
	
	
	
nx=int(5) #DIVENTA INPUT #minuti
lx=nx/60 #ore
tx=seconds+lx*60*60 #secondi

def azzardo():
	azz=0.5	
	for i in range(nx):
		y_x=m3_q3(Area3,l3)[0]*lx+m3_q3(Area3,l3)[1]
		p_y=(p/sig0)*y_x
		azz.append(y_x)
		azz_p.append(p_y)
	return azz,azz_p
#pred=azzardo()[0]
#prezzi_azzardo=azzardo()[1]
	
#print('Azzardo',pred)
#print('Prezzi azzardo', prezzi_azzardo)

##
print('!!!!!!!!!!!!!!!!!!SIAMO IN AGGUATO!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!SIAMO IN AGGUATO!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!SIAMO IN AGGUATO!!!!!!!!!!!!!!!!!!!!')
#print('Devo aspettare',nx*60, 'secondi')

go=input('GO')
def spetta():
	t=nx*60
	conta=0
	for i in range(t):
		print(conta)
		conta=conta+1
		time.sleep(1)
	return print('FINE ATTESA')
spetta()
print('!!!!!!!!!!!!!!!!!!A G G U A T O!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!A G G U A T O!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!A G G U A T O!!!!!!!!!!!!!!!!!!!!')


#DEFINISCO FUNZIONI N_II
input('Procedo???')
##########################################

def area(m,q,l):
	def y(x):
		y=m*x + q
		return y
	yi=y(1)
	yf=y(1+l)
	h=yf-yi
	area=(1+l)*h
	
	return area

Area1=area(-0.002676274215359397,0.6396558483680869,l1)
Area2=area(0.0010881214655276252,0.5269780208902707,l2)

print('Area1', Area1)
print('Area2', Area2)


##################################################

l3=float((l1+l2)/2)

w1,w2,b=rd.random(),rd.random(),rd.random()

def A3(A1,A2):
	
	area3=w1*A1+w2*A2+b
	
	return area3
	
	
Area3=A3(Area1,Area2)
print('Area3',Area3)


##################################################

def m3_q3(A3,elle3):
	h=(A3*2)/elle3
	xi=0
	xf=elle3
	yi=sig0
	yf=h
	m3=(yf-yi)/(xf-xi)
	q3=sig0-m3*elle3
	return m3,q3,h

##################################################
#DISEGNO IL TRIANGOLO A3
seconds=time.time()
print('Data e ora>',time.ctime(seconds))

t3=seconds+l3*60*60
m3=m3_q3(Area3,l3)[0]
q3=m3_q3(Area3,l3)[1]

print('T3',l3,'Quindi il', time.ctime(t3),'y3',)

print('m3>',m3_q3(Area3,l3)[0],'q3>',m3_q3(Area3,l3)[1],'Y3',m3*l3-m3*0+sig0)


#disegno il triangolo Ax


############################################################


def normalize(vettore):
	normale=np.linalg.norm(vettore)
	norm=vettore/normale
	return norm

#SU IPOTENUSA DI A3 CHIEDO Y PREZZO E SEGNALE DOPO X MINUTI
#######################################################
nx=int(5) #DIVENTA INPUT
lx=nx/60
tx=seconds+lx*60*60

def AreaX(A3,x):
	h=x*m3_q3(Area3,l3)[0]+m3_q3(Area3,l3)[1]
	area=(x*h)/2
	return area
	 
print('Stampo Area x', AreaX(Area3,nx))

def azzardo():
	
	azz=[sig0]
	azz_p=[p]
	
	for i in range(nx):
		y_x=m3_q3(Area3,l3)[0]*lx+m3_q3(Area3,l3)[1]
		p_y=(p/sig0)*y_x
		azz.append(y_x)
		azz_p.append(p_y)
	return azz,azz_p
pred=azzardo()[0]
prezzi_azzardo=azzardo()[1]
	
print('Azzardo',pred)
print('Prezzi azzardo', prezzi_azzardo)

##
print('!!!!!!!!!!!!!!!!!!SIAMO IN AGGUATO!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!SIAMO IN AGGUATO!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!SIAMO IN AGGUATO!!!!!!!!!!!!!!!!!!!!')
#print('Devo aspettare',nx*60, 'secondi')

go=input('GO')
def spetta():
	t=nx*60
	conta=0
	for i in range(t):
		print(conta)
		conta=conta+1
		time.sleep(1)
	return print('FINE ATTESA')
spetta()
print('!!!!!!!!!!!!!!!!!!A G G U A T O!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!A G G U A T O!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!A G G U A T O!!!!!!!!!!!!!!!!!!!!')




############################
#GENERA TARGET ZONE#########
############################

################
#Modulo Request
################



query={'symbol':'BTCUSDT', "interval":"1m",'limit':nx+1}
r=requests.get('https://api.binance.com/api/v3/klines', params=query)
response=json.loads(r.text)

#print(response)
#print(type(response))
#print(len(response))
print('Esco da request')

############################################################################
#Modulo Numpy, crea array
################################################################################

response_array=np.asarray(response)
response_array=np.array(response_array).astype(np.float64)

print('Response Array', response_array)

########################################################


#########################################################
def genera_target():
	target=[p]
	for i in range(nx):
		media=((response_array[i][1])+(response_array[i][4]))/2
		target.append(media)
	print('#Genero Medie ultimi',nx,'minuti', target)
	return np.array(target).astype(np.float64)
	
vettore_target_nonorm=genera_target()
vettore_target=normalize(vettore_target_nonorm)

print('Azzardo',pred)
print('vettore target', vettore_target)

#########################################################
	

def train(T,P):
	w1=rd.random()
	w2=rd.random()
	b=rd.random()
	iterazioni=500
	learning_rate=0.5
	errore=[]
	previsione=P
	errore=[]
	print('Previsione',P)
	
	for k in range(nx+1):
		
		print('K vale',k)
		print('Azzardo di k vale', P[k])
		
		for i in range(iterazioni):
			m=m3_q3(Area3,50)[0]
			q=m3_q3(Area3,50)[1]
			z= k*m*(1+w1)+q*(1+w2)+b
			pred=sigmoide(z)
			target=sigmoide(T[k])
			#print('Target',target)
			cost=(2*pred-2*target)**2
			#print('Errore', cost)
			errore.append(cost)
			#print('pred',pred)
			dcost_dpred=2*(2*pred-2*target)
			dpred_dz=sigmoide_p(z)
			dz_dw1=k*m
			dz_dw2=q
			dz_db=1
			dcost_dz=dcost_dpred*dpred_dz
			dcost_dw1=dcost_dz*dz_dw1
			dcost_dw2=dcost_dz*dz_dw2
			dcost_db=dcost_dz*dz_db
			w1=w1-learning_rate*dcost_dw1
			w2=w2-learning_rate*dcost_dw2
			b=b-learning_rate*dcost_db
		#plt.plot(errore)
		#plt.show()
		print('Azzardo Ricalcolato', np.arcsin(pred),'sigmoide', pred, 'prezzo',p*(np.arcsin(pred)/sig0))
		print('Target T[k]', vettore_target[k], 'sigmoide', target)
		#time.sleep(2)
	
	#print('Pesi',w1,w2,b)
	
	return w1,w2,b




print('Pesi',train(vettore_target,pred))
print('$$$$$>>>>>>>>>>>>>>>>>>>>>>>>>>$$$$$$$$$$$$$$$$$$$$$$$$$')
print('####  Goodbye to NEURO_II_v1.0 by SShow ################')
print('$$$$>>>>>>>>>>>>>>>>>>>>>>>>>>>$$$$$$$$$$$$$$$$$$$$$$$$$')


