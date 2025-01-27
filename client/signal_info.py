from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
import modem_config as config

def get_signal_info(url) -> dict:
    with Connection(url, username=config.USERNAME, password=config.PASSWORD) as connection:
        client = Client(connection)
        return client.device.signal()


if __name__ == "__main__":
    print(get_signal_info('http://192.168.8.1/'))