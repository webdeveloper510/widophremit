
from .package import *
import socket
import datetime
from datetime import datetime
import logging



def error_logs(message):
    logging.basicConfig(filename='error_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info(str(message))

def success_logs(message):
    logging.basicConfig(filename='success_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info(str(message))

def get_current_date():
	return timezone.now().date()

def get_current_year():
    return timezone.now().year

def get_current_datetime():
    return timezone.now()


def float_int(value):
    value = replace_comma(value)
    if '.' in str(value):
        return float(value)
    else:
        return int(value)
    
def replace_comma(value):
    value = str(value).replace(",","")
    return value

def comma_value(value):
    if value ==  None or str(value).strip() == "":
        value = 0    
    value = float(replace_comma(value))
    if value > float(1) or value == float(1):
        value = "{0:,.2f}".format(value)
    else:
        value = "{:.4f}".format(value) 
    return str(value)
    
