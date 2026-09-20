def ocr_page(page):
    try:
        import pytesseract
        from PIL import Image
    except Exception as e: raise RuntimeError('OCR requires Pillow and pytesseract.') from e
    pix=page.get_pixmap(matrix=__import__('pymupdf').Matrix(2,2),alpha=False)
    image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    return pytesseract.image_to_string(image)
