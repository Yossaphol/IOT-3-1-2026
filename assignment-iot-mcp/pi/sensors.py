"""อ่านเซนเซอร์บน Raspberry Pi (ดัดแปลงจาก week04/sht31.py และ week03/ex5_ultrasonic.py)"""
import threading
import time

import RPi.GPIO as GPIO
import smbus3

import config

_lock = threading.Lock()   # กัน publisher กับ MCP Server อ่านเซนเซอร์พร้อมกัน
_gpio_ready = False


def init_gpio():
    global _gpio_ready
    if _gpio_ready:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.LED_PIN, GPIO.OUT)
    GPIO.setup(config.TRIG_PIN, GPIO.OUT)
    GPIO.setup(config.ECHO_PIN, GPIO.IN)
    GPIO.output(config.TRIG_PIN, False)
    _gpio_ready = True


def read_sht31():
    """คืน (temperature_c, humidity_percent) อ่านค่าใหม่ทุกครั้งที่เรียก"""
    with _lock:
        bus = smbus3.SMBus(1)
        try:
            bus.i2c_wr(config.SHT31_ADDR, [0x2C, 0x06])
            time.sleep(0.5)
            data = bytes(bus.i2c_rd(config.SHT31_ADDR, 6))
        finally:
            bus.close()
    raw_t = data[0] * 256 + data[1]
    raw_h = data[3] * 256 + data[4]
    temperature = -45 + (175 * raw_t / 65535.0)
    humidity = 100 * raw_h / 65535.0
    return round(temperature, 2), round(humidity, 2)


def read_distance_cm(timeout=0.05):
    """คืนระยะทางเป็น cm หรือ None ถ้าไม่มีเสียงสะท้อน (มี timeout กันโปรแกรมค้าง)"""
    with _lock:
        GPIO.output(config.TRIG_PIN, False)
        time.sleep(0.05)
        GPIO.output(config.TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(config.TRIG_PIN, False)

        deadline = time.time() + timeout
        pulse_start = time.time()
        while GPIO.input(config.ECHO_PIN) == 0:
            pulse_start = time.time()
            if pulse_start > deadline:
                return None

        deadline = time.time() + timeout
        pulse_end = time.time()
        while GPIO.input(config.ECHO_PIN) == 1:
            pulse_end = time.time()
            if pulse_end > deadline:
                return None

    return round((pulse_end - pulse_start) * 17150, 2)


def read_all():
    """อ่านเซนเซอร์ทั้งหมดเป็น dict (ค่าที่อ่านไม่ได้เป็น None)"""
    result = {"temperature": None, "humidity": None, "distance": None}
    try:
        result["temperature"], result["humidity"] = read_sht31()
    except Exception as exc:  # noqa: BLE001 - อ่านไม่ได้ก็ข้าม ไม่ให้ทั้งระบบล่ม
        print(f"[sensors] SHT31 error: {exc}")
    try:
        result["distance"] = read_distance_cm()
    except Exception as exc:  # noqa: BLE001
        print(f"[sensors] ultrasonic error: {exc}")
    return result


def set_led(on: bool):
    GPIO.output(config.LED_PIN, GPIO.HIGH if on else GPIO.LOW)


def cleanup():
    GPIO.cleanup()
