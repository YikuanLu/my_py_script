import sys

import mysql.connector
from xml.dom.minidom import parse


def read_product_info(product):
    db_config = {
        'host': '192.168.2.113',
        'user': 'zmhj-devel',
        'passwd': 'Zmhj@123456',
        'port': 3306,
        'auth_plugin': 'mysql_native_password',
        'db': 'ALGOTS_DB',
    }

    db_connecter = mysql.connector.connect(**db_config)
    cur = db_connecter.cursor()

    sql = F"select `password` from `product` where product_id = '{product}'"
    cur.execute(sql)
    datas = cur.fetchall()
    return datas[0][0]


def updateXML(product):
    domTree = parse(F"{product}.xml")
    rootNode = domTree.documentElement

    # xml_username = rootNode.getElementsByTagName('username')
    # xml_username[0].firstChild.data = username

    psd = read_product_info(product)

    xml_password = rootNode.getElementsByTagName('password')
    xml_password[0].firstChild.data = psd

    with open('./XTP_T0_01.xml', 'w') as f:
        domTree.writexml(f, addindent='', encoding='utf-8')


if __name__ == '__main__':
    product = sys.argv[1]
    updateXML(product)
