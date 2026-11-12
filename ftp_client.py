#!/usr/bin/env python3
"""
Cliente FTP de consola - TP N 7 Redes de Informacion (UTN FRM)

Usa solo la biblioteca estandar de Python (ftplib), no hay que instalar nada.
Cada comando del usuario se traduce a comandos del protocolo FTP (RFC 959),
y con "debug on" se ve el dialogo real cliente <-> servidor.

Uso:
    python ftp_client.py                 -> arranca sin conectarse
    python ftp_client.py localhost 2121  -> arranca y conecta
"""

import ftplib
import getpass
import os
import shlex
import sys

AYUDA = """
Comandos disponibles (entre parentesis, el comando FTP real que se envia):

  Conexion
    open <host> [puerto]     Conectar al servidor           (conexion TCP al puerto 21)
    login [usuario]          Autenticarse                   (USER / PASS)
    quit                     Cerrar sesion y salir          (QUIT)

  Navegacion y listados (en el servidor)
    pwd                      Directorio actual              (PWD)
    cd <dir>                 Cambiar de directorio          (CWD)
    cdup                     Subir un nivel                 (CDUP)
    ls [dir]                 Listado detallado              (LIST)
    nlst [dir]               Solo nombres                   (NLST)

  Transferencia
    get <remoto> [local]     Descargar archivo              (RETR)
    put <local> [remoto]     Subir archivo                  (STOR)

  Gestion de archivos (en el servidor)
    mkdir <dir>              Crear directorio               (MKD)
    rmdir <dir>              Borrar directorio vacio        (RMD)
    delete <archivo>         Borrar archivo                 (DELE)
    rename <viejo> <nuevo>   Renombrar                      (RNFR / RNTO)
    size <archivo>           Tamanio en bytes               (SIZE)
    syst                     Sistema del servidor           (SYST)

  Configuracion
    binary | ascii           Modo de transferencia          (TYPE I / TYPE A)
    passive on|off           Modo pasivo o activo           (PASV / PORT)
    debug on|off             Ver el dialogo del protocolo

  Locales (en tu PC)
    lpwd | lcd <dir> | lls   Directorio local actual / cambiar / listar

  help                       Muestra esta ayuda
"""


class ClienteFTP:
    def __init__(self):
        self.ftp = None
        self.pasivo = True
        self.modo_binario = True
        self.debug = 1  # 1 = muestra comandos y respuestas del protocolo

    # ------------------------------------------------------------------ util
    def _conectado(self):
        if self.ftp is None:
            raise RuntimeError("No hay conexion. Usa: open <host> [puerto]")
        return self.ftp

    # ------------------------------------------------------------ conexion
    def cmd_open(self, host=None, puerto="21"):
        if not host:
            print("Uso: open <host> [puerto]")
            return
        if self.ftp is not None:
            self.cmd_quit(salir=False)
        self.ftp = ftplib.FTP()
        self.ftp.set_debuglevel(self.debug)
        welcome = self.ftp.connect(host, int(puerto), timeout=15)
        self.ftp.set_pasv(self.pasivo)
        if not self.debug:
            print(welcome)

    def cmd_login(self, usuario=None):
        ftp = self._conectado()
        if usuario is None:
            usuario = input("Usuario (Enter = anonymous): ").strip() or "anonymous"
        if usuario == "anonymous":
            clave = "anonymous@"
        else:
            clave = getpass.getpass("Contrasenia: ")
        resp = ftp.login(usuario, clave)
        if not self.debug:
            print(resp)

    def cmd_quit(self, salir=True):
        if self.ftp is not None:
            try:
                self.ftp.quit()
            except ftplib.all_errors:
                self.ftp.close()
            self.ftp = None
        if salir:
            print("Hasta luego.")
            sys.exit(0)

    # ---------------------------------------------------------- navegacion
    def cmd_pwd(self):
        print(self._conectado().pwd())

    def cmd_cd(self, directorio=None):
        if not directorio:
            print("Uso: cd <directorio>")
            return
        resp = self._conectado().cwd(directorio)
        if not self.debug:
            print(resp)

    def cmd_cdup(self):
        self._conectado().cwd("..")
        if not self.debug:
            print("Subiste un nivel.")

    def cmd_ls(self, directorio=""):
        ftp = self._conectado()
        ftp.retrlines(("LIST " + directorio).strip())

    def cmd_dir(self, directorio=""):
        self.cmd_ls(directorio)

    def cmd_nlst(self, directorio=""):
        ftp = self._conectado()
        for nombre in ftp.nlst(directorio) if directorio else ftp.nlst():
            print(nombre)

    # ------------------------------------------------------- transferencia
    def cmd_get(self, remoto=None, local=None):
        if not remoto:
            print("Uso: get <archivo_remoto> [archivo_local]")
            return
        ftp = self._conectado()
        local = local or os.path.basename(remoto)
        total = 0
        try:
            if self.modo_binario:
                with open(local, "wb") as f:
                    def escribir(bloque):
                        nonlocal total
                        f.write(bloque)
                        total += len(bloque)
                    ftp.retrbinary("RETR " + remoto, escribir)
            else:
                with open(local, "w", encoding="utf-8", newline="") as f:
                    def escribir_linea(linea):
                        nonlocal total
                        f.write(linea + "\n")
                        total += len(linea) + 1
                    ftp.retrlines("RETR " + remoto, escribir_linea)
        except ftplib.all_errors:
            # si falla, no dejar un archivo local a medio escribir
            if os.path.exists(local) and os.path.getsize(local) == 0:
                os.remove(local)
            raise
        print(f"Descargado '{remoto}' -> '{local}' ({total} bytes)")

    def cmd_put(self, local=None, remoto=None):
        if not local:
            print("Uso: put <archivo_local> [nombre_remoto]")
            return
        if not os.path.isfile(local):
            print(f"No existe el archivo local: {local}")
            return
        ftp = self._conectado()
        remoto = remoto or os.path.basename(local)
        if self.modo_binario:
            with open(local, "rb") as f:
                ftp.storbinary("STOR " + remoto, f)
        else:
            with open(local, "rb") as f:
                ftp.storlines("STOR " + remoto, f)
        print(f"Subido '{local}' -> '{remoto}' ({os.path.getsize(local)} bytes)")

    # --------------------------------------------------------- gestion
    def cmd_mkdir(self, nombre=None):
        if not nombre:
            print("Uso: mkdir <directorio>")
            return
        print("Creado:", self._conectado().mkd(nombre))

    def cmd_rmdir(self, nombre=None):
        if not nombre:
            print("Uso: rmdir <directorio>")
            return
        resp = self._conectado().rmd(nombre)
        if not self.debug:
            print(resp)

    def cmd_delete(self, nombre=None):
        if not nombre:
            print("Uso: delete <archivo>")
            return
        resp = self._conectado().delete(nombre)
        if not self.debug:
            print(resp)

    def cmd_rename(self, viejo=None, nuevo=None):
        if not viejo or not nuevo:
            print("Uso: rename <nombre_viejo> <nombre_nuevo>")
            return
        resp = self._conectado().rename(viejo, nuevo)
        if not self.debug:
            print(resp)

    def cmd_size(self, nombre=None):
        if not nombre:
            print("Uso: size <archivo>")
            return
        ftp = self._conectado()
        ftp.voidcmd("TYPE I")  # SIZE solo es confiable en modo binario
        print(f"{nombre}: {ftp.size(nombre)} bytes")

    def cmd_syst(self):
        print(self._conectado().sendcmd("SYST"))

    # ------------------------------------------------------ configuracion
    def cmd_binary(self):
        self.modo_binario = True
        print("Modo de transferencia: BINARIO (TYPE I)")

    def cmd_ascii(self):
        self.modo_binario = False
        print("Modo de transferencia: ASCII (TYPE A)")

    def cmd_passive(self, valor=None):
        if valor not in ("on", "off"):
            print("Uso: passive on|off  (actual: %s)" % ("on" if self.pasivo else "off"))
            return
        self.pasivo = valor == "on"
        if self.ftp:
            self.ftp.set_pasv(self.pasivo)
        print("Modo pasivo:", "ACTIVADO (PASV)" if self.pasivo else "DESACTIVADO -> modo activo (PORT)")

    def cmd_debug(self, valor=None):
        if valor not in ("on", "off"):
            print("Uso: debug on|off  (actual: %s)" % ("on" if self.debug else "off"))
            return
        self.debug = 1 if valor == "on" else 0
        if self.ftp:
            self.ftp.set_debuglevel(self.debug)
        print("Debug del protocolo:", "ACTIVADO" if self.debug else "DESACTIVADO")

    # ------------------------------------------------------------- locales
    def cmd_lpwd(self):
        print(os.getcwd())

    def cmd_lcd(self, directorio=None):
        if not directorio:
            print("Uso: lcd <directorio>")
            return
        os.chdir(directorio)
        print(os.getcwd())

    def cmd_lls(self, directorio="."):
        for nombre in sorted(os.listdir(directorio)):
            ruta = os.path.join(directorio, nombre)
            marca = "<DIR>" if os.path.isdir(ruta) else f"{os.path.getsize(ruta):>10}"
            print(f"{marca:>10}  {nombre}")

    def cmd_help(self):
        print(AYUDA)

    # ---------------------------------------------------------------- loop
    def ejecutar(self, linea):
        try:
            partes = shlex.split(linea, posix=(os.name != "nt"))
        except ValueError as e:
            print("Error en el comando:", e)
            return
        partes = [p.strip('"') for p in partes]
        if not partes:
            return
        nombre, args = partes[0].lower(), partes[1:]
        if nombre in ("exit", "bye"):
            nombre = "quit"
        metodo = getattr(self, "cmd_" + nombre, None)
        if metodo is None:
            print(f"Comando desconocido: {nombre}. Escribi 'help' para ver la lista.")
            return
        try:
            metodo(*args)
        except TypeError:
            print("Cantidad de argumentos incorrecta. Escribi 'help'.")
        except RuntimeError as e:
            print(e)
        except ftplib.error_perm as e:
            print("Permiso denegado / error del servidor:", e)
        except ftplib.all_errors as e:
            print("Error de red/FTP:", e)
        except (OSError, ValueError) as e:
            print("Error local:", e)

    def correr(self):
        print("Cliente FTP - UTN FRM. Escribi 'help' para ver los comandos.")
        while True:
            try:
                estado = "conectado" if self.ftp else "desconectado"
                linea = input(f"ftp ({estado})> ")
            except (EOFError, KeyboardInterrupt):
                print()
                self.cmd_quit()
            self.ejecutar(linea)


if __name__ == "__main__":
    cliente = ClienteFTP()
    if len(sys.argv) >= 2:
        cliente.ejecutar("open " + " ".join(sys.argv[1:3]))
        if cliente.ftp:
            cliente.ejecutar("login")
    cliente.correr()
