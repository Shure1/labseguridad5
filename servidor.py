# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 21:31:49 2022

@author: elias
"""

from socket import *
import random
from secrets import token_bytes
from Crypto.Cipher import DES
from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes


#CONEXION Y DEFINICION DE VARIABLES
direccionServidor = "localhost"
puertoservidor = 1234
#Generamos un nuevo socket y establecemos la conexion
socketServidor = socket(AF_INET, SOCK_STREAM)
#Establacemos la conexion
socketServidor.bind((direccionServidor,puertoservidor ))
#escuchamos al servidor
socketServidor.listen()
#variables para el diffie helman
l= ['P','G','b']
d=dict()
n=0


while True:
    try:
        key = DES3.adjust_key_parity(get_random_bytes(24))
        break
    except ValueError:
        pass

def encrypt(msg):
    cipher = DES3.new(key, DES3.MODE_EAX)
    nonce = cipher.nonce
    ciphertext = cipher.encrypt(msg.encode('ascii'))
    return nonce, ciphertext

def decrypt(nonce, ciphertext):
    cipher = DES3.new(key, DES3.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode('ascii')

def AS():
    key = token_bytes(16)
    
    file = open("mensajeentrada.txt", "r")
    mensaje_entrada = str(file.readline().lower()).encode()
    file.close()
    
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(mensaje_entrada)

    mensaje_codificado = cipher.nonce + tag + ciphertext
    
    file = open("mensajecifrado.txt", "w+")
    file.write(str(mensaje_codificado))
    file.close()
    
    nonce = mensaje_codificado[:AES.block_size]
    tag = mensaje_codificado[AES.block_size:AES.block_size * 2]
    ciphertext = mensaje_codificado[AES.block_size * 2:]

    cipher = AES.new(key, AES.MODE_EAX, nonce)
    
    mensaje_recibido=cipher.decrypt_and_verify(ciphertext, tag).decode()
    
    file = open("mensajerecibido.txt", "w+")
    file.write(str(mensaje_recibido))
    file.close()
    return

def TDS():
    file = open("mensajeentrada.txt", "r")
    mensaje_entrada = str(file.readline().lower())
    file.close()
    
    nonce, ciphertext= encrypt(mensaje_entrada)
    mensaje_codificado= nonce, ciphertext
    
    file = open("mensajecifrado.txt", "w+")
    file.write(str(mensaje_codificado))
    file.close()
    
    plaintext = decrypt(nonce, ciphertext)
    file = open("mensajerecibido.txt", "w+")
    file.write(plaintext)
    file.close()
    
    return
    
    

def DS():
   key = token_bytes(8)    #(solo 8)
   iv = token_bytes(8)    # Vector de inicialización
   
   file = open("mensajeentrada.txt", "r")
   mensaje_entrada = str(file.readline().lower()).encode()
   file.close()
   
   cipher1 = DES.new(key, DES.MODE_CFB, iv)
   mensaje_codificado = cipher1.encrypt(mensaje_entrada)
   
   file = open("mensajecifrado.txt", "w+")
   file.write(str(mensaje_codificado))
   file.close()
   
   cipher2 = DES.new(key, DES.MODE_CFB, iv)
   mensaje_recibido = cipher2.decrypt(mensaje_codificado).decode()
   file = open("mensajerecibido.txt", "w+")
   file.write(mensaje_recibido)
   file.close()
   return
    

def dh(d):
    #variables para diffie helman
    #llave privada del server
    a= random.randint(0,(d['P']-1))
    # se obtiene la llave generada para el servidor
    A = int(pow(d['G'],a,d['P'])) 
    # se obtiene la llave generada por el cliente
    B = int(pow(d['G'],d['b'],d['P'])) 
    # llave secreta del servidor
    ka = int(pow(B,a,d['P']))
     
    # llave secreta del cliente
    kb = int(pow(A,d['b'],d['P']))
    if kb==ka:
        return True
    return False

#recibimos las solicitudes
while True:
      #establecemos la conexion con la direccion del cliente y la conexion en si
      socketConexion, addr = socketServidor.accept()
      #se conecto correctamente
      print("Conectado con un cliente", addr)
      #inicia la interaccion de mensajes
      while True:
          #recibe la cadena que envio el cliente mediante la funcion recv
          mensajeRecibido = socketConexion.recv(4096).decode()
          print(mensajeRecibido)
          d[l[n]]=int(mensajeRecibido)
          n+=1
          #si n=2 quiere decir que ya tenemos todos los datos necesarios para el df
          if n==3 and dh(d)==True:
              #le avisamos al cliente que las llaves coinciden
              socketConexion.send("las llaves coinciden".encode())
              #se cifra el mensaje que este en el txt
              AS()
              #se le envia el mensaje que se cifro correctamente
              socketConexion.send('mensaje cifrado correctamente'.encode())#arreglar este send no lo muestra el cliente
                  
          #si la cadena es adios salimos del chat
          if mensajeRecibido == 'x':
              break
      break #arreglar este break pendiente.
print("Desconectado el cliente", addr)
#cerramos conexion
socketConexion.close()      


