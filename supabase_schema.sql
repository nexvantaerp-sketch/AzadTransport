-- ============================================================
-- NEW UNITED AZAD TRANSPORT ERP — Supabase schema (v2)
-- FRESH install: run this whole file once in Supabase → SQL Editor.
-- EXISTING database: run migration_v2.sql instead (keeps your data).
-- The admin user (admin / admin123) is created automatically by the app
-- on first launch — change the password immediately from Settings.
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS vehicles (
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

CREATE TABLE IF NOT EXISTS drivers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL, cnic VARCHAR(20) UNIQUE,
    phone VARCHAR(20), phone2 VARCHAR(20), address TEXT,
    license_number VARCHAR(50), license_expiry DATE,
    date_of_joining DATE, salary DECIMAL(12,2) DEFAULT 0,
    emergency_contact VARCHAR(20), status VARCHAR(20) DEFAULT 'Active',
    photo_url TEXT, notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
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

CREATE TABLE IF NOT EXISTS trips (
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
    freight_basis VARCHAR(30) DEFAULT 'Loading Weight',
    rate_per_ton DECIMAL(12,2) DEFAULT 0,
    total_freight DECIMAL(14,2) DEFAULT 0,
    distance_km DECIMAL(10,2) DEFAULT 0,
    loading_datetime TIMESTAMPTZ, unloading_datetime TIMESTAMPTZ,
    status VARCHAR(30) DEFAULT 'Pending', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expenses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    trip_id UUID REFERENCES trips(id), vehicle_id UUID REFERENCES vehicles(id),
    driver_id UUID REFERENCES drivers(id), category VARCHAR(50) NOT NULL,
    description TEXT, amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(30) DEFAULT 'Cash',
    receipt_number VARCHAR(50), notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
    customer_id UUID REFERENCES customers(id),
    total_amount DECIMAL(14,2) DEFAULT 0,
    tax_amount DECIMAL(14,2) DEFAULT 0,
    net_amount DECIMAL(14,2) DEFAULT 0,
    paid_amount DECIMAL(14,2) DEFAULT 0,
    balance DECIMAL(14,2) DEFAULT 0, due_date DATE,
    status VARCHAR(20) DEFAULT 'Pending', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES trips(id), description TEXT,
    quantity DECIMAL(12,2) DEFAULT 1, rate DECIMAL(12,2) DEFAULT 0,
    amount DECIMAL(14,2) DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    invoice_id UUID REFERENCES invoices(id), customer_id UUID REFERENCES customers(id),
    amount DECIMAL(14,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(30) DEFAULT 'Bank Transfer',
    reference_number VARCHAR(100), bank_name VARCHAR(100),
    cheque_number VARCHAR(50), cheque_date DATE,
    status VARCHAR(30) DEFAULT 'Received', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS driver_advances (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    advance_date DATE NOT NULL DEFAULT CURRENT_DATE,
    driver_id UUID REFERENCES drivers(id), trip_id UUID REFERENCES trips(id),
    amount DECIMAL(14,2) NOT NULL DEFAULT 0, purpose VARCHAR(200),
    status VARCHAR(20) DEFAULT 'Given', notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app_users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(200), role VARCHAR(30) DEFAULT 'admin',
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trips_date ON trips(trip_date);
CREATE INDEX IF NOT EXISTS idx_trips_vehicle ON trips(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_trips_customer ON trips(customer_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_vehicle ON expenses(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_customer ON payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['vehicles','drivers','customers','trips','expenses','invoices','payments'] LOOP
    EXECUTE format('DROP TRIGGER IF EXISTS trg_%1$s ON %1$s', t);
    EXECUTE format('CREATE TRIGGER trg_%1$s BEFORE UPDATE ON %1$s FOR EACH ROW EXECUTE FUNCTION update_modified_column()', t);
  END LOOP;
END $$;

-- Row Level Security: the app connects with the anon key and does its own login,
-- so policies must allow the anon role. (See README → "Security notes".)
DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['vehicles','drivers','customers','trips','expenses','invoices',
                           'invoice_items','payments','driver_advances','app_users'] LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS "Allow all" ON %I', t);
    EXECUTE format('CREATE POLICY "Allow all" ON %I FOR ALL USING (true) WITH CHECK (true)', t);
  END LOOP;
END $$;

-- Dropdown Lists (add / remove options from the app)
CREATE TABLE IF NOT EXISTS dropdown_options (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_key   TEXT NOT NULL,                 -- e.g. 'expenses.category'
    value      TEXT NOT NULL,                 -- the option text
    is_hidden  BOOLEAN NOT NULL DEFAULT FALSE,-- TRUE = a built-in option that was removed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (list_key, value)
);
ALTER TABLE dropdown_options ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON dropdown_options;
CREATE POLICY "Allow all" ON dropdown_options FOR ALL USING (true) WITH CHECK (true);
