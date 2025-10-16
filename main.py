import os
import json
from fastapi import FastAPI, HTTPException
from zai import ZhipuAiClient
#from dotenv import load_dotenv
#load_dotenv()

# --- 1. 配置与初始化 ---

# 从环境变量获取 API Key，如果不存在则服务无法启动
api_key = os.environ.get("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("环境变量 ZHIPUAI_API_KEY 未设置，服务无法启动。")

# 从环境变量获取模型名称，如果不存在则使用默认值 "glm-4-flash"，但是更推荐 "glm-4.5-flash" 深度思考质量更高
model_name = os.environ.get("ZHIPUAI_MODEL", "glm-4-flash")

# 初始化 ZhipuAI 客户端
client = ZhipuAiClient(api_key=api_key)

print(f"服务已启动，使用 AI 模型: {model_name}")

# --- 2. AI 聊天核心函数 ---

def chat(user_prompt: str) -> str:
    if not user_prompt or not user_prompt.strip():
        # 如果输入为空，直接返回提示，不调用 API
        return {"message": "输入内容不能为空。"}
        
    # 定义 tools 和 content
    tools = [
        {
            "type": "function",
            "function": {
                "name": "output_schdules",
                "description": "输出直播日程列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "schedule_list": {
                            "type": "array",
                            "description": "包含所有日程项目的列表",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "直播标题，不含表情包和后面表情包后面的额外备注。不要翻译为中文。"
                                    },
                                    "title-zh": {
                                        "type": "string",
                                        "description": "直播标题翻译成中文，通常不能照抄原文。符合示例翻译中格式的请严格参考示例翻译。"
                                    },
                                    "timestamp": {
                                        "type": "number",
                                        "description": "直播时间戳"
                                    },
                                    "notice": {
                                        "type": "string",
                                        "description": "额外备注，一般是表情包后的**加粗**的文字。如果没有就留空。不要翻译为中文。"
                                    }
                                },
                                "required": ["title", "title-zh", "timestamp", "notice"]
                            }
                        }
                    },
                    "required": ["schedule_list"]
                }
            }
        }
    ]
    
    content = f"""你是直播日程分析和翻译专家。请给以下直播日程重新格式化解读。

{user_prompt}

## 你应该了解这些原文格式：

- <t:114514>
  时间戳：在提取时间戳时要用到。

- [text](url)
  超链接：如有遇到，只保留超链接文本，即[]里的text。

- <a:abc:114514>
  表情包：表情包不应输出。

- <:abc:114514>
  表情包：表情包不应输出。

## 请参考以下内容解读：

- **title**
  描述：直播标题，不含表情包和后面表情包后面的额外备注。不要翻译为中文。

- **title-zh**
  描述：直播标题翻译成中文，通常不能照抄原文。符合示例翻译中格式的请严格参考示例翻译。
  示例翻译：
  - Offline -- 休息中…
  - Neuro Stream -- Neuro 直播中
  - Evil Karaoke -- Evil 卡拉OK
  - Dev Stream -- 开发者直播
  - Mimi & Neuro Collab -- Mimi和Neuro联动
  - Planet Zoo w/ Cerber & Evil -- Cerber和Evil玩动物园之星

- **timestamp**
  描述：直播时间戳。

- **notice**
  描述：额外备注，一般是表情包后的**加粗**的文字（标题正文中的加粗不是，例如“Neuro Gives **YOU** Financial Advice”均为标题正文，未含额外备注）。如果没有就留空。不要翻译为中文。

### 请使用 output_schdules 函数输出结果"""
    
    messages = [
        {"role": "system", "content": "你是直播日程分析和翻译专家。"},
        {"role": "user", "content": content}
    ]
    
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    
    if response.choices[0].message.tool_calls:
        return response.choices[0].message.tool_calls[0].function.arguments
    else:
        return {"message": f"输出异常：{response.choices[0].message.content}"}


# --- 3. FastAPI 应用 ---

app = FastAPI(
    title="fastapi-zhipu-chat-api",
    description="一个基于 FastAPI 的智谱 AI 聊天服务，提供简洁的 REST API 接口，支持快速部署和环境变量配置。",
    version="1.0.0",
)


from fastapi import Request

@app.post("/api/chat")
async def handle_chat_request(request: Request):
    try:
        request_data = await request.json()
        if isinstance(request_data, str):
            user_input = request_data
        else:
            try:
                user_input = json.dumps(request_data, ensure_ascii=False)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={"data": "输入数据格式无效，应为字符串或可序列化的 JSON 对象。"}
                )
        # 调用 chat 函数处理从请求中提取的文本
        ai_result = chat(user_input)
        return {"data": json.loads(ai_result)}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail={"data": "请求体必须是有效的 JSON 格式。"}
        )
    except Exception as e:
        # 如果 chat 函数内部（如 API 调用）发生错误，打印日志并返回 500 错误
        print(f"处理请求时发生错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail={"data": "与 AI 服务通信时发生内部错误，请稍后再试。"}
        )

# 可选：添加一个根路径的 GET 请求，用于健康检查或基本说明
@app.get("/")
def root():
    return {"data": f"服务已就绪: {model_name}"}
