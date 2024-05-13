import asyncio
import websockets
import os
import json
import pyautogui
from io import BytesIO
import base64
import requests
from time import sleep

class WSClient:
    def __init__(self):
        self.svr_ip = os.getenv('WS_IP')
        self.resp_dct = {'status': None}

    async def _run(self, msg):
        async with websockets.connect(f'ws://{self.svr_ip}:8800') as websocket:
            await websocket.send(msg)
            response = await websocket.recv()
            self.resp_dct['status'] = response

    def run(self, msg):
        return asyncio.run(self._run(msg))

class WSServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.func_dct = {
            'recolor_model': self.recolor_model
        }

    def locate(self, query):
        ss = pyautogui.screenshot(region=(0, 0, 2560, 1030))
        buff = BytesIO()
        ss.save(buff, format='PNG')
        ss_b64 = base64.b64encode(buff.getvalue()).decode()

        response = requests.post(
            f'https://api.openinterpreter.com/v0/point/',
            json={'query': query, 'base64': ss_b64}
        )
        js = response.json()[0]
        coords = (int(js[0] * 2560),
            int(js[1] * 1030))
        
        return coords

    def recolor_model(self, current_color, new_color):
        # open appearance tab
        x, y = self.locate('sphere multicolor')
        pyautogui.moveTo(x, y)
        pyautogui.click()
        sleep(0.5)

        # open current color
        x, y = self.locate(f'{current_color} sphere')
        pyautogui.moveTo(x, y)
        pyautogui.doubleClick()
        sleep(0.5)

        # change to new color
        x, y = self.locate(f'{new_color} square')
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.press('enter')

        return 'recolor complete'

    async def handler(self, websocket):
        async for msg in websocket:
            print(f'{msg=}')
            jmsg = json.loads(msg)
            func_name = jmsg['name']

            if func_name in self.func_dct:
                func_to_call = self.func_dct[func_name]
                func_args = jmsg['arguments']
                func_resp = func_to_call(**func_args)

            await websocket.send(func_resp)

    async def _run(self):
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()

    def run(self):
        print(f'JARVIS WSServer started on {self.host}:{self.port}')
        return asyncio.run(self._run())


if __name__ == '__main__':
    server = WSServer('0.0.0.0', 8800)
    server.run()