import socket
import random
import json
HOST = "127.0.0.1"
PORT = 65432
buffer_size = 1024

verde = '\033[92m'
naranja = '\033[93m'
azul = '\033[94m'
reset = '\033[0m'
gris = '\033[90m'
morado = '\033[95m'
rojo = '\033[91m'

def crear_tablero(dificultad):
    cont_mina = 0
    if dificultad == '1':
        tablero = [['-']*9 for _ in range(9)]
        mina_extra = random.randint(0, 8)
        for fila in range(9):
            mina = random.randint(0, 8)
            tablero[fila][mina] = 'X'
            cont_mina += 1
            if fila == mina_extra:
                while True:
                    celda = random.randint(0, 8)
                    if tablero[fila][celda] != 'X':
                        tablero[fila][celda] = 'X'
                        cont_mina += 1
                        break
    elif dificultad == '2':
        # 40 minas en total
        tablero = [['-']*16 for _ in range(16)]
        # 8 filas random con mina extra
        filas_extra = {random.randint(0, 15) for _ in range(8)}
        while len(filas_extra) < 8: # Por si se repiten random
            filas_extra.add(random.randint(0, 15))
        # Rellenamos
        for fila in range(16):
            # De ley cada fila con 2 minas (16*2=32)
            minas= {random.randint(0, 15) for _ in range(2)}
            while len(minas) < 2: # Por si se repiten random
                minas.add(random.randint(0, 15))
            for mina in minas: # rellenamos aquí
                tablero[fila][mina] = 'X'
                cont_mina += 1
            if fila in filas_extra: # 8 filas con mina extra
                mina_extra = random.randint(0, 15)
                while mina_extra in minas:
                    mina_extra = random.randint(0, 15)
                tablero[fila][mina_extra] = 'X'
                cont_mina += 1     

    return tablero, cont_mina

def imprimir_tablero(tablero):
    separador = '-' * 75
    if len(tablero) < 11:
        Un_digito = ''.join([f'   {i}' for i in range(len(tablero[0]))])
        Columnas = [f'   {i}' for i in range(10)]
        print(separador + '\n\n\t ' + azul + Un_digito + reset + '\n')
    else:
        Un_digito = ''.join([f'   {i}' for i in range(10)])
        Dos_digitos = ''.join([f'  {i}' for i in range(10, len(tablero[0]))])
        Col_un_digito = [f'   {i}' for i in range(10)]
        Col_dos_digitos = [f'  {i}' for i in range(10, len(tablero[0]))]
        Columnas = Col_un_digito + Col_dos_digitos
        print(separador + '\n\n\t ' + azul + Un_digito + ' ' + Dos_digitos + reset + '\n')

    for columna, fila in enumerate(tablero):
        print(f'     {verde}' + str(Columnas[columna]) + f'{reset}', end='')
        for celda in fila:
            if celda == 'X':
                print('   ' + f'{gris}X{reset}', end='')
            elif celda == '*':
                print('   ' + f'{rojo}X{reset}', end='')
            else:
                print('   ' + celda, end='')
        print('\n')
    print(f'{separador}\n')

def actualizar_tablero(tablero, coordenadas):
    columna = coordenadas['columna']
    fila = coordenadas['fila']

    if tablero[fila][columna] == 'X':
        tablero[fila][columna] = '*'
        msj = '¡Perdiste!'
        return tablero, 'PierdeCliente', msj
    elif tablero[fila][columna] == ' ':
        msj = 'Ya se eligió esa casilla, intenta de nuevo'
        return tablero, 'RepiteCliente', msj
    else:
        tablero[fila][columna] = ' '
        msj = 'Bien'
        return tablero, 'Continua', msj

def juego():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.bind((HOST, PORT))
        TCPServerSocket.listen()
        print(f'{morado}Servidor Listo:{reset}')
        print('Esperando respuesta de Dificultad.')

        Client_conn, _ = TCPServerSocket.accept()
        dificultad = f'Para comenzar por favor elija la dificultad: \n1. {verde}Principiante{reset}\n2. {rojo}Avanzado{reset}\n'
        mensaje_inicial = {'estado' : 'Conectado',
                           'mensaje' : dificultad}
        mensaje_inicial = json.dumps(mensaje_inicial)
        score = 0

        with Client_conn:
            Client_conn.sendall(mensaje_inicial.encode('utf-8'))
            dificultad = Client_conn.recv(buffer_size).decode('utf-8')
            
            print('Dificultad: ', dificultad) 
            tablero, minas = crear_tablero(dificultad)
            print(f'Se crearon {minas} minas')
            imprimir_tablero(tablero)
            Client_conn.sendall(json.dumps(tablero).encode('utf-8'))
            while True:
                # [Esperando Cliente]
                data = Client_conn.recv(buffer_size)
                coordenadas = json.loads(data.decode('utf-8'))
                
                tablero, estatus, msj = actualizar_tablero(tablero, coordenadas)
                
                if estatus != 'RepiteCliente':
                    imprimir_tablero(tablero)
                
                envio = {'tablero' : tablero,
                        'estatus' : estatus,
                        'msj' : msj}
                if envio['estatus'] == 'Continua':
                    score += 1
                    if score == (len(tablero)*len(tablero[0])) - minas:
                        envio['estatus'] = 'GanaCliente'
                        envio['msj'] = '¡Felicidades, Ganaste!'
                        envio = json.dumps(envio)
                        Client_conn.sendall(envio.encode('utf-8'))
                        exit()

                envio = json.dumps(envio)
                Client_conn.sendall(envio.encode('utf-8'))

                if estatus == 'PierdeCliente':
                    exit()

if __name__ == "__main__":
    juego()