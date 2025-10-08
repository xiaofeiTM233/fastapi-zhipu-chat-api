import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from zai import ZhipuAiClient

# --- 1. 配置与初始化 ---

# 从环境变量获取 API Key，如果不存在则服务无法启动
api_key = os.environ.get("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("环境变量 ZHIPUAI_API_KEY 未设置，服务无法启动。")

# 从环境变量获取模型名称，如果不存在则使用默认值 "glm-4-flash"
model_name = os.environ.get("ZHIPUAI_MODEL", "glm-4-flash")

# 初始化 ZhipuAI 客户端
client = ZhipuAiClient(api_key=api_key)

print(f"服务已启动，使用 AI 模型: {model_name}")

# --- 2. AI 聊天核心函数 ---

def chat(user_prompt: str) -> str:
    if not user_prompt or not user_prompt.strip():
        # 如果输入为空，直接返回提示，不调用 API
        return "输入内容不能为空。"
        
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    ai_response = response.choices[0].message.content
    return ai_response.strip()


# --- 3. FastAPI 应用 ---

app = FastAPI(
    title="fastapi-zhipu-chat-api",
    description="一个基于 FastAPI 的智谱 AI 聊天服务，提供简洁的 REST API 接口，支持快速部署和环境变量配置。",
    version="1.0.0",
)

# 定义请求体的数据模型，确保请求的 JSON 中包含一个名为 'data' 的字符串
class ChatRequest(BaseModel):
    data: str = Field(..., min_length=1, description="用户发送给 AI 的纯文本内容")

@app.post("/api/chat", response_class=PlainTextResponse)
async def handle_chat_request(request: ChatRequest):
    try:
        # 调用 chat 函数处理从请求中提取的文本
        ai_result = chat(request.data)
        return ai_result
    except Exception as e:
        # 如果 chat 函数内部（如 API 调用）发生错误，打印日志并返回 500 错误
        print(f"处理请求时发生错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail="与 AI 服务通信时发生内部错误，请稍后再试。"
        )

# 可选：添加一个根路径的 GET 请求，用于健康检查或基本说明
@app.get("/", response_class=PlainTextResponse)
def root():
    return f"AI 聊天服务已就绪。\n请向 /api/chat 发送 POST 请求。\n模型: {model_name}"
