from flask import Flask, render_template, request, redirect, session, jsonify, flash
from captcha import generate_captcha_image
import pymysql
import io

from API import (check_login_api, get_state_api, get_city_api, get_property_api, insert_appointment_api,
                 get_contracts_api, publish_property_api, register_api)


app = Flask(__name__, template_folder="templates")
app.secret_key = 'IS2710'  # 用于加密 session 数据的密钥，请替换成你自己的密钥


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
        password_result = check_login_api(username).json['password']
        if password_result and password_result == password:
            session['logged_in'] = True
            session['username'] = username  # 或 session['user_id'] = user_id，取决于你如何管理会话

            if user_type == 'tenant':
                return redirect('/dashboard_tenant')
            else:
                return redirect('/dashboard_landlord')

        error_message = 'Invalid username or password'
        return render_template('login.html', error_message=error_message)
    else:
        error_message = 'Invalid captcha'
        return render_template('login.html', error_message=error_message)


@app.route('/dashboard_tenant', methods=['GET', 'POST'])
def dashboard_tenant():
    if request.method == 'GET':
        # 处理GET请求，渲染模板并提供州的下拉菜单
        states = get_state_api().json
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
            cities = get_city_api(selected_state).json  # 从数据库中获取该州的城市列表
            html_data_city = '<label for="city">City:</label><select id="city"><option value="">Select City</option>'
            for city in cities:
                city_name = city.get('city_name')
                html_data_city += f'<option value="{city_name}">{city_name}</option>'
            html_data_city += '</select>'

            # html_data_city = f'<div id="city-selection">{html_data_city}</div>'
            return jsonify({'html_data_city': html_data_city})



@app.route('/property_details', methods=['POST'])
def property_details():
    selected_city = request.form.get('city')
    properties = get_property_api(selected_city).json
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

    result = insert_appointment_api(property_id, appointment_name, appointment_date)

    return result


@app.route('/dashboard_landlord', methods=['GET'])
def dashboard_landlord():
    if request.method == 'GET':
        # 从数据库获取所有合同信息
        contracts = get_contracts_api()

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

    responses = publish_property_api(state, city, address, description).json
    if responses['status'] == 'success':
        flash(responses['message'], 'success')  # Flash a success message
        return redirect(render_template('dashboard_landlord.html'))  # Redirect to the form page
    elif responses['status'] == 'error':
        flash(responses['message'], 'error')  # Flash an error message


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

        responses = register_api(username, password, confirm_password, user_type).json
        if responses['status'] == 'success':
            flash(responses['message'], 'success')  # Flash a success message
            return redirect('/')
        elif responses['status'] == 'error':
            return render_template('register.html', error_message=responses['message'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
