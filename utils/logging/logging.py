import logging
import sys
import pytz
from discord.utils import utcnow

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

from Constants import log_path

from .classes import TextStyling

def init_logging():
    colorama_init()

    # Set the root logger's level to the lowest level you want to log
    logging.basicConfig(level=logging.INFO)

    # Create a console handler and set its log level to INFO,
    datefmt = "%d.%m.%Y %H:%M:%S"
    console_formatter = logging.Formatter(f"{TextStyling.BOLD if supports_bold() else ''}{Fore.LIGHTBLACK_EX}%(asctime)s {Fore.BLUE}%(levelname)-8s{TextStyling.END if supports_bold() else ''} {Fore.CYAN}%(name)s{Style.RESET_ALL} %(message)s", datefmt=datefmt)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Create a file handler and set its log level to DEBUG
    file_formatter = logging.Formatter(f"%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt=datefmt)
    ist_timezone = pytz.timezone("Europe/Istanbul")
    curr_time = ist_timezone.normalize(utcnow().astimezone(ist_timezone))
    time_str = curr_time.strftime("%d-%m-%Y %H-%M")
    log_file_path = f'{log_path}bot {time_str}.log'
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Add the handlers to the root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def supports_bold():
    return sys.stdout.isatty()