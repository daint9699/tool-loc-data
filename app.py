# -*- coding: utf-8 -*-
from flask import Flask
from filter_routes import filter_bp
from split_routes import split_bp

app = Flask(__name__)

# Đăng ký Blueprint cho các phần của ứng dụng
app.register_blueprint(filter_bp, url_prefix='/filter')
app.register_blueprint(split_bp, url_prefix='/split')

# Trang chủ để chọn tính năng
@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Data Processing Options</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 600px;
            }
            .card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }
            .card-title {
                font-weight: 500;
                color: #202124;
            }
            .btn-primary {
                background-color: #4285f4;
                border: none;
                font-weight: 500;
            }
            .btn-secondary {
                background-color: #fbbc05;
                border: none;
                font-weight: 500;
                color: #202124;
            }
            .btn-primary:hover {
                background-color: #357ae8;
            }
            .btn-secondary:hover {
                background-color: #eaa300;
            }
            .text-center a {
                margin: 10px;
            }
            .illustration {
                width: 100%;
                max-width: 400px;
                margin: 20px auto;
                display: block;
            }
            .footer-note {
                margin-top: 30px;
                font-size: 0.9em;
                color: #757575;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body text-center">
                    <img src="https://static.vecteezy.com/system/resources/previews/008/258/236/non_2x/filling-out-the-scrum-board-for-a-business-plan-free-vector.jpg" alt="Illustration" class="illustration">
                    <h1 class="card-title mb-4">Hello, bạn muốn xử lý dữ liệu như nào?</h1>
                    <a href="/filter" class="btn btn-primary btn-lg">Lọc Data</a>
                    <a href="/split" class="btn btn-secondary btn-lg">Tách File Con</a>
                </div>
            </div>
            <div class="footer-note">
                Website được tạo 100% bởi AI Chat GPT
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5001)
