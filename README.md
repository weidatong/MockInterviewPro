# MockInterviewPro
一个基于大语言模型的综合型 AI Agent。它不仅能与用户进行多轮模拟面试，还能根据用户的回答动态调整提问策略（追问或提示），在算法环节自动执行代码判题，并在面试结束后结合用户的“历史薄弱点”生成深度的复盘报告。

项目使用到的大模型

向量模型：

```tex
qwen3-embedding:8b
```

推理模型：

```tex
Deepseek-v4-pro
```

### 项目目录结构

```tex
MockInterview-Pro/
│
├── .env                        # 环境变量配置 (API Keys, 数据库路径等，绝不提交到 Git)
├── .gitignore                  # Git 忽略文件配置 (忽略 .env, vector_db/, __pycache__ 等)
├── requirements.txt            # 项目依赖清单 (langchain, langgraph, streamlit 等)
├── README.md                   # 项目说明文档 (包含架构图、运行指南)
├── main.py                     # CLI 主入口 (用于终端命令行交互调试)
│
├── data/                       # 原始数据目录 (RAG 知识源)
│   ├── jds/                    # 存放岗位描述 (JD) 的 PDF/TXT 文件
│   ├── resume/                 # 存放建立的 PDF/WORD 文件
│   └── interviews/             # 存放面经、技术文档的 PDF/TXT 文件
│
├── vector_db/                  # 向量数据库本地持久化目录 (ChromaDB 生成，需加入 .gitignore)
│
├── app/                        # 核心业务代码目录 (Core Logic)
│   ├── __init__.py
│   ├── config.py               # 全局配置 (加载 .env，初始化 LLM、Embeddings 模型实例)
│   ├── state.py                # LangGraph 状态定义 (InterviewState TypedDict)
│   │
│   ├── prompts/                # Prompt 模板目录 (实现 Prompt 与代码分离，方便迭代)
│   │   ├── __init__.py
│   │   ├── init_prompt.py      # 初始化/开场白 Prompt
│   │   ├── evaluate_prompt.py  # 评估回答质量的 Prompt (含结构化输出 Schema)
│   │   └── review_prompt.py    # 最终复盘报告的 Prompt
│   │
│   ├── nodes/                  # LangGraph 节点逻辑目录 (避免 graph.py 变成几千行的上帝文件)
│   │   ├── __init__.py
│   │   ├── init_node.py        # 解析 JD，生成面试计划
│   │   ├── evaluate_node.py    # 评估回答，决定路由 (追问/换题/调工具/结束)
│   │   ├── probe_node.py       # 深度追问节点 (结合 RAG)
│   │   └── review_node.py      # 生成最终复盘报告
│   │
│   ├── tools/                  # 自定义工具目录 (Tool Calling)
│   │   ├── __init__.py
│   │   ├── code_executor.py    # Python 代码执行工具 (封装 REPL)
│   │   └── web_search.py       # 联网搜索工具 (封装 Tavily API)
│   │
│   ├── rag/                    # RAG 知识库管理目录
│   │   ├── __init__.py
│   │   ├── ingest.py           # 文档加载、切分、向量化入库逻辑
│   │   └── retriever.py        # 检索器封装 (根据 Query 动态检索)
│   │
│   ├── memory/                 # 记忆管理目录
│   │   ├── __init__.py
│   │   └── long_term.py        # 长期记忆管理 (读写 SQLite/JSON，管理 weak_points)
│   │
│   ├── graph.py                # LangGraph 核心编排 (定义节点、边、条件路由、编译 Graph)
│   │
│   └── ui/                     # 前端 UI 目录
│       ├── __init__.py
│       ├── streamlit_app.py    # Streamlit 主程序 (聊天界面、文件上传)
│       └── components.py       # 自定义 UI 组件 (如：折叠面板展示 Agent 思考过程)
│
└── tests/                      # 单元测试目录 (可选，但推荐)
    ├── test_tools.py           # 测试代码执行和搜索工具是否正常
    └── test_rag.py             # 测试 RAG 检索结果是否准确
```

# 部署教程
切换到当前根目录下，然后执行下面的命令
```shell
uv pip install -r requirements.txt
```





