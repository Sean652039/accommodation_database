import pymysql
from flask import jsonify

# MySQL 数据库连接配置
DB_HOST = '164.90.137.194'
DB_PORT = 3306
DB_USER = 'xix110'
DB_PASSWORD = 'InfSci2710_4692005'
DB_NAME = 'accomodation_database'


def connect_db():
    return pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def get_state_city():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT state_name FROM State")
    state_name = jsonify(cursor.fetchall())
    cursor.execute("SELECT city_name FROM City")
    city_name = jsonify(cursor.fetchall())

    cursor.close()
    db.close()

    return state_name, city_name