from flask import request,render_template,send_from_directory
from . import main
from .db import FireBase
firebase= FireBase()
@main.route('/',methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    
@main.route('/images/<path:filename>')
def serve_image(filename):
    folder_path = r"C:\Users\Idan's PC\OneDrive\Desktop\Pandabuy\pandabuy\Items"
    return send_from_directory(folder_path, filename)

@main.route('/search')
def search():
    if request.method == 'GET': 
        if 'item' in request.args:
                user_item_arg = request.args['item']
                items = firebase.get_item_name(user_item_arg)

                if items is None:
                    return render_template('search.html',error=True)
                
                elif items:
                    return render_template('search.html',items=items)
                
        return render_template('search.html')