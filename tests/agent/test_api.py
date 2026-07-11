import json
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.responses import JSONResponse

from agent.api import execute_agent, global_exception_handler


@pytest.mark.asyncio
async def test_global_exception_handler_returns_safe_json_response():
    response = await global_exception_handler(None, RuntimeError("private provider detail"))

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    payload = json.loads(response.body)
    assert payload["error"] == "Internal server error"
    assert "private provider detail" not in response.body.decode()
    assert payload["request_id"]


@pytest.mark.asyncio
async def test_execute_agent_reads_current_pydantic_ai_output(monkeypatch):
    result = Mock(output="grounded answer")
    result.all_messages.return_value = []
    monkeypatch.setattr("agent.api.rag_agent.run", AsyncMock(return_value=result))
    monkeypatch.setattr("agent.api.get_conversation_context", AsyncMock(return_value=[]))

    answer, tools, citations = await execute_agent(
        "question", "session-id", save_conversation=False
    )

    assert answer == "grounded answer"
    assert tools == []
    assert citations == []
