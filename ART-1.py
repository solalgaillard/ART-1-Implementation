#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Le module de contrôle pour l'étage de reconnaissance
def ctrl_mod_r(X):
    return 1 if 1 in X else 0 #Seulement si vecteur d'entré n'est pas nul

#Module RAZ, calcul de S, la similitude
def S(X, C):
    count_X = count_C = 0 #No need for bitarrays to be same length
    for xi in X :
        if xi == 1 : count_X += 1
    for ci in C :
        if ci == 1 : count_C += 1
    return count_C/float(count_X)

#Raz Pilote

from bitarray import bitarray

def RAZ(X, C, sigma=.8):
    return 1 if S(bitarray(X), bitarray(C)) <= sigma else 0 #Transform into bitarray

#Le module de contrôle pour l'étage de comparaison
def ctrl_mod_c(X,R):
    return 1 if (1 in X and 1 not in R) else 0

#And ternaire pour module_comp
def and_tern(X,T,ctrl_c):
    return 1 if X and (ctrl_c or T) else 0

#Module de Comparaison
def module_comp(X,Tj, ctrl_c):
    return [and_tern(X[x],Tj[x], ctrl_c) for x in xrange(len(X))]


#Modify excitation list
def get_exc(C, B, exc):
    for x in xrange(len(exc),len(B)): #Pour toute différence entre le nombre d'attracteurs et le nombre de valeurs d'excitation, on rajoute une nouvelle valeur
        exc.append(0)
        for y in xrange(len(C)): #Produit Scalaire de l'attracteur avec le vecteur d'entrée
            exc[x] += B[x][y]*C[y]

#Calcul de l'attracteur actif
def sor_R(exc, inhib_list, sigma = 0):
    exc_lmt = [exc[x] if not inhib_list[x] else 0 for x in xrange(len(exc))] #Modification de la liste contenant les valeurs d'excitation pour mettre à 0 les éléments inhibés.
    return [1 if (x==exc_lmt.index(max(exc_lmt)) and exc_lmt[exc_lmt.index(max(exc_lmt))] > sigma) else 0 for x in xrange(len(exc_lmt))] #Sélectionne la valeur maximum depuis la liste

#Recognize a form
def rec_form(C, B, exc, inhib_list):
    if len(exc) < len(B) : get_exc(C, B, exc) #Si nouvel attracteur, on calcule son excitation
    return sor_R(exc, inhib_list) #Puis on obtient R, avec attracteur excité


#Apprend une nouvelle forme
def learn_form(C,T,B,idx,L=2):
    T[idx] = C[:] #T est une copie de C
    for i in xrange(len(C)):
        B[idx][i] = C[i] * (L/(L-1. + C.count(1))) #B ou chaque 1 de T est pondéré par la norme du vecteur


#Crée un nouveau vecteur qui est potentiellement activable par n'importe quelle entrée.
def create_vecs(B, T, inhib_list, n, L=2):
    B.append([L/(L-1.+n)] * n)
    T.append([1] * n) #Tous les T à 1
    inhib_list.append(0) #Alonge la liste des inhibitions.

#Module de reconnaissance complet
def module_rec(C, raz, R, B, T, ctrl_r, exc, inhib_list):
    if 1 in R: #Seulement si un attracteur est actif
        if raz: inhib_list[R.index(1)] = 1 #Si Raz, inhibe l'attracteur
        else:
            learn_form( C, T, B, R.index(1), L=2) #Sinon, apprend la forme et quitte le programme
            return -1 #Break signal
    if ctrl_r : #Purement cosmetique pour un signal d'entrée à 0
        R = rec_form(C, B, exc, inhib_list) #Renvoie le vecteur où 1 est à l'index de l'attracteur.
        if 1 not in R : create_vecs(B, T, inhib_list, len(B[0]), L=2) #Si aucun attracteur est sélectionné, crée l'attracteur
    else : return -1 #Break signal
    return R



#Attracteurs dans le scope global
B = []
T = []

#Art Pilote, prend vecteurs et attracteurs en argument
def art(X, B, T):
    if (type(X[0]) != list) : X = [X] #One or a list of vectors
    for x in X:
        ctrl_r = ctrl_mod_r(x) #Module de contrôle CTRL_R
        R = [0] * len(T) #Initialise R comme un vecteur où toutes les valeurs sont 0
        exc = [] #Keep vector of values of excitation as to keep parallelism possible (close emulation of system)
        inhib_list = [0] * len(R) #Liste de vecteurs inhibés produit par RAZ
        if not R: create_vecs(B, T, inhib_list, len(x), L=2) #Si il n'existe aucun attracteur lors de l'entrée du premier signal
        while True:
            Tj = T[R.index(1)] if 1 in R else [0]*len(x) #Select Tj, ou crée vecteur où toutes les valeurs sont 0 si R n'a pas activé un attracteur
            C = module_comp(x, Tj, ctrl_mod_c(x, R)) #Etage de comparaison, CTRL_C in param
            R = module_rec(C, RAZ(x,C), R, B, T, ctrl_r, exc, inhib_list) #Etage de reconnaissance, RAZ in param
            if R == -1 : break #Go to next it



#To test algorithm

on = '1' ; off = '0'

def binary(integer, *BinForm) :
    if BinForm != () : b = BinForm[0]
    else : b = ''
    if integer is 0 : return b
    if integer % 2 is 0 : return binary(integer / 2, '0' + b)
    return binary((integer - 1) / 2, '1' + b)

def make_samples(start) :
    samples = list()
    for b in range(start, 0, -1) :
        samples += [binary(b)]
    return samples

def binform(samples) :
    inputs = [[x is on for x in input] for input in samples]
    N = max([len(input) for input in inputs])
    for x in range(len(inputs)) :
        inputs[x] = [False] * (N - len(inputs[x])) + inputs[x]
    return inputs

inputs = binform(make_samples(26))

B = []
T = []
i = 0

while len(inputs) > len(T) : art(inputs, B, T) ; i = i + 1

from pprint import pprint

print("\nWe give the network 26 vectors to work with:")
pprint(inputs)

print("\nAfter " +str(i)+  " passes, the network has saved all the vectors:")
pprint(T)
print("as there are " + str(len(T)) + " vectors saved\n")

print("\nMaximum recognition for the vector length can be achieved by setting the vigilance parameter with: \n\nfrom math import log\nbits_amt = int(log(Z+1,2)) #Where Z is the number of vectors passed to ART()\nvigilance = (bits_amt - 1) * (1. / bits_amt) + 1. / 1000\n")

