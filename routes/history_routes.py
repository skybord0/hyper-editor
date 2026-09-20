from flask import Blueprint,jsonify
from services.history_service import get_history,clear_history
history_bp=Blueprint('history_api',__name__,url_prefix='/api/history')
@history_bp.get('')
def history():return jsonify({'success':True,'items':get_history()})
@history_bp.post('/clear')
def clear():clear_history();return jsonify({'success':True})
