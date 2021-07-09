import pickle

print('-'*25)
with open('stratcout.dat', 'rb') as sc:
	data = pickle.load(sc)
	print('\n' + str(data) + '\n')
with open('strategies.dat', 'rb') as sg:
	data = pickle.load(sg)
	print('\n' + str(data) + '\n')
	print('-'*25)
with open('tradelog.txt', 'r') as tl:
	data = tl.read()
	print(str(data)[9:] + '\n')
print('-'*25)
