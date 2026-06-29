import time

import serial
from serial.tools.list_ports import comports

SWEEP_AMPLITUDE = 500
SWEEP_PERIOD_SECONDS = 4.0
COMMAND_INTERVAL_SECONDS = 0.02


def open_tx() -> serial.Serial | None:
    for port in comports():
        if port.pid == 22336 and port.vid == 1155:
            return serial.Serial(port.device, 115200)
    return None


def triangle_wave(phase: float) -> float:
    """Return a triangle wave in range [-1.0, 1.0] for phase [0.0, 1.0)."""
    shifted_phase = (phase + 0.25) % 1.0
    return abs(4.0 * shifted_phase - 2.0) - 1.0


def main() -> None:
    device = open_tx()
    if device is None:
        print("No device found")
        return
    device.write(b"telemetry on\r\n")

    start_time = time.perf_counter()
    prev_packet_times = {}
    try:
        while True:
            elapsed = time.perf_counter() - start_time
            phase = (elapsed / SWEEP_PERIOD_SECONDS) % 1.0

            channel_0 = int(SWEEP_AMPLITUDE * triangle_wave(phase))
            channel_1 = int(SWEEP_AMPLITUDE * triangle_wave((phase + 0.5) % 1.0))

            # device.write(f"trainer 0 {channel_0}\r\n".encode())
            device.write(f"trainer 1 {channel_1}\r\n".encode())
            print(f"trainer 0={channel_0:>4}, trainer 1={channel_1:>4}", end="\r")

            response = device.read_all()
            now = time.perf_counter()
            if response:
                for frame in response.split(b"\xea"):  # CRSF start byte
                    if not frame:
                        continue
                    frame_type = frame[1:2]
                    delta_time = now - prev_packet_times.get(frame_type, now)
                    prev_packet_times[frame_type] = now
                    print(f"\nDelay: {delta_time:0.3f}, Frame type: {frame_type}")
                    if frame_type != b"\x1e":  # Attitude frame
                        continue
                    roll = int.from_bytes(frame[2:4], "big", signed=True) / 10000
                    pitch = int.from_bytes(frame[4:6], "big", signed=True) / 10000
                    yaw = int.from_bytes(frame[6:8], "big", signed=True) / 10000
                    print(f"Roll: {roll:0.2f}, Pitch: {pitch:0.2f}, Yaw: {yaw:0.2f}")
            time.sleep(COMMAND_INTERVAL_SECONDS)

    finally:
        print()
        device.write(b"telemetry off\r\n")
        device.close()


if __name__ == "__main__":
    main()
