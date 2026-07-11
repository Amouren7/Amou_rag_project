# 电商运营知识 RAG Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 MIT 开源 Agentic RAG 基座交付可运行、可测试、可评测、回答带证据的电商运营知识 RAG Agent。

**Architecture:** 保留 FastAPI、PydanticAI、PostgreSQL/pgvector、Streamlit 和 Docker Compose 主体；新增统一配置层、多格式文档加载、中文 pg_trgm 召回、RRF 排名融合、结构化 citations 与离线评测。所有外部模型调用通过 OpenAI-compatible 接口配置，自动化测试使用 mock。

**Tech Stack:** Python 3.12、FastAPI、PydanticAI、asyncpg、PostgreSQL 17、pgvector、pg_trgm、LangChain text splitters、Docling、Streamlit、pytest、Docker Compose

---

### Task 1: 引入基座并建立版本边界

**Files:**
- Copy: `D:/360ANQUAN/agentic_rag_project-main/*`
- Preserve: `LICENCE`
- Create: `UPSTREAM.md`
- Preserve: `docs/superpowers/specs/2026-07-11-ecommerce-rag-agent-design.md`
- Preserve: `docs/superpowers/plans/2026-07-11-ecommerce-rag-agent.md`

- [ ] **Step 1: 将基座复制到目标目录**

使用 PowerShell 复制源目录内容，但跳过源目录 `.git`，并保留目标目录现有 `docs/superpowers`：

```powershell
Copy-Item -Path 'D:\360ANQUAN\agentic_rag_project-main\*' -Destination 'D:\CC\rag-project' -Recurse -Force
```

- [ ] **Step 2: 初始化独立 Git 历史**

```powershell
git init
git checkout -b feature/ecommerce-rag-agent
git add .
git commit -m "chore: import MIT agentic RAG upstream"
```

预期：分支为 `feature/ecommerce-rag-agent`，首次提交包含原许可证。

- [ ] **Step 3: 写明上游来源**

创建 `UPSTREAM.md`：

```markdown
# Upstream

This project is a business-focused derivative of Serkan Yaşar's MIT-licensed
`ntt_rag_project`:

- Upstream: https://github.com/serkanyasr/ntt_rag_project
- License: MIT
- Original copyright: Copyright (c) 2025 Serkan Yaşar

The `LICENCE` file is preserved. See `README.md` for the derivative feature list.
```

- [ ] **Step 4: 提交来源说明**

```powershell
git add UPSTREAM.md docs/superpowers
git commit -m "docs: record upstream and ecommerce RAG design"
```

### Task 2: 建立安全的模型与应用配置层

**Files:**
- Create: `agent/config.py`
- Modify: `agent/providers.py`
- Modify: `.env.example`
- Test: `tests/agent/test_config.py`
- Test: `tests/agent/test_providers.py`

- [ ] **Step 1: 编写配置测试**

测试必须覆盖独立 LLM/Embedding key、base URL、模型名、超时、向量维度，以及缺少 key 时不会使用字符串形式的假密钥：

```python
def test_settings_support_independent_openai_compatible_endpoints(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "llm-test")
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_MODEL", "chat-model")
    monkeypatch.setenv("EMBEDDING_API_KEY", "embed-test")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "https://embed.example/v1")
    monkeypatch.setenv("EMBEDDING_MODEL", "embedding-model")
    monkeypatch.setenv("EMBEDDING_DIMENSION", "1024")
    settings = Settings.from_env()
    assert settings.llm_api_key == "llm-test"
    assert settings.embedding_dimension == 1024
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run pytest tests/agent/test_config.py tests/agent/test_providers.py -q
```

预期：因 `agent.config` 不存在而失败。

- [ ] **Step 3: 实现 Settings 和 Provider**

`Settings.from_env()` 对整数、URL 和空密钥做显式校验；`get_llm_model()` 使用 `OpenAIProvider(base_url=..., api_key=...)`；Embedding 客户端使用独立配置。不得使用 `os.getenv('OPENAI_API_KEY', 'LLM_API_KEY')` 这种把变量名当默认密钥的写法。

- [ ] **Step 4: 更新安全环境变量示例**

`.env.example` 只保留空值：

```dotenv
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
MODEL_TIMEOUT_SECONDS=60
```

- [ ] **Step 5: 运行测试并提交**

```powershell
uv run pytest tests/agent/test_config.py tests/agent/test_providers.py -q
git add agent/config.py agent/providers.py .env.example tests/agent
git commit -m "feat: add safe OpenAI-compatible provider configuration"
```

### Task 3: 定义引用与统一响应模型

**Files:**
- Modify: `agent/models.py`
- Create: `agent/citations.py`
- Test: `tests/agent/test_citations.py`
- Modify: `tests/agent/test_models.py`

- [ ] **Step 1: 编写 citation 去重测试**

```python
def test_build_citations_deduplicates_chunk_ids_and_keeps_page():
    rows = [
        {"chunk_id": "c1", "document_title": "售后规则", "document_source": "after_sales.md", "page_number": 2, "content": "七天内可申请退换", "score": 0.9, "search_type": "hybrid"},
        {"chunk_id": "c1", "document_title": "售后规则", "document_source": "after_sales.md", "page_number": 2, "content": "七天内可申请退换", "score": 0.8, "search_type": "vector"},
    ]
    citations = build_citations(rows)
    assert len(citations) == 1
    assert citations[0].page_number == 2
    assert citations[0].search_type == "hybrid"
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run pytest tests/agent/test_citations.py -q
```

- [ ] **Step 3: 实现模型**

新增 `Citation`、`GroundedAnswer`、扩展 `ChunkResult` 和 `ChatResponse`。Citation 必须包含 `chunk_id`、`document_title`、`document_source`、`page_number`、`snippet`、`score`、`search_type`。

- [ ] **Step 4: 实现稳定去重**

`build_citations()` 按 chunk ID 去重、保留首次最高排名、限制片段长度为 240 字，并过滤缺少来源的行。

- [ ] **Step 5: 测试并提交**

```powershell
uv run pytest tests/agent/test_models.py tests/agent/test_citations.py -q
git add agent/models.py agent/citations.py tests/agent
git commit -m "feat: add grounded response and citation models"
```

### Task 4: 支持多格式文档与切分降级

**Files:**
- Create: `ingestion/loaders.py`
- Modify: `ingestion/extract_files.py`
- Modify: `ingestion/chunker.py`
- Modify: `ingestion/ingest.py`
- Test: `tests/ingestion/test_loaders.py`
- Modify: `tests/ingestion/test_chunker.py`

- [ ] **Step 1: 编写 Markdown/TXT 加载测试**

```python
def test_load_markdown_preserves_title_and_content(tmp_path):
    path = tmp_path / "售后规则.md"
    path.write_text("# 售后规则\n七天内可申请退换。", encoding="utf-8")
    docs = load_document(path)
    assert docs[0].metadata["title"] == "售后规则"
    assert docs[0].metadata["source_file"] == "售后规则.md"
    assert "七天内" in docs[0].page_content
```

- [ ] **Step 2: 编写切分降级测试**

Mock 语义切分抛出异常，断言输出块的 `chunk_method` 为 `recursive_fallback`，且保留 `page_number`、`source_file`。

- [ ] **Step 3: 运行测试确认失败**

```powershell
uv run pytest tests/ingestion/test_loaders.py tests/ingestion/test_chunker.py -q
```

- [ ] **Step 4: 实现加载器与降级**

`load_document()` 按扩展名路由；Markdown 标题取第一个 `#` 标题，TXT 标题取文件名；不支持的扩展名抛出 `UnsupportedDocumentError`。切分器保留来源元数据，语义切分异常时使用递归切分。

- [ ] **Step 5: 测试并提交**

```powershell
uv run pytest tests/ingestion -q
git add ingestion tests/ingestion
git commit -m "feat: add multi-format ingestion with deterministic fallback"
```

### Task 5: 重构数据库 Schema 与中文混合检索

**Files:**
- Modify: `sql/schema.sql`
- Modify: `agent/db_utils.py`
- Create: `agent/retrieval.py`
- Test: `tests/agent/test_retrieval.py`
- Modify: `tests/agent/test_db_utils.py`

- [ ] **Step 1: 编写 RRF 单元测试**

```python
def test_rrf_merge_rewards_documents_found_by_both_retrievers():
    vector = [{"chunk_id": "a", "score": 0.9}, {"chunk_id": "b", "score": 0.8}]
    keyword = [{"chunk_id": "b", "score": 0.95}, {"chunk_id": "c", "score": 0.7}]
    merged = reciprocal_rank_fusion(vector, keyword, k=60)
    assert merged[0]["chunk_id"] == "b"
    assert merged[0]["search_type"] == "hybrid"
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run pytest tests/agent/test_retrieval.py -q
```

- [ ] **Step 3: 更新 Schema**

将固定 `vector(1536)` 改为由初始化脚本注入安全的整数维度；chunks 增加 `page_number`、`source_file`、`content_type`、`chunk_method`。中文关键词函数使用 `similarity(c.content, query_text)`、`ILIKE` 和 `pg_trgm` 索引，不再使用英文 `to_tsvector`。

- [ ] **Step 4: 实现检索与过滤**

数据库层分别返回向量和关键词排名；Python 层执行 RRF，支持 document ID、content type 和 JSONB metadata 过滤。所有 SQL 值使用参数绑定。

- [ ] **Step 5: 修正最近会话窗口**

SQL 先按 `created_at DESC LIMIT $2` 取最近消息，再在外层按时间升序返回；禁止字符串拼接 LIMIT。

- [ ] **Step 6: 测试并提交**

```powershell
uv run pytest tests/agent/test_retrieval.py tests/agent/test_db_utils.py -q
git add sql/schema.sql agent/db_utils.py agent/retrieval.py tests/agent
git commit -m "feat: add Chinese hybrid retrieval with RRF"
```

### Task 6: 重构 Agent 工具与 Grounded Prompt

**Files:**
- Modify: `agent/tools.py`
- Modify: `agent/agent.py`
- Modify: `agent/prompts.py`
- Test: `tests/agent/test_tools.py`
- Create: `tests/agent/test_grounding.py`

- [ ] **Step 1: 编写工具结果测试**

Mock 数据库结果，断言向量/混合检索工具返回页码、source file、search type 和可用于 citations 的 chunk ID。

- [ ] **Step 2: 编写拒答规则测试**

断言系统 Prompt 明确包含“先检索”“不得编造”“证据不足时说明无法确认”“引用文档和页码”。

- [ ] **Step 3: 运行测试确认失败**

```powershell
uv run pytest tests/agent/test_tools.py tests/agent/test_grounding.py -q
```

- [ ] **Step 4: 实现四类工具**

统一工具输入校验与错误模型；混合检索默认 TopK=8，权重参数改为 RRF k；全文读取按 chunk index 返回内容与页码；文档列表支持分页。

- [ ] **Step 5: 更新 Prompt**

Prompt 指定电商运营助手角色、工具选择规则、来源要求、冲突证据处理和拒答规则，不承诺知识库外事实。

- [ ] **Step 6: 测试并提交**

```powershell
uv run pytest tests/agent/test_tools.py tests/agent/test_grounding.py -q
git add agent tests/agent
git commit -m "feat: ground agent tools and answers in citations"
```

### Task 7: 统一普通问答与 SSE 响应

**Files:**
- Modify: `agent/api.py`
- Modify: `agent/models.py`
- Modify: `ui/app.py`
- Create: `tests/agent/test_api.py`

- [ ] **Step 1: 编写 API schema 测试**

使用 FastAPI TestClient 和 mock agent，断言 `/chat` 返回 answer、citations、tools_used、session_id；`/chat/stream` 的 `final` 事件包含同样字段。

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run pytest tests/agent/test_api.py -q
```

- [ ] **Step 3: 重构执行结果**

`execute_agent()` 返回统一 `AgentExecutionResult`；从实际工具输出构建 citations；保存 assistant message 时将 citation IDs 写入 metadata。

- [ ] **Step 4: 统一 SSE 事件**

事件类型固定为 `status`、`token`、`tool`、`final`、`error`；每条使用 JSON 编码，异常不泄漏密钥或完整堆栈。

- [ ] **Step 5: UI 展示引用**

Streamlit 在回答后展示去重来源卡片：文档、页码、片段、相关度和检索方式。

- [ ] **Step 6: 测试并提交**

```powershell
uv run pytest tests/agent/test_api.py -q
git add agent/api.py agent/models.py ui/app.py tests/agent/test_api.py
git commit -m "feat: unify grounded chat and streaming responses"
```

### Task 8: 建立离线评测工具与演示知识库

**Files:**
- Create: `evaluation/__init__.py`
- Create: `evaluation/metrics.py`
- Create: `evaluation/run_evaluation.py`
- Create: `evaluation/dataset.json`
- Create: `documents_demo/product_handbook.md`
- Create: `documents_demo/after_sales_policy.md`
- Create: `documents_demo/content_sop.md`
- Create: `documents_demo/geo_sop.md`
- Create: `tests/evaluation/test_metrics.py`

- [ ] **Step 1: 编写指标测试**

```python
def test_recall_mrr_and_citation_coverage():
    rows = [
        {"expected_sources": ["after_sales_policy.md"], "retrieved_sources": ["product_handbook.md", "after_sales_policy.md"], "citations": ["after_sales_policy.md"], "latency_ms": 12.0}
    ]
    metrics = calculate_metrics(rows, k=2)
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 0.5
    assert metrics["citation_coverage"] == 1.0
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run pytest tests/evaluation/test_metrics.py -q
```

- [ ] **Step 3: 实现指标与 CLI**

CLI 读取 dataset，调用可注入 retriever，输出 `evaluation/results.json` 与 `evaluation/results.md`。失败问题记录 error，不从分母中静默删除。

- [ ] **Step 4: 编写演示数据**

四份文档使用虚构品牌“DemoRide”，明确标记演示资料；数据集至少 12 个问题，每题包含 query、expected_sources、expected_answer_keywords、requires_citation。

- [ ] **Step 5: 测试并提交**

```powershell
uv run pytest tests/evaluation -q
git add evaluation documents_demo tests/evaluation
git commit -m "feat: add reproducible retrieval and citation evaluation"
```

### Task 9: 更新容器、文档与安全检查

**Files:**
- Modify: `docker-compose.yml`
- Modify: `Dockerfile`
- Modify: `pyproject.toml`
- Replace: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/resume-evidence.md`
- Create: `scripts/security_scan.py`
- Test: `tests/test_security_scan.py`

- [ ] **Step 1: 编写安全扫描测试**

临时创建包含 `sk-test-realistic-secret-value` 的文件，断言扫描器失败；安全占位符和 `.env.example` 空值必须通过。

- [ ] **Step 2: 实现扫描器**

扫描受版本控制文本文件中的 OpenAI 风格 key、Feishu App Secret、Bearer token、Cookie；跳过 `.git`、lock 文件和测试夹具中的显式安全标记。

- [ ] **Step 3: 更新 Docker 与依赖**

Compose 使用健康检查、只从 `.env` 取配置、暴露 API/UI；Dockerfile 使用非 root 用户和明确启动命令；pyproject 增加评测包与测试依赖。

- [ ] **Step 4: 重写中文 README**

README 包含业务场景、架构图、快速启动、环境变量、摄取、API 示例、评测命令、测试命令、目录说明、上游来源、已有/新增能力边界和面试可讲点。

- [ ] **Step 5: 测试并提交**

```powershell
uv run pytest tests/test_security_scan.py -q
uv run python scripts/security_scan.py
docker compose config --quiet
git add .
git commit -m "docs: package ecommerce RAG for reproducible delivery"
```

### Task 10: 完整验证与交付证据

**Files:**
- Modify: `evaluation/results.md` only when a real or deterministic evaluation is executed
- Modify: `docs/resume-evidence.md`

- [ ] **Step 1: 运行完整测试**

```powershell
uv run pytest -q
```

预期：0 failures。

- [ ] **Step 2: 运行静态导入检查**

```powershell
uv run python -c "import agent.api, agent.agent, ingestion.ingest, evaluation.metrics"
```

预期：退出码 0。

- [ ] **Step 3: 验证容器配置与安全**

```powershell
docker compose config --quiet
uv run python scripts/security_scan.py
```

预期：两个命令退出码均为 0。

- [ ] **Step 4: 运行确定性评测**

```powershell
uv run python -m evaluation.run_evaluation --dataset evaluation/dataset.json --mode fixture
```

预期：生成非空 JSON/Markdown；README 只引用这次实际输出。

- [ ] **Step 5: 核对 Git 与许可证**

```powershell
git status --short
git log --oneline --decorate -10
Get-Content -Raw LICENCE
```

预期：工作区干净，许可证保留，提交历史能区分上游导入与二开步骤。

- [ ] **Step 6: 更新并提交证据文档**

`docs/resume-evidence.md` 记录实际通过的测试数量、评测输出路径、关键代码文件和仍需真实 API 验证的边界。

```powershell
git add docs/resume-evidence.md evaluation/results.*
git commit -m "test: record verified ecommerce RAG evidence"
```
