"""
题库 App - PDF 生成脚本
从 Supabase 获取试卷数据并生成 PDF
"""

import os
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

# Supabase 配置（需要替换为你的实际值）
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"


def get_paper_questions(paper_id: str) -> dict:
    """从 Supabase 获取试卷和题目数据"""
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

    # 获取试卷信息
    paper_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/papers?id=eq.{paper_id}", headers=headers
    )
    paper = paper_resp.json()[0] if paper_resp.json() else None

    # 获取试卷题目（按顺序）
    questions_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/paper_questions?paper_id=eq.{paper_id}&order=order_num",
        headers=headers,
    )
    paper_questions = questions_resp.json()

    # 获取题目详情
    questions = []
    for pq in paper_questions:
        q_resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/questions?id=eq.{pq['question_id']}",
            headers=headers,
        )
        if q_resp.json():
            questions.append(q_resp.json()[0])

    return {"paper": paper, "questions": questions}


def download_image(url: str) -> Image.Image:
    """下载图片并返回 PIL Image"""
    resp = requests.get(url)
    return Image.open(BytesIO(resp.content))


def generate_pdf(paper_id: str, output_path: str, include_answers: bool = True):
    """
    生成 PDF 试卷

    Args:
        paper_id: 试卷 ID
        output_path: 输出 PDF 路径
        include_answers: 是否包含答案
    """
    data = get_paper_questions(paper_id)
    paper = data["paper"]
    questions = data["questions"]

    if not paper:
        print(f"试卷 {paper_id} 不存在")
        return

    # 创建 PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # 标题页
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 3 * cm, paper["name"])
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 4 * cm, f"共 {len(questions)} 题")
    c.showPage()

    # 题目页
    for i, question in enumerate(questions, 1):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, height - 2 * cm, f"第 {i} 题")

        # 绘制题目图片
        if question.get("question_image_url"):
            try:
                img = download_image(question["question_image_url"])
                img_reader = ImageReader(img)

                # 计算图片尺寸（保持比例，最大宽度为页面宽度减4cm）
                max_width = width - 4 * cm
                img_width, img_height = img.size
                ratio = min(max_width / img_width, 15 * cm / img_height)
                display_width = img_width * ratio
                display_height = img_height * ratio

                # 居中绘制
                x = (width - display_width) / 2
                y = height - 3 * cm - display_height

                c.drawImage(img_reader, x, y, display_width, display_height)
            except Exception as e:
                c.drawString(2 * cm, height - 3 * cm, f"图片加载失败: {e}")

        c.showPage()

    # 答案页（如果包含答案）
    if include_answers:
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 2 * cm, "参考答案")
        c.showPage()

        for i, question in enumerate(questions, 1):
            if question.get("answer_image_url"):
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2 * cm, height - 2 * cm, f"第 {i} 题答案")

                try:
                    img = download_image(question["answer_image_url"])
                    img_reader = ImageReader(img)

                    max_width = width - 4 * cm
                    img_width, img_height = img.size
                    ratio = min(max_width / img_width, 15 * cm / img_height)
                    display_width = img_width * ratio
                    display_height = img_height * ratio

                    x = (width - display_width) / 2
                    y = height - 3 * cm - display_height

                    c.drawImage(img_reader, x, y, display_width, display_height)
                except Exception as e:
                    c.drawString(2 * cm, height - 3 * cm, f"图片加载失败: {e}")

                c.showPage()

    c.save()
    print(f"PDF 已生成: {output_path}")


def generate_pdf_by_tags(
    tag_names: list, output_path: str, include_answers: bool = True
):
    """
    按标签生成 PDF

    Args:
        tag_names: 标签名称列表
        output_path: 输出 PDF 路径
        include_answers: 是否包含答案
    """
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

    # 获取标签 ID
    tag_ids = []
    for tag_name in tag_names:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/tags?name=eq.{tag_name}", headers=headers
        )
        if resp.json():
            tag_ids.append(resp.json()[0]["id"])

    if not tag_ids:
        print("未找到指定标签")
        return

    # 获取包含这些标签的题目
    questions = []
    for tag_id in tag_ids:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/question_tags?tag_id=eq.{tag_id}&select=question_id",
            headers=headers,
        )
        for item in resp.json():
            q_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/questions?id=eq.{item['question_id']}",
                headers=headers,
            )
            if q_resp.json():
                questions.append(q_resp.json()[0])

    # 去重
    questions = list({q["id"]: q for q in questions}.values())

    # 创建 PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # 标题页
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 3 * cm, "题库练习")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 4 * cm, f"标签: {', '.join(tag_names)}")
    c.drawCentredString(width / 2, height - 5 * cm, f"共 {len(questions)} 题")
    c.showPage()

    # 绘制题目和答案
    for i, question in enumerate(questions, 1):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, height - 2 * cm, f"第 {i} 题")

        if question.get("question_image_url"):
            try:
                img = download_image(question["question_image_url"])
                img_reader = ImageReader(img)

                max_width = width - 4 * cm
                img_width, img_height = img.size
                ratio = min(max_width / img_width, 12 * cm / img_height)
                display_width = img_width * ratio
                display_height = img_height * ratio

                x = (width - display_width) / 2
                y = height - 3 * cm - display_height

                c.drawImage(img_reader, x, y, display_width, display_height)

                # 答案在同一页面（如果有）
                if include_answers and question.get("answer_image_url"):
                    try:
                        ans_img = download_image(question["answer_image_url"])
                        ans_reader = ImageReader(ans_img)

                        ans_width, ans_height = ans_img.size
                        ans_ratio = min(max_width / ans_width, 8 * cm / ans_height)
                        ans_display_width = ans_width * ans_ratio
                        ans_display_height = ans_height * ans_ratio

                        ans_x = (width - ans_display_width) / 2
                        ans_y = y - ans_display_height - 1 * cm

                        if ans_y > 1 * cm:
                            c.setFont("Helvetica-Bold", 10)
                            c.drawString(
                                2 * cm, ans_y + ans_display_height + 0.5 * cm, "答案:"
                            )
                            c.drawImage(
                                ans_reader,
                                ans_x,
                                ans_y,
                                ans_display_width,
                                ans_display_height,
                            )
                    except:
                        pass

            except Exception as e:
                c.drawString(2 * cm, height - 3 * cm, f"图片加载失败: {e}")

        c.showPage()

    c.save()
    print(f"PDF 已生成: {output_path}")


if __name__ == "__main__":
    # 示例用法
    # 1. 按试卷生成
    # generate_pdf("your-paper-id", "exam.pdf", include_answers=True)

    # 2. 按标签生成
    # generate_pdf_by_tags(["数学", "第一章"], "practice.pdf", include_answers=True)

    print("请在代码中配置 SUPABASE_URL 和 SUPABASE_KEY 后使用")
    print("示例:")
    print('  generate_pdf("paper-id", "exam.pdf")')
    print('  generate_pdf_by_tags(["数学"], "practice.pdf")')
