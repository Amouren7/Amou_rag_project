# 架构与数据流

文档摄取将文件内容与 `title/source_file/page_number/content_type/chunk_method` 一起写入 chunk 元数据。查询阶段分别执行向量召回和中文关键词召回，再通过 RRF 合并排名。工具执行结果保存在请求级 ContextVar 中，由 API 构建去重 citations，避免并发请求之间互相污染。

SSE 事件依次为 session、text、tools、final 或 error；final 包含完整 answer、citations、tools_used 和 session_id。
