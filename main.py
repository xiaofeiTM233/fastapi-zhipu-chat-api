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
                "name": "output_tags",
                "description": "按分类批量输出标签，校园墙稿件审核标签体系，按风险等级和功能分类，含标签名称及具体描述，用于精准标记内容属性、指导审核决策",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "通用": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "所有稿件必选的基础属性标签，描述内容的形式/身份特征，用于快速筛选和分类"
                        },
                        "高风险": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "涉及违法违规、人身伤害、严重侵权或破坏校园秩序的内容"
                        },
                        "中风险": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "可能引发争议、不适或轻微违规的内容"
                        },
                        "低风险": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "常规校园互动内容，符合社区氛围"
                        }
                    },
                    "required": ["通用"]
                }
            }
        }
    ]
    
    content = f"""你是内容安全审查专家。请给以下校园墙投稿文本内容打标签。

投稿详情（已JSON化处理，具体消息列表在list数组里，消息类型在消息type里）：
{user_prompt}

请根据以下标准判断内容是否安全：

# 校园墙稿件审核标签体系  
**体系定位**：按「风险等级+功能」分类的标签系统，包含标签名称与具体描述，用于精准标记内容属性、指导审核决策。  

## 通用（所有稿件必选，描述内容形式/身份特征，用于快速筛选分类）  
- **匿名**：作者主动隐藏投稿身份（如匿名、打码、码死及谐音/emoji变体🐎等）  
- **非匿名**：作者明确使用投稿账号身份（如“不匿”等表述）  
- **纯文字**：内容仅为文字，无图片/视频/链接等附件  
- **含图片**：附带至少1张图片/截图（如聊天记录、证件照等，需额外审核图片违规性）  
- **含不支持类型消息**：含标准输入（text、image、face）以外的附件类型  
- **需人工处理**：内容涉及多投稿或AI无法判断的模糊场景  

## 高风险（违法违规/人身伤害/严重侵权/破坏秩序）  
- **涉政敏感**：不当讨论国家政策/领导人形象/时政事件（如调侃政策、传不实政治谣言），或使用敏感符号/言论  
- **暴力描述**：具体描写打架斗殴、伤害他人身体（如“XX被打出血”）、自残（割腕/自杀未遂细节）或血腥画面  
- **人身攻击**：针对个人/群体的辱骂、歧视言论（如地域黑“某省人都XX”、性别攻击“女生不如男生”）  
- **隐私泄露**：未经允许公开他人敏感信息（身份证号/手机号/住址/行程轨迹/带个人信息的聊天截图等）  
- **造谣诽谤**：无证据指控他人（如“XX偷钱包”“XX考试作弊”），可能损害名誉（需作者提供实证否则违规）  
- **煽动对立**：刻意挑拨学生与学校/老师/同学的关系（如“所有教授都压榨学生”），可能引发群体冲突  
- **违法引导**：传授违法方法（作弊/伪造证件）、推广违禁品（管制刀具/假烟假酒）或诱导不良行为（网贷/赌博）  

## 中风险（可能引发争议/不适/轻微违规）  
- **负面过载**：大段宣泄极端负面情绪（如“活着没意思”“想退学”），无正向引导，可能引发模仿或心理不适  
- **争议话题**：易引发群体对立的内容（如“支持/反对强制早八”“评教该不该打低分”），需判断是否超正常讨论范围  
- **挂人预警**：未明确证据的指责（如“XX总逃课还打小报告”），可能升级为网络暴力或私下矛盾  
- **过度吐槽**：具体批评教学/管理问题（如“XX老师只会念PPT”“后勤修水管拖一周”），无建设性反馈，可能激化对立  
- **广告嫌疑**：广告以及未标“广告”的暗广（如“推荐XX考研机构”“代取快递1元一次”），需判断是否隐蔽营销  
- **暧昧暗示**：未明确表白的亲密关系描述（如“最近和某人走得近”“TA是不是喜欢我？”），可能引发误会或隐私争议  

## 低风险（常规校园互动，符合社区氛围）  
- **询问**：具体问题咨询（课程难度/选课建议/快递点/失物招领/活动安排/校园卡办理等），寻求客观信息  
- **祝福**：生日/考试/比赛/节日的正向情感表达（如“祝室友生日快乐”“高考加油”；需注意反语/暗语攻击）  
- **找搭子**：轻社交需求（拼课/拼饭/图书馆自习/看电影/健身搭子等），不涉及金钱或敏感信息  
- **正能量**：分享积极经历（获奖/志愿活动/学习干货/校园美景打卡等），传递正向价值  
- **树洞倾诉**：非负面过载的个人心情记录（如“今天看到晚霞很开心”“完成小目标”），无攻击性或过度情绪  
- **活动宣传**：社团活动/比赛组队/读书会/运动局等非商业集体邀请（如“英语角招新，每周六下午”）  
- **科普干货**：实用信息分享（学习技巧/考试攻略/校园生活小贴士/兼职防骗等），无商业推广意图

请使用 output_tags 函数输出结果"""
    
    messages = [
        {"role": "system", "content": "你是内容安全审查专家。"},
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
