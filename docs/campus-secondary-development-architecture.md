# Open WebUI 校园二开架构与目录边界

更新时间：2026-07-03

本文档用于约束当前本地 Open WebUI + RAGFlow 二开工作的代码边界，避免后续继续拉取代码、接工具、加页面时出现重复实现和职责混乱。

## 当前主线

唯一继续开发的 Open WebUI 主仓库：

```text
/Users/liyu/docker/openweb UI/open-webui-official-v0.10.1
```

当前分支：

```text
feature/artifacts-document-canvas
```

该仓库负责用户可见产品体验：

- 移动端应用中心
- 校情 / 应用 / 研判 / 智库 / 我的
- 学校管理和权限入口
- RAGFlow 适配层
- Artifacts 报告、PPT、图片、文档画布
- 模型工具入口和前台交互

旧目录：

```text
/Users/liyu/docker/openweb UI/yili-webui-yili-main
```

该目录不是当前 Git 主线。除非做历史对比，否则不要继续在这里开发新功能。

## 外部平台定位

RAGFlow 仓库：

```text
/Users/liyu/docker/openweb UI/ragflow
```

RAGFlow 定位为智库后端平台，不作为校园移动端前台继续深度二开。

RAGFlow 负责：

- 知识库管理
- 数据源管理
- 文档上传、解析、切片
- Embedding、检索、引用来源
- Assistant 配置
- OpenAI-compatible API

Open WebUI 负责：

- 学校用户入口
- 移动端 App 壳
- 应用中心
- 当前学校上下文
- 调用 RAGFlow API 并展示答案、引用、状态

## 运行服务边界

当前本地开发端口：

```text
5173  Open WebUI 前端
8080  Open WebUI 后端
9222  RAGFlow 管理前端
9380  RAGFlow 后端 API
29001 MinIO 控制台
29000 MinIO API
3306  RAGFlow MySQL
26379 RAGFlow Redis
9200  RAGFlow OpenSearch
4222  RAGFlow NATS
```

注意：Open WebUI 当前数据库仍依赖 Docker Desktop 中的 PostgreSQL `127.0.0.1:15432`。在迁移到本机 PostgreSQL 前，不要关闭 Docker Desktop。

## 功能责任 Owner

### 应用中心

Owner：

```text
src/routes/(app)/apps/+page.svelte
```

职责：

- 移动端应用中心 UI
- 底部固定导航
- 卡片列表滚动区域
- 智库、应用、研判等入口展示

不负责：

- 文档解析
- RAG 检索
- 直接连接数据库
- 复杂业务规则计算

### 校园智库适配

Owner：

```text
backend/open_webui/routers/campus_knowledge.py
src/lib/apis/campus/knowledge.ts
```

职责：

- 把 Open WebUI 当前用户问题转发给 RAGFlow
- 规范 Open WebUI 前台所需的 answer / references 输出
- 隔离 RAGFlow API key 和 chat_id

不负责：

- 自己实现 RAG
- 自己解析文件
- 自己维护知识库文档

### RAGFlow 本地开发脚本

Owner：

```text
ragflow/scripts/start-local-dev-deps.sh
ragflow/scripts/start-local-ragflow-backend.sh
ragflow/scripts/start-local-ragflow-web.sh
ragflow/scripts/seed-local-campus-knowledge.py
```

职责：

- 本机开发启动
- 生成本地测试账号、知识库、Assistant、API Token
- 配置本地依赖端口

不负责：

- 产品功能逻辑
- Open WebUI 前台页面
- 客户生产部署策略

### Artifacts 画布

Owner 仍使用 Open WebUI 原生链路：

```text
src/lib/components/chat/Chat.svelte
src/lib/components/chat/Artifacts/
src/lib/utils/index.ts
src/lib/utils/artifacts.test.ts
```

职责：

- 显示显式 artifact fence
- 报告、文档、图片、PPT 等画布预览
- 后续工具打开时再渲染画布

不负责：

- 自动接管所有 Markdown 报告
- 图片生成模型适配
- PPT 生成任务执行

### 图片生成

Owner：

```text
backend/open_webui/routers/images.py
```

职责：

- Open WebUI 图片生成 API
- DashScope / 百炼 / 通义万相 adapter
- 生成结果文件化后交给前端或 Artifact 展示

不负责：

- RAGFlow 知识库
- 应用中心业务卡片

## 不要重复建设的能力

### 知识库

不要同时维护两套面向学校业务的知识库：

```text
Open WebUI Knowledge
RAGFlow Dataset / Assistant
```

当前校园智库统一以 RAGFlow 为后端。Open WebUI 的 Knowledge 可以保留为原生功能，但不要再作为校园智库主线扩展。

### 工具体系

下面几类不要混为一个概念：

```text
RAGFlow Data Source     文档/知识来源
Open WebUI Tools/MCP    模型可调用工具
Campus App API          应用中心业务接口
Artifacts               前端画布和预览
CyberPPT Tool Server    外部 PPT 生成服务
Postgres MCP            数据库查询工具
```

新增能力前先判断它属于哪一类，不要因为名字都叫 tool/data source 就写到同一层。

### 多学校

多学校不要通过复制页面、复制 RAGFlow 实例配置硬编码实现。

推荐方向：

```text
school_id -> school config -> RAGFlow app binding -> Open WebUI UI render
```

后续应新增统一配置表或配置模型，而不是为每个学校新建一套路由。

## 建议的数据模型方向

后续在 Open WebUI 侧新增校园配置时，优先围绕以下概念：

```text
campus_schools
- id
- code
- name
- logo_url
- status

campus_user_school_roles
- user_id
- school_id
- role

campus_ragflow_apps
- school_id
- name
- ragflow_base_url
- ragflow_api_key
- ragflow_chat_id
- enabled

campus_app_cards
- school_id
- category
- title
- subtitle
- route
- sort_order
- enabled
```

第一阶段可以先用配置文件或轻量数据库表，不要一开始做复杂租户平台。

## 提交与忽略规则

应该提交：

- Open WebUI 产品代码
- Open WebUI 校园功能前后端
- RAGFlow 本地开发脚本
- 最小必要配置说明
- 文档

不应该提交：

- `.env`
- `.local/`
- MinIO 数据
- Redis dump
- RAGFlow 下载的二进制依赖包
- `node_modules/`
- `.venv/`
- 构建产物

RAGFlow 里的 `.local/campus_knowledge_seed.json` 包含本地账号、API Token、Chat ID，只能本地使用，不要提交到远端仓库。

## 后续开发顺序

建议按这个顺序推进：

1. 固化目录和职责边界。
2. 保持 `open-webui-official-v0.10.1` 为唯一 Open WebUI 开发主线。
3. 把 RAGFlow 保持为外部智库后台。
4. 将 `/apps` 页面拆成更清晰的校园应用中心组件。
5. 将 `campus_knowledge` 从单一环境变量改成按学校读取配置。
6. 新增学校管理后台。
7. 接入多学校 RAGFlow Assistant。
8. 再扩展 Artifacts 的报告、PPT、图片画布。

## 判断新功能放哪里的规则

新增需求时先问四个问题：

1. 这个能力是给学校用户看的前台体验吗？
   - 是：放 Open WebUI。

2. 这个能力是文档解析、知识库、检索、引用吗？
   - 是：优先放 RAGFlow 或调用 RAGFlow。

3. 这个能力是模型可调用的外部动作吗？
   - 是：优先做 OpenAPI Tool Server 或 MCP，再由 Open WebUI 接入。

4. 这个能力是画布预览吗？
   - 是：放 Open WebUI Artifacts，不要塞进 RAGFlow。

如果答案不清楚，先写一页设计说明，不要直接创建新目录或新服务。
