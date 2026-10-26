-- ============================================================
-- MIGRATION v2 — run ONCE on your EXISTING Supabase database.
-- Keeps all your data. Safe to run more than once.
-- ============================================================

-- Invoices: columns the billing module needs
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(14,2) DEFAULT 0;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS net_amount DECIMAL(14,2) DEFAULT 0;
UPDATE invoices SET net_amount = total_amount - COALESCE(tax_amount,0) WHERE COALESCE(net_amount,0) = 0;
UPDATE invoices SET balance = net_amount - COALESCE(paid_amount,0) WHERE COALESCE(balance,0) = 0 AND net_amount > 0;

-- Trips: freight basis (Loading Weight / Unloading Weight)
ALTER TABLE trips ADD COLUMN IF NOT EXISTS freight_basis VARCHAR(30) DEFAULT 'Loading Weight';

-- Payments: allow longer status text ("Pending Clearance")
ALTER TABLE payments ALTER COLUMN status TYPE VARCHAR(30);

-- Remove the broken placeholder admin (its fake hash could never match).
-- The app re-creates  admin / admin123  automatically on next launch.
DELETE FROM app_users WHERE password_hash LIKE 'pbkdf2:sha256:600000$azad$%';

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_trips_customer ON trips(customer_id);
CREATE INDEX IF NOT EXISTS idx_expenses_vehicle ON expenses(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id);

-- Make sure policies allow inserts/updates (WITH CHECK)
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
