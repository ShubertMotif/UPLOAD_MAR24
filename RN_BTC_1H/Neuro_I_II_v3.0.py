
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
print('####  Welcome to RETE-NEURALEv2.0 by SSHOW ################')
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
print('\n log v1.1 Media ponderata \n log v1.2 Aggiorno stati grafici, bug seconda retta \n log 1.3 implemento impostazioni da JSON \n log v1.3.1 implemento learning rate e numero iterazioni nel JSON \n log v2.0 Massimi/Minimi sul grafico')
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
###############
import json
import os
###############
#CARICO PARAMETRI
#LA DIRECTORY E' DA IMPOSTARE A MANO!!!!!!!!!!
full_path = os.path.realpath(__file__)
direct=str('/home/linuz/PycharmProjects/UPLOAD_MAR24/RN_BTC_1H/')

f=open(direct+'config.json')
impostazioni=json.load(f)
print('LEGGO INFO NEL JSON')
configurazione=impostazioni['name']
simbolo=impostazioni['simbolo']
ore_locali=impostazioni['ore']
intervallo=impostazioni['intervallo']
n_iterazioni=impostazioni['iterazioni']
LR=impostazioni['learning_rate']


print('#########\n',configurazione,'\n #########','\n SIMBOLO_',simbolo,'\n ORE_',ore_locali,'\n INTERVALLO_',intervallo, '\n Iterazioni',n_iterazioni, '\n learning rate', LR)

input('Procedo?')
############################################################################
#################################

import BGC
#import DB
import numpy as np
import math as mt
import random as rd
import matplotlib
matplotlib.use('TkAgg')  # Usa il backend TkAgg per Matplotlib

# Ora puoi importare gli altri moduli Matplotlib
import matplotlib.pyplot as plt

import seaborn as sns
import time
import zipfile
import os
from scipy.signal import argrelextrema
############

input('Procedo?')

#variabile delta-t
print("Quante ore vuoi considerare?")
ore=int(100)


############################################

def sigmoide(t):
    return 1/(1+mt.exp(-t))
################################################

#definiamo la derivata
def sigmoide_p(t):
    return sigmoide(t)*(1-sigmoide(t))

#################################################
def normalize(vettore):
	minimo=np.sort(vettore)[0]
	massimo=np.sort(vettore)[-1]
	#print('massimo', massimo)
	#print('minimo', minimo)
	norm=[]
	for i in range(len(vettore)):
		normale=(vettore[i]-minimo)/(massimo-minimo)
		norm.append(normale)
		
	#print('Norma', norm)
	return norm

##################################################

def seed_dati():
	dataset=[]
	p_medi=normalize(BGC.genera_prezzi_medi())
	valori_rsi=normalize(BGC.calcola_RSI())
	volumi=normalize(BGC.genera_volumi())
	#print('Stampo p_medi', p_medi)
		
	for i in range(len(p_medi)):
		data=[]
		data.append(p_medi[i])
		data.append(valori_rsi[i])
		data.append(volumi[i])
		dataset.append(data)

	return dataset
	
dati=seed_dati()

#print('Data', dati)
#########################################################

def stampo_grafico(vettore):
	lista=[]
	for i in range(ore):
		lista.append(vettore[i])
	plt.plot(lista)
	plt.ylabel('Segnale')
	plt.xlabel('Ore')
	plt.xticks(range(10, 10))
	plt.grid(True,linewidth=0.5,color='#cccccc',linestyle='-')
	return plt.show()
	
#########################################################
def genera_prezzi(dataset):
	prezzi=[]
	for i in range(len(dataset)):
		prezzi.append(dataset[i][0])
	return prezzi
	
############################################################


#genero segnale

print('RETE')

def genera_segnale():
	segnali=[]
	for i in range(len(dati)):
		point=dati[i]
		segnale=(point[0]+point[1]+point[2])/3
		#print('Segnale', segnale)
		segnali.append(segnale)
	return segnali

#print('Genero Segnali')
	
sig=genera_segnale()
sig_norm=normalize(sig)

#print('Segnali', sig)

outsig=[]
for i in range(len(sig)):
	outsig.append(sig_norm[i])
	
#################V1.4 Selezioniamo Max/min in automatico con scipy


MIN_LIST=argrelextrema(np.array(outsig), np.less)
MAX_LIST=argrelextrema(np.array(outsig), np.greater)

print('X MINIMI', MIN_LIST, '\n X MASSIMI',MAX_LIST)



leX_min=[]
leY_min=[]
for LIST in MIN_LIST:
	print(LIST)
	for x in LIST:
		print(x)
		print(outsig[x])
		leX_min.append(x)
		leY_min.append(outsig[x])
		for i_leX_min,i_leY_min in zip(leX_min,leY_min):
			plt.text(i_leX_min,i_leY_min,'({},{:.2f})'.format(i_leX_min,i_leY_min))

leX_max=[]
leY_max=[]
for LIST in MAX_LIST:
	print(LIST)
	for x in LIST:
		print(x)
		print(outsig[x])
		leX_max.append(x)
		leY_max.append(outsig[x])
		for i_leX_max,i_leY_max in zip(leX_max,leY_max):
			plt.text(i_leX_max,i_leY_max,'({},{:.2f})'.format(i_leX_max,i_leY_max))

plt.plot(range(0,101),outsig,label='SIG')
plt.plot(leX_min,leY_min,'X',label='minimi')
plt.plot(leX_max,leY_max,'X',label='massimi')
#plt.plot(range(1,101),outsig)
plt.legend()
plt.draw()
input('Procedo?')

#####################################################################

print('X MINIMI', MIN_LIST, '\n X MASSIMI',MAX_LIST)

MIN_COORD=[]
for i in MIN_LIST:
	print(i)
input('Procedo?')

###########################
	

def deriva_segnale(sig):
	derivate=[]
	for i in range(len(sig)-1):
		delta_assoluto=abs(sig[i]-sig[i+1])
		derivate.append(delta_assoluto)
	
	massimo=max(derivate)
	
	prima=[]
	dopo=[]
	is_max=False
	for i in range(len(derivate)):
		
		if derivate[i]==massimo:
			dopo.append(derivate[i])
			is_max=True
		elif is_max==False:
			prima.append(derivate[i])
			
		else:
			dopo.append(derivate[i])
	
	return massimo,prima,dopo;
		
print('Max Derivate', deriva_segnale(sig)[0])
print('Prima',len(deriva_segnale(sig)[1]),'elementi' )
print('Dopo', len(deriva_segnale(sig)[2]), 'elementi')

#########################################################

len_R=int(len(deriva_segnale(sig)[1]))

print('Len R',len_R)

conta_stati=[]

def stati_grafici(r):
	n_min=int(input('Quanti BUY?'))
	n_max=int(input('Quanti SELL?'))
	x_buy=[]
	x_sell=[]
	
	if len(conta_stati)==0:
		diff=0
	else:
		diff=len_R
	print('DIFFERENZA',diff)
	input('Procedo?')
		
	for i in range(n_min):
		x_min=int(input('Dammi X de BUY'))
		x_buy.append(x_min-diff)
	for i in range(n_max):
		x_max=int(input('Dammi X de SELL'))
		x_sell.append(x_max-diff)
	stati=[]
	stati.append(x_buy)
	stati.append(x_sell)
	target=[]
	print('Stati', stati)
	input('Procedo?')
	
	for i in range(r):
		if i in stati[0]:
			target.append(0)
			print(i,'=BUY')
		elif i in stati[1]:
			target.append(1)
			print(i,'=SELL')
		else:
			target.append(0.5)
			print('NOTHING')
	conta_stati.append(1)
	return target

target_r=stati_grafici(len_R)

len_S=int(len(deriva_segnale(sig)[2]))

print('Len R',len_S)

target_s=stati_grafici(len_S)

print('########################')
print('Target R',target_r)
print('########################')
print('Target S',target_s)
print('########################')

#####################
print('Taglio il DB')

def taglia_db():
	p=sig[:int(len_R)]
	d=sig[int(len(sig)-len_S):]
	return p,d
	
print('Prima>',taglia_db()[0])
print('Dopo>',taglia_db()[1])
prima=taglia_db()[0]
dopo=taglia_db()[1]


#Grafico Distribuzione
#sns.boxplot(data=taglia_db())
#plt.show()
################################################################
def crea_rette(r,T):
	mediay=np.mean(r)
	dev=np.std(r)
	x=np.arange(1+len(r))
	mediax=np.mean(x)
	sx=[]
	sy=[]
	sxy=[]
	sx2=[]
	RSSv=[]
	TSSv=[]
	ESSv=[]
	for i in range(len(r)):
		scx=float(x[i]-mediax)
		scx2=float(scx**2)
		scy=float(r[i]-mediay)
		sy_x=scy*scx
		sx2.append(scx2)
		sx.append(scx)
		sy.append(scy)
		sxy.append(sy_x)
	

	m=(np.sum(sxy)/np.sum(sx2))
	q=np.average(r)-m*mediax
	def y(xi):
		return m*xi-q
	Yr=[]
	#dammix=int(input('Dammi x'))
	#print('Y=', y(dammix))
	for i in range(len(r)):
		yr=y(r[i])
		tss=float((r[i]-mediay)**2)
		rss=float((r[i]-yr)**2)
		ess=float(yr-mediay)
		Yr.append(yr)
		ESSv.append(ess)
		RSSv.append(rss)
		TSSv.append(tss)
	
	R2=float((np.sum(ESSv)/np.sum(TSSv)))

	
	#for i in range(len(r)):
		#print('Conto x=',i)
		#t=i*w1*m+q*w2+b
		#print('Target casuale',t)

	def train(T):
		w1=rd.random()
		w2=rd.random()
		b=rd.random()
		iterazioni=n_iterazioni
		learning_rate=LR
		errore=[]
		W1=[]
		W2=[]
		B=[]
		
		ysig=r[0]
			#errore=[]
			#print('Pesi',w1,w2,b)
		for i in range(iterazioni):
			z= 0*m*(w1)+q*(w2)+b
			pred=sigmoide(z)
			target=T[0]
			#print('Target',target)
			cost=(pred-target)**2
			#print('Errore', cost)
			#errore.append(cost)
			#print('pred',pred)
			dcost_dpred=2*(pred-target)
			dpred_dz=sigmoide_p(z)
			dz_dw1=0*m
			dz_dw2=q
			dz_db=1
			dcost_dz=dcost_dpred*dpred_dz
			dcost_dw1=dcost_dz*dz_dw1
			dcost_dw2=dcost_dz*dz_dw2
			dcost_db=dcost_dz*dz_db
			w1=w1-learning_rate*dcost_dw1
			w2=w2-learning_rate*dcost_dw2
			b=b-learning_rate*dcost_db
		#print('Pesi',w1,w2,b)
		W1.append(w1)
		W2.append(w2)
		B.append(b)
		
		w1=W1[0]
		w2=W2[0]
		b=B[0]
		
		for k in range(len(r)):
			w1=np.mean(W1)
			w2=np.mean(W2)
			b=np.mean(B)
			#print('K vale',k)
			ysig=r[k]
			#errore=[]
			#print('Pesi',w1,w2,b)
			for i in range(iterazioni):
				z= k*m*(w1)+q*(w2)+b
				pred=sigmoide(z)
				target=T[k]
				#print('Target',target)
				cost=(pred-target)**2
				#print('Errore', cost)
				errore.append(np.average(W1))
				#print('pred',pred)
				dcost_dpred=2*(pred-target)
				dpred_dz=sigmoide_p(z)
				dz_dw1=k*m
				dz_dw2=q
				dz_db=0
				dcost_dz=dcost_dpred*dpred_dz
				dcost_dw1=dcost_dz*dz_dw1
				dcost_dw2=dcost_dz*dz_dw2
				dcost_db=dcost_dz*dz_db
				w1=w1-learning_rate*dcost_dw1
				w2=w2-learning_rate*dcost_dw2
				b=b-learning_rate*dcost_db
			#print('Pesi',w1,w2,b)
			W1.append(w1)
			W2.append(w2)
			B.append(b)
			
		w1=np.average(W1)
		w2=np.average(W2)
		b=np.average(B)
		print('HO ITERATO RETTA')
		
		plt.plot(errore)
		plt.show()
		return w1,w2,b
        #print('calcoliamo tutte le derivate parziali')
        
	w1,w2,b=train(T)

	print('Return Train',w1,w2,b)		
	
	print('R2',R2)	
	#print('Scarti X',sx)	
	#print('scarti Y',sy)
	print('Rapporto angolare m>',m, 'Intercetta Q',q)
	print('Rapporto angolare corretto mw1>',m*(1+w1), 'Intercetta Q corretta>', q*(1+w2))
	return [m,q,len(r),w1,w2,b]
	
r1=crea_rette(prima,target_r)
r2=crea_rette(dopo,target_s)



lg=np.array([r1[0],r1[1],r1[2],r1[3],r1[4],r1[5],r2[0],r2[1],r2[2],r2[3],r2[4],r2[5]])
print('lg',lg)

################################################
#neurone II
################################################
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
	
plt.plot(X1,Y1, label='Prima Previsione')
plt.plot(X2,Y2, label='Seconda Previsione')

######################################################
#STAMPA LE RETTE
#######################################################

mR=float(lg[0])
w1R=float(lg[3])
qR=float(lg[1])
w2R=float(lg[4])
le_xR=range(0,int(lg[2]))
biasR=float(lg[5])

mS=float(lg[6])
w1S=float(lg[9])
qS=float(lg[7])
w2S=float(lg[10])
le_xS=range(int(lg[2]),int(ore_locali))
biasS=float(lg[11])

def crea_vettore_retta(m,q,w1,w2,bias,X):
	le_y=[]
	def Y(x):
		y=m*x*w1+q*w2 + bias
		return y
	for i in X:
		y=Y(i)
		le_y.append(y)
	return le_y
	
			
le_yR=crea_vettore_retta(mR,qR,w1R,w2R,biasR,le_xR)
le_yS=crea_vettore_retta(mS,qS,w1S,w2S,biasS,le_xS)

etichetta_R='m°w_>'+str(mR*w1R)+'__q°w_>'+str(qR*w2R)
etichetta_S='m°w_>'+str(mS*w1S)+'__q°w_>'+str(qS*w2S)

plt.plot(le_xR,le_yR,label=etichetta_R)
plt.plot(le_xS,le_yS,label=etichetta_S)
plt.plot(range(0,101),outsig,label='segnale')

plt.legend()		
plt.show()

######################################################
#ARCHIVIA I RISULTATI
#######################################################

archivio= zipfile.ZipFile(direct+'Data_base.zip')
x='N1_log_'+str(len(archivio.namelist()))+'.npy'
archivio.close()
print('X =',x)

np.save(direct+'h1/'+x,lg)
print('Salvo Log')

archivio= zipfile.ZipFile(direct+'Data_base.zip','a')
nome=direct+'h1/'+x

archivio= zipfile.ZipFile(direct+'Data_base.zip','a')

archivio.write(nome, compress_type=zipfile.ZIP_DEFLATED)

archivio.close()

archivio= zipfile.ZipFile(direct+'Data_base.zip','a')
print(archivio.namelist())
archivio.close()

input('pulisco temp?')
os.remove(nome)




#############################################################
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
print('####  Goodbye to RETE-NEURALEv2.0 by SShow ################')
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
