# The Data News 📰 — Setup Guide

## 1. Create the table in Supabase
Go to your Supabase project → Table Editor → New Table

Table name: `posts`

Columns:
- id (int8, Primary Key, auto-increment)
- title (text)
- content (text)
- source_url (text, nullable)
- category (text)
- created_at (timestamptz, default: now())

## 2. Create an admin user
Supabase → Authentication → Users → Add user

Pick an email and password — this is what you'll use to log in on the `/login` page of the site.

## 3. Get your API keys
Supabase → Project Settings → API

- Project URL → goes in `.env` as SUPABASE_URL
- anon public key → goes in `.env` as SUPABASE_KEY

Copy the example file and fill it in:

    cp .env.example .env

## 4. Run it locally

    pip install -r requirements.txt
    python app.py

Open in browser: http://localhost:5000

## 5. Log in and add a post

1. Click "Log in" (top right)
2. Use the email/password you created in step 2
3. Click "+ New Post" to write and publish

No need to touch the Supabase dashboard anymore — everything is managed from the site itself.

## Next steps (later)

- **Phase 2:** write a script that automatically pulls news from an RSS feed into Supabase
- **Phase 3:** schedule that script with GitHub Actions to run daily

Ask Claude when you're ready to build these.
