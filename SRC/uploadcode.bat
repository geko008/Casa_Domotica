esptool --port COM3 erase_flash
esptool --port COM3 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20251209-v1.27.0.bin
ampy --port COM3 put main.py
ampy --port COM3 put umqtt_simple.py