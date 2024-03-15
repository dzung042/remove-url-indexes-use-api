# hướng dẫn xoá index sử dụng google api
Cài thư viện cần thiết
```pre
cd remove-url-indexes-use-api
pip install -r requirements.txt
```
- Khai thông tin các url vào file abc_com.csv trong phần action_status chọn Unactioned các url để trạng thái này sẽ được xoá
- Khai thông tin các các phần cấu hình trong file "googleUnixdexer.py" gồm JSON_KEY_FILE đường dẫn tới file API google đã tải về, "filename"  tên file chứa danh sách các url cần xoá
