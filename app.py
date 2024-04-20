from flask import Flask, render_template, request, redirect, session, jsonify, render_template_string

from captcha import generate_captcha_image
import pymysql
import json
import io

from read_function import get_state, get_city, get_property

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
        if selected_city:
            properties = get_property(selected_city).json
            return jsonify({'properties': properties})



@app.route('/property_details', methods=['POST'])
def property_details():
    selected_city = request.form.get('city')
    properties = get_property(selected_city).json
    return jsonify({'properties': properties})


@app.route('/appointment', methods=['POST'])
def make_appointment():
    appointment_data = request.json
    # 解析预约信息
    property_id = appointment_data['property_id']
    tenant_id = appointment_data['tenant_id']
    appointment_time = appointment_data['appointment_time']

    connection = connect_db()
    # 将预约信息插入到数据库中
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO appointment (property_id, tenant_id, appointment_time) VALUES (%s, %s, %s)"
            cursor.execute(sql, (property_id, tenant_id, appointment_time))
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        connection.close()



@app.route('/dashboard_landlord')
def dashboard_landlord():
    return "这是房东仪表板"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)