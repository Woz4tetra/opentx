import time

import pygame
import serial
from serial.tools.list_ports import comports


def open_tx() -> serial.Serial | None:
    for port in comports():
        if port.pid == 22336 and port.vid == 1155:
            return serial.Serial(port.device, 115200)
    return None


def draw_text(screen, text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def main() -> None:
    pygame.init()
    pygame.joystick.init()

    device = open_tx()
    if device is None:
        print("No device found")
        return
    device.write(b"telemetry on\r\n")

    joysticks = []
    horizontal_value = 1000
    vertical_value = 1000
    prev_receive_time = time.perf_counter()
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks.append(joy)
            for joystick in joysticks:
                horiz_axis = joystick.get_axis(0)
                vert_axis = joystick.get_axis(1)
                horizontal_value = int(500 * horiz_axis)
                vertical_value = int(-500 * vert_axis)

            rotate_command = f"trainer 0 {horizontal_value}\r\n"
            linear_command = f"trainer 3 {vertical_value}\r\n"
            device.write(rotate_command.encode())
            device.write(linear_command.encode())

            response = device.read_all()
            if response:
                for frame in response.split(b"\xea"):  # CRSF start byte
                    if not frame:
                        continue
                    now = time.perf_counter()
                    delta_time = now - prev_receive_time
                    prev_receive_time = now
                    print(f"Delay: {delta_time:0.3f}, Frame: {frame}")
                    if not frame[1:2] == b"\x1e":  # Attitude frame
                        continue
                    roll = int.from_bytes(frame[2:4], "big", signed=True) / 10000
                    pitch = int.from_bytes(frame[4:6], "big", signed=True) / 10000
                    yaw = int.from_bytes(frame[6:8], "big", signed=True) / 10000
                    print(
                        f"Delay: {delta_time:0.3f}, Roll: {roll:0.2f}, Pitch: {pitch:0.2f}, Yaw: {yaw:0.2f}"
                    )
            time.sleep(0.01)

    finally:
        device.write(b"telemetry off\r\n")
        device.close()
        pygame.quit()


if __name__ == "__main__":
    main()
