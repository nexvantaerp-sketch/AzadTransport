-- NEW UNITED AZAD TRANSPORT — Supabase Database Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE vehicles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    vehicle_number VARCHAR(50) NOT NULL UNIQUE,
    vehicle_type VARCHAR(30) DEFAULT 'Tanker',
    make VARCHAR(100), model VARCHAR(100), year INTEGER,
    chassis_number VARCHAR(100), engine_number VARCHAR(100),
    registration_date DATE, registration_expiry DATE,
    insurance_expiry DATE, fitness_expiry DATE,
    capacity_tons DECIMAL(10,2) DEFAULT 0,
    fuel_type VARCHAR(20) DEFAULT 'Diesel',
    status VARCHAR(20) DEFAULT 'Active', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE drivers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL, cnic VARCHAR(20) UNIQUE,
    phone VARCHAR(20), phone2 VARCHAR(20), address TEXT,
    license_number VARCHAR(50), license_expiry DATE,
    date_of_joining DATE, salary DECIMAL(12,2) DEFAULT 0,
    emergency_contact VARCHAR(20), status VARCHAR(20) DEFAULT 'Active',
    photo_url TEXT, notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE customers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(300) NOT NULL, short_name VARCHAR(50),
    customer_type VARCHAR(30) DEFAULT 'Sugar Mill',
    contact_person VARCHAR(200), phone VARCHAR(20),
    email VARCHAR(200), address TEXT, city VARCHAR(100),
    ntn VARCHAR(50), payment_terms INTEGER DEFAULT 30,
    rate_per_ton DECIMAL(12,2) DEFAULT 0,
    contract_start DATE, contract_end DATE,
    status VARCHAR(20) DEFAULT 'Active', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE trips (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    trip_number VARCHAR(50) NOT NULL UNIQUE,
    trip_date DATE NOT NULL DEFAULT CURRENT_DATE,
    vehicle_id UUID REFERENCES vehicles(id),
    driver_id UUID REFERENCES drivers(id),
    customer_id UUID REFERENCES customers(id),
    loading_point VARCHAR(300), unloading_point VARCHAR(300),
    product VARCHAR(100) DEFAULT 'Molasses',
    loading_weight DECIMAL(12,2) DEFAULT 0,
    unloading_weight DECIMAL(12,2) DEFAULT 0,
    weight_difference DECIMAL(12,2) DEFAULT 0,
    weighbridge_slip_loading VARCHAR(100),
    weighbridge_slip_unloading VARCHAR(100),
    rate_per_ton DECIMAL(12,2) DEFAULT 0,
    total_freight DECIMAL(14,2) DEFAULT 0,
    distance_km DECIMAL(10,2) DEFAULT 0,
    loading_datetime TIMESTAMPTZ, unloading_datetime TIMESTAMPTZ,
    status VARCHAR(30) DEFAULT 'Pending', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE expenses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    trip_id UUID REFERENCES trips(id), vehicle_id UUID REFERENCES vehicles(id),
    driver_id UUID REFERENCES drivers(id), category VARCHAR(50) NOT NULL,
    description TEXT, amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(30) DEFAULT 'Cash',
    receipt_number VARCHAR(50), notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE invoices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
    customer_id UUID REFERENCES customers(id),
    total_amount DECIMAL(14,2) DEFAULT 0, paid_amount DECIMAL(14,2) DEFAULT 0,
    balance DECIMAL(14,2) DEFAULT 0, due_date DATE,
    status VARCHAR(20) DEFAULT 'Pending', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE invoice_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES trips(id), description TEXT,
    quantity DECIMAL(12,2) DEFAULT 1, rate DECIMAL(12,2) DEFAULT 0,
    amount DECIMAL(14,2) DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE payments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    invoice_id UUID REFERENCES invoices(id), customer_id UUID REFERENCES customers(id),
    amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(30) DEFAULT 'Bank Transfer',
    reference_number VARCHAR(100), bank_name VARCHAR(100),
    cheque_number VARCHAR(50), cheque_date DATE,
    status VARCHAR(20) DEFAULT 'Received', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE driver_advances (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    advance_date DATE NOT NULL DEFAULT CURRENT_DATE,
    driver_id UUID REFERENCES drivers(id), trip_id UUID REFERENCES trips(id),
    amount DECIMAL(14,2) NOT NULL DEFAULT 0, purpose VARCHAR(200),
    status VARCHAR(20) DEFAULT 'Given', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE app_users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(200), role VARCHAR(30) DEFAULT 'admin',
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Default admin: username=admin, password=admin123 (change after first login)
INSERT INTO app_users (username, password_hash, full_name, role) VALUES
('admin', 'pbkdf2:sha256:600000$azad$e3b0c44298fc1c149afbf4c8996fb924', 'Administrator', 'admin');

CREATE INDEX idx_trips_date ON trips(trip_date);
CREATE INDEX idx_trips_vehicle ON trips(vehicle_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
CREATE INDEX idx_payments_customer ON payments(customer_id);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_vehicles BEFORE UPDATE ON vehicles FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER trg_drivers BEFORE UPDATE ON drivers FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER trg_customers BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER trg_trips BEFORE UPDATE ON trips FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER trg_expenses BEFORE UPDATE ON expenses FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER trg_invoices BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER trg_payments BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_modified_column();

ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE driver_advances ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON vehicles FOR ALL USING (true);
CREATE POLICY "Allow all" ON drivers FOR ALL USING (true);
CREATE POLICY "Allow all" ON customers FOR ALL USING (true);
CREATE POLICY "Allow all" ON trips FOR ALL USING (true);
CREATE POLICY "Allow all" ON expenses FOR ALL USING (true);
CREATE POLICY "Allow all" ON invoices FOR ALL USING (true);
CREATE POLICY "Allow all" ON invoice_items FOR ALL USING (true);
CREATE POLICY "Allow all" ON payments FOR ALL USING (true);
CREATE POLICY "Allow all" ON driver_advances FOR ALL USING (true);
CREATE POLICY "Allow all" ON app_users FOR ALL USING (true);
