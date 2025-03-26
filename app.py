from flask import Flask, render_template, request, send_file, redirect, url_for, flash, abort
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 10000 * 1024 * 1024  # 20000MB limit
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx', 'zip', 'rar'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_icon(filename):
    """Get emoji icon based on file extension"""
    extension = filename.split('.')[-1].lower()
    icons = {
        'pdf': '📄',
        'txt': '📝',
        'png': '🖼️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'gif': '🖼️',
        'docx': '📑',
        'xlsx': '📊',
        'pptx': '📽️',
        'zip': '📁',
        'rar': '📁',
        'tar': '📁',
        'gz': '📁',
        '7z': '📁',
        'mp3': '🎵',   
        'wav': '🎵',   
        'mp4': '🎬',    
        'mov': '🎬',   
        'avi': '🎬',  
    }
    return icons.get(extension, '📁')

@app.route('/')
def index():
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                files.append({
                    'name': filename,
                    'size': f"{size / 1024:.1f} KB",
                    'icon': get_file_icon(filename)
                })
        return render_template('index.html', files=files)
    except Exception as e:
        flash('Error loading files')
        app.logger.error(f"Error loading files: {str(e)}")
        return render_template('index.html', files=[])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('File type not allowed')
        return redirect(url_for('index'))
    
    try:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'{filename} uploaded successfully')
    except Exception as e:
        flash('Error uploading file')
        app.logger.error(f"Error uploading file: {str(e)}")
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(path):
            abort(404)
        return send_file(path, as_attachment=True)
    except Exception as e:
        flash('Error downloading file')
        app.logger.error(f"Error downloading {filename}: {str(e)}")
        return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(path):
            os.remove(path)
            flash(f'{filename} deleted successfully')
        else:
            flash('File not found')
    except Exception as e:
        flash('Error deleting file')
        app.logger.error(f"Error deleting {filename}: {str(e)}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')