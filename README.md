# PDF to JPG Converter

一個簡潔優雅的網頁服務，將 PDF 檔案轉換為高品質 JPG 圖片。

## 功能特色

- **拖放上傳** - 直接拖放 PDF 檔案或點擊選擇
- **自訂解析度** - DPI 範圍 72-600，滿足不同需求
- **品質控制** - JPG 品質 1-100% 可調整
- **批次輸出** - 多頁 PDF 自動轉換並打包成 ZIP
- **中文支援** - 完整支援中文檔名

## 系統需求

- Python 3.9+
- Poppler（PDF 渲染引擎）

## 安裝

### 1. 安裝 Poppler

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
下載 [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) 並加入 PATH

### 2. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

## 使用方式

### 啟動服務

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

或使用 reload 模式（開發用）:

```bash
uvicorn main:app --reload
```

### 存取服務

- **網頁介面**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs

## API

### POST /api/convert

將 PDF 轉換為 JPG 圖片。

**參數:**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| file | File | (必填) | PDF 檔案 |
| dpi | int | 150 | 解析度 (72-600) |
| quality | int | 85 | JPG 品質 (1-100) |

**回應:**
- 成功: ZIP 檔案 (application/zip)
- 失敗: JSON 錯誤訊息

**範例:**
```bash
curl -X POST "http://localhost:8000/api/convert" \
  -F "file=@document.pdf" \
  -F "dpi=300" \
  -F "quality=90" \
  -o output.zip
```

## 專案結構

```
pdf2jpg/
├── main.py              # FastAPI 應用程式
├── requirements.txt     # Python 依賴
├── static/
│   └── index.html       # 前端頁面
└── README.md
```

## 技術棧

- **後端**: FastAPI + Uvicorn
- **PDF 處理**: pdf2image + Poppler
- **前端**: HTML + CSS（純手刻，無框架）

## 授權

MIT License

## 作者

Jackie Yeh
