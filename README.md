# RSS2Toot

An Python program which uses GitHub Actions to forward RSS feed updates to Mastodon

[![Fetch and Sync RSS Feeds](https://github.com/Jonathan523/RSS2Toot/actions/workflows/fetch_and_sync.yml/badge.svg)](https://github.com/Jonathan523/RSS2Toot/actions/workflows/fetch_and_sync.yml)[![Publish Docker image](https://github.com/Jonathan523/RSS2Toot/actions/workflows/publish_docker_image.yml/badge.svg)](https://github.com/Jonathan523/RSS2Toot/actions/workflows/publish_docker_image.yml)![Docker Pulls](https://img.shields.io/docker/pulls/jonathan52306/rss2toot)

## Requirements

- A Mastodon Account
- A supabase-based Postgres Database (Or other Postgres Databases)
  You can get an account [HERE](https://supabase.com/)

## Deployment

1. Fork this repo
2. Go to `Settings > Secrets and variables > Actions > Secrets` and set these three secrets:
   - DB_PASSWORD
   - DB_HOST
   - ACCESS_TOKEN (from Mastodon)
   - MASTODON_HOST
3. Go to `Settings > Secrets and variables > Actions > Variables` and set these four variables:
   - DB_USER
   - DB_NAME
   - DB_PORT
4. Edit bot.py (Line 22-) to your RSS feed origin
