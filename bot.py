
import feedparser
import psycopg2
import requests

# PostgreSQL数据库连接信息，请修改为您的实际信息
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "LnBFmMODl2QKM9pz"
DB_HOST = "db.jwudenrwkkxmfdapbewo.supabase.co"
DB_PORT = "5432"

# RSS源列表，请修改为您需要订阅的RSS源链接
RSS_FEEDS = [
    "https://rss.feed1.com",
    "https://rss.feed2.com",
    "https://rss.feed3.com"
]

# 连接到PostgreSQL数据库
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# 创建数据库表
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS rss_items (
        id SERIAL PRIMARY KEY,
        title TEXT,
        link TEXT,
        published TIMESTAMP
    );
""")
conn.commit()

# 检查每个RSS源的最新项目并将其插入到数据库中
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    latest_item = None

    for item in feed.entries:
        if latest_item is None or item.published_parsed > latest_item.published_parsed:
            latest_item = item

    cur.execute("SELECT id FROM rss_items WHERE link = %s", (latest_item.link,))
    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO rss_items (title, link, published)
            VALUES (%s, %s, %s)
        """, (latest_item.title, latest_item.link, latest_item.published))
        conn.commit()

        # 发送HTTP POST请求到example.com，请求内容为标题和链接
        post_data = {
            "title": latest_item.title,
            "link": latest_item.link
        }
        requests.post("https://example.com", data=post_data)

cur.close()
conn.close()