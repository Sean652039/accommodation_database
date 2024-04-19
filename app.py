from flask import Flask, render_template, request, redirect, session, jsonify
from captcha import generate_captcha_image
import pymysql
import io

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
        cursor.execute("SELECT * FROM User WHERE user_id = %s ", (username))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['logged_in'] = True
            session['username'] = username
            if user_type == 'tenant':
                return redirect('/dashboard_tenant')
            else:
                return redirect('/dashboard_Landlord')
        else:
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    else:
        error_message = 'Invalid captcha'
        return render_template('login.html', error_message=error_message)


@app.route('/dashboard_tenant')
def dashboard_tenant():
    # 假设这里有一些从数据库或其他来源获取的房源信息
    # 假设这里有一些房源数据
    properties = [
        {"id": 1, "title": "Property 1", "rating": 4.5,
         "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        {"id": 2, "title": "Property 2", "rating": 4.0,
         "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        # 更多房源信息
    ]
    return render_template('dashboard_tenant.html', properties=properties)

properties = [
        {"id": 1, "title": "Property 1", "rating": 4.5,
         "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        {"id": 2, "title": "Property 2", "rating": 4.0,
         "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        # 更多房源信息
    ]

@app.route('/property/<int:property_id>')
def property_details(property_id):
    # 根据房源ID查找房源信息
    property = next((p for p in properties if p['id'] == property_id), None)
    if property:
        return render_template('property_details.html', property=property)
    else:
        return "Property not found", 404


@app.route('/appointment', methods=['POST'])
def make_appointment():
    if request.method == 'POST':
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