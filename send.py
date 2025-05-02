import cv2
import numpy as np
import mss
import websocket
import time
import threading

def capture_screen():
    sct = mss.mss()
    monitor = sct.monitors[1]  # По умолчанию захватывает первый экран
    bounding_box = {'top': 0, 'left': 0, 'width': monitor['width'], 'height': monitor['height']}

    while True:
        img = sct.grab(bounding_box)
        frame = np.array(img)

        # Преобразуем изображение в формат RGB565
        img_resized = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_resized, (240, 135))  # Уменьшаем для передачи
        return img_resized  # Возвращаем одно изображение для передачи

def send_frame(ws):
    while True:
        frame = capture_screen()

        # Преобразуем изображение в RGB565
        rgb565 = frame.astype(np.uint16)
        r5 = (rgb565[..., 0] >> 3).astype(np.uint16) << 11
        g6 = (rgb565[..., 1] >> 2).astype(np.uint16) << 5
        b5 = (rgb565[..., 2] >> 3).astype(np.uint16)
        rgb565_flat = r5 | g6 | b5
        data = rgb565_flat.flatten()

        # Отправляем данные через WebSocket
        ws.send_binary(data.tobytes())

def on_open(ws):
    threading.Thread(target=send_frame, args=(ws,)).start()

def run_websocket_server():
    ws = websocket.WebSocketApp("ws://<IP вашего компьютера>:<порт>/", on_open=on_open)
    ws.run_forever()

if __name__ == "__main__":
    run_websocket_server()
