from flask import Blueprint, jsonify
tools_bp=Blueprint("tools",__name__,url_prefix="/api/tools")
@tools_bp.get("")
def tool_catalog():
    return jsonify({"success":True,"tools":["merge_pdf","split_pdf","compress_pdf","rotate_pdf","delete_pages","extract_pages","reorder_pages","page_numbers","watermark_pdf","extract_images"]})
