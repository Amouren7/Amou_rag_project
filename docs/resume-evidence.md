# 简历与面试证据

## 已有源码证据

- `ingestion/loaders.py`：PDF、Markdown、TXT 加载与来源元数据
- `ingestion/chunker.py`：语义切分与递归降级
- `agent/retrieval.py`：RRF 排名融合
- `agent/db_utils.py`：pgvector、pg_trgm 检索与最近会话窗口
- `agent/tools.py`：四类 Agent 工具与请求级检索追踪
- `agent/citations.py`：引用去重和片段裁剪
- `agent/api.py`：普通问答、SSE 与 citations 输出
- `evaluation/metrics.py`：Recall@K、MRR、引用覆盖率和响应时间

## 本次验证记录

- `uv run pytest -q`：62 项测试通过，0 项失败。
- Python 导入检查：`agent.api`、`agent.agent`、`ingestion.ingest`、`evaluation.metrics` 均可导入。
- `docker compose config --quiet`：配置解析通过。
- `scripts/security_scan.py`：未发现疑似明文密钥。
- fixture 评测：12 个问题完成指标管线验证；fixture 结果仅证明计算流程可运行，不代表真实模型效果。
- Docker Desktop daemon 当前未启动，因此本轮未完成 PostgreSQL 容器启动和真实数据库集成测试。

## 不能提前声称的内容

- fixture 评测不代表真实模型效果。
- 没有真实 API 和数据库集成测试时，不声称生产可用或达到某项准确率。
- 项目基于 MIT 上游二次开发，不描述为从零实现。
