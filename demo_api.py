import requests

# 1. REST API 地址
url = "http://127.0.0.1:8000/api/tasks"

# 2. 发送 GET 请求
response = requests.get(url)

# 3. 查看状态码
print(response.status_code)

# 4. 查看返回的数据
print(response.json())