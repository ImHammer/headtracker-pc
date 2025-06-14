import asyncio
import websockets
import socket

UDP_PORT = 5555
WS_PORT = 8765
clients = set()

async def ws_handler(websocket, path):
    print(f"Novo cliente WebSocket conectado: {websocket.remote_address}")
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)
        print(f"Cliente WebSocket desconectado: {websocket.remote_address}")

async def udp_listener():
    loop = asyncio.get_event_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', UDP_PORT))
    sock.setblocking(False)

    print(f"Recebendo dados UDP na porta {UDP_PORT}")
    while True:
        try:
            data, addr = await loop.sock_recvfrom(sock, 1024)
            try:
                msg = data.decode('utf-8').strip()
                # Valida formato yaw,pitch,roll
                try:
                    msg = msg.replace(',', '.')
                    yaw, pitch, roll = map(float, msg.split(';'))
                    if abs(pitch) > 90:
                        print(f"Erro: Pitch inválido ({pitch}) de {addr}")
                        continue
                    print(f">> Recebido de {addr}: yaw={yaw:.2f}, pitch={pitch:.2f}, roll={roll:.2f}")
                except ValueError as err:
                    print(err)
                    print(f"Erro: Formato inválido ({msg}) de {addr}")
                    continue
                if not clients:
                    print("Nenhum cliente WebSocket conectado")
                for client in clients.copy():
                    try:
                        await client.send(msg)
                        print(f"Enviado para WebSocket {client.remote_address}: {msg}")
                    except Exception as e:
                        print(f"Erro ao enviar para WebSocket {client.remote_address}: {e}")
                        clients.remove(client)
            except UnicodeDecodeError:
                print(f"Erro: Dados UDP inválidos recebidos de {addr}")
        except Exception as e:
            print(f"Erro ao processar UDP: {e}")

async def main():
    print(f"Iniciando servidor WebSocket na porta {WS_PORT}")
    await asyncio.gather(
        websockets.serve(ws_handler, '0.0.0.0', WS_PORT),
        udp_listener()
    )

if __name__ == "__main__":
    asyncio.run(main())