"""อุปกรณ์บน Raspberry Pi: Ultrasonic HC-SR04 + LED
(ดัดแปลงจาก week03/ex5_ultrasonic.py และ week01/led.py)
"""
import threading
import time

import RPi.GPIO as GPIO

import config

_lock = threading.Lock()   # กัน publisher กับ MCP Server สั่ง ultrasonic พร้อมกัน
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
    """อ่านเซนเซอร์บน Pi เป็น dict (ค่าที่อ่านไม่ได้เป็น None)"""
    try:
        distance = read_distance_cm()
    except Exception as exc:  # noqa: BLE001 - อ่านไม่ได้ก็ข้าม ไม่ให้ทั้งระบบล่ม
        print(f"[sensors] ultrasonic error: {exc}")
        distance = None
    return {"distance": distance}


def set_led(on: bool):
    GPIO.output(config.LED_PIN, GPIO.HIGH if on else GPIO.LOW)


def cleanup():
    GPIO.cleanup()
