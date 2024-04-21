from flask import Flask, render_template, request, redirect, session, jsonify, render_template_string,flash
from captcha import generate_captcha_image
import pymysql
import json
import io

from read_function import get_state, get_city, get_property, insert_appointment,get_contracts,connect_db, check_or_insert, connect_tables


app = Flask(__name__, template_folder="templates")
app.secret_key = 'IS2710'  # 用于加密 session 数据的密钥，请替换成你自己的密钥

# MySQL 数据库连接配置
DB_HOST = '164.90.137.194'
DB_PORT = 3306
DB_USER = 'xix110'
DB_PASSWORD = 'InfSci2710_4692005'
DB_NAME = 'accomodation_database'


def connect_db():
    return pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/captcha')
def captcha():
    # 使用上述函数生成验证码图片
    image, captcha_text = generate_captcha_image()

    # 将验证码文本存储到session，以便之后进行验证
    session['captcha'] = captcha_text

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue(), 200, {
        'Content-Type': 'image/png',
        'Content-Length': str(len(buf.getvalue()))
    }


@app.route('/login', methods=['POST'])
def login():
    user_type = request.form['user_type']
    username = request.form['username']
    password = request.form['password']
    captcha = request.form['captcha']


    if captcha.upper() == session.get('captcha', '').upper():
        # 在这里进行数据库查询，验证用户名和密码是否匹配
        db = connect_db()
        cursor = db.cursor()

        # 首先查询 User 表以获取 user_id
        cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]

            # 然后查询关联表以获取 password_id
            cursor.execute("SELECT password_id FROM UserUsePassword WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                password_id = result[0]
                # 使用 password_id 查询明文密码
                cursor.execute("SELECT password FROM Password WHERE password_id = %s", (password_id,))
                password_result = cursor.fetchone()
                if password_result and password_result[0] == password:
                    session['logged_in'] = True
                    session['username'] = username  # 或 session['user_id'] = user_id，取决于你如何管理会话
                    cursor.close()
                    db.close()
                    if user_type == 'tenant':
                        return redirect('/dashboard_tenant')
                    else:
                        return redirect('/dashboard_Landlord')
        cursor.close()
        db.close()
        error_message = 'Invalid username or password'
        return render_template('login.html', error_message=error_message)
    else:
        error_message = 'Invalid captcha'
        return render_template('login.html', error_message=error_message)


@app.route('/dashboard_tenant', methods=['GET', 'POST'])
def dashboard_tenant():
    if request.method == 'GET':
        # 处理GET请求，渲染模板并提供州的下拉菜单
        states = get_state().json
        html_data_state = '<label for="state">State:</label><select id="state"><option value="">Select State</option>'
        for state in states:
            state_name = state.get('state_name')
            html_data_state += f'<option value="{state_name}">{state_name}</option>'
        html_data_state += '</select>'

        return render_template('dashboard_tenant.html', html_data_state=html_data_state)
    elif request.method == 'POST':
        # 处理POST请求，获取选定的州并返回城市列表
        selected_state = request.form.get('state')  # 获取选定的州
        if selected_state:
            cities = get_city(selected_state).json  # 从数据库中获取该州的城市列表
            html_data_city = '<label for="city">City:</label><select id="city"><option value="">Select City</option>'
            for city in cities:
                city_name = city.get('city_name')
                html_data_city += f'<option value="{city_name}">{city_name}</option>'
            html_data_city += '</select>'

            # html_data_city = f'<div id="city-selection">{html_data_city}</div>'
            return jsonify({'html_data_city': html_data_city})
        selected_city = request.form.get('city')
        # if selected_city:
        #     properties = get_property(selected_city).json
        #     return jsonify({'properties': properties})



@app.route('/property_details', methods=['POST'])
def property_details():
    selected_city = request.form.get('city')
    properties = get_property(selected_city).json
    html_data_property = ''
    for property in properties:
        html_data_property += f"""
        <div class="property">
            <h3>{property['property_id']}</h3>
            <p>{property['description']}</p>
            <button class="details-button" onclick="showDetails({property['property_id']})">Details</button>
            <!-- 详细信息 -->
            <div id="details{property['property_id']}" class="details">
                <p>Property Detail ID: {property['property_id']}</p>
                <p>Year Built: {property['year_built']}</p>
                <p>Square Feet: {property['square_feet']}</p>
                <p>Bedrooms: {property['bedrooms_num']}</p>
                <p>Bathrooms: {property['bathrooms_num']}</p>
                <!-- 预约按钮 -->
                <button class="appointment-button" onclick="makeAppointment({property['property_id']})">Make Appointment</button>
            </div>
        </div>
        """
    return jsonify({'html_data_property': html_data_property})


@app.route('/appointment', methods=['POST'])
def make_appointment():

    # 解析预约信息
    property_id = request.json.get('property_id')
    appointment_name = request.json.get('tenant_name')
    appointment_date = request.json.get('appointment_time')

    result = insert_appointment(property_id, appointment_name, appointment_date)

    return result


@app.route('/dashboard_landlord', methods=['GET'])
def dashboard_landlord():
    if request.method == 'GET':
        # 从数据库获取所有合同信息
        contracts = get_contracts()

        # 生成合同信息的 HTML 内容
        html_data_contracts = '<div class="contracts-listing">'
        for contract in contracts:
            html_data_contracts += f'<div class="contract-item"><p>Signing Date: {contract["signing_date"]}</p><p>Contract Price: {contract["contract_price"]}</p></div>'
        html_data_contracts += '</div>'

        # 向模板传递合同数据
        return render_template('dashboard_landlord.html', html_data_contracts=html_data_contracts)


@app.route('/publish_property', methods=['POST'])
def publish_property():
    description = request.form['description']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']

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
            flash('Publish Success', 'success')  # Flash a success message
            return redirect(render_template('dashboard_landlord.html'))  # Redirect to the form page
    except Exception as e:
        db.rollback()
        flash(str(e), 'error')  # Flash an error message
    finally:
        db.close()
    return render_template('dashboard_landlord.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)