from clickhouse_driver import Client


class ClickhouseConfig():
    link_config = {
        'host': '192.168.2.175',
        'port': '9000',
        'user': 'research',
        'password': 'Zmhj@123456',
        'database': 'LEVEL2'
    }

    def create_client(self):
        click_client = Client(**self.link_config)
        return click_client
