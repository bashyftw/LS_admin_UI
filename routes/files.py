from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from app import  app
import os


app.config['UPLOAD_FOLDER'] = 'uploads'

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_files():
#     if request.method == 'POST':
#         if 'files[]' not in request.files:
#             return 'No file part'
#         files = request.files.getlist('files[]')
#         for file in files:
#             if file.filename == '':
#                 return 'No selected file'
#             if file:
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         return 'Files uploaded successfully'
#     return render_template('controllers/upload.html')


@app.route('/upload', methods=['GET'])
def upload_file_get():
    return render_template('controllers/upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file[]')
    for file in files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return 'files uploaded successfully'
