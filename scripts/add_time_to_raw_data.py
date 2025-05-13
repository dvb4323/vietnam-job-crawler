import os
import json
from datetime import datetime

# Đường dẫn thư mục raw_data (chỉnh theo vị trí thực tế của bạn)
RAW_DIR = os.path.join(os.path.dirname(__file__), '../raw_data')

file_count = 0
updated_count = 0

for filename in os.listdir(RAW_DIR):
    if not filename.endswith('.json'):
        continue

    file_path = os.path.join(RAW_DIR, filename)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_count += 1

        # Nếu đã có trường 'created_at' thì bỏ qua
        if 'created_at' in data:
            continue

        # Lấy ngày tạo file từ hệ thống
        try:
            created_timestamp = os.path.getmtime(file_path)
            created_at = datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d')
        except Exception:
            created_at = datetime.now().strftime('%Y-%m-%d')

        # Thêm vào JSON
        data['created_at'] = created_at

        # Ghi đè lại file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        updated_count += 1

    except Exception as e:
        print(f"[Lỗi] File {filename}: {e}")

print(f"Đã xử lý {file_count} file. Đã thêm 'created_at' cho {updated_count} file.")
