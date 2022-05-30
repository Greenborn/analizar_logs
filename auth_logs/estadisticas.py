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
    
    if not(primera_palabra in logs_palabra):
      logs_palabra[ primera_palabra ] = []

    logs_palabra[ primera_palabra ].append(registro)

    #Catalogar por ipv4
    if mensaje_ip4 == '':
      mensaje_ip4 = 'sin ip'
    
    if not(mensaje_ip4 in logs_ip):
      logs_ip[ mensaje_ip4 ] = []
      listado_ips[ mensaje_ip4 ] = { "cant_intentos": 1 }
    else:
      listado_ips[ mensaje_ip4 ][ "cant_intentos" ] += 1

    logs_ip[ mensaje_ip4 ].append(registro)
  archivo.close()

procesar_log("logs/auth.log")

print (listado_ips)

