-- Creating indexes based on application usage

-- Indexes for primary key columns
CREATE INDEX idx_id_property ON Property (property_id);
CREATE INDEX idx_id_user ON User (user_id);
CREATE INDEX idx_id_appointment ON Appointments (appointment_id);
CREATE INDEX idx_id_contract ON Contract (contract_id);
CREATE INDEX idx_id_review ON Review (review_id);

-- Indexes for foreign key columns used in JOINs
CREATE INDEX idx_fk_property_id_contract ON Contract (fk_property_id);
CREATE INDEX idx_fk_user_id_review ON Review (fk_user_id);
CREATE INDEX idx_fk_property_id_review ON Review (fk_property_id);

-- Indexes for frequently used columns in WHERE clauses
CREATE INDEX idx_appointment_time ON Appointments (appointment_time);
CREATE INDEX idx_contract_id ON Contract (contract_id);
