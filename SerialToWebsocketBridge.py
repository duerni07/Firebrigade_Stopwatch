import serial, serial.tools.list_ports #pip install pyserial
from websockets.sync.client import connect #pip install websockets
import os
import threading
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WEBSOCKET_URL = "ws://localhost:5000/websocket/control_watch"
ESP32_DEVICE_NAME = "Silicon Labs CP210x USB to UART Bridge"

def getESP32Port(deviceName: str = ESP32_DEVICE_NAME):
    esp32Port = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if deviceName in str(port):
            esp32Port = str(port).split(" ")[0]
            return esp32Port
    logger.debug(f"No connected esp32 with name \"{deviceName}\" found.")
    return None

class SerialToWebsocketBridge:
    def __init__(self, esp32Port, baudrate=115200, websocket_url=WEBSOCKET_URL):
        self.esp32Port = esp32Port
        self.baudrate = baudrate
        self.ser = None
        self.websocket_url = websocket_url
        self.websocket = None

    def discover_esp32(self):
        self.esp32Port = getESP32Port()
        if self.esp32Port is not None:
            logger.debug(f"Discovered ESP32 at port {self.esp32Port}")

    def close(self):
        self.esp32Port = None
        if self.ser is not None:
            self.ser.close()
            logger.debug(f"Closed serial port {self.esp32Port}")
        if self.websocket is not None:
            logger.debug(f"Disconnected from websocket {self.websocket_url}")
            self.websocket.close()

    def connect_to_serial(self):
        try:
            logger.debug(f"Try to connect to esp32 on serial port {self.esp32Port} with baudrate {self.baudrate}")
            self.ser = serial.Serial(self.esp32Port, self.baudrate, timeout=None)
            self.ser.flush()
            logger.info(f"Successfully connected to esp32 on serial port {self.esp32Port}")
        except serial.serialutil.SerialException as e:
            error_message = f"Could not connect to esp32 on serial port {self.esp32Port}.  Serial port already in use. Close any other program using it and try again"
            logger.error(error_message)
            raise PermissionError(error_message)
        
    def connect_to_websocket(self):
        try:
            logger.debug(f"Try to connect to websocket {self.websocket_url}")
            self.websocket = connect(self.websocket_url)
            logger.debug(f"Successfully connected to websocket {self.websocket_url}")
        except Exception as e:
            logger.error(f"Could not connect to websocket {self.websocket_url}")

    def _read_from_serial_and_forward_to_websocket(self):
        while True:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().strip().decode("iso-8859-1")
                logger.debug(f"Received on serial and forward it to websocket: {line}")
                self.websocket.send(line)
                message = self.websocket.recv()
                logger.debug(f"Received on websocket: {message}")
                if message is not None and message.startswith("$"):
                    message = message[1:]
                    logger.debug(f"Forwarding message to serial: {message}")
                    self.ser.write(message.encode("iso-8859-1"))

    def start(self):
        while True:
            while self.esp32Port is None:
                self.discover_esp32()
                threading.Event().wait(1)
            logger.info(f"Starting Serial to Websocket Bridge")
            self.connect_to_serial()
            self.connect_to_websocket()
            try:
                self._read_from_serial_and_forward_to_websocket()
            except serial.serialutil.SerialException as e:
                logger.debug(f"Serial port {self.esp32Port} has been disconnected. Trying to reconnect.")
                self.close()
                threading.Event().wait(3)
            except KeyboardInterrupt:
                self.close()
                break
            except Exception as e:
                logger.error(f"Shutting down the Serial to Websocket Bridge because of an error: {e}")
                self.close()
                break
