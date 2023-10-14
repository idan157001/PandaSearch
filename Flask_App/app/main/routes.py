from flask import request,render_template,send_from_directory
from . import main
from app import limiter
from .db import Search
import os
from dotenv import load_dotenv
load_dotenv()


search_cls = Search()


@main.route('/images/<path:filename>')
def serve_image(filename):
    folder_path = os.getenv('folder_path')
    return send_from_directory(folder_path, filename)


@main.route('/',methods=['GET'])
@limiter.limit('5 per second')

def index():
    if request.method == 'GET':
        return render_template('index.html')
    

@main.route('/search')
@limiter.limit('5 per second')
def search():
    if request.method == 'GET': 
        if 'item' in request.args:
                user_item_arg = request.args['item']
                items = search_cls.search_runner(user_item_arg)

                if items is None:
                    return render_template('search.html',error=True)
                
                elif items:
                    return render_template('search.html',items=items)
                
        return render_template('search.html')