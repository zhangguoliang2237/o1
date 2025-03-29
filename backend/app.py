from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 获取CSV文件路径
csv_path = os.path.join(os.path.dirname(__file__), '../data/stock_600519_20200101_20250326.csv')

# 读取CSV数据
df = pd.read_csv(csv_path)

@app.route('/api/data', methods=['GET'])
def get_data():
    # 返回所有数据
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/data/<column>/<value>', methods=['GET'])
def filter_data(column, value):
    # 根据列名和值过滤数据
    try:
        filtered = df[df[column].astype(str) == value]
        return jsonify(filtered.to_dict(orient='records'))
    except KeyError:
        return jsonify({'error': 'Invalid column name'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)