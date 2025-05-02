import cv2
import numpy as np
import mss
import websocket
import time
import threading

def capture_screen(monitor_width, monitor_height):
    sct = mss.mss()
    bounding_box = {'top': 0, 'left': 0, 'width': monitor_width, 'height': monitor_height}

    while True:
        img = sct.grab(bounding_box)
        frame = np.array(img)

        # Преобразуем изображение в формат RGB565
        img_resized = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_resized, (240, 135))  # Уменьшаем для передачи
        return img_resized  # Возвращаем одно изображение для передачи

def send_frame(ws, monitor_width, monitor_height):
    while True:
        frame = capture_screen(monitor_width, monitor_height)

        # Преобразуем изображение в RGB565
        rgb565 = frame.astype(np.uint16)
        r5 = (rgb565[..., 0] >> 3).astype(np.uint16) << 11
        g6 = (rgb565[..., 1] >> 2).astype(np.uint16) << 5
        b5 = (rgb565[..., 2] >> 3).astype(np.uint16)
        rgb565_flat = r5 | g6 | b5
        data = rgb565_flat.flatten()

        # Отправляем данные через WebSocket
        ws.send_binary(data.tobytes())

def on_open(ws, monitor_width, monitor_height):
    threading.Thread(target=send_frame, args=(ws, monitor_width, monitor_height)).start()

def run_websocket_server(ip_address, monitor_width, monitor_height):
    ws = websocket.WebSocketApp(f"ws://{ip_address}:81/", on_open=lambda ws: on_open(ws, monitor_width, monitor_height))
    ws.run_forever()

if __name__ == "__main__":
    # Запрашиваем у пользователя IP-адрес и разрешение экрана
    ip_address = input("Введите IP-адрес устройства: ")
    monitor_width = int(input("Введите ширину экрана (например, 1920): "))
    monitor_height = int(input("Введите высоту экрана (например, 1080): "))

    # Запускаем сервер WebSocket
    run_websocket_server(ip_address, monitor_width, monitor_height)
