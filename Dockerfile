# 使用 Python 3.9 作为基础镜像
FROM python:3.11.3-alpine

# 将当前目录下的所有文件复制到容器中的 /app 目录中
COPY . /app

# 设置工作目录为 /app
WORKDIR /app

# 更新 pip，并安装 requirements.txt 中列出的所有依赖项
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

# 在容器启动时运行 bot.py
CMD ["python3", "bot.py"]
