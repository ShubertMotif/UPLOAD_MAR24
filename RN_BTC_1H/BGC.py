#DA FARE

# >sistema tempi perchè binance utc2 e noi utc1
# >calcola un rsi a mano e conferma i timeframe


#Binance Richiedi Candele

import requests
import json
import time
import numpy as np
import matplotlib.pyplot as plt

print('##########################################################')
print('####WELCOME TO GESTORE_CANDELEv1.0 by Show################')
print('##########################################################')

################################################################################
#Modulo time
################################################################################

seconds=time.time()
print('Data e ora>',time.ctime(seconds))

utc1=seconds+1*60*60

print('UTC+2 Adesso', time.ctime(utc1))

################################################################################
#Modulo StartTime e EndTime
################################################################################

###############
#CARICO PARAMETRI
direct=str('/home/linuz/PycharmProjects/UPLOAD_MAR24/RN_BTC_1H/')
f=open(direct+'config.json')
impostazioni=json.load(f)
print('LEGGO INFO NEL JSON')
configurazione=impostazioni['name']
simbolo=impostazioni['simbolo']
ore_locali=impostazioni['ore']
intervallo=impostazioni['intervallo']
print('#########\n',configurazione,'\n #########','\n SIMBOLO_',simbolo,'\n ORE_',ore_locali,'\n INTERVALLO_',intervallo)

input('Procedo?')

############################################################################

ore=ore_locali+1
time.sleep(1)

############################################################################
#Modulo Request
################################################################################

query={'symbol':simbolo, "interval":intervallo,'limit':ore}
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
point=response_array[0][0]

########################################################


#########################################################
def genera_aperture():
	aperture=[]
	for i in range(ore):
		apertura=response_array[int(i)][1]
		aperture.append(apertura)
	print('#Genero Aperture', aperture)
	return np.array(aperture).astype(np.float64)
	
vettore_aperture=genera_aperture()

#########################################################
def genera_chiusure():
	chiusure=[]
	for i in range(ore):
		chiusura=response_array[int(i)][4]
		chiusure.append(chiusura)
	print('#Genero Chiusure', chiusure)
	return np.array(chiusure).astype(np.float64)
	
vettore_chiusure=genera_chiusure()

#########################################################
def genera_hight():
	altezze=[]
	for i in range(ore):
		hight=response_array[int(i)][2]
		altezze.append(hight)
	print('#Genero Altezze',altezze)
	return np.array(altezze).astype(np.float64)
	
vettore_altezze=genera_hight()

#########################################################
def genera_low():
	minimi=[]
	for i in range(ore):
		low=response_array[int(i)][3]
		minimi.append(low)
	print('#Genero Minimi',minimi)
	return np.array(minimi).astype(np.float64)
	
vettore_minimi=genera_low()

#########################################################
def genera_num_scambi():
	num_scambi=[]
	for i in range(ore):
		scambio=response_array[int(i)][8]
		num_scambi.append(scambio)
	print('#Genero Numero Scambi',)
	return np.array(num_scambi).astype(np.float64)
	
vettore_num_scambi=genera_num_scambi()

#########################################################
	
media_aperture=np.median(vettore_aperture,axis=0)
media_chiusure=np.median(vettore_chiusure,axis=0)

#########################################################
#
#def genera_aste():
#	sedute_rialzo=[]
#	sedute_ribasso=[]
#	
#	for i in range(ore):
#		print('#####################')
#		print('Time Frame',time.ctime((seconds-(ore-i-1)*3600)))
#		print('Apertura', vettore_aperture[i])
#		print('Chiusura', vettore_chiusure[i])
#		diff=vettore_chiusure[i]-vettore_aperture[i]
#		print ('Differenza', int(diff))
#		print('RSI Stocastico', int(vettore_RSI[i]))
#		if diff>0:
#			sedute_rialzo.append(diff)			
#		else: 
#			sedute_ribasso.append(diff)
#				
#	print('sedute_ribasso', sedute_ribasso)
#	print('Sedute_rialzo', sedute_rialzo)
#		
#
#########################################################
def max_min():
	vet_min=np.sort(vettore_minimi)
	vet_max=np.sort(vettore_altezze)
	min_max=[vet_min[1],vet_max[-1]]
	print('Minimi', vet_min)
	print('Massimi',vet_max)
	return min_max
vet_min_max=np.array(max_min())


#########################################################



def calcola_RSI():
	RSI_vet=[]
	for chiusura in vettore_chiusure:
		RSI=100*((chiusura-vet_min_max[0])/(vet_min_max[1]-vet_min_max[0]))
		RSI_vet.append(RSI)
	print('Vettore RSI',RSI_vet)
	return np.array(RSI_vet).astype(np.float64)

vettore_RSI=calcola_RSI()



#########################################################

def stampo_grafico():
	lista_RSI=[]
	for i in range(ore):
		lista_RSI.append(vettore_RSI[i])
	plt.plot(lista_RSI)
	plt.ylabel('RSI')
	plt.xlabel('Ore')
	return plt.show()
	
#########################################################
#########################################################
def genera_prezzi_medi():
	p_medio=[]
	for i in range(ore):
		media=(vettore_aperture[i]+vettore_chiusure[i])/2
		p_medio.append(media)
	print('#Genero Medie',p_medio)
	return np.array(p_medio).astype(np.float64)
	
vettore_media=genera_prezzi_medi()

#########################################################
def genera_volumi():
	volumi=[]
	for i in range(ore):
		volume=response_array[int(i)][5]
		volumi.append(volume)
	print('#Genero Volumi',volumi)
	return np.array(volumi).astype(np.float64)
	
vettore_volumi=genera_volumi()

#########################################################

#def normalize():
#	response_norm=[]
#	for i in range(len(response_array)):
#		apri_norm=np.linalg.norm(genera_aperture())
#		print('apri_norm', apri_norm)
#		chiudi_norm=np.linalg.norm(genera_chiusure())
#		vol_norm=np.linalg.norm(genera_volumi())
#		rsi_norm=np.linalg.norm(calcola_RSI())
#		response_norm.append(apri_norm)
#		response_norm.append(chiudi_norm)
#		response_norm.append(vol_norm)
#		response_norm.append(rsi_norm)
#		print('ciao')
#	return response_norm

def normalize(vettore):
	normale=np.linalg.norm(vettore)
	norm=vettore/normale
	return norm

########################################################

print('##########################################################')
print('####GOODBYE TO GESTORE_CANDELEv1.0 by Show################')
print('##########################################################')







