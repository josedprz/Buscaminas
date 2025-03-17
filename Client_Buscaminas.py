import socket
import random
import json

HOST = "127.0.0.1"
PORT = 65432
buffer_size = 1024

verde = '\033[92m'
amarillo = '\033[93m'
azul = '\033[94m'
reset = '\033[0m'
gris = '\033[90m'
morado = '\033[95m'
rojo = '\033[91m'

def crear_tablero():
    tablero = [['0']*10 for _ in range(10)]
    for fila in tablero:
        minas = [random.randint(0, 9) for _ in range(3)]
        for mina in minas:
            fila[mina] = 'X'
    return tablero

def imprimir_tablero(tablero, revelar=False, fin=False):
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
                if revelar:
                    print('   ' + f'{amarillo}X{reset}', end='')
                elif fin:
                    print('   ' + f'{morado}X{reset}', end='')
                else:
                    print('   ' + ' ', end='')
            elif celda == '*':
                print('   ' + f'{rojo}X{reset}', end='')
            elif celda == ' ':
                print('   ' + f'-', end='')
            else:
                print('   ' + ' ', end='')
        print('\n')
    print(f'{separador}\n')

def juego():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))
        # Bloqueo hasta recibir mensaje
        data = TCPClientSocket.recv(4096)
        mensaje_inicial = json.loads(data.decode('utf-8'))
        print(f'{morado}Estado de la conexión:{reset} {mensaje_inicial["estado"]}')
        print(mensaje_inicial['mensaje'])
        dificultad = input('Elección: ')
        TCPClientSocket.sendall(dificultad.encode('utf-8'))
        tablero = TCPClientSocket.recv(4096)
        tablero = json.loads(tablero.decode('utf-8'))
        imprimir_tablero(tablero)
        rango = range(9 if dificultad == '1' else 16)
        fila = None
        columna = None

        while True:
            try:
                fila = int(input(f'{verde}Elige fila: {reset}'))
            except ValueError:
                print(f'{rojo}Por favor, ingresa un número válido{reset}')
            while fila not in rango:
                fila = int(input(f'{rojo}Elige una fila válida: {reset}'))
            try:
                columna = int(input(f'{azul}Elige columna: {reset}'))
            except ValueError:
                print(f'{rojo}Por favor, ingresa un número válido{reset}')
            while columna not in rango:
                columna = int(input(f'{rojo}Elige una columna válida: {reset}'))
            coordenadas = {'fila' : fila, 
                           'columna' : columna}
            coordenadas = json.dumps(coordenadas)
            # Envío coordenadas
            TCPClientSocket.sendall(coordenadas.encode('utf-8'))

            # [Esperando Server]
            data = TCPClientSocket.recv(4096)
            data = json.loads(data.decode('utf-8'))
            
            if data['estatus'] == 'PierdeCliente':
                imprimir_tablero(data['tablero'], True)
                print(rojo + data['msj'] + reset + '\n') # Perdiste!
                exit()
            elif data['estatus'] == 'RepiteCliente':
                print(rojo + data['msj'] + reset) # Repite
                continue
            else:
                if data['estatus'] == 'GanaCliente':
                    imprimir_tablero(data['tablero'], fin=True)
                    print(verde + data['msj'] + reset + '\n')
                    break
                else:
                    imprimir_tablero(data['tablero'])



if __name__ == "__main__":
    juego()
