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


def insert_appointment(property_id, appointment_name, appointment_date):
    connection = connect_db()
    # 将预约信息插入到数据库中
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT fk_user_id FROM UserOwnProperty WHERE fk_property_id = %s", (property_id,))
            user_result = cursor.fetchone()
            if user_result:
                landlord_id = user_result[0]
                cursor.execute("SELECT user_id FROM User WHERE username = %s", (appointment_name,))
                user_result_tenant = cursor.fetchone()
                if user_result_tenant:
                    tenant_id = user_result_tenant[0]
                    print(tenant_id)
            sql = "INSERT INTO Appointments (property_id, initiator_user_id, receiver_user_id, appointment_time, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (property_id, tenant_id, landlord_id, appointment_date, 'scheduled'))
        connection.commit()
        connection.close()
        return jsonify({'success': True})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'error': str(e)})

