# fastapi-zhipu-chat-api

一个基于 FastAPI 的智谱 AI 聊天服务，提供简洁的 REST API 接口与智谱 AI 进行对话。

## 功能特性

- 🚀 基于 FastAPI 构建，性能优异
- 🤖 集成智谱 AI (ZhipuAI) 聊天功能
- 📝 支持纯文本对话交互
- 🔧 环境变量配置，灵活部署
- 📚 自动生成 API 文档
- 🛡️ 完善的错误处理机制

## 快速开始

### 环境要求

- Python 3.8+
- 智谱 AI API Key

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

创建 `.env` 文件并设置以下环境变量：

```env
ZHIPUAI_API_KEY=your_zhipuai_api_key_here
ZHIPUAI_MODEL=glm-4-flash
```

## 部署

### Vercel 部署
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/xiaofeiTM233/fastapi-zhipu-chat-api)

1. Fork 本项目到你的 GitHub
2. 在 Vercel 中导入项目
3. 设置环境变量 `ZHIPUAI_API_KEY` 和 `ZHIPUAI_MODEL`
4. 部署完成

## 配置说明

| 环境变量 | 必需 | 默认值 | 说明 |
|---------|------|--------|------|
| `ZHIPUAI_API_KEY` | ✅ | - | 智谱 AI API 密钥 |
| `ZHIPUAI_MODEL` | ❌ | `glm-4-flash` | 使用的模型名称 |

## 说明

本 README 文档由 AI 辅助生成。如有问题，请提交 Issue 或[与我联系](https://github.com/xiaofeiTM233)！
