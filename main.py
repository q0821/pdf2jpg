"""PDF to JPG 網頁服務"""

import io
import zipfile
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError

app = FastAPI(
    title="PDF to JPG Converter",
    description="將 PDF 檔案轉換為 JPG 圖片",
    version="1.0.0",
)

# 掛載靜態檔案目錄
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """首頁 - 返回前端頁面"""
    return FileResponse(static_dir / "index.html")


@app.post("/api/convert")
async def convert_pdf_to_jpg(
    file: UploadFile = File(..., description="PDF 檔案"),
    dpi: int = Form(default=150, ge=72, le=600, description="解析度 (72-600)"),
    quality: int = Form(default=85, ge=1, le=100, description="JPG 品質 (1-100)"),
):
    """
    將 PDF 轉換為 JPG 圖片

    - **file**: 要轉換的 PDF 檔案
    - **dpi**: 輸出圖片的解析度，預設 150
    - **quality**: JPG 壓縮品質，預設 85
    """
    # 驗證檔案類型
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供檔案名稱")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只接受 PDF 檔案")

    # 讀取上傳的 PDF
    try:
        pdf_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"讀取檔案失敗: {str(e)}")

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="檔案為空")

    # 轉換 PDF 為圖片
    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi)
    except PDFPageCountError:
        raise HTTPException(status_code=400, detail="無法讀取 PDF 頁數，檔案可能已損壞")
    except PDFSyntaxError:
        raise HTTPException(status_code=400, detail="PDF 格式錯誤")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 轉換失敗: {str(e)}")

    if not images:
        raise HTTPException(status_code=400, detail="PDF 沒有任何頁面")

    # 建立 ZIP 檔案
    base_name = Path(file.filename).stem
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, image in enumerate(images, start=1):
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="JPEG", quality=quality)
            img_buffer.seek(0)

            # 檔名格式：原檔名_頁碼.jpg
            img_filename = f"{base_name}_{i:03d}.jpg"
            zip_file.writestr(img_filename, img_buffer.getvalue())

    zip_buffer.seek(0)

    # 回傳 ZIP 檔案
    # 使用 RFC 5987 編碼支援中文檔名
    zip_filename = f"{base_name}_images.zip"
    encoded_filename = quote(zip_filename)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )


@app.get("/api/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "ok"}
