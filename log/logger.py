import logging
import os

def configure_logger_file():
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'logs.log')
    return log_file

log_file = configure_logger_file()
logger = logging.getLogger('Simulation_app_logger')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s -[in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)
