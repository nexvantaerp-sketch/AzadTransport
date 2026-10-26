# 🚛 New United Azad Transport — Molasses Transportation ERP

Streamlit + Supabase ERP: Trips · Vehicles · Drivers · Customers · Billing · Payments · Expenses · Driver Advances · Reports.

## 1. Supabase setup (sirf ek dafa)
| Situation | Kya karna hai |
|---|---|
| **Naya database** | `supabase_schema.sql` ko Supabase → SQL Editor mein paste karke Run karein |
| **Purana database (data maujood)** | `migration_v2.sql` Run karein — data safe rehta hai |

## 2. Secrets
Streamlit Cloud → App → Settings → Secrets:
```toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-key"
```
Local chalane ke liye `.env.example` ko `.env` bana kar yahi do values daalein.

## 3. Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 4. Pehla login
`admin` / `admin123` — app pehli dafa khud admin bana deti hai. **Foran Settings → My Account se password badal dein.**
Users (admin / staff / viewer) Settings → Users se banayein. *viewer* sirf dekh sakta hai.

## 5. GitHub update
Purane repo ki **saari files delete** karke is folder ki files upload karein
(khaas taur par purana `pages/` folder hata dein — wohi sidebar ko kharab karta tha).

## Workflow
1. Customers, Vehicles, Drivers add karein (customer ka default rate/ton daal dein)
2. **Trips** → trip add karein (rate 0 chhorein to customer ka rate khud lag jata hai) → status *Delivered* karein
3. **Billing → Create Invoice** → delivered trips select → invoice ban jati hai, trips *Billed* ho jate hain
4. **Payments** → payment invoice ke against daalein → invoice ka balance/status khud update
5. **Dashboard / Reports** → profit, receivables ageing, document-expiry alerts

## Security notes
* Login passwords ab salted PBKDF2 se store hote hain.
* App anon key + open RLS policy ke saath chalti hai. Behtar security ke liye `harden_security.sql` dekhein
  (service_role key sirf Streamlit secrets mein rakhein, GitHub mein kabhi nahi). GitHub repo **private** rakhein.

## Tests
`python tests/test_app.py` and `python tests/test_dialogs.py` — in-memory fake Supabase ke saath poori app (login, forms, billing, payments) ko test karte hain.
