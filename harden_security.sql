-- OPTIONAL but recommended once everything works.
-- Use the *service_role* key (Supabase → Project Settings → API) as SUPABASE_KEY in
-- Streamlit secrets ONLY (never in GitHub). That key bypasses RLS, so you can remove the
-- open "Allow all" policies — then the public anon key can no longer read/write your data.
DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['vehicles','drivers','customers','trips','expenses','invoices',
                           'invoice_items','payments','driver_advances','app_users'] LOOP
    EXECUTE format('DROP POLICY IF EXISTS "Allow all" ON %I', t);
  END LOOP;
END $$;
