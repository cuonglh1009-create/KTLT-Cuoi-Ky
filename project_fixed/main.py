"""
Điểm vào chính cho Hệ thống Quản lý Hóa đơn.

Chạy file này để khởi động ứng dụng:
    python main.py
"""

import sys
import os

# Đảm bảo Python tìm đúng các module trong cùng thư mục
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.gui import start_gui

def main():
    """
    Điểm vào chính cho Hệ thống Quản lý Hóa đơn.
    Khởi tạo và bắt đầu giao diện người dùng đồ họa.
    """
    try:
        start_gui()
    except Exception as e:
        print(f"Lỗi khi khởi động ứng dụng: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
