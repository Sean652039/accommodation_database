from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from captcha import generate_captcha_image
import io

from API import (check_login_api, get_state_api, get_city_api, get_property_api, insert_appointment_api,
                 get_contracts_api, publish_property_api, register_api, transaction_sign_contract_api)


app = Flask(__name__, template_folder="templates")
app.secret_key = 'IS2710'


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/captcha')
def captcha():
    # Generate a CAPTCHA image using the above function
    image, captcha_text = generate_captcha_image()

    # Store CAPTCHA text to session for later validation
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
            session['username'] = username  # or session['user_id'] = user_id depending on how you manage the session

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
        # Handle GET requests, render templates and provide state dropdowns
        states = get_state_api().json
        html_data_state = '<label for="state">State:</label><select id="state"><option value="">Select State</option>'
        for state in states:
            state_name = state.get('state_name')
            html_data_state += f'<option value="{state_name}">{state_name}</option>'
        html_data_state += '</select>'

        return render_template('dashboard_tenant.html', html_data_state=html_data_state)
    elif request.method == 'POST':
        # Process the POST request, get the selected state and return a list of cities
        selected_state = request.form.get('state')  # Get selected states
        if selected_state:
            cities = get_city_api(selected_state).json  # Get a list of cities in the state from the database
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
            <!-- Detailed information -->
            <div id="details{property['property_id']}" class="details">
                <p>Property Detail ID: {property['property_id']}</p>
                <p>Year Built: {property['year_built']}</p>
                <p>Square Feet: {property['square_feet']}</p>
                <p>Bedrooms: {property['bedrooms_num']}</p>
                <p>Bathrooms: {property['bathrooms_num']}</p>
                <!--  Appointment button -->
                <button class="appointment-button" onclick="makeAppointment({property['property_id']})">Make Appointment</button>
                <button class="contract-button" onclick="signContract({property['property_id']})">Sign Contract</button>
            </div>
        </div>
        """
    return jsonify({'html_data_property': html_data_property})


@app.route('/appointment', methods=['POST'])
def make_appointment():
    # Parsing reservation information
    property_id = request.json.get('property_id')
    appointment_name = request.json.get('tenant_name')
    appointment_date = request.json.get('appointment_time')

    result = insert_appointment_api(property_id, appointment_name, appointment_date)

    return result


@app.route('/contract', methods=['POST'])
def execute_contract():
    property_id = request.json.get('property_id')
    tenant_name = request.json.get('tenant_name')
    contract_price = request.json.get('price')
    payment_amount = contract_price

    response = transaction_sign_contract_api(property_id, tenant_name, contract_price, payment_amount)

    return response


@app.route('/dashboard_landlord', methods=['GET'])
def dashboard_landlord():
    if request.method == 'GET':
        # :: Obtain information on all contracts from the database
        contracts = get_contracts_api()

        # Generate HTML content for contract information
        html_data_contracts = '<div class="contracts-listing">'
        for contract in contracts:
            html_data_contracts += f'<div class="contract-item"><p>Signing Date: {contract["signing_date"]}</p><p>Contract Price: {contract["contract_price"]}</p></div>'
        html_data_contracts += '</div>'

        # Contract data passed to templates
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
