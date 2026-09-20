# HYPER EDITOR

HYPER EDITOR is a local-first Flask workspace for file conversion, PDF utilities, a professional browser PDF Studio, and a Word Studio.

## Run

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Main capabilities

### Conversion
- PNG/JPG/WEBP image conversion
- Images to PDF and Word
- PDF to JPG, PNG, TXT, Word
- DOCX to TXT, PDF, JPG, PNG
- XLSX to CSV/PDF and CSV to XLSX
- PPTX to PDF/JPG/PNG
- TXT/HTML to PDF and TXT to Word
- ZIP extraction

### PDF utilities
- Merge
- Split by page range or pages per file
- Compress
- Rotate
- Delete pages
- Extract pages
- Reorder pages
- Add page numbers
- Watermark
- Extract embedded images

### PDF Studio
- Render every page with thumbnails
- Select existing text spans
- Replace existing text while keeping approximate position, size, colour and font family
- Change text box position and size
- Add text
- Highlight, underline, strikeout and redact
- Rectangle, ellipse and line drawing
- Freehand drawing
- Insert images
- Typed signature placement
- OCR text extraction pathway
- Rotate, delete, duplicate and add pages
- Reorder pages
- Undo and redo
- Save edited PDF

### Word Studio
- Load DOCX paragraphs and tables
- Content editing
- Bold, italic, underline and alignment controls
- Font size and colour controls
- Table editing
- Save edited DOCX

## Runtime folders

Uploaded and generated files are intentionally excluded from the project archive. The application recreates the required folders on startup.

## Expanded tool catalog
The All Tools page now exposes PDF, Office, ebook, image, security and page-management tools from the requested catalog. Apple-specific formats are handled as compatible Office files: PDF to Pages produces DOCX and PDF to Keynote produces PPTX because native `.pages` and `.key` creation requires Apple's apps on macOS. PDF to Numbers produces XLSX. EPUB/MOBI conversions use Calibre when the `ebook-convert` command is installed; EPUB to PDF also has a Python fallback.
