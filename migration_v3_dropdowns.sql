-- Dropdown Lists page: stores the options you add / remove from the app.
-- Supabase → SQL Editor → paste → Run (safe to run more than once).
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
