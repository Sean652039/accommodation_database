from flask import Flask, render_template, request, redirect, session, jsonify, render_template_string

from captcha import generate_captcha_image
import pymysql
import json
import io

from read_function import get_state, get_city, get_property, insert_appointment

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


@app.route('/dashboard_landlord')
def dashboard_landlord():
    return "这是房东仪表板"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

from flask import Flask, render_template, request, redirect, session, jsonify, render_template_string

from captcha import generate_captcha_image
import pymysql
import json
import io

from read_function import get_state, get_city, get_property, insert_appointment

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


@app.route('/dashboard_landlord')
def dashboard_landlord():
    return "这是房东仪表板"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # Get user input from the registration form
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']  # Get the selected user type
        # Add more fields as needed

        # Check if the username already exists
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        cursor.close()
        db.close()

        if existing_user:
            error_message = "Username already exists. Please enter a different username."
            return render_template('register.html', error_message=error_message)
        elif password != confirm_password:
            error_message = "The passwords entered twice are inconsistent."
            return render_template('register.html', error_message=error_message)
        elif password == confirm_password:
            # Insert the new user into the database
            db = connect_db()
            cursor = db.cursor()
            try:
                cursor.execute("INSERT INTO User (username) VALUES (%s)", (username, ))
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
                flash('Registration successful! You can now login.')
                # Redirect to login page after successful registration
                return redirect('/')

            except Exception as e:
                # Handle registration errors
                error_message = "Registration failed. Please try again."
                return render_template('register.html', error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)
