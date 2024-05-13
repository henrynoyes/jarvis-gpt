import asyncio
import websockets
import os

class WSClient:
    def __init__(self):
        self.svr_ip = os.getenv('WS_IP')

    async def _run(self, msg):
        async with websockets.connect(f'ws://{self.svr_ip}:8800') as websocket:
            await websocket.send(msg)
            response = await websocket.recv()
            print(f'received {response}')

    def run(self, msg):
        return asyncio.run(self._run(msg))

class WSServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handler(self, websocket):
        async for msg in websocket:
            print(f'{msg=}')

            await websocket.send(f'response to {msg}')

    async def _run(self):
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()

    async def run(self):
        return asyncio.run(self._run())


if __name__ == '__main__':
    server = WSServer('0.0.0.0', 8800)
    server.run()











def recolor_model(clr):
    print('coloring')
    return 'done'

func_dct = {'recolor_model': recolor_model}

async def handler(websocket):
    async for msg in websocket:
        print(f'{msg=}')
        func_resp = 'no'

        if msg in func_dct.keys():
            func = func_dct[msg]
            func_resp = func('blue')

        await websocket.send(f'{func_resp}')

async def main():
    server = await websockets.serve(handler, '0.0.0.0', 8800)
    await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())