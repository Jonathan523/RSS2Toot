import feedparser
import psycopg2
import requests
import os
import re

URL = f"https://{os.environ['MASTODON_HOST']}/api/v1/statuses?access_token={os.environ['ACCESS_TOKEN']}"

# 从链接中提取 Hostname 的正则表达式
pattern = r'^(?:https?:\/\/)?(?:www\.)?([^:\/\n]+)'

# RSS 源列表，请修改为您需要订阅的 RSS 源链接
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
    "https://www.ithome.com/rss/",
    "https://blog.cloudflare.com/rss/",
    "https://www.solidot.org/index.rss",
    "https://www.dejavu.moe/index.xml",
    "https://www.ifanr.com/feed",
    "https://ohevan.com/atom.xml",
    "https://www.9998k.cn/feed/"
]

# 连接到 PostgreSQL 数据库
conn = psycopg2.connect(
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT']
)
cur = conn.cursor()

# 判断数据库是否存在
cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'rss_items')")
if not cur.fetchone()[0]:
    print("First run detected, I will initialize the database and I won't send toots.")
    FirstRUN = True
    # 创建数据库表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rss_items (
            id SERIAL PRIMARY KEY,
            title TEXT,
            link TEXT,
            published TIMESTAMP
        );
    """)
    conn.commit()
else:
    FirstRUN = False




# 检查每个 RSS 源的最新项目并将其插入到数据库中
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    print(f'Checking {feed.feed.title} ---- {feed_url}')
    latest_item = None
    origin_host = re.search(pattern, feed.entries[0].link, re.IGNORECASE).group(1)
    cur.execute("SELECT EXISTS (SELECT 1 FROM rss_items WHERE link LIKE %s)", ('%'+origin_host+'%',))
    host_exists = cur.fetchone()[0]
    if not host_exists:
        print("This feed seems to be newly added, I will add them to the database and I won't send toots for this time.")
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
                if cur.fetchone() is None:
                    # print(latest_item.link,end=' ---- ')
                    # print(latest_item.title)
                    if not FirstRUN and host_exists:
                        # 发送 HTTP POST 请求到 MASTODON_HOST，请求内容为标题和链接
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
                            print(f"POST FAILED: {latest_item.title}")
                            print(result.text)
                    else:
                        print(f'ADDED TO DATABASE: {latest_item.title}')
                        cur.execute("""
                                INSERT INTO rss_items (title, link, published)
                                VALUES (%s, %s, %s)
                            """, (latest_item.title, latest_item.link, latest_item.published))
                        conn.commit()
                else:
                    print(f'ALREADY POSTED: {latest_item.title}')
                    continue
        elif method == 'updated':
            if latest_item is None or item.updated_parsed > latest_item.updated_parsed or cur.fetchone() is None:
                latest_item = item
                if cur.fetchone() is None:
                    # print(latest_item.link,end=' ---- ')
                    # print(latest_item.title)
                    post_data = {"status": f"{latest_item.title} \n{latest_item.link}"}
                    if not FirstRUN and host_exists:
                        # 发送 HTTP POST 请求到 MASTODON_HOST，请求内容为标题和链接
                        result = requests.post(URL,data=post_data)
                        if result.status_code == 200:
                            print(f'POSTED: {latest_item.title}')
                            cur.execute("""
                                INSERT INTO rss_items (title, link, published)
                                VALUES (%s, %s, %s)
                            """, (latest_item.title, latest_item.link, latest_item.updated))
                            conn.commit()
                        else:
                            print(f"POST FAILED: {latest_item.title}")
                            print(result.text)
                    else:
                        print(f'ADDED TO DATABASE: {latest_item.title}')
                        cur.execute("""
                            INSERT INTO rss_items (title, link, published)
                            VALUES (%s, %s, %s)
                            """, (latest_item.title, latest_item.link, latest_item.updated))
                        conn.commit()
                else:
                    print(f'ALREADY POSTED: {latest_item.title}')
                    continue
cur.close()
conn.close()