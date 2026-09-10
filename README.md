# MockInterview Pro 🎯

> 基于 LangGraph 的智能模拟面试官 Agent —— 不止是问答，更是深度评估

---

## 📋 项目简介

MockInterview Pro 是一个基于大语言模型的综合型 AI Agent。它不仅能与用户进行多轮模拟面试，还能根据用户的回答**动态调整提问策略**（追问或提示），在算法环节自动执行**代码判题**，并在面试结束后结合用户的"历史薄弱点"生成深度的**复盘报告**。

### 核心亮点

| 特性 | 说明 |
|------|------|
| 🤖 **智能路由** | 根据回答质量动态切换追问、换题或工具调用 |
| 📚 **RAG 增强** | 追问环节实时检索知识库，生成有针对性的深度问题 |
| 🔧 **工具集成** | Python 代码沙箱执行 + Tavily 联网搜索验证 |
| 🧠 **双轨记忆** | 短期对话上下文 + 长期薄弱点追踪 |
| 📊 **复盘报告** | 面试结束自动生成 Markdown 格式的完整评估报告 |
| 🖥️ **双模式** | CLI 调试模式 + Streamlit Web UI |

---

## 🏗️ 系统架构

### LangGraph 状态机流转

```mermaid
graph TD
    A[START: 用户上传 JD] --> B(Init: 解析 JD, 生成面试计划)
    B --> C(Ask: 提出问题)
    C --> D{interrupt: 等待候选人回答}
    D --> E(Evaluate: 结构化评估)
    E -->|回答合格| F(Ask: 下一题)
    E -->|需要深挖| G(Probe: RAG检索+深度追问)
    E -->|面试完成| H(Review: 生成复盘报告)
    G --> D
    F --> D
    H --> I[END]
```

### 项目目录结构

```
MockInterview-Pro/
│
├── main.py                     # 🚀 CLI 主入口
├── .env                        # 🔒 环境变量配置（不提交 Git）
├── .gitignore                  # Git 忽略规则
├── pyproject.toml              # 📦 项目依赖
├── README.md                   # 📖 本文件
│
├── app/                        # 💻 核心业务代码
│   ├── __init__.py
│   ├── config.py               # ⚙️ 全局配置（LLM、Embeddings、Milvus）
│   ├── state.py                # 🧠 InterviewState TypedDict
│   ├── graph.py                # 🕸️ LangGraph 图编排（节点、边、条件路由）
│   │
│   ├── prompts/                # 📝 Prompt 模板（与代码分离）
│   │   ├── init_prompt.py
│   │   ├── evaluate_prompt.py  # 评估 Schema + Prompt
│   │   ├── probe_prompt.py     # 深度追问 Prompt
│   │   └── review_prompt.py    # 复盘报告 Prompt
│   │
│   ├── nodes/                  # 🧩 LangGraph 节点逻辑
│   │   ├── init_node.py        # JD 解析 → 面试计划
│   │   ├── evaluate_node.py    # 回答评估 → 路由决策
│   │   ├── probe_node.py       # 深度追问（RAG 增强）
│   │   └── review_node.py      # 复盘报告生成
│   │
│   ├── tools/                  # 🛠️ 工具调用
│   │   ├── code_executor.py    # Python 沙箱执行
│   │   ├── web_search.py       # Tavily 联网搜索
│   │   └── rag_search.py       # Milvus 向量检索
│   │
│   ├── rag/                    # 📚 RAG 知识库
│   │   ├── ingest.py           # 文档加载 → 切分 → 向量化 → 入库
│   │   └── retriever.py        # 向量检索封装
│   │
│   ├── memory/                 # 💾 记忆管理
│   │   └── long_term.py        # PostgreSQL 长期记忆
│   │
│   └── ui/                     # 🎨 Streamlit 前端
│       ├── streamlit_app.py    # 主程序（聊天 + 文件上传）
│       └── components.py       # 自定义组件（侧边栏、消息渲染）
│
├── data/                       # 📁 原始数据（RAG 知识源）
│   ├── jds/                    # 岗位描述 JD
│   └── interviews/             # 面经/技术文档
│
├── vector_db/                  # 🗄️ 向量数据库持久化（Git 忽略）
│
└── tests/                      # 🧪 单元测试
    ├── test_tools.py
    └── test_rag.py
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **核心框架** | LangChain + LangGraph | 状态机编排、节点通信、中断恢复 |
| **大语言模型** | DeepSeek Chat | 面试提问、回答评估、报告生成 |
| **结构化输出** | Pydantic (`with_structured_output`) | 评估结果 Schema 强制解析 |
| **向量模型** | Qwen3-Embedding:8b (Ollama) | 文档向量化、相似度检索 |
| **向量数据库** | Milvus | RAG 知识库存储与检索 |
| **联网搜索** | Tavily API | 实时查证候选人提到的技术 |
| **代码执行** | Python `exec` 沙箱 | 运行候选人提交的算法代码 |
| **短期记忆** | LangGraph InMemorySaver | 对话上下文维持 |
| **长期记忆** | PostgreSQL / LangGraph Store | 跨会话薄弱点持久化 |
| **前端 UI** | Streamlit | 聊天界面、文件上传、状态面板 |

---

## 🚀 快速开始

### 前置条件

- Python >= 3.14
- Ollama（本地运行 Embedding 模型）
- Milvus（向量数据库）
- （可选）PostgreSQL（长期记忆）

### 1. 克隆与环境配置

```bash
# 克隆仓库
git clone https://github.com/your-username/MockInterviewPro.git
cd MockInterviewPro

# 创建虚拟环境
python -m venv .venv

# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .example.env .env
```

编辑 `.env` 文件：

```env
# ===== API Keys =====
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
TAVILY_API_KEY=tvly-your-tavily-api-key

# ===== 模型配置 =====
CHAT_MODEL=deepseek-chat

# ===== Embedding 模型（Ollama 本地部署） =====
EMBEDDING_MODEL=qwen3-embedding:8b
EMBEDDING_HOST=http://localhost:11434

# ===== Milvus 向量数据库 =====
MILVUS_URI=http://localhost:19530
DB_NAME=mock_interview_pro
COLLECTION_NAME=interview_knowledge_base

# ===== PostgreSQL（可选，用于长期记忆持久化） =====
POSTGRESQL_URL=postgresql://user:password@localhost:5432/mockinterview_pro
```

### 3. 启动基础设施

```bash
# 启动 Ollama（Embedding 模型）
ollama pull qwen3-embedding:8b
ollama serve

# 启动 Milvus（向量数据库）
# 使用 Docker 方式：
docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
```

### 4. 构建 RAG 知识库（可选）

将岗位描述（JD）和面经文档放入 `data/` 目录，然后执行：

```bash
python -c "
from app.rag.ingest import RAGIngestor
ingestor = RAGIngestor(data_dir='data/jds', collection_name='interview_knowledge_base')
ingestor.run()
"
```

### 5. 运行

#### CLI 模式（适合调试）

```bash
python main.py
```

交互流程：

```
请输入JD：
[粘贴岗位描述...]

面试官：你好，我已经读取你的JD，准备开始面试。
面试官：问题：请解释 Redis 的持久化机制有哪些？有什么区别？

候选人回答：
[输入你的回答...]

面试官：回答不错，我们继续下一题。
面试官：问题：MySQL 索引的底层数据结构是什么？

（输入 'quit' 退出面试）
```

#### Streamlit Web UI（适合展示）

```bash
streamlit run app/ui/streamlit_app.py
```

浏览器打开 `http://localhost:8501`，界面包含：

- **主聊天区**：多轮面试对话
- **侧边栏**：实时显示面试阶段、进度、薄弱知识点
- **文件上传**：支持 PDF/TXT/MD 格式的 JD 上传

---

## 🧠 核心设计详解

### 1. LangGraph 状态机

```
State (InterviewState)
├── messages: Annotated[Sequence[BaseMessage], operator.add]  # 对话历史
├── interview_plan: list          # 面试问题列表
├── current_question_index: int   # 当前问题索引
├── current_stage: str            # 当前阶段
├── weak_points: list             # 薄弱知识点（长期记忆）
├── knowledge_points: list        # 知识点列表
├── jd: str                       # 岗位描述原文
└── route_decision: str           # 路由决策（ask/probe/review）
```

**节点流转逻辑：**

| 节点 | 输入 | 输出 | 说明 |
|------|------|------|------|
| `init` | JD 原文 | 面试计划 + 知识点 | 用 `with_structured_output` 解析 JD |
| `ask` | current_question_index | 面试问题 | 从 plan 中取出对应问题 |
| `evaluate` | 问题 + 回答 | 评估结果 + 路由决策 | 结构化评估，决定下一跳 |
| `probe` | 问题 + 回答 + 薄弱点 | 深度追问 | 结合 RAG 检索生成针对性问题 |
| `review` | 全量对话 + 薄弱点 | 复盘报告 | Markdown 格式完整报告 |

**中断机制：**

```
interrupt_after=["ask", "probe"]
```

在提问后中断图执行，等待用户输入。用户输入通过 `update_state` 注入，然后用 `Command(resume=None)` 恢复执行。

### 2. 评估路由策略

```
evaluate 节点
    │
    ├── is_correct=True, 还有下一题  ──→  ask（下一题）
    ├── is_correct=False             ──→  probe（深度追问）
    ├── need_deep_probe=True         ──→  probe（需要深挖）
    ├── need_tool_call=True          ──→  预留工具调用
    └── 所有问题已问完               ──→  review（复盘）
```

### 3. 双轨记忆系统

```
短期记忆（InMemorySaver）
    └── 维持当前面试的对话上下文
    └── 通过 checkpointer 实现中断恢复

长期记忆（weak_points in State）
    └── evaluate 节点判定答错时自动追加
    └── review 节点在报告中重点分析
    └── 可扩展为 PostgreSQL 持久化
```

### 4. RAG 增强追问

```
probe 节点
    │
    ├── 1. 提取当前问题和候选人回答
    ├── 2. 调用 rag_search 检索相关知识
    ├── 3. 构造 PROBE prompt（含 RAG 上下文）
    └── 4. LLM 生成针对性追问
```

---

## 🔧 工具调用说明

### Python 代码执行

```python
@app.tools.code_executor
def execute_python_code(code: str) -> Dict:
    """
    沙箱执行 Python 代码
    
    限制：
    - 只允许安全的内置函数
    - 捕获 stdout/stderr
    - 异常安全返回
    """
```

适用于面试中要求候选人写算法题或代码片段的场景。

### 联网搜索

```python
@app.tools.web_search
def search_from_web(question: str) -> List:
    """
    使用 Tavily API 搜索技术话题
    
    适用于：
    - 验证候选人提到的开源项目
    - 查证最新技术动态
    - 补充面试官的知识储备
    """
```

---

## ⚙️ 配置参考

### 环境变量完整列表

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | ✅ | - | DeepSeek API 密钥 |
| `TAVILY_API_KEY` | ✅ | - | Tavily 搜索 API 密钥 |
| `CHAT_MODEL` | ❌ | `deepseek-chat` | 大模型名称 |
| `EMBEDDING_MODEL` | ❌ | `qwen3-embedding:8b` | Embedding 模型 |
| `EMBEDDING_HOST` | ❌ | `http://localhost:11434` | Ollama 服务地址 |
| `MILVUS_URI` | ❌ | `http://localhost:19530` | Milvus 服务地址 |
| `DB_NAME` | ❌ | `mock_interview_pro` | Milvus 数据库名 |
| `COLLECTION_NAME` | ❌ | `interview_knowledge_base` | Milvus 集合名 |
| `POSTGRESQL_URL` | ❌ | - | PostgreSQL 连接串 |

### 结构化输出 Schema

```python
class EvaluationResult(BaseModel):
    """评估候选人回答"""
    is_correct: bool          # 回答是否基本正确
    need_deep_probe: bool     # 是否需要深度追问
    need_tool_call: bool      # 是否需要调用工具
    tool_name: str            # 工具名称
    feedback: str             # 评价反馈

class EvaluateOutput(BaseModel):
    """JD 分析输出"""
    interview_plan: List[str]       # 5个核心问题
    knowledge_points: List[str]     # 对应知识点列表
```

---

## 🧪 开发路线图

| Phase | 内容 | 状态 |
|-------|------|------|
| **Phase 1** | 基础设施：State 定义、Graph 构建、CLI 交互闭环 | ✅ 完成 |
| **Phase 2** | RAG 知识库：文档加载、向量化、动态检索追问 | ✅ 完成 |
| **Phase 3** | 工具调用：代码执行、联网搜索、条件路由 | ✅ 完成 |
| **Phase 4** | 记忆系统：短期/长期记忆、薄弱点追踪、复盘报告 | ✅ 完成 |
| **Phase 5** | UI 封装：Streamlit 界面、文件上传、状态面板 | ✅ 完成 |

---

## 🚨 避坑指南

1. **State 膨胀问题**：不要把 LLM 的中间思考过程（如 JSON 解析前的原始字符串）塞进 State。State 只保留跨节点必须共享的核心数据。

2. **结构化输出失败**：在 evaluate 节点让 LLM 输出评估结果时，**务必**使用 `llm.with_structured_output(EvaluationSchema)`。不要试图用正则去解析 LLM 返回的 Markdown 代码块里的 JSON，一定会出错。

3. **工具死循环**：如果工具返回的结果不符合预期，Agent 可能会疯狂重复调用同一个工具。**解决办法**：在 Prompt 中明确限制"最多调用 2 次工具"，或在 LangGraph 中设置 `recursion_limit`。

4. **Token 消耗过快**：多轮面试会导致上下文极长。建议在 evaluate 节点中，定期使用一个小模型对历史 messages 进行 Summary（摘要），替换掉早期的详细对话。

---

## 📝 简历包装建议

当你在简历上写这个项目时，**不要只写"使用了 LangGraph"**，请参考以下话术：

- **架构设计**："基于 LangGraph 设计了包含 5 个核心节点的状态机，利用 `interrupt` 机制实现了 Human-in-the-loop 的多轮面试交互，解决了传统 Chain 无法动态调整流程的痛点。"

- **RAG 结合**："摒弃了静态 RAG，设计了动态检索策略。在深挖环节（Depth_Probe），根据候选人回答实时生成 Query 检索向量库，实现了'千人千面'的压力面试。"

- **记忆系统**："设计了双轨记忆系统。短期记忆基于 InMemorySaver 维持上下文，长期记忆通过自定义 State 动态记录候选人薄弱知识点，并在最终复盘节点（Final_Review）进行针对性反馈。"

- **工具编排**："集成了代码执行与联网搜索工具，通过 LangGraph 的条件边（Conditional Edges）实现了基于回答质量的动态工具路由，提升了面试评估的客观性。"

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交改动：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 发起 Pull Request

---

## 📄 License

MIT License

---

> 项目状态：✅ 核心功能已全部完成，欢迎 Star ⭐ 和 Issue 反馈！
