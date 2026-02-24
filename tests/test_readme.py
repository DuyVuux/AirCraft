import os
import unittest
import re

class TestREADME(unittest.TestCase):
    def setUp(self):
        self.readme_path = "/home/duykhongngu28/massive/aircraft/AirCraftPort/README.md"
        self.project_root = "/home/duykhongngu28/massive/aircraft/AirCraftPort"

    def test_readme_exists(self):
        """Kiểm tra tệp README.md có tồn tại không."""
        self.assertTrue(os.path.exists(self.readme_path), "README.md không tồn tại.")

    def test_links_and_paths(self):
        """Kiểm tra các đường dẫn tương đối trong README có hợp lệ không."""
        with open(self.readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tìm tất cả các đường dẫn tương đối kiểu [name](./path)
        links = re.findall(r'\[.*?\]\(((\./|\.\./|/)[^\)]+)\)', content)
        
        for link, prefix in links:
            # Bỏ qua các liên kết external (http/https đã được lọc bởi regex trên nhưng kiểm tra lại cho chắc)
            if link.startswith('http'):
                continue
            
            # Giải quyết đường dẫn tuyệt đối để kiểm tra
            full_path = os.path.abspath(os.path.join(self.project_root, link.replace('./', '')))
            
            # Một số link có thể dẫn đến anchor (#), bỏ qua phần anchor
            base_path = full_path.split('#')[0]
            
            if base_path:
                self.assertTrue(os.path.exists(base_path), f"Đường dẫn không hợp lệ trong README: {link} (Base: {base_path})")

    def test_required_sections(self):
        """Kiểm tra xem README có đủ các phần quan trọng không."""
        required_headers = [
            "# ✈️ AirCraftPort",
            "## 🏗️ Kiến trúc hệ thống",
            "## ✨ Tính năng chính",
            "## 🚀 Cài đặt nhanh",
            "## 📁 Cấu trúc thư mục",
            "## 🧪 Kiểm thử",
            "## 📄 Giấy phép"
        ]
        
        with open(self.readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for header in required_headers:
            self.assertIn(header, content, f"Thiếu phần tiêu đề: {header}")

if __name__ == "__main__":
    unittest.main()
