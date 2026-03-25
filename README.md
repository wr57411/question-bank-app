# 题库 App

一个简单的题库管理系统，支持图片题目、标签分类和 PDF 生成。

## 功能

- 上传题目图片和答案图片
- 为题目添加标签
- 按标签创建试卷
- 导出 PDF 试卷

## 技术栈

- **数据库/存储**: Supabase
- **前端**: HTML + JavaScript
- **PDF 生成**: Python + ReportLab

## 快速开始

### 1. 创建 Supabase 项目

1. 访问 [supabase.com](https://supabase.com) 注册账号
2. 创建新项目
3. 在 SQL Editor 中执行 `database/init.sql`
4. 在 Storage 中创建名为 `images` 的 bucket，设为公开

### 2. 配置前端

编辑 `frontend/index.html`，替换以下配置：

```javascript
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_KEY = 'your-anon-key';
```

### 3. 运行前端

直接在浏览器中打开 `frontend/index.html`，或使用本地服务器：

```bash
cd frontend
python -m http.server 8000
```

然后访问 http://localhost:8000

### 4. 配置 Python 脚本

编辑 `scripts/generate_pdf.py`，替换 Supabase 配置。

安装依赖：

```bash
cd scripts
pip install -r requirements.txt
```

### 5. 生成 PDF

```python
from generate_pdf import generate_pdf, generate_pdf_by_tags

# 按试卷生成
generate_pdf("试卷ID", "exam.pdf", include_answers=True)

# 按标签生成
generate_pdf_by_tags(["数学", "第一章"], "practice.pdf", include_answers=True)
```

## 文件结构

```
question-bank-app/
├── database/
│   └── init.sql          # 数据库初始化脚本
├── scripts/
│   ├── generate_pdf.py   # PDF 生成脚本
│   └── requirements.txt  # Python 依赖
├── frontend/
│   └── index.html        # Web 界面
└── README.md
```

## 数据库表结构

- `questions`: 题目表（存储图片 URL）
- `tags`: 标签表
- `question_tags`: 题目标签关联表
- `papers`: 试卷表
- `paper_questions`: 试卷题目关联表

## 注意事项

- Supabase 免费版有存储和带宽限制
- 建议压缩图片后再上传
- 生产环境请启用用户认证和 RLS 策略
