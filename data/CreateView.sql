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
