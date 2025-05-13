import os
import json

# Cấu hình
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "training_data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "requirements_data.jsonl")
MAX_FILES = 1000

# Đảm bảo thư mục output tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)

count = 0  # Đếm số file đã xử lý

with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    for filename in os.listdir(RAW_DIR):
        if count >= MAX_FILES:
            break  # Dừng lại nếu đã đủ 1000 file

        if filename.endswith(".json"):
            file_path = os.path.join(RAW_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    data = json.load(infile)

                    # Dữ liệu là một object (1 job)
                    if isinstance(data, dict):
                        requirements = data.get("requirements", "").strip()
                        if requirements:
                            json_line = {"text": requirements, "labels": []}
                            outfile.write(json.dumps(json_line, ensure_ascii=False) + "\n")
                            count += 1

                    # Dữ liệu là một list (nhiều job trong 1 file)
                    elif isinstance(data, list):
                        for job in data:
                            if count >= MAX_FILES:
                                break
                            requirements = job.get("requirements", "").strip()
                            if requirements:
                                json_line = {"text": requirements, "labels": []}
                                outfile.write(json.dumps(json_line, ensure_ascii=False) + "\n")
                                count += 1

            except Exception as e:
                print(f"⚠️ Lỗi đọc {file_path}: {e}")

print(f"✅ Hoàn tất: Đã xử lý {count} mẫu. Dữ liệu lưu tại: {OUTPUT_FILE}")
