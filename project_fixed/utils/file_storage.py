#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/file_storage.py
Lưu trữ dữ liệu vào/đọc dữ liệu từ file text dạng JSON.

Mỗi bảng dữ liệu tương ứng một file .json trong thư mục data/:
    data/products.json
    data/customers.json
    data/invoices.json
    data/invoice_items.json

Module này hoạt động SONG SONG với SQLite:
- Mọi thao tác ghi (thêm/sửa/xóa) đều cập nhật cả DB lẫn file JSON.
- File JSON dùng để kiểm tra, backup, hoặc đọc lại khi cần.
"""

import json
import os
from typing import Any

# Thư mục chứa các file text
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _get_file_path(table: str) -> str:
    """Trả về đường dẫn file JSON tương ứng với tên bảng."""
    return os.path.join(DATA_DIR, f"{table}.json")


def _ensure_data_dir():
    """Tạo thư mục data/ nếu chưa tồn tại."""
    os.makedirs(DATA_DIR, exist_ok=True)


# ================================================================== #
# ĐỌC / GHI FILE JSON
# ================================================================== #

def read_all(table: str) -> list[dict]:
    """
    Đọc toàn bộ dữ liệu từ file text JSON của một bảng.

    Tham số:
        table: Tên bảng (products / customers / invoices / invoice_items)

    Trả về:
        Danh sách các bản ghi dạng dict. Trả về [] nếu file chưa tồn tại.
    """
    path = _get_file_path(table)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def write_all(table: str, records: list[dict]) -> bool:
    """
    Ghi toàn bộ danh sách bản ghi vào file text JSON (ghi đè).

    Tham số:
        table   : Tên bảng.
        records : Danh sách dict cần lưu.

    Trả về:
        True nếu thành công, False nếu lỗi.
    """
    _ensure_data_dir()
    path = _get_file_path(table)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def append_record(table: str, record: dict) -> bool:
    """
    Thêm một bản ghi vào cuối file JSON.

    Tham số:
        table  : Tên bảng.
        record : Bản ghi mới dạng dict.

    Trả về:
        True nếu thành công.
    """
    records = read_all(table)
    records.append(record)
    return write_all(table, records)


def update_record(table: str, key_field: str, key_value: Any, new_data: dict) -> bool:
    """
    Cập nhật bản ghi trong file JSON theo khóa chính.

    Tham số:
        table     : Tên bảng.
        key_field : Tên trường khóa (vd: 'product_id').
        key_value : Giá trị khóa cần tìm.
        new_data  : Dict chứa các trường cần cập nhật.

    Trả về:
        True nếu tìm thấy và cập nhật thành công.
    """
    records = read_all(table)
    updated = False
    for record in records:
        if record.get(key_field) == key_value:
            record.update(new_data)
            updated = True
            break
    if updated:
        return write_all(table, records)
    return False


def delete_record(table: str, key_field: str, key_value: Any) -> bool:
    """
    Xóa bản ghi khỏi file JSON theo khóa chính.

    Tham số:
        table     : Tên bảng.
        key_field : Tên trường khóa.
        key_value : Giá trị khóa cần xóa.

    Trả về:
        True nếu xóa thành công.
    """
    records = read_all(table)
    new_records = [r for r in records if r.get(key_field) != key_value]
    if len(new_records) < len(records):
        return write_all(table, new_records)
    return False


def sync_from_db(table: str, rows: list[dict]) -> bool:
    """
    Đồng bộ toàn bộ dữ liệu từ DB vào file JSON.
    Gọi hàm này sau mỗi lần load_data từ SQLite để giữ file text nhất quán.

    Tham số:
        table : Tên bảng.
        rows  : Danh sách dict từ SQLite (kết quả của load_data).

    Trả về:
        True nếu ghi thành công.
    """
    return write_all(table, rows)
