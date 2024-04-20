from flask import jsonify
import pymysql
import pandas as pd
import json

# MySQL 数据库连接配置
DB_HOST = '164.90.137.194'
DB_PORT = 3306
DB_USER = 'xix110'
DB_PASSWORD = 'InfSci2710_4692005'
DB_NAME = 'accomodation_database'


def connect_db():
    return pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def get_state():
    db = connect_db()
    state_name = pd.read_sql("SELECT state_name FROM State;", con=db)
    db.close()

    return jsonify(json.loads(state_name.to_json(orient='records')))

def get_city(state):
    db = connect_db()
    query = "SELECT city_name FROM City c JOIN CityLocateState cls ON c.city_id = cls.fk_city_id JOIN " \
            "State s ON s.state_id = cls.fk_state_id WHERE s.state_name = %s;"
    city_name = pd.read_sql(query, con=db, params=(state,))
    db.close()

    return jsonify(json.loads(city_name.to_json(orient='records')))

def get_property(city):
    db = connect_db()
    query = "SELECT * FROM PropertyInfo WHERE city_name = %s"
    properties = pd.read_sql(query, con=db, params=(city,))
    db.close()

    return jsonify(json.loads(properties.to_json(orient='records')))