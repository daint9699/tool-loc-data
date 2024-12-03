# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template_string, send_file
import pandas as pd
import os
import shutil
from zipfile import ZipFile

split_bp = Blueprint('split', __name__)

UPLOAD_FOLDER = 'uploads'
SPLIT_FOLDER = 'splits'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SPLIT_FOLDER, exist_ok=True)

# Trang upload file cho Split Data
@split_bp.route('/')
def split_index():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Upload File for Splitting</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center">Upload File for Splitting</h1>
                    <form action="/split/upload" method="post" enctype="multipart/form-data" class="text-center">
                        <div class="form-group">
                            <input type="file" name="file" accept=".xlsx" class="form-control-file" required>
                        </div>
                        <button type="submit" class="btn btn-secondary">Upload</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# Xử lý upload file và chọn sheet cho Split Data
@split_bp.route('/upload', methods=['POST'])
def split_upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Đọc file và lấy danh sách sheet
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names

        # Trang chọn sheet cho Split Data
        return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <title>Select Sheet for Splitting</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h1 class="card-title text-center">Select Sheet for Splitting</h1>
                        <form action="/split/select_sheet" method="post" class="text-center">
                            <input type="hidden" name="file_path" value="{{ file_path }}">
                            <div class="form-group">
                                <label for="sheet">Choose a sheet:</label>
                                <select name="sheet" class="form-control" required>
                                  {% for sheet in sheets %}
                                    <option value="{{ sheet }}">{{ sheet }}</option>
                                  {% endfor %}
                                </select>
                            </div>
                            <button type="submit" class="btn btn-secondary">Select</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        </html>
        ''', sheets=sheets, file_path=file_path)

# Route xử lý chọn sheet và chọn hàng tiêu đề
@split_bp.route('/select_sheet', methods=['POST'])
def split_select_sheet():
    file_path = request.form['file_path']
    sheet_name = request.form['sheet']

    # Đọc dữ liệu từ sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Render trang để người dùng chọn hàng nào sẽ làm tiêu đề
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Select Header Row for Splitting</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center">Select Header Row for Splitting</h1>
                    <form action="/split/select_header" method="post" class="text-center">
                        <input type="hidden" name="file_path" value="{{ file_path }}">
                        <input type="hidden" name="sheet_name" value="{{ sheet_name }}">
                        <div class="form-group">
                            <label for="header_row">Choose a row to use as header (0-based index):</label>
                            <select name="header_row" class="form-control" required>
                              {% for row in range(df.shape[0]) %}
                                <option value="{{ row }}">Row {{ row + 1 }}</option>
                              {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-secondary">Select</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', file_path=file_path, sheet_name=sheet_name, df=df)

# Route xử lý chọn hàng làm tiêu đề và tách dữ liệu
@split_bp.route('/select_header', methods=['POST'])
def split_select_header():
    file_path = request.form['file_path']
    sheet_name = request.form['sheet_name']
    header_row = int(request.form['header_row'])

    # Đọc dữ liệu từ sheet với hàng làm tiêu đề
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

    # Lựa chọn cột để phân tách
    columns = df.columns.tolist()
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Split Data by Column</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center">Select Column to Split Data By</h1>
                    <form action="/split/process" method="post" class="text-center">
                        <input type="hidden" name="file_path" value="{{ file_path }}">
                        <input type="hidden" name="sheet_name" value="{{ sheet_name }}">
                        <input type="hidden" name="header_row" value="{{ header_row }}">
                        <div class="form-group">
                            <label for="split_column">Choose a column to split by:</label>
                            <select name="split_column" class="form-control" required>
                              {% for column in columns %}
                                <option value="{{ column }}">{{ column }}</option>
                              {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-secondary">Split Data</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', file_path=file_path, sheet_name=sheet_name, header_row=header_row, columns=columns)

# Route xử lý việc tách dữ liệu và tạo file zip
@split_bp.route('/process', methods=['POST'])
def split_process():
    file_path = request.form['file_path']
    sheet_name = request.form['sheet_name']
    header_row = int(request.form['header_row'])
    split_column = request.form['split_column']

    # Đọc dữ liệu từ sheet với hàng làm tiêu đề
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

    # Tạo thư mục để lưu các file đã tách
    shutil.rmtree(SPLIT_FOLDER, ignore_errors=True)
    os.makedirs(SPLIT_FOLDER, exist_ok=True)

    # Tách dữ liệu thành nhiều file dựa trên giá trị của cột đã chọn
    unique_values = df[split_column].unique()
    for value in unique_values:
        subset_df = df[df[split_column] == value]
        subset_file_path = os.path.join(SPLIT_FOLDER, f"{split_column}_{value}.xlsx")
        subset_df.to_excel(subset_file_path, index=False)

    # Tạo file zip từ các file đã tách
    zip_file_path = os.path.join(UPLOAD_FOLDER, 'split_data.zip')
    with ZipFile(zip_file_path, 'w') as zipf:
        for file_name in os.listdir(SPLIT_FOLDER):
            file_path = os.path.join(SPLIT_FOLDER, file_name)
            zipf.write(file_path, file_name)

    # Trả về file zip cho người dùng tải về
    return send_file(zip_file_path, as_attachment=True)
