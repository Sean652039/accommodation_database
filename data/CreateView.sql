CREATE VIEW UserPropertyDetails AS
SELECT 
    u.user_id,
    u.f_name,
    u.l_name,
    p.property_id,
    p.description,
    pd.year_built,
    pd.square_feet,
    pd.bedrooms_num,
    pd.bathrooms_num
FROM 
    User u
JOIN 
    Property p ON u.user_id = p.property_id
JOIN 
    PropertyDetail pd ON p.property_id = pd.property_id;
CREATE VIEW PropertyMarketListings AS
SELECT 
    p.property_id,
    p.description,
    ml.listing_id,
    ml.listing_date,
    ml.listing_price,
    ml.status
FROM 
    Property p
JOIN 
    MarketListings ml ON p.property_id = ml.property_id;

DROP VIEW IF EXISTS PropertyInfo;
CREATE VIEW PropertyInfo AS
SELECT p.property_id, p.description, year_built, square_feet, bedrooms_num, bathrooms_num, c.city_name FROM Property p
JOIN PropertyLocateAddress pla ON p.property_id = pla.fk_property_id
JOIN Address a ON pla.fk_address_id = a.address_id
JOIN AddressLocateCity alc ON a.address_id = alc.fk_address_id
JOIN City c ON alc.fk_city_id = c.city_id
JOIN PropertyDetail pd ON p.property_id = pd.property_id;