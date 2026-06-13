#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/db_utils.py
Các hàm tiện ích thao tác trực tiếp với SQLite.

Module này cung cấp 4 hàm CRUD cơ bản dùng chung cho toàn bộ project:
    save_data()   — INSERT một bản ghi vào bảng
    load_data()   — SELECT nhiều bản ghi từ bảng (có thể lọc theo điều kiện)
    update_data() — UPDATE bản ghi theo điều kiện
    delete_data() — DELETE bản ghi theo điều kiện

Tất cả hàm đều:
- Tự mở và đóng kết nối sau mỗi lần gọi (không giữ kết nối liên tục)
- Dùng try/finally để đảm bảo connection luôn được đóng, tránh "database is locked"
- Trả về tuple (bool/list, str) để báo kết quả và lỗi
- Xử lý ngoại lệ sqlite3.Error an toàn
"""

import sqlite3
import os
from typing import Any, List, Dict, Optional, Tuple
from database.database import DATABASE_PATH


def ensure_database_exists() -> Tuple[bool, str]:
    """
    Kiểm tra thư mục chứa DB tồn tại, tạo mới nếu chưa có.

    Trả về:
        (True, "") nếu OK.
        (False, lỗi) nếu không tạo được thư mục.
    """
    try:
        db_dir = os.path.dirname(DATABASE_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        return True, ""
    except (OSError, IOError) as e:
        return False, f"Lỗi khi kiểm tra database: {e}"


def save_data(table: str, data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Chèn một bản ghi mới vào bảng (INSERT).

    Tự động xây dựng câu lệnh SQL từ dict đầu vào:
        INSERT INTO <table> (col1, col2, ...) VALUES (?, ?, ...)

    Tham số:
        table : Tên bảng đích.
        data  : Dict {tên_cột: giá_trị} cần chèn.

    Trả về:
        (True, "") nếu thành công.
        (False, lỗi) nếu thất bại.
    """
    db_ok, db_error = ensure_database_exists()
    if not db_ok:
        return False, db_error
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")  # Giảm thiểu database lock
        cursor = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        return True, ""
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"Lỗi khi lưu dữ liệu vào bảng {table}: {e}"
    finally:
        if conn:
            conn.close()  # Luôn đóng connection dù thành công hay lỗi


def load_data(table: str, conditions: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], str]:
    """
    Tải dữ liệu từ bảng (SELECT).

    Nếu conditions được truyền vào, thêm mệnh đề WHERE:
        SELECT * FROM <table> WHERE col1=? AND col2=? ...

    Dùng conn.row_factory = sqlite3.Row để có thể truy cập
    kết quả theo tên cột (dict-like).

    Tham số:
        table      : Tên bảng cần đọc.
        conditions : Dict {tên_cột: giá_trị} làm điều kiện lọc (tùy chọn).

    Trả về:
        (list[dict], "") nếu thành công.
        ([], lỗi)        nếu thất bại.
    """
    db_ok, db_error = ensure_database_exists()
    if not db_ok:
        return [], db_error
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = f"SELECT * FROM {table}"
        params = []
        if conditions:
            where_clauses = [f"{key} = ?" for key in conditions.keys()]
            params = list(conditions.values())
            query += " WHERE " + " AND ".join(where_clauses)
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results, ""
    except sqlite3.Error as e:
        return [], f"Lỗi khi tải dữ liệu từ bảng {table}: {e}"
    finally:
        if conn:
            conn.close()


def update_data(table: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Cập nhật bản ghi trong bảng (UPDATE).

    Xây dựng câu lệnh:
        UPDATE <table> SET col1=?, col2=? WHERE cond1=? AND cond2=?

    Tham số:
        table      : Tên bảng.
        data       : Dict {tên_cột: giá_trị_mới} cần cập nhật.
        conditions : Dict {tên_cột: giá_trị} làm điều kiện WHERE.

    Trả về:
        (True, "") nếu thành công.
        (False, lỗi) nếu thất bại.
    """
    db_ok, db_error = ensure_database_exists()
    if not db_ok:
        return False, db_error
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        set_clauses   = [f"{key} = ?" for key in data.keys()]
        where_clauses = [f"{key} = ?" for key in conditions.keys()]
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        params = list(data.values()) + list(conditions.values())
        cursor.execute(query, params)
        conn.commit()
        return True, ""
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"Lỗi khi cập nhật dữ liệu trong bảng {table}: {e}"
    finally:
        if conn:
            conn.close()


def delete_data(table: str, conditions: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Xóa bản ghi khỏi bảng (DELETE).

    Xây dựng câu lệnh:
        DELETE FROM <table> WHERE cond1=? AND cond2=?

    Tham số:
        table      : Tên bảng.
        conditions : Dict {tên_cột: giá_trị} làm điều kiện WHERE.

    Trả về:
        (True, "") nếu thành công.
        (False, lỗi) nếu thất bại.
    """
    db_ok, db_error = ensure_database_exists()
    if not db_ok:
        return False, db_error
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        where_clauses = [f"{key} = ?" for key in conditions.keys()]
        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        cursor.execute(query, list(conditions.values()))
        conn.commit()
        return True, ""
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"Lỗi khi xóa dữ liệu từ bảng {table}: {e}"
    finally:
        if conn:
            conn.close()
