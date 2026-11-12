Pasos para levantar cliente y servidor:
1- Instalar Python (acá se usa versión 3.13.5)
2- Instalar librería con "pip install pyftpdlib"
3- Ejecutar estos dos comandos en las distintas terminales:

Terminal 1 (levanta servidor): python servidor_prueba.py
Terminal 2 (levanta cliente): python ftp_client.py localhost 2121

4- Ingresar usuario = alumno y password = utn123
5- Ejecutar esta secuencia de comandos para ver que ande todo bien:

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

