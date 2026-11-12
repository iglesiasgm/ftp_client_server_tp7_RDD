#!/usr/bin/env python3
"""
Servidor FTP de prueba para probar el cliente en tu propia PC.

Requiere instalar UNA biblioteca:   pip install pyftpdlib
Se ejecuta con:                     python servidor_prueba.py

Datos para conectarte con el cliente:
    host: localhost      puerto: 2121
    usuario: alumno      contrasenia: utn123
La carpeta que ve el cliente es "ftp_raiz" (se crea sola junto a este archivo).
"""

import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ftp_raiz")
os.makedirs(RAIZ, exist_ok=True)

# Un archivo de ejemplo para tener algo que descargar
ejemplo = os.path.join(RAIZ, "hola.txt")
if not os.path.exists(ejemplo):
    with open(ejemplo, "w", encoding="utf-8") as f:
        f.write("Hola desde el servidor FTP de prueba!\n")

autorizador = DummyAuthorizer()
# Permisos: e=cd, l=listar, r=descargar, a=append, d=borrar, f=renombrar, m=mkdir, w=subir
autorizador.add_user("alumno", "utn123", RAIZ, perm="elradfmw")

handler = FTPHandler
handler.authorizer = autorizador
handler.banner = "Servidor FTP de prueba - UTN FRM"
handler.passive_ports = range(60000, 60100)  # puertos para el modo pasivo

servidor = FTPServer(("0.0.0.0", 2121), handler)
print("Servidor FTP escuchando en el puerto 2121. Ctrl+C para detenerlo.")
servidor.serve_forever()
