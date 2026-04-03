from fastapi import FastAPI, HTTPException
import requests
import pdfplumber
from io import BytesIO
import uvicorn

app = FastAPI()

@app.post("/parse_pdf")
async def parse_pdf(file_url: str):
    """
    接收 Coze 传来的 PDF 文件 URL，下载并提取文本
    """
    try:
        # 下载 PDF
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(file_url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"PDF download failed: HTTP {resp.status_code}")
        
        # 用 pdfplumber 提取文本
        with pdfplumber.open(BytesIO(resp.content)) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from PDF")
        
        # 限制长度（Coze 大模型上下文限制）
        if len(text) > 50000:
            text = text[:50000] + "\n...(内容过长，已截断)"
        
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点（可选）
@app.get("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
