import os
import csv

def get_ipv4( text ):
  ip = ''
  numero_grupo = ''
  caracter_anterior = ''
  cant_puntos = 0
  c = 1
  len_text = len(text)
  if len_text > 0:
    caracter_anterior = text[0]

  while  c < len_text:
    if text[c].isnumeric():
      numero_grupo += text[c]
    elif text[c] == '.' or (text[c] == ' ' and caracter_anterior.isnumeric() and cant_puntos < 4):
      cant_puntos += 1
      if numero_grupo.isnumeric() and int(numero_grupo) < 256:
        ip += numero_grupo
        if cant_puntos < 4:
          ip += '.'
        numero_grupo = ''
    caracter_anterior = text[c]
    c += 1
  
  if cant_puntos == 4:
    return ip
  else:
    return ''

logs_palabra = {}
logs_fecha_hora = {}
logs_ip = {}
listado_ips = {}

def procesar_log( nombre_archivo ):
  archivo = open(nombre_archivo, mode="r")
  for linea in archivo:
    split_linea = linea.split(":")
    fecha   = split_linea[0].split(" ")
    mes     = fecha[0]
    dia     = fecha[1]
    hora    = fecha[2]
    minuto  = split_linea[1]
    if (len(fecha) == 4):
      dia     = fecha[2]
      hora    = fecha[3]

    split_linea_2_s = split_linea[2].split(" ")

    segundo = split_linea_2_s[0]

    host = split_linea_2_s[1]

    app = split_linea_2_s[2]
    app_split = app.split('[')
    prioridad = ''
    
    if len(app_split) == 2:
      app = app_split[0]
      prioridad = app_split[1].split(']')[0]

    len_s_linea = len(split_linea) 

    c = 4
    mensaje = split_linea[3]
    while c < len_s_linea:
      mensaje = mensaje + ':' + split_linea[c]
      c += 1

    primera_palabra = mensaje.split(" ")[1]

    #Buscamos IPs IPv4
    mensaje_ip4 = get_ipv4(mensaje)
    
    #Armamos el registro
    registro = { "fecha":[mes, dia], "hora":[hora, minuto, segundo], "ip": mensaje_ip4, "primera_palabra":primera_palabra, "mensaje":mensaje }

    #Catalogar por primera palabra del mensaje
    
    if not primera_palabra in logs_palabra:
      logs_palabra[ primera_palabra ] = []

    logs_palabra[ primera_palabra ].append(registro)

    #Catalogar por ipv4
    if mensaje_ip4 == '':
      mensaje_ip4 = 'sin_catalogar'
    
    if not mensaje_ip4 in logs_ip:
      logs_ip[ mensaje_ip4 ] = []
      listado_ips[ mensaje_ip4 ] = { "cant_intentos": 1 }
    else:
      listado_ips[ mensaje_ip4 ][ "cant_intentos" ] += 1

    logs_ip[ mensaje_ip4 ].append(registro)

    #Catalogar por fecha y hora
    if not mes in logs_fecha_hora:
      logs_fecha_hora[mes] = {}
    
    if not dia in logs_fecha_hora[mes]:
      logs_fecha_hora[mes][dia] = {}
    
    if not hora in logs_fecha_hora[mes][dia]:
      logs_fecha_hora[mes][dia][hora] = {}
    
    if not minuto in logs_fecha_hora[mes][dia][hora]:
      logs_fecha_hora[mes][dia][hora][minuto] = {}

    if not segundo in logs_fecha_hora[mes][dia][hora][minuto]:
      logs_fecha_hora[mes][dia][hora][minuto][segundo] = []

    logs_fecha_hora[mes][dia][hora][minuto][segundo].append(registro)
  
  archivo.close()

lista_archivos = os.listdir("logs")

print('############################################################# \n LISTADO DE LOGS ENCONTRADOS \n')

print(lista_archivos)

for archivo in lista_archivos:
  print('procesando archivo: '+archivo)
  procesar_log("logs/"+archivo)

print('------------------------------------------------------------- \n LISTADO DE CANTIDAD DE REGISTROS POR IP \n')



with open('resultado/ips.csv', 'w') as csvfile:
  filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  filewriter.writerow(['IP', 'Cantidad registros'])
  #Se genera archivo .CSV cantidad intentos por IP
  for ip in listado_ips:
    print(ip + ' > ' + str(listado_ips[ip]["cant_intentos"]))
    filewriter.writerow([ip, listado_ips[ip]["cant_intentos"]])

with open('resultado/incidencias_dia.csv', 'w') as csvfile:
  filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  filewriter.writerow(['Mes', 'Día', 'Cantidad incidencias'])

  #Se cuantan la cantidad de incidencias por día
  cant_incidencias_fecha = {}
  for log_mes in logs_fecha_hora:
    cant_incidencias_fecha[log_mes] = {}
    for log_dia in logs_fecha_hora[log_mes]:
      cant_incidencias_fecha[log_mes][log_dia] = 0
      for log_hora in logs_fecha_hora[log_mes][log_dia]:
        for log_minuto in logs_fecha_hora[log_mes][log_dia][log_hora]:
          for log_segundo in logs_fecha_hora[log_mes][log_dia][log_hora][log_minuto]:
            for log in logs_fecha_hora[log_mes][log_dia][log_hora][log_minuto][log_segundo]:
              cant_incidencias_fecha[log_mes][log_dia] = cant_incidencias_fecha[log_mes][log_dia] + 1
  
  for _mes in cant_incidencias_fecha:
    for _dia in cant_incidencias_fecha[_mes]:
      print(_mes + ' ' + _dia + ' > ' +  str(cant_incidencias_fecha[_mes][_dia]))
      filewriter.writerow([_mes, _dia, str(cant_incidencias_fecha[_mes][_dia])])
