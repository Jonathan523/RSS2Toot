# RSS2Toot

An Python program which uses GitHub Actions to forward RSS feed updates to Mastodon

## Requirements

- A Mastodon Account
- A supabase-based Postgres Database (Or other Postgres Databases)

## Deployment

1. Fork this repo
2. Go to `Settings > Secrets and variables > Actions > Secrets` and set these three secrets:
   - DB_PASSWORD
   - DB_HOST
   - ACCESS_TOKEN (from Mastodon)
3. Go to `Settings > Secrets and variables > Actions > Variables` and set these four variables:
   - DB_USER
   - DB_NAME
   - DB_PORT
   - MASTODON_HOST
4. Edit bot.py (Line 22-37) to your RSS feed origin