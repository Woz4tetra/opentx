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

    joysticks = []
    horizontal_value = 1000
    vertical_value = 1000
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

            rotate_command = f"trainer 0 0 {horizontal_value}\r\n"
            linear_command = f"trainer 0 3 {vertical_value}\r\n"
            device.write(rotate_command.encode())
            device.write(linear_command.encode())
            time.sleep(0.01)

    finally:
        device.close()
        pygame.quit()


if __name__ == "__main__":
    main()
