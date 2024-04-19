/* 
Jiazhe Wen(jiw321@pitt.edu)
Zhiyun Chen(zhc148@pitt.edu)
Xianglong Xu(xix110@pitt.edu)
*/

USE accomodation_database;

# Drop
DROP TABLE IF EXISTS PaymentUsePaymentMethod;
DROP TABLE IF EXISTS PaymentOfContract;
DROP TABLE IF EXISTS Contract;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS PaymentMethod;
DROP TABLE IF EXISTS PropertyLocateAddress;
DROP TABLE IF EXISTS ZipCodeOfAddress;
DROP TABLE IF EXISTS AddressLocateCity;
DROP TABLE IF EXISTS CityLocateState;
DROP TABLE IF EXISTS ZipCode;
DROP TABLE IF EXISTS Address;
DROP TABLE IF EXISTS City;
DROP TABLE IF EXISTS State;
DROP TABLE IF EXISTS PropertyDetail;
DROP TABLE IF EXISTS UserUsePassword;
DROP TABLE IF EXISTS UserIsUserType;
DROP TABLE IF EXISTS Password;
DROP TABLE IF EXISTS UserType;

DROP TABLE IF EXISTS Appointments;
DROP TABLE IF EXISTS Images;
DROP TABLE IF EXISTS MarketListings;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Property;


# Create
CREATE TABLE IF NOT EXISTS Payment(
	payment_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    payment_date DATETIME NOT NULL,
    amount DOUBLE NOT NULL
)ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS PaymentMethod(
	method_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    method_type VARCHAR(30) NOT NULL
)ENGINE = InnoDB;

CREATE TABLE User (
	user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    f_name VARCHAR(30) NOT NULL,
    l_name VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE UserType (
    type_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Password (
    password_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Property (
    property_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ZipCode(
	zipcode_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    number VARCHAR(20) NOT NULL
)ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS Address(
	address_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    line1 VARCHAR(255) NOT NULL,
    line2 VARCHAR(255)
)ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS City(
	city_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    city_name VARCHAR(20) NOT NULL
)ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS State(
	state_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    state_name VARCHAR(20) NOT NULL,
    short_name VARCHAR(10)
)ENGINE = InnoDB;

CREATE TABLE UserIsUserType (
    user_id INT,
    type_id INT,
    PRIMARY KEY (user_id, type_id),
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES User(user_id),
    CONSTRAINT fk_type_id FOREIGN KEY (type_id) REFERENCES UserType(type_id)
) ENGINE=InnoDB;

CREATE TABLE UserUsePassword (
    user_id INT UNIQUE,
    password_id INT,
    PRIMARY KEY (user_id, password_id),
    CONSTRAINT fk_user_id1 FOREIGN KEY (user_id) REFERENCES User(user_id),
    CONSTRAINT fk_password_id1 FOREIGN KEY (password_id) REFERENCES Password(password_id)
) ENGINE=InnoDB;



CREATE TABLE PropertyDetail (
	property_detail_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    year_built YEAR NOT NULL,
    square_feet INT NOT NULL,
    bedrooms_num INT NOT NULL,
    bathrooms_num INT NOT NULL,
    property_id INT UNIQUE,
    CONSTRAINT fk_property_id FOREIGN KEY (property_id) REFERENCES Property(property_id)
) ENGINE=InnoDB;



-- MarketListings table
CREATE TABLE MarketListings (
    listing_id INT NOT NULL AUTO_INCREMENT,
    property_id INT NOT NULL,
    listing_date DATE NOT NULL,
    listing_price DECIMAL NOT NULL,
    status VARCHAR(255) NOT NULL,
    PRIMARY KEY (listing_id),
    CONSTRAINT fk_MarketListings_Property
        FOREIGN KEY (property_id) REFERENCES Property(property_id)
);

-- Images table
CREATE TABLE Images (
    image_id INT NOT NULL AUTO_INCREMENT,
    property_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (image_id),
    CONSTRAINT fk_Images_Property
        FOREIGN KEY (property_id) REFERENCES Property(property_id)
);
-- Appointments table
CREATE TABLE Appointments (
    appointment_id INT NOT NULL AUTO_INCREMENT,
    property_id INT NOT NULL,
    initiator_user_id INT NOT NULL,
    receiver_user_id INT NOT NULL,
    appointment_time DATE NOT NULL,
    status VARCHAR(255) NOT NULL,
    PRIMARY KEY (appointment_id),
    CONSTRAINT fk_Appointments_Property
        FOREIGN KEY (property_id) REFERENCES Property(property_id),
    CONSTRAINT fk_Appointments_InitiatorUser
        FOREIGN KEY (initiator_user_id) REFERENCES User(user_id),
    CONSTRAINT fk_Appointments_ReceiverUser
        FOREIGN KEY (receiver_user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS Contract(
	contract_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    signing_date DATETIME NOT NULL,
    contract_price DOUBLE NOT NULL,
    fk_first_party INT NOT NULL,
    fk_second_party INT NOT NULL,
    fk_property_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE Contract
ADD CONSTRAINT
FOREIGN KEY(fk_first_party)
REFERENCES User(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_second_party)
REFERENCES User(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_property_id)
REFERENCES Property(property_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS Review(
	review_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    rating INT NOT NULL,
    comments VARCHAR(255) NOT NULL,
    fk_user_id INT NOT NULL,
    fk_property_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE Review
ADD CONSTRAINT
FOREIGN KEY(fk_user_id)
REFERENCES User(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_property_id)
REFERENCES Property(property_id)
ON DELETE CASCADE
ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS PaymentUsePaymentMethod(
	fk_payment_id INT NOT NULL,
    fk_method_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE PaymentUsePaymentMethod
ADD CONSTRAINT
FOREIGN KEY(fk_payment_id)
REFERENCES Payment(payment_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_method_id)
REFERENCES PaymentMethod(method_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS PaymentOfContract(
	fk_payment_id INT NOT NULL,
    fk_contract_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE PaymentOfContract
ADD CONSTRAINT
FOREIGN KEY(fk_payment_id)
REFERENCES Payment(payment_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_contract_id)
REFERENCES Contract(contract_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS PropertyLocateAddress(
	fk_property_id INT NOT NULL,
    fk_address_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE PropertyLocateAddress
ADD CONSTRAINT
FOREIGN KEY(fk_property_id)
REFERENCES Property(property_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_address_id)
REFERENCES Address(address_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS ZipCodeOfAddress(
	fk_zipcode_id INT NOT NULL,
    fk_address_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE ZipCodeOfAddress
ADD CONSTRAINT
FOREIGN KEY(fk_zipcode_id)
REFERENCES ZipCode(zipcode_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_address_id)
REFERENCES Address(address_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS AddressLocateCity(
	fk_address_id INT NOT NULL,
    fk_city_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE AddressLocateCity
ADD CONSTRAINT
FOREIGN KEY(fk_address_id)
REFERENCES Address(address_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_city_id)
REFERENCES City(city_id)
ON DELETE CASCADE
ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS CityLocateState(
	fk_city_id INT NOT NULL,
    fk_state_id INT NOT NULL
)ENGINE = InnoDB;
# Add Constraint
ALTER TABLE CityLocateState
ADD CONSTRAINT
FOREIGN KEY(fk_city_id)
REFERENCES City(city_id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT
FOREIGN KEY(fk_state_id)
REFERENCES State(state_id)
ON DELETE CASCADE
ON UPDATE CASCADE;


