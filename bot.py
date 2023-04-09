import feedparser
import psycopg2
import requests
import os

# PostgreSQL数据库连接信息，请修改为您的实际信息
# DB_NAME = os.environ['DB_NAME']
# DB_USER = os.environ['DB_USER']
# DB_PASSWORD = os.environ['DB_PASSWORD']
# DB_HOST = os.environ['DB_HOST']
# DB_PORT = os.environ['DB_PORT']

# MASTODON_HOST=os.environ['MASTODON_HOST']
# ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

URL = f"https://{os.environ['MASTODON_HOST']}/api/v1/statuses?access_token={os.environ['ACCESS_TOKEN']}"

# RSS源列表，请修改为您需要订阅的RSS源链接
RSS_FEEDS = [
    "http://www.ruanyifeng.com/blog/atom.xml",
    "https://feeds.appinn.com/appinns/",
    "https://sspai.com/feed",
    "https://github.blog/feed/",
    "https://www.geekpark.net/rss",
    "https://rsshub.cestlavie.moe/guokr/scientific",
    "https://irithys.com/index.xml",
    "https://github.com/casdoor/casdoor/releases.atom",
    "https://github.com/usememos/memos/releases.atom",
    "https://github.com/mastodon/mastodon/releases.atom",
    "https://main.iceco.icu/index.xml",
    "https://www.cestlavie.moe/index.xml",
    "https://github.com/Chanzhaoyu/chatgpt-web/releases.atom",
    "https://www.ithome.com/rss/"
]

# 连接到PostgreSQL数据库
conn = psycopg2.connect(
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT']
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
    print(f'Checking {feed_url}')
    feed = feedparser.parse(feed_url)
    latest_item = None
    if 'published' in str(feed.entries[0].items()):
        method = 'published'
    else:
        method = 'updated'
    # print(method)
    for item in feed.entries:
        cur.execute("SELECT id FROM rss_items WHERE link = %s", (item.link,))
        if method == 'published':
            if latest_item is None or item.published_parsed > latest_item.published_parsed or cur.fetchone() is None:
                latest_item = item
                print(latest_item.link,end=' ---- ')
                print(latest_item.title)
                post_data = {"status": f"{latest_item.title} \n{latest_item.link}"}
                result = requests.post(URL,data=post_data)
                if result.status_code == 200:
                    print(f'POSTED: {latest_item.title}')
                    cur.execute("""
                            INSERT INTO rss_items (title, link, published)
                            VALUES (%s, %s, %s)
                        """, (latest_item.title, latest_item.link, latest_item.published))
                    conn.commit()
                else:
                    print(result.text)
        elif method == 'updated':
            if latest_item is None or item.updated_parsed > latest_item.updated_parsed or cur.fetchone() is None:
                latest_item = item
                print(latest_item.link,end=' ---- ')
                print(latest_item.title)
                post_data = {"status": f"{latest_item.title} \n{latest_item.link}"}
                result = requests.post(URL,data=post_data)
                if result.status_code == 200:
                    print(f'POSTED: {latest_item.title}')
                    cur.execute("""
                        INSERT INTO rss_items (title, link, published)
                        VALUES (%s, %s, %s)
                    """, (latest_item.title, latest_item.link, latest_item.updated))
                    conn.commit()
                else:
                    print(result.text)
    if method == 'published':
        cur.execute("SELECT id FROM rss_items WHERE link = %s", (latest_item.link,))
        if cur.fetchone() is None:
            # cur.execute("""
            #     INSERT INTO rss_items (title, link, published)
            #     VALUES (%s, %s, %s)
            # """, (latest_item.title, latest_item.link, latest_item.published))
            # conn.commit()
            pass
        else:
            print(f'ALREADY POSTED:{latest_item.title}')
            continue
    if method == 'updated':
        cur.execute("SELECT id FROM rss_items WHERE link = %s", (latest_item.link,))
        if cur.fetchone() is None:
            # cur.execute("""
            #     INSERT INTO rss_items (title, link, published)
            #     VALUES (%s, %s, %s)
            # """, (latest_item.title, latest_item.link, latest_item.updated))
            # conn.commit()
            pass
        else:
            print(f'ALREADY POSTED:{latest_item.title}')
            continue

    # # 发送HTTP POST请求到MASTODON_HOST，请求内容为标题和链接
    # print(latest_item.link,end=' ---- ')
    # print(latest_item.title)
    # post_data = {"status": f"{latest_item.title} \n{latest_item.link}"}
    # result = requests.post(URL,data=post_data)
    # if result.status_code == 200:
    #     print(f'POSTED: {latest_item.title}')
    #     if method == 'published':
    #         cur.execute("""
    #                 INSERT INTO rss_items (title, link, published)
    #                 VALUES (%s, %s, %s)
    #             """, (latest_item.title, latest_item.link, latest_item.published))
    #         conn.commit()
    #     elif method == 'updated':
    #         cur.execute("""
    #             INSERT INTO rss_items (title, link, published)
    #             VALUES (%s, %s, %s)
    #         """, (latest_item.title, latest_item.link, latest_item.updated))
    #         conn.commit()
    # else:
    #     print(result.text)
cur.close()
conn.close()