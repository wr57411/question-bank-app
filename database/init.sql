-- 题库 App 数据库初始化脚本
-- 在 Supabase SQL Editor 中执行

-- 1. 题目表
CREATE TABLE IF NOT EXISTS questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    question_image_url TEXT NOT NULL,
    answer_image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 标签表
CREATE TABLE IF NOT EXISTS tags (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name)
);

-- 3. 题目标签关联表（多对多）
CREATE TABLE IF NOT EXISTS question_tags (
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (question_id, tag_id)
);

-- 4. 试卷表
CREATE TABLE IF NOT EXISTS papers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 试卷题目关联表
CREATE TABLE IF NOT EXISTS paper_questions (
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    order_num INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (paper_id, question_id)
);

-- 6. 创建索引
CREATE INDEX idx_question_tags_question ON question_tags(question_id);
CREATE INDEX idx_question_tags_tag ON question_tags(tag_id);
CREATE INDEX idx_paper_questions_paper ON paper_questions(paper_id);
CREATE INDEX idx_paper_questions_order ON paper_questions(paper_id, order_num);

-- 7. 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 8. 启用 RLS（行级安全，可选）
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE papers ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_questions ENABLE ROW LEVEL SECURITY;

-- 9. 创建公开访问策略（简化版，生产环境需调整）
CREATE POLICY "Allow all" ON questions FOR ALL USING (true);
CREATE POLICY "Allow all" ON tags FOR ALL USING (true);
CREATE POLICY "Allow all" ON question_tags FOR ALL USING (true);
CREATE POLICY "Allow all" ON papers FOR ALL USING (true);
CREATE POLICY "Allow all" ON paper_questions FOR ALL USING (true);
