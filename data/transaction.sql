CREATE DEFINER=`jiw321`@`%`
PROCEDURE `CreateContractAndPayment`(
    IN p_contract_price DOUBLE,
    IN p_first_party_id INT,
    IN p_second_party_id INT,
    IN p_property_id INT,
    IN p_payment_amount DOUBLE
)
BEGIN
    -- Declare variables for storing the IDs of the newly inserted contract and payment
    DECLARE v_contract_id INT;
    DECLARE v_payment_id INT;

    -- Error handling: declare an exit handler for SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Rollback the transaction if any SQL error occurs
        ROLLBACK;
    END;

    -- Start a new transaction
    START TRANSACTION;

    -- Insert a new contract record into the Contract table
    INSERT INTO Contract (signing_date, contract_price, fk_first_party, fk_second_party, fk_property_id)
    VALUES (CURRENT_DATE(), p_contract_price, p_first_party_id, p_second_party_id, p_property_id);

    -- Retrieve the ID of the newly inserted contract record
    SET v_contract_id = LAST_INSERT_ID();

    -- Insert a new payment record into the Payment table
    INSERT INTO Payment (payment_date, amount)
    VALUES (CURRENT_DATE(), p_payment_amount);

    -- Retrieve the ID of the newly inserted payment record
    SET v_payment_id = LAST_INSERT_ID();

    -- Link the contract and payment records in the PaymentOfContract table
    INSERT INTO PaymentOfContract (fk_payment_id, fk_contract_id)
    VALUES (v_payment_id, v_contract_id);

    -- Attempt to commit the transaction
    COMMIT;
END