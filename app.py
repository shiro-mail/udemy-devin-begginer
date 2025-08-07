from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'json'

def load_shipping_data_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        return []

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('ファイルが選択されていません')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('ファイルが選択されていません')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        session['uploaded_file'] = filepath
        return redirect(url_for('display_data'))
    else:
        flash('JSONファイルのみアップロード可能です')
        return redirect(request.url)

@app.route('/display')
def display_data():
    if 'uploaded_file' not in session:
        flash('先にJSONファイルをアップロードしてください')
        return redirect(url_for('index'))
    
    filepath = session['uploaded_file']
    if not os.path.exists(filepath):
        flash('アップロードされたファイルが見つかりません')
        return redirect(url_for('index'))
    
    shipping_data = load_shipping_data_from_file(filepath)
    return render_template('display.html', shipping_data=shipping_data)

@app.route('/sample')
def sample_data():
    sample_file = 'sample_data.json'
    if os.path.exists(sample_file):
        session['uploaded_file'] = sample_file
        return redirect(url_for('display_data'))
    else:
        flash('サンプルデータが見つかりません')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
