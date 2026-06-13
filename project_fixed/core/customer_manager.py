"""
core/customer_manager.py
Tầng xử lý nghiệp vụ: Quản lý khách hàng.

Lớp CustomerManager chịu trách nhiệm toàn bộ logic liên quan đến khách hàng:
- Tải, thêm, sửa, xóa khách hàng trong SQLite
- Đồng bộ dữ liệu ra file text JSON sau mỗi thao tác
- Áp dụng thuật toán Linear Search để kiểm tra trùng mã và tìm kiếm
"""

from typing import List, Optional
from models import Customer
from utils.db_utils import load_data, save_data, update_data, delete_data
from utils.validation import validate_required_field, validate_string_length
from database.database import initialize_database
from utils.file_storage import sync_from_db, append_record, update_record, delete_record


class CustomerManager:
    """
    Quản lý toàn bộ thao tác CRUD với khách hàng.

    Thuộc tính:
        customers (List[Customer]): Danh sách khách hàng trong bộ nhớ,
                                    được tải lại từ SQLite sau mỗi thay đổi.
    """

    def __init__(self):
        """
        Khởi tạo CustomerManager.
        - Đảm bảo DB đã tồn tại.
        - Tải toàn bộ khách hàng vào self.customers.
        """
        self.customers: List[Customer] = []
        initialize_database()   # Tạo DB/bảng nếu chưa có
        self.load_customers()   # Nạp dữ liệu vào bộ nhớ

    # TẢI DỮ LIỆU

    def load_customers(self) -> tuple[bool, str]:
        """
        Tải toàn bộ khách hàng từ SQLite vào self.customers.

        Sau khi tải xong, đồng bộ kết quả ra file text JSON (customers.json).

        Trả về:
            (True, thông báo) nếu thành công.
            (False, lỗi)      nếu thất bại.
        """
        self.customers = []
        rows, error = load_data("customers")   # SELECT * FROM customers
        if error:
            return False, error
        if rows:
            # Chuyển từng dict thành đối tượng Customer
            self.customers = [Customer(**row) for row in rows]
        # Đồng bộ sang file text JSON
        sync_from_db("customers", rows if rows else [])
        return True, f"Đã tải {len(self.customers)} khách hàng."

    # THUẬT TOÁN CÀI ĐẶT: TÌM KIẾM TUYẾN TÍNH (LINEAR SEARCH)

    def linear_search(self, customer_id: str) -> int:
        """
        Thuật toán Tìm kiếm tuyến tính (Linear Search).

        Duyệt tuần tự từ đầu đến cuối danh sách self.customers,
        so sánh từng phần tử với customer_id cần tìm.

        Tham số:
            customer_id (str): Mã khách hàng cần tìm (đã upper).

        Trả về:
            int: Chỉ số (index) nếu tìm thấy.
                 -1 nếu không tìm thấy.

        Độ phức tạp thời gian: O(n)
        Độ phức tạp không gian: O(1)
        """
        for i in range(len(self.customers)):                      # Duyệt từ đầu đến cuối
            if self.customers[i].customer_id == customer_id:
                return i                                          # Tìm thấy → trả về vị trí
        return -1                                                 # Không tìm thấy → trả về -1

    def find_customer(self, customer_id: str) -> Optional[Customer]:
        """
        Tìm khách hàng theo mã ID, sử dụng Linear Search.

        Tham số:
            customer_id (str): Mã khách hàng cần tìm.

        Trả về:
            Customer nếu tìm thấy, None nếu không.
        """
        index = self.linear_search(customer_id.upper())   # Chuẩn hóa và tìm kiếm
        return self.customers[index] if index != -1 else None

    # THÊM KHÁCH HÀNG

    def add_customer(self, customer_id: str, name: str,
                     phone: str = "", address: str = "") -> tuple[bool, str]:
        """
        Thêm khách hàng mới vào hệ thống.

        Quy trình:
        1. Xác thực mã và tên khách hàng.
        2. Dùng Linear Search kiểm tra mã đã tồn tại chưa.
        3. INSERT vào SQLite.
        4. Ghi bổ sung vào file JSON.

        Tham số:
            customer_id : Mã khách hàng (sẽ được chuyển thành chữ hoa).
            name        : Họ tên khách hàng (2–50 ký tự).
            phone       : Số điện thoại (tùy chọn).
            address     : Địa chỉ (tùy chọn).

        Trả về:
            (True, thông báo) hoặc (False, lỗi).
        """
        # Bước 1: Xác thực dữ liệu
        valid, error = validate_required_field(customer_id, "Mã khách hàng")
        if not valid:
            return False, error
        valid, error = validate_required_field(name, "Tên khách hàng")
        if not valid:
            return False, error
        valid, error = validate_string_length(name, "Tên khách hàng", 2, 50)
        if not valid:
            return False, error

        cid = customer_id.strip().upper()   # Chuẩn hóa mã khách hàng

        # Bước 2: Kiểm tra trùng mã bằng Linear Search
        if self.find_customer(cid):
            return False, f"Mã khách hàng '{cid}' đã tồn tại!"

        # Bước 3: INSERT vào SQLite
        success, error = save_data("customers", {
            "customer_id": cid,
            "name": name.strip(),
            "phone": phone.strip(),
            "address": address.strip(),
        })
        if success:
            # Bước 4: Ghi bổ sung vào file JSON
            append_record("customers", {
                "customer_id": cid, "name": name.strip(),
                "phone": phone.strip(), "address": address.strip()
            })
            self.load_customers()
            return True, f"Đã thêm khách hàng '{name}' thành công!"
        return False, error

    # CẬP NHẬT KHÁCH HÀNG

    def update_customer(self, customer_id: str, name: str = None,
                        phone: str = None, address: str = None) -> tuple[bool, str]:
        """
        Cập nhật thông tin khách hàng (không đổi mã ID).

        Quy trình:
        1. Kiểm tra khách hàng tồn tại (Linear Search).
        2. Xác thực tên nếu được cập nhật.
        3. UPDATE trong SQLite.
        4. Cập nhật bản ghi trong file JSON.

        Tham số:
            customer_id : Mã khách hàng cần cập nhật.
            name        : Tên mới (tùy chọn).
            phone       : SĐT mới (tùy chọn).
            address     : Địa chỉ mới (tùy chọn).

        Trả về:
            (True, thông báo) hoặc (False, lỗi).
        """
        cid = customer_id.strip().upper()

        # Bước 1: Kiểm tra tồn tại
        if not self.find_customer(cid):
            return False, f"Không tìm thấy khách hàng '{cid}'!"

        # Xây dựng dict các trường cần cập nhật
        data = {}
        if name is not None:
            valid, error = validate_string_length(name, "Tên khách hàng", 2, 50)
            if not valid:
                return False, error
            data["name"] = name.strip()
        if phone is not None:
            data["phone"] = phone.strip()
        if address is not None:
            data["address"] = address.strip()

        if not data:
            return True, "Không có thông tin nào được cập nhật."

        # Bước 3: UPDATE trong SQLite
        success, error = update_data("customers", data, {"customer_id": cid})
        if success:
            # Bước 4: Cập nhật trong file JSON
            update_record("customers", "customer_id", cid, data)
            self.load_customers()
            return True, f"Đã cập nhật khách hàng '{cid}' thành công!"
        return False, error

    # XÓA KHÁCH HÀNG

    def delete_customer(self, customer_id: str) -> tuple[bool, str]:
        """
        Xóa khách hàng khỏi hệ thống.

        Quy trình:
        1. Kiểm tra khách hàng tồn tại (Linear Search).
        2. DELETE khỏi SQLite.
        3. Xóa bản ghi khỏi file JSON.

        Tham số:
            customer_id: Mã khách hàng cần xóa.

        Trả về:
            (True, thông báo) hoặc (False, lỗi).
        """
        cid = customer_id.strip().upper()

        # Bước 1: Kiểm tra tồn tại
        if not self.find_customer(cid):
            return False, f"Không tìm thấy khách hàng '{cid}'!"

        # Bước 2: DELETE khỏi SQLite
        success, error = delete_data("customers", {"customer_id": cid})
        if success:
            # Bước 3: Xóa khỏi file JSON
            delete_record("customers", "customer_id", cid)
            self.load_customers()
            return True, f"Đã xóa khách hàng '{cid}' thành công!"
        return False, error
