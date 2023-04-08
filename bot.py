import feedparser
import psycopg2
import requests
import os

# PostgreSQL数据库连接信息，请修改为您的实际信息
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']


MASTODON_HOST=os.environ['MASTODON_HOST']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

URL = f'https://{MASTODON_HOST}/api/v1/statuses?access_token={ACCESS_TOKEN}'

titles = []
links = []
# RSS源列表，请修改为您需要订阅的RSS源链接
RSS_FEEDS = [
    "http://www.ruanyifeng.com/blog/atom.xml",
    "https://feeds.appinn.com/appinns/",
    "https://sspai.com/feed"
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

        # 发送HTTP POST请求到MASTODON_HOST，请求内容为标题和链接
        links.append(latest_item.link)
        titles.append(latest_item.title)
        post_data = f'{"status": "{latest_item.link} \n {latest_item.title}"}'
        result = requests.post(URL, data=post_data)
        print(result.text)

cur.close()
conn.close()
for i in range(0,len(links)-1):
    print(f'{links[i]}--{titles[i]}')