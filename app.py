from flask import Flask, render_template, request, redirect, session, jsonify
import pymysql

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

@app.route('/login', methods=['POST'])
def login():
    user_type = request.form['user_type']
    username = request.form['username']
    password = request.form['password']

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


@app.route('/dashboard_tenant')
def dashboard_tenant():
    # 假设这里有一些从数据库或其他来源获取的房源信息
    properties = [
        {"id": 1, "title": "Property 1", "rating": 4.5,
         "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        {"id": 2, "title": "Property 2", "rating": 4.0,
         "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
        # 更多房源信息
    ]
    return render_template('dashboard_tenant.html', properties=properties)

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
