import logging
import serial
import RPi.GPIO as GPIO

from log import get_logger


logger = get_logger(__name__, logging.INFO)


class SMSHandler:
    """
    This module is for control Sim900A.
    More documents is available at:
    https://www.developershome.com/sms/
    """
    GPIO.setmode(GPIO.BOARD)

    # AT commands are instructions used to control a modem.
    # AT is the abbreviation of ATtention. Every command line starts with "AT" or "at".
    # And every commands must end with a carriage return character, in this case: "\r\n".
    # Common AT commands:
    STATUS_COMMAND = "AT"  # Check device status. Example: OK/ERROR
    MANUFACTURER_COMMAND = "AT+CMGI"  # Name of manufacturer. Example: SIMCOM_Ltd
    MODULE_NUMBER_COMMAND = "AT+CGMM"  # Example: SIMCOM_SIM900A
    IMEI_NUMBER_COMMAND = "AT+CGSN"  # Example: 359771032619408
    ECHO_COMMAND = "ATE"  # 1/0 = on/off
    SOFTWARE_VERSION_COMMAND = "AT+CGMR"  # Example: Revision:1137B11SIM900A32_ST
    SUBSCRIBE_SMS_COMMAND = "AT+CNMI"  # Obtain notifications of newly received SMS messages
    MESSAGE_FORMAT_COMMAND = "AT+CMGF"  # Select the operating mode of the GSM/GPRS modem or mobile phone. Text mode is 1.

    def __init__(self, port="/dev/ttyS0", baudrate=9600, timeout=1):
        self.modem = serial.Serial(port, baudrate, timeout=timeout)

    def response(self):
        msg = b''
        while self.modem.in_waiting > 0:
            msg += self.modem.read(self.modem.in_waiting)

        resp = msg
        try:
            return resp.decode('utf8', 'ignore')
        except Exception as e:
            logger.error(e)
            logger.debug(resp)
            return resp.decode('utf8', "ignore")

    def send_command(self, command):
        command = command + "\r\n"
        self.modem.write(command.encode())
        logger.debug("Send command: {}".format(command))

    def set_text_mode(self):
        self.send_command(self.MESSAGE_FORMAT_COMMAND + "=1")   # AT+CMGF=1

    def ping(self):
        resp = self.send_command(self.STATUS_COMMAND)
        r = self.response()
        if "OK" in r:
            return True
        return False

    def set_echo(self, status='0'):
        self.send_command(self.ECHO_COMMAND + status)  # ATE0

    def subscribe(self, params='3,2,0,0,0'):
        self.send_command(self.SUBSCRIBE_SMS_COMMAND + "={}".format(params))  # AT+CNMI=3,1,0,0,0

