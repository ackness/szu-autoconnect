import socket
import time

import requests
import retrying
from loguru import logger

DEFAULT_CONFIGS = {
    'ip-ping': 'www.baidu.com',
    'header': {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    },
    'zone': {
        'office': 'https://drcom.szu.edu.cn',
        'dormitory': 'http://172.30.255.2/0.htm'
    }
}


class DisconnectError(Exception):
    pass


def disconnect_error(exception):
    return isinstance(exception, ZeroDivisionError)


class Connector:
    def __init__(self, config, log_printer=None):
        self.run_flag = False
        self.set_logger(log_printer)
        self.set_config(config)

    @staticmethod
    def set_logger(log_printer):
        log_fmt = "{time:YYYY-MM-DD | HH:mm:ss} | {level} | {message}"
        if log_printer is not None:
            logger.add(log_printer, level="DEBUG", format=log_fmt)
        else:
            logger.add('auto-connect.log', level="DEBUG", format=log_fmt)
        logger.info("Auto-Connect Init")

    def set_config(self, config: dict):
        try:
            self.headers = DEFAULT_CONFIGS['header']
            self.login_url = DEFAULT_CONFIGS['zone'][config['zone']]
            self.ping_ip = DEFAULT_CONFIGS['ip-ping']
            self.data_send = {
                "DDDDD": f"{config['username']}",
                "upass": f"{config['password']}",
                "R1": "0",
                "R2": "",
                "R6": "0",
                "para": "00",
                "OMKKey": "123456"
            }
            self.interval = config['interval']
            logger.info(f"Auto-Connect Load config {config}")
        except KeyError as e:
            logger.error(f'Please check the config, {e}')

    def connect(self):
        # requests.packages.urllib3.disable_warnings()
        session = requests.session()
        r = session.post(self.login_url, headers=self.headers, data=self.data_send, verify=False)
        # print(r.text)

    def check_connect(self):
        s = socket.socket()
        s.settimeout(3)
        try:
            status = s.connect_ex((self.ping_ip, 443))
            if status == 0:
                s.close()
                logger.info("Connected")
                return True
            else:
                logger.info("Disconnected")
                raise DisconnectError
                # return False
        except Exception as e:
            logger.error(f'Find Error in check connect, {e}')
            raise DisconnectError

    def stop(self):
        logger.info("Stop")
        self.run_flag = False

    @retrying.retry(retry_on_exception=disconnect_error)
    def run(self):
        logger.info('Start Run')
        try:
            self.check_connect()
        except DisconnectError:
            self.connect()
        except Exception as e:
            logger.error(f'Find Error when running: {e}')
            raise DisconnectError
        finally:
            # double check
            self.check_connect()

    def loop(self):
        self.run_flag = True
        while self.run_flag:
            self.run()
            time.sleep(60)
