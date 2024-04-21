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


def check_login_api(username):
    # Perform a database query here to verify username and password match
    db = connect_db()
    cursor = db.cursor()

    # First query the User table for user_id
    cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
    user_result = cursor.fetchone()
    if user_result:
        user_id = user_result[0]

        # Then query the related table to get the password_id
        cursor.execute("SELECT password_id FROM UserUsePassword WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            password_id = result[0]
            # Query plaintext passwords using password_id
            cursor.execute("SELECT password FROM Password WHERE password_id = %s", (password_id,))
            password_result = cursor.fetchone()[0]
            cursor.close()
            db.close()

    return jsonify({'password': password_result})


def get_state_api():
    db = connect_db()
    state_name = pd.read_sql("SELECT state_name FROM State;", con=db)
    db.close()

    return jsonify(json.loads(state_name.to_json(orient='records')))


def get_city_api(state):
    db = connect_db()
    query = "SELECT city_name FROM City c JOIN CityLocateState cls ON c.city_id = cls.fk_city_id JOIN " \
            "State s ON s.state_id = cls.fk_state_id WHERE s.state_name = %s;"
    city_name = pd.read_sql(query, con=db, params=(state,))
    db.close()

    return jsonify(json.loads(city_name.to_json(orient='records')))


def get_property_api(city):
    db = connect_db()
    query = "SELECT * FROM PropertyInfo WHERE city_name = %s"
    properties = pd.read_sql(query, con=db, params=(city,))
    db.close()

    return jsonify(json.loads(properties.to_json(orient='records')))


def insert_appointment_api(property_id, appointment_name, appointment_date):
    connection = connect_db()
    # Insertion of reservation information into the database
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
            sql = "INSERT INTO Appointments (property_id, initiator_user_id, receiver_user_id, appointment_time, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (property_id, tenant_id, landlord_id, appointment_date, 'scheduled'))
        connection.commit()
        connection.close()
        return jsonify({'success': True})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'error': str(e)})


def transaction_sign_contract_api(property_id, tenant_name, contract_price, payment_amount):
    db = connect_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT fk_user_id FROM UserOwnProperty WHERE fk_property_id = %s", (property_id,))
            user_result = cursor.fetchone()
            if user_result:
                second_party_id = user_result[0]
                cursor.execute("SELECT user_id FROM User WHERE username = %s", (tenant_name,))
                user_result_tenant = cursor.fetchone()
                if user_result_tenant:
                    first_party_id = user_result_tenant[0]
            # Calling Stored Procedures
            cursor.callproc('CreateContractAndPayment', (contract_price, first_party_id, second_party_id, property_id, payment_amount))
            # Commit transactions
            db.commit()
            return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)})

    finally:
        db.close()


def get_contracts_api():
    db = connect_db()
    try:
        # 只查询 signing_date 和 contract_price 两列
        query = "SELECT signing_date, contract_price FROM Contract;"
        contracts_data = pd.read_sql(query, con=db)
        return contracts_data.to_dict(orient='records')  # Convert the result to a dictionary list
    finally:
        db.close()


def check_or_insert(cursor, table, column, value, id_column_name):
    """Check if the value exists in the table; if not, insert it and return its id."""
    query = f"SELECT {id_column_name} FROM {table} WHERE {column} = %s"
    cursor.execute(query, (value,))
    result = cursor.fetchone()
    if result:
        return result[id_column_name]
    else:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s)", (value,))
        cursor.connection.commit()  # Ensure the insert is committed if needed
        return cursor.lastrowid


def connect_tables(cursor, table, column1, column2, value1, value2):
    """Connect entries in junction tables."""
    cursor.execute(f"INSERT INTO {table} ({column1}, {column2}) VALUES (%s, %s)", (value1, value2))


def publish_property_api(state, city, address, description):
    db = connect_db()
    try:
        with db.cursor() as cursor:
            # Check or insert state and city with the correct id column names
            state_id = check_or_insert(cursor, "State", "state_name", state, "state_id")
            city_id = check_or_insert(cursor, "City", "city_name", city, "city_id")

            # Insert into Address table
            cursor.execute("INSERT INTO Address (line1) VALUES (%s)", (address,))
            address_id = cursor.lastrowid

            # Insert into Property table
            cursor.execute("INSERT INTO Property (description) VALUES (%s)", (description,))
            property_id = cursor.lastrowid

            # Establish relationships through foreign keys
            connect_tables(cursor, "CityLocateState", "fk_city_id", "fk_state_id", city_id, state_id)
            connect_tables(cursor, "PropertyLocateAddress", "fk_property_id", "fk_address_id", property_id, address_id)
            connect_tables(cursor, "AddressLocateCity", "fk_address_id", "fk_city_id", address_id, city_id)

            db.commit()
            response = {'status': 'success', 'message': 'Publish Success'}
            return jsonify(response)  # Return JSON response upon success
    except Exception as e:
        db.rollback()
        response = {'status': 'error', 'message': str(e)}
    finally:
        db.close()
    return jsonify(response)


def register_api(username, password, confirm_password, user_type):
    # Check if the username already exists
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    cursor.close()
    db.close()

    if existing_user:
        error_message = "Username already exists. Please enter a different username."
        response = {'status': 'error', 'message': error_message}
        return jsonify(response)
    elif password != confirm_password:
        error_message = "The passwords entered twice are inconsistent."
        response = {'status': 'error', 'message': error_message}
        return jsonify(response)
    elif password == confirm_password:
        # Insert the new user into the database
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO User (username) VALUES (%s)", (username,))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO UserIsUserType (user_id, type_id) VALUES (%s, %s)",
                           (user_id, 1 if user_type == 'tenant' else 2))
            cursor.execute("INSERT INTO Password (password) VALUES (%s)", (password,))
            password_id = cursor.lastrowid
            cursor.execute("INSERT INTO UserUsePassword (user_id, password_id) VALUES (%s, %s)",
                           (user_id, password_id))
            db.commit()
            cursor.close()
            db.close()
            response = {'status': 'success', 'message': 'Registration successful! You can now login.'}
            return jsonify(response)  # Return JSON response upon success

        except Exception as e:
            # Handle registration errors
            error_message = "Registration failed. Please try again."
            response = {'status': 'error', 'message': error_message}
            return jsonify(response)

