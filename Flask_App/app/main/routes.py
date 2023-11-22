from flask import request,render_template,send_from_directory,jsonify,redirect,url_for
from . import main
from .. import limiter
from .db import Search
import os


search_cls = Search()


@main.route('/images/<path:filename>')
def serve_image(filename):
    folder_path = os.getenv('folder_path')
    return send_from_directory(folder_path, filename)


@main.route('/',methods=['GET'])
@limiter.limit('5 per second')
def home():
    search = request.args.get('q','')
    brands = search_cls.brand_quick_search()
    top_items = search_cls.home_page_top_items()

    if search:
        items = search_cls.search_runner(search)
        if items:
            return render_template('search.html',brands=brands,item=top_items,items=items)
        
    return render_template('search.html',brands=brands,item=top_items)




@main.route('/search_products',methods=['POST'])
@limiter.limit('5 per second')
def search_products():
    if request.method == 'POST':
        search_query = request.form['search_query']
        
        if search_query:
            items = search_cls.search_runner(search_query)
            if items is None:
                return render_template('products.html',error=True)
            elif items:
                return render_template('products.html',items=items)
       
    