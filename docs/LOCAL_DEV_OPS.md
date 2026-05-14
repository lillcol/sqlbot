# SQLBot 本地前后端运维命令

本文档记录本地开发环境常用的前端、后端、数据库、日志查看命令。路径统一使用 `~/IdeaProjects/SQLBot` 作为项目根目录示例。

## 1. 本地服务地址

| 服务 | 地址 | 说明 |
| --- | --- | --- |
| 前端页面 | `http://localhost:5173/` | Vite 开发服务 |
| 后端服务 | `http://localhost:8000` | FastAPI / Uvicorn |
| 后端接口文档 | `http://localhost:8000/docs` | Swagger UI |
| 后端 API 前缀 | `http://localhost:8000/api/v1` | 前端 `.env.development` 使用的接口地址 |
| PostgreSQL | `localhost:5432/postgres` | SQLBot 元数据库 |

默认登录账号：

```text
账号：admin
密码：SQLBot@123456
```

## 2. 目录约定

```text
~/IdeaProjects/SQLBot/                 # 项目根目录
~/IdeaProjects/SQLBot/backend/         # 后端工程
~/IdeaProjects/SQLBot/frontend/        # 前端工程
~/IdeaProjects/SQLBot/.env             # 后端本地环境变量
~/IdeaProjects/SQLBot/data/sqlbot/     # 本地运行数据目录
~/IdeaProjects/SQLBot/backend/.venv/   # 后端 Python 虚拟环境
```

当前本地 `.env` 中将运行数据放到：

```text
~/IdeaProjects/SQLBot/data/sqlbot/file
~/IdeaProjects/SQLBot/data/sqlbot/images
~/IdeaProjects/SQLBot/data/sqlbot/excel
~/IdeaProjects/SQLBot/data/sqlbot/models
~/IdeaProjects/SQLBot/data/sqlbot/scripts
```

## 3. 后端运维命令

### 3.1 安装 uv

如果本机没有 `uv`：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装后可用：

```bash
~/.local/bin/uv --version
```

### 3.2 安装 Python 3.11

后端 `pyproject.toml` 要求 Python `3.11.*`：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv python install 3.11
```

### 3.3 安装后端依赖

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv sync --python 3.11
```

如果只是运行某个命令，也可以直接使用：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python --version
```

### 3.4 初始化本地运行目录

```bash
mkdir -p ~/IdeaProjects/SQLBot/data/sqlbot/file \
  ~/IdeaProjects/SQLBot/data/sqlbot/images \
  ~/IdeaProjects/SQLBot/data/sqlbot/excel \
  ~/IdeaProjects/SQLBot/data/sqlbot/models \
  ~/IdeaProjects/SQLBot/data/sqlbot/scripts
```

### 3.5 执行数据库迁移

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 alembic upgrade head
```

查看当前迁移版本：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres')
with conn.cursor() as cur:
    cur.execute('select version_num from alembic_version')
    print(cur.fetchone()[0])
conn.close()
PY
```

### 3.6 启动后端服务

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后会看到类似输出：

```text
Uvicorn running on http://0.0.0.0:8000
Application startup complete.
```

### 3.7 后台启动后端服务

```bash
cd ~/IdeaProjects/SQLBot/backend
nohup ~/.local/bin/uv run --python 3.11 uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
  > ~/IdeaProjects/SQLBot/data/sqlbot/backend.log 2>&1 &
```

查看后台日志：

```bash
tail -f ~/IdeaProjects/SQLBot/data/sqlbot/backend.log
```

### 3.8 停止后端服务

按端口停止：

```bash
lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill
```

或按进程名停止：

```bash
pkill -f 'uvicorn main:app'
```

如果进程没有退出，可强制停止：

```bash
lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill -9
```

### 3.9 检查后端服务状态

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
curl -sS -o /tmp/sqlbot_docs.html -w 'docs_http_code=%{http_code}\n' http://localhost:8000/docs
```

`docs_http_code=200` 表示后端文档页面可访问。

## 4. 前端运维命令

### 4.1 安装前端依赖

```bash
cd ~/IdeaProjects/SQLBot/frontend
npm install
```

### 4.2 启动前端服务

```bash
cd ~/IdeaProjects/SQLBot/frontend
npm run dev -- --host 0.0.0.0
```

启动成功后会看到类似输出：

```text
VITE ready
Local:   http://localhost:5173/
```

### 4.3 后台启动前端服务

```bash
cd ~/IdeaProjects/SQLBot/frontend
nohup npm run dev -- --host 0.0.0.0 \
  > ~/IdeaProjects/SQLBot/data/sqlbot/frontend.log 2>&1 &
```

查看后台日志：

```bash
tail -f ~/IdeaProjects/SQLBot/data/sqlbot/frontend.log
```

### 4.4 停止前端服务

按端口停止：

```bash
lsof -tiTCP:5173 -sTCP:LISTEN | xargs kill
```

或按进程名停止：

```bash
pkill -f 'vite --host 0.0.0.0'
```

如果进程没有退出，可强制停止：

```bash
lsof -tiTCP:5173 -sTCP:LISTEN | xargs kill -9
```

### 4.5 检查前端服务状态

```bash
lsof -nP -iTCP:5173 -sTCP:LISTEN
curl -sS -I http://localhost:5173/
```

返回 `HTTP/1.1 200 OK` 表示前端可访问。

## 5. PostgreSQL 运维命令

### 5.1 当前连接信息

```text
postgresql://root:123456@localhost:5432/postgres
```

`.env` 配置位置：

```text
~/IdeaProjects/SQLBot/.env
```

主要配置：

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=root
POSTGRES_PASSWORD=123456
POSTGRES_DB=postgres
```

### 5.2 查看 PostgreSQL 容器

```bash
/Applications/Docker.app/Contents/Resources/bin/docker ps --format '{{.ID}} {{.Names}} {{.Image}} {{.Ports}}'
```

当前本地 PostgreSQL 容器示例：

```text
postgres postgres:latest 0.0.0.0:5432->5432/tcp
```

### 5.3 安装 pgvector 扩展

SQLBot 的术语库和 SQL 示例 embedding 需要 PostgreSQL `vector` 扩展。

进入容器安装：

```bash
/Applications/Docker.app/Contents/Resources/bin/docker exec -u root postgres bash -lc \
  "apt-get update && apt-get install -y postgresql-18-pgvector"
```

创建数据库扩展：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres', autocommit=True)
with conn.cursor() as cur:
    cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
    cur.execute("select extname from pg_extension order by extname")
    print([r[0] for r in cur.fetchall()])
conn.close()
PY
```

### 5.4 查看已创建的表

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres')
with conn.cursor() as cur:
    cur.execute("select table_name from information_schema.tables where table_schema='public' order by table_name")
    for row in cur.fetchall():
        print(row[0])
conn.close()
PY
```

### 5.5 查询默认用户

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres')
with conn.cursor() as cur:
    cur.execute('select id, account, name, oid, status from sys_user order by id')
    for row in cur.fetchall():
        print(row)
conn.close()
PY
```

### 5.6 重置 admin 默认密码

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres', autocommit=True)
with conn.cursor() as cur:
    cur.execute("""
        update sys_user
        set password = '8f32d1e371702c1b1b7346f4b07a701d',
            status = 1,
            oid = 1
        where account = 'admin'
    """)
    print('updated:', cur.rowcount)
conn.close()
PY
```

重置后默认登录信息：

```text
账号：admin
密码：SQLBot@123456
```

## 6. 日志查看命令

### 6.1 前后端后台日志

如果使用本文档中的 `nohup` 启动命令：

```bash
tail -f ~/IdeaProjects/SQLBot/data/sqlbot/backend.log
```

```bash
tail -f ~/IdeaProjects/SQLBot/data/sqlbot/frontend.log
```

### 6.2 后端应用文件日志

后端日志配置在：

```text
~/IdeaProjects/SQLBot/backend/common/utils/utils.py
~/IdeaProjects/SQLBot/backend/common/core/config.py
```

默认日志目录：

```text
~/IdeaProjects/SQLBot/backend/logs
```

常见日志文件：

```text
debug.log
info.log
warn.log
error.log
sql.log
```

查看错误日志：

```bash
tail -f ~/IdeaProjects/SQLBot/backend/logs/error.log
```

### 6.3 Cursor 当前运行终端日志

如果服务是通过 Cursor 后台工具启动的，运行输出会保存在 Cursor 终端记录中，例如：

```text
~/.cursor/projects/Users-lillcol-IdeaProjects-SQLBot/terminals/
```

当前本地服务示例：

```text
后端日志：~/.cursor/projects/Users-lillcol-IdeaProjects-SQLBot/terminals/613006.txt
前端日志：~/.cursor/projects/Users-lillcol-IdeaProjects-SQLBot/terminals/849070.txt
```

查看后端实时日志：

```bash
tail -f ~/.cursor/projects/Users-lillcol-IdeaProjects-SQLBot/terminals/613006.txt
```

查看前端实时日志：

```bash
tail -f ~/.cursor/projects/Users-lillcol-IdeaProjects-SQLBot/terminals/849070.txt
```

### 6.4 查看 SQLBot 问数任务日志

问数任务日志保存在元数据库表中：

```text
chat_record
chat_log
```

查看最近问数记录：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres')
with conn.cursor() as cur:
    cur.execute('select id, chat_id, question, sql, error, finish from chat_record order by id desc limit 20')
    for row in cur.fetchall():
        print(row)
conn.close()
PY
```

查看最近模型调用日志：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 python - <<'PY'
import psycopg
conn = psycopg.connect('postgresql://root:123456@localhost:5432/postgres')
with conn.cursor() as cur:
    cur.execute('select id, type, operate, pid, start_time, finish_time from chat_log order by id desc limit 20')
    for row in cur.fetchall():
        print(row)
conn.close()
PY
```

## 7. 常见问题

### 7.1 `zsh: command not found: alembic`

说明没有激活后端 Python 环境，推荐使用：

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 alembic upgrade head
```

### 7.2 `extension "vector" is not available`

说明 PostgreSQL 容器没有安装 `pgvector`，参考本文档 `5.3 安装 pgvector 扩展`。

### 7.3 `/opt/sqlbot` 权限不足

本地开发不要写 `/opt/sqlbot`，在 `.env` 中把路径改到项目目录下：

```env
BASE_DIR=/Users/lillcol/IdeaProjects/SQLBot/data/sqlbot
UPLOAD_DIR=/Users/lillcol/IdeaProjects/SQLBot/data/sqlbot/file
MCP_IMAGE_PATH=/Users/lillcol/IdeaProjects/SQLBot/data/sqlbot/images
EXCEL_PATH=/Users/lillcol/IdeaProjects/SQLBot/data/sqlbot/excel
LOCAL_MODEL_PATH=/Users/lillcol/IdeaProjects/SQLBot/data/sqlbot/models
```

### 7.4 前端接口请求失败

本机访问时检查 `frontend/.env.development`：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

如果需要让局域网内其他机器访问，不能使用 `localhost`，要改成本机局域网 IP，例如：

```env
VITE_API_BASE_URL=http://172.26.140.234:8000/api/v1
```

同时 `.env` 中建议配置允许访问的前端来源：

```env
FRONTEND_HOST=http://172.26.140.234:5173
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://172.26.140.234:5173
```

修改后需要重启前后端服务。

确认后端是否启动：

```bash
curl -sS -o /tmp/sqlbot_docs.html -w 'docs_http_code=%{http_code}\n' http://localhost:8000/docs
```

确认局域网地址是否可访问：

```bash
curl -sS -o /tmp/sqlbot_docs.html -w 'docs_http_code=%{http_code}\n' http://172.26.140.234:8000/docs
curl -sS -I http://172.26.140.234:5173/
```

### 7.5 `Failed to load license generator script`

其他机器访问前端时报：

```text
Failed to load license generator script
```

通常是前端仍然使用了 `localhost:8000` 作为后端地址。其他机器浏览器里的 `localhost` 指的是访问者自己的电脑，不是运行 SQLBot 的机器，所以会加载不到后端静态脚本。

处理方式：

1. 获取运行 SQLBot 机器的局域网 IP：

```bash
ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null
```

2. 修改 `frontend/.env.development`：

```env
VITE_API_BASE_URL=http://运行SQLBot机器IP:8000/api/v1
```

3. 修改根目录 `.env`：

```env
FRONTEND_HOST=http://运行SQLBot机器IP:5173
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://运行SQLBot机器IP:5173
```

4. 重启后端和前端：

```bash
pkill -f 'uvicorn main:app' 2>/dev/null || true
pkill -f 'vite --host 0.0.0.0' 2>/dev/null || true
pkill -f 'npm run dev' 2>/dev/null || true
```

```bash
cd ~/IdeaProjects/SQLBot/backend
~/.local/bin/uv run --python 3.11 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd ~/IdeaProjects/SQLBot/frontend
npm run dev -- --host 0.0.0.0
```

5. 其他机器访问：

```text
http://运行SQLBot机器IP:5173/
```

如果浏览器仍然请求 `localhost:8000`，清理缓存或强制刷新页面。

### 7.6 数据源连接失败

后端日志中如果出现类似：

```text
Access denied for user ...
```

说明业务数据库账号、密码、host、端口或授权有问题。需要检查页面中配置的数据源连接信息，以及数据库是否允许来自当前机器或 Docker 网关的连接。
