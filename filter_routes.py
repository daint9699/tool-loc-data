from flask import Blueprint, request, send_file, render_template_string
import pandas as pd
import os
import json

filter_bp = Blueprint('filter', __name__)

# Thiết lập thư mục lưu trữ file upload
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route trang chủ (hiển thị form upload file)
@filter_bp.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Upload File Excel</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center">Upload File Excel</h1>
                    <form action="/filter/upload" method="post" enctype="multipart/form-data" class="text-center">
                        <div class="form-group">
                            <input type="file" name="file" accept=".xlsx" class="form-control-file" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Upload</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# Route xử lý upload file và hiển thị các sheet có trong file
@filter_bp.route('/upload', methods=['POST'])
def upload_file():
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

        # Render trang chọn sheet
        return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <title>Select Sheet</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h1 class="card-title text-center">Select Sheet to Process Data</h1>
                        <form action="/filter/select_sheet" method="post" class="text-center">
                            <input type="hidden" name="file_path" value="{{ file_path }}">
                            <div class="form-group">
                                <label for="sheet">Choose a sheet:</label>
                                <select name="sheet" class="form-control" required>
                                  {% for sheet in sheets %}
                                    <option value="{{ sheet }}">{{ sheet }}</option>
                                  {% endfor %}
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">Select</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
        </html>
        ''', sheets=sheets, file_path=file_path)

# Route xử lý chọn sheet và chọn hàng tiêu đề
@filter_bp.route('/select_sheet', methods=['POST'])
def select_sheet():
    file_path = request.form['file_path']
    sheet_name = request.form['sheet']

    # Đọc dữ liệu từ sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Render trang để người dùng chọn hàng nào sẽ làm tiêu đề
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Select Header Row</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center">Select Header Row</h1>
                    <form action="/filter/select_header" method="post" class="text-center">
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
                        <button type="submit" class="btn btn-primary">Select</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', file_path=file_path, sheet_name=sheet_name, df=df)

# Route xử lý chọn hàng làm tiêu đề và hiển thị dữ liệu để lọc
@filter_bp.route('/select_header', methods=['POST'])
def select_header():
    file_path = request.form['file_path']
    sheet_name = request.form['sheet_name']
    header_row = int(request.form['header_row'])

    # Đọc dữ liệu từ sheet với hàng làm tiêu đề
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

    # Chuyển đổi các giá trị không thể chuyển sang JSON thành chuỗi
    df = df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.api.types.is_datetime64_any_dtype(type(x)) else x)
    df = df.applymap(lambda x: str(x) if pd.isna(x) else x)

    # Chuyển bảng dữ liệu sang JSON để JavaScript sử dụng
    data_json = df.applymap(str).to_dict(orient='list')

    # Render trang hiển thị bảng dữ liệu và bộ lọc nâng cao
    columns = df.columns.tolist()
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Advanced Filter Data</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h1 class="card-title text-center">Advanced Filter Data</h1>

                    <form id="filter-form" action="/filter/filter_data" method="post">
                        <input type="hidden" name="file_path" value="{{ file_path }}">
                        <input type="hidden" name="sheet_name" value="{{ sheet_name }}">
                        <input type="hidden" name="header_row" value="{{ header_row }}">
                        
                        <div id="filters" class="form-group">
                            <div class="filter-group mb-3">
                                <label for="column_0">Choose a column to filter:</label>
                                <select class="column form-control" name="column_0" onchange="updateFilterValues(0)" required>
                                  <option value="" selected disabled>-- Select Column --</option>
                                  {% for column in columns %}
                                    <option value="{{ column }}">{{ column }}</option>
                                  {% endfor %}
                                </select>
                                
                                <div id="filter_values_0" class="mt-3 row">
                                    <!-- Checkboxes for Filter Values will be inserted here -->
                                </div>
                            </div>
                        </div>

                        <button type="button" class="btn btn-secondary" onclick="addFilter()">Add Another Filter</button><br><br>

                        <div id="date-filter" class="form-group">
                            <h3>Date Filter (Optional)</h3>
                            <label for="start_date">Start Date:</label>
                            <input type="date" name="start_date" class="form-control mb-3"><br>
                            <label for="end_date">End Date:</label>
                            <input type="date" name="end_date" class="form-control mb-3"><br>
                        </div>

                        <button type="button" class="btn btn-primary" onclick="filterData()">Filter Data</button>
                        <button type="submit" class="btn btn-success mt-3">Download Filtered Data</button>
                        <button type="button" class="btn btn-danger mt-3" onclick="resetFilter()">Clear Filters</button>
                    </form>

                    <h2 class="mt-5">Filtered Data Table</h2>
                    <div id="filtered-data" class="table-responsive mt-3">
                      <!-- Filtered data will be shown here -->
                    </div>
                </div>
            </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            const data = {{ data_json | tojson }};
            let filterCount = 1;

            function updateFilterValues(filterIndex) {
                const columnSelect = document.getElementsByClassName("column")[filterIndex];
                const selectedColumn = columnSelect.value;
                const filterValuesDiv = document.getElementById(`filter_values_${filterIndex}`);
                
                // Clear existing checkboxes
                filterValuesDiv.innerHTML = '';

                if (selectedColumn && data[selectedColumn]) {
                    const uniqueValues = [...new Set(data[selectedColumn])];
                    uniqueValues.forEach(value => {
                        const checkboxWrapper = document.createElement("div");
                        checkboxWrapper.className = "col-md-3 mb-2";

                        const checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.name = `filter_value_${filterIndex}`;
                        checkbox.value = value;
                        checkbox.className = "mr-1";

                        const label = document.createElement("label");
                        label.appendChild(checkbox);
                        label.appendChild(document.createTextNode(value));

                        checkboxWrapper.appendChild(label);
                        filterValuesDiv.appendChild(checkboxWrapper);
                    });
                }
            }

            function addFilter() {
                const filtersDiv = document.getElementById("filters");
                const newFilterIndex = filterCount;

                const filterGroup = document.createElement("div");
                filterGroup.className = "filter-group mb-3";
                filterGroup.innerHTML = `
                    <label for="column_${newFilterIndex}">Choose a column to filter:</label>
                    <select class="column form-control" name="column_${newFilterIndex}" onchange="updateFilterValues(${newFilterIndex})" required>
                      <option value="" selected disabled>-- Select Column --</option>
                      {% for column in columns %}
                        <option value="{{ column }}">{{ column }}</option>
                      {% endfor %}
                    </select>
                    
                    <div id="filter_values_${newFilterIndex}" class="mt-3 row">
                        <!-- Checkboxes for Filter Values will be inserted here -->
                    </div>
                `;
                filtersDiv.appendChild(filterGroup);
                filterCount++;
            }

            function filterData() {
                const formData = new FormData(document.getElementById("filter-form"));
                const filters = {};

                for (let i = 0; i < filterCount; i++) {
                    const column = formData.get(`column_${i}`);
                    const values = formData.getAll(`filter_value_${i}`);
                    if (column && values.length > 0) {
                        filters[column] = values;
                    }
                }

                let filteredData = data;

                // Lọc dữ liệu dựa trên các cột đã chọn
                for (const [column, values] of Object.entries(filters)) {
                    filteredData = Object.keys(filteredData).reduce((result, key) => {
                        result[key] = filteredData[key].filter((_, index) => values.includes(filteredData[column][index]));
                        return result;
                    }, {});
                }

                // Lọc dữ liệu dựa trên ngày
                const startDate = formData.get("start_date");
                const endDate = formData.get("end_date");

                if (startDate || endDate) {
                    const dateColumn = Object.keys(filteredData).find(key => key.toLowerCase().includes("ngày") || key.toLowerCase().includes("date"));

                    if (dateColumn) {
                        filteredData = Object.keys(filteredData).reduce((result, key) => {
                            result[key] = filteredData[key].filter((_, index) => {
                                const dateValue = new Date(filteredData[dateColumn][index]);
                                const isValidStartDate = startDate ? dateValue >= new Date(startDate) : true;
                                const isValidEndDate = endDate ? dateValue <= new Date(endDate) : true;
                                return isValidStartDate && isValidEndDate;
                            });
                            return result;
                        }, {});
                    }
                }

                renderFilteredDataTable(filteredData);
            }

            function resetFilter() {
                // Reset all filters to initial state
                document.getElementById("filters").innerHTML = `
                    <div class="filter-group mb-3">
                        <label for="column_0">Choose a column to filter:</label>
                        <select class="column form-control" name="column_0" onchange="updateFilterValues(0)" required>
                          <option value="" selected disabled>-- Select Column --</option>
                          {% for column in columns %}
                            <option value="{{ column }}">{{ column }}</option>
                          {% endfor %}
                        </select>
                        
                        <div id="filter_values_0" class="mt-3 row">
                            <!-- Checkboxes for Filter Values will be inserted here -->
                        </div>
                    </div>
                `;
                filterCount = 1;

                // Reset date filters
                document.querySelector('input[name="start_date"]').value = '';
                document.querySelector('input[name="end_date"]').value = '';

                renderFilteredDataTable(data);
            }

            function renderFilteredDataTable(filteredData) {
                const tableDiv = document.getElementById("filtered-data");
                if (Object.keys(filteredData).length === 0) {
                    tableDiv.innerHTML = "<p>No data available</p>";
                    return;
                }

                let tableHtml = '<table class="table table-bordered table-striped"><thead class="thead-dark"><tr>';
                for (const column of {{ columns | tojson }}) {
                    tableHtml += `<th>${column}</th>`;
                }
                tableHtml += '</tr></thead><tbody>';

                const rowCount = filteredData[Object.keys(filteredData)[0]].length;
                for (let i = 0; i < rowCount; i++) {
                    tableHtml += '<tr>';
                    for (const column of {{ columns | tojson }}) {
                        tableHtml += `<td>${filteredData[column][i]}</td>`;
                    }
                    tableHtml += '</tr>';
                }

                tableHtml += '</tbody></table>';
                tableDiv.innerHTML = tableHtml;
            }
        </script>
    </body>
    </html>
    ''', file_path=file_path, sheet_name=sheet_name, header_row=header_row, columns=columns, data_json=data_json)

# Route xử lý lọc và tải xuống dữ liệu đã lọc
@filter_bp.route('/filter_data', methods=['POST'])
def filter_data():
    file_path = request.form['file_path']
    sheet_name = request.form['sheet_name']
    header_row = int(request.form['header_row'])

    # Đọc dữ liệu từ sheet với hàng làm tiêu đề
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

    # Áp dụng các bộ lọc
    filters = {}
    for key, value in request.form.items():
        if key.startswith("column_") and value:
            index = key.split("_")[1]
            filter_values = request.form.getlist(f"filter_value_{index}")
            if filter_values:
                filters[value] = filter_values

    for column, filter_values in filters.items():
        df = df[df[column].isin(filter_values)]

    # Lọc dữ liệu dựa trên ngày
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if start_date or end_date:
        date_columns = [col for col in df.columns if 'ngày' in col.lower() or 'date' in col.lower()]
        if date_columns:
            date_column = date_columns[0]  # Lấy cột có chứa ngày
            if pd.api.types.is_datetime64_any_dtype(df[date_column]):
                if start_date:
                    df = df[df[date_column] >= pd.to_datetime(start_date)]
                if end_date:
                    df = df[df[date_column] <= pd.to_datetime(end_date)]

    # Lưu kết quả vào file mới
    filtered_file_path = os.path.join(UPLOAD_FOLDER, 'filtered_data.xlsx')
    df.to_excel(filtered_file_path, index=False)

    return send_file(filtered_file_path, as_attachment=True)
