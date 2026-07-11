import streamlit as st
import requests
import aiohttp
import asyncio
import json
from dotenv import load_dotenv
import os
load_dotenv()

# Application configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

API_URL = os.getenv("API_URL", f"http://localhost:{APP_PORT}")

st.set_page_config(page_title="电商运营知识 RAG Agent", page_icon="🧠", layout="wide")
USER_ID = "user"

# Session state init
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Health check
def check_health(base_url: str):
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        if resp.status_code == 200:
            return True
        return False
    except Exception:
        return False

async def stream_chat(message: str, base_url: str):
    request_data = {
        "message": message,
        "session_id": st.session_state.session_id,
        "user_id": USER_ID,
        "search_type": "hybrid"
    }

    response_box = st.empty()
    full_response = ""

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/chat/stream", json=request_data) as resp:
            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if not line.startswith("data: "):
                    continue

                try:
                    data = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue

                if data.get("type") == "session":
                    st.session_state.session_id = data.get("session_id")

                elif data.get("type") == "text":
                    content = data.get("content", "")
                    full_response += content
                    response_box.write(full_response)
                    
                elif data.get("type") == "tools":
                    tools = data.get("tools", [])
                    for tool in tools:
                        tool_name = tool.get("tool_name", "")
                        tool_args = tool.get("args", {})
                        full_response += f"\n [Tool: {tool_name}] \n Args: {tool_args}"
                    response_box.write(full_response)
                    
                elif data.get("type") == "final":
                    citations = data.get("citations", [])
                    if citations:
                        full_response += "\n\n**参考来源**"
                        for citation in citations:
                            page = f" 第 {citation['page_number']} 页" if citation.get("page_number") else ""
                            full_response += f"\n- {citation.get('document_title', citation.get('document_source'))}{page}: {citation.get('snippet', '')}"
                    response_box.write(full_response)
                    break

    response_box.write(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

def run_async(message: str, base_url: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(stream_chat(message, base_url))

# Sidebar
with st.sidebar:
    st.header("运行设置")
    base_url = st.text_input("API 地址", value=API_URL)

    if st.button("Check Health"):
        if check_health(base_url):
            st.success("API is healthy")
        else:
            st.error("API not reachable")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()
    
    st.divider()

# Main chat
st.title("电商运营知识 RAG Agent")
st.caption("面向商品资料、平台规则、内容规范与运营 SOP 的可追溯问答")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("请输入运营问题，例如：商品签收后几天内可以退换？"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            run_async(prompt, base_url)
