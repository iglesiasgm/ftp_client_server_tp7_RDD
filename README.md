# Cómo levantar el cliente y el servidor

## Requisitos e instalación

1. Instalar Python. En este proyecto se utiliza la versión **3.13.5**.
2. Instalar la librería necesaria ejecutando:

   ```bash
   pip install pyftpdlib
   ```

## Ejecución

Ejecutar los siguientes comandos en dos terminales diferentes:

**Terminal 1 – Levantar el servidor:**

```bash
python servidor_prueba.py
```

**Terminal 2 – Levantar el cliente:**

```bash
python ftp_client.py localhost 2121
```

## Credenciales de acceso

Al iniciar el cliente, ingresar las siguientes credenciales:

- **Usuario:** `alumno`
- **Contraseña:** `utn123`

## Pruebas de funcionamiento

Una vez conectado, ejecutar la siguiente secuencia de comandos para verificar el correcto funcionamiento del cliente y el servidor:

```bash
pwd
ls
get hola.txt
put ftp_client.py
ls
mkdir carpeta
rename carpeta carpeta2
rmdir carpeta2
delete ftp_client.py
quit
```
