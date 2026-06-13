"""
core/product_manager.py
Tầng xử lý nghiệp vụ: Quản lý sản phẩm.

Lớp ProductManager chịu trách nhiệm toàn bộ logic liên quan đến sản phẩm:
- Tải, thêm, sửa, xóa sản phẩm trong SQLite
- Đồng bộ dữ liệu ra file text JSON sau mỗi thao tác
- Áp dụng thuật toán Linear Search để kiểm tra trùng mã và tìm kiếm
"""

from typing import List, Optional

from models import Product
from utils.db_utils import load_data, save_data, update_data, delete_data
from utils.validation import (
    validate_required_field,
    validate_positive_number,
    validate_product_id,
    validate_string_length
)
from utils.formatting import format_product_id
from database.database import initialize_database
from utils.file_storage import sync_from_db, append_record, update_record, delete_record


class ProductManager:
    """
    Quản lý toàn bộ thao tác CRUD với sản phẩm.

    Thuộc tính:
        products (List[Product]): Danh sách sản phẩm đang giữ trong bộ nhớ,
                                  được tải từ SQLite mỗi khi có thay đổi.
    """

    def __init__(self):
        """
        Khởi tạo ProductManager.
        - Gọi initialize_database() để đảm bảo DB và bảng đã tồn tại.
        - Tải toàn bộ sản phẩm vào self.products.
        """
        self.products: List[Product] = []
        initialize_database()   # Tạo DB/bảng nếu chưa có
        self.load_products()    # Nạp dữ liệu vào bộ nhớ

    # TẢI DỮ LIỆU

    def load_products(self) -> tuple[bool, str]:
        """
        Tải toàn bộ sản phẩm từ SQLite vào self.products.

        Sau khi tải xong, đồng bộ kết quả ra file text JSON (products.json)
        để đảm bảo file luôn phản ánh trạng thái mới nhất của DB.

        Trả về:
            (True, thông báo) nếu thành công.
            (False, lỗi)      nếu thất bại.
        """
        self.products = []
        rows, error = load_data("products")   # SELECT * FROM products
        if error:
            return False, error
        if rows:
            # Chuyển từng dict thành đối tượng Product
            self.products = [Product(**row) for row in rows]
        # Đồng bộ sang file text JSON để lưu trữ song song
        sync_from_db("products", rows if rows else [])
        return True, f"Đã tải {len(self.products)} sản phẩm từ database."

    # THUẬT TOÁN CÀI ĐẶT: TÌM KIẾM TUYẾN TÍNH (LINEAR SEARCH)

    def linear_search(self, product_id: str) -> int:
        """
        Thuật toán Tìm kiếm tuyến tính (Linear Search).

        Duyệt tuần tự qua danh sách self.products từ đầu đến cuối,
        so sánh từng phần tử với product_id cần tìm.

        Tham số:
            product_id (str): Mã sản phẩm cần tìm (đã chuẩn hóa).

        Trả về:
            int: Chỉ số (index) của sản phẩm nếu tìm thấy.
                 -1 nếu không tìm thấy.

        Độ phức tạp thời gian: O(n)
        Độ phức tạp không gian: O(1)
        """
        for i in range(len(self.products)):              # Duyệt từ đầu đến cuối
            if self.products[i].product_id == product_id:
                return i                                 # Tìm thấy → trả về vị trí
        return -1                                        # Duyệt hết mà không thấy → trả về -1

    def find_product(self, product_id: str) -> Optional[Product]:
        """
        Tìm sản phẩm theo mã ID, sử dụng Linear Search.

        Tham số:
            product_id (str): Mã sản phẩm cần tìm.

        Trả về:
            Product nếu tìm thấy, None nếu không.
        """
        product_id = format_product_id(product_id)   # Chuẩn hóa: strip + upper
        index = self.linear_search(product_id)        # Gọi Linear Search
        if index != -1:
            return self.products[index]               # Trả về sản phẩm tại vị trí index
        return None

    # THÊM SẢN PHẨM

    def add_product(self, product_id: str, name: str, unit_price: float,
                    calculation_unit: str = "đơn vị", category: str = "Chung") -> tuple[bool, str]:
        """
        Thêm sản phẩm mới vào hệ thống.

        Quy trình:
        1. Xác thực dữ liệu đầu vào (mã, tên, đơn giá).
        2. Dùng Linear Search kiểm tra mã đã tồn tại chưa.
        3. INSERT vào SQLite.
        4. Ghi bản ghi mới vào file JSON.
        5. Reload danh sách.

        Tham số:
            product_id       : Mã sản phẩm (chỉ chữ hoa và số, 3–10 ký tự).
            name             : Tên sản phẩm (2–50 ký tự).
            unit_price       : Đơn giá (phải > 0).
            calculation_unit : Đơn vị tính (mặc định: "đơn vị").
            category         : Danh mục (mặc định: "Chung").

        Trả về:
            (True, thông báo thành công) hoặc (False, thông báo lỗi).
        """
        # Bước 1: Xác thực dữ liệu đầu vào
        valid, error = validate_product_id(product_id)
        if not valid:
            return False, error
        valid, error = validate_required_field(name, "Tên sản phẩm")
        if not valid:
            return False, error
        valid, error = validate_string_length(name, "Tên sản phẩm", 2, 50)
        if not valid:
            return False, error
        valid, error = validate_positive_number(unit_price, "Đơn giá")  # Kiểm tra đơn giá > 0
        if not valid:
            return False, error

        # Bước 2: Kiểm tra trùng mã bằng Linear Search
        if self.find_product(product_id):
            return False, f"Sản phẩm với Mã '{product_id}' đã tồn tại!"

        product_id = format_product_id(product_id)   # Chuẩn hóa mã

        # Bước 3: INSERT vào SQLite
        success, error = save_data("products", {
            "product_id": product_id,
            "name": name,
            "unit_price": unit_price,
            "calculation_unit": calculation_unit,
            "category": category
        })

        if success:
            # Bước 4: Ghi bổ sung vào file text JSON
            append_record("products", {
                "product_id": product_id, "name": name,
                "unit_price": unit_price, "calculation_unit": calculation_unit,
                "category": category
            })
            # Bước 5: Reload danh sách trong bộ nhớ
            self.load_products()
            return True, f"Đã thêm sản phẩm '{name}' thành công!"
        return False, error

    # CẬP NHẬT SẢN PHẨM

    def update_product(self, product_id: str, name: Optional[str] = None,
                       unit_price: Optional[float] = None, calculation_unit: Optional[str] = None,
                       category: Optional[str] = None) -> tuple[bool, str]:
        """
        Cập nhật thông tin sản phẩm (không đổi mã ID).

        Quy trình:
        1. Dùng Linear Search kiểm tra sản phẩm có tồn tại không.
        2. Xác thực các trường được cập nhật.
        3. UPDATE trong SQLite.
        4. Cập nhật bản ghi tương ứng trong file JSON.

        Tham số:
            product_id       : Mã sản phẩm cần cập nhật.
            name             : Tên mới (tùy chọn).
            unit_price       : Đơn giá mới (tùy chọn, phải > 0).
            calculation_unit : Đơn vị tính mới (tùy chọn).
            category         : Danh mục mới (tùy chọn).

        Trả về:
            (True, thông báo thành công) hoặc (False, thông báo lỗi).
        """
        product_id = format_product_id(product_id)

        # Bước 1: Kiểm tra sản phẩm tồn tại (dùng Linear Search qua find_product)
        if not self.find_product(product_id):
            return False, f"Không tìm thấy sản phẩm với Mã '{product_id}'!"

        # Bước 2: Xác thực các trường cần cập nhật
        if name is not None:
            valid, error = validate_string_length(name, "Tên sản phẩm", 2, 50)
            if not valid:
                return False, error
        if unit_price is not None:
            valid, error = validate_positive_number(unit_price, "Đơn giá")
            if not valid:
                return False, error

        # Xây dựng dict chứa các trường cần cập nhật
        update_data_dict = {}
        if name is not None:             update_data_dict["name"] = name
        if unit_price is not None:       update_data_dict["unit_price"] = unit_price
        if calculation_unit is not None: update_data_dict["calculation_unit"] = calculation_unit
        if category is not None:         update_data_dict["category"] = category

        if not update_data_dict:
            return True, "Không có thông tin nào được cung cấp để cập nhật."

        # Bước 3: UPDATE trong SQLite
        success, error = update_data("products", update_data_dict, {"product_id": product_id})

        if success:
            # Bước 4: Cập nhật bản ghi trong file JSON
            update_record("products", "product_id", product_id, update_data_dict)
            self.load_products()
            return True, f"Đã cập nhật sản phẩm '{product_id}' thành công!"
        return False, error

    # XÓA SẢN PHẨM
    def delete_product(self, product_id: str) -> tuple[bool, str]:
        """
        Xóa sản phẩm khỏi hệ thống.

        Quy trình:
        1. Kiểm tra sản phẩm tồn tại (Linear Search).
        2. DELETE khỏi SQLite.
        3. Xóa bản ghi khỏi file JSON.

        Tham số:
            product_id: Mã sản phẩm cần xóa.

        Trả về:
            (True, thông báo) hoặc (False, lỗi).
        """
        product_id = format_product_id(product_id)

        # Bước 1: Kiểm tra tồn tại
        if not self.find_product(product_id):
            return False, f"Không tìm thấy sản phẩm với Mã '{product_id}'!"

        # Bước 2: DELETE khỏi SQLite
        success, error = delete_data("products", {"product_id": product_id})

        if success:
            # Bước 3: Xóa khỏi file JSON
            delete_record("products", "product_id", product_id)
            self.load_products()
            return True, f"Đã xóa sản phẩm '{product_id}' thành công!"
        return False, error

    # HIỂN THỊ (CLI)
    def list_products(self) -> None:
        """Hiển thị danh sách sản phẩm dạng bảng ra console (dùng cho CLI)."""
        if not self.products:
            print("Danh sách sản phẩm trống!")
            return
        print("\n" + "="*80)
        print(f"{'MÃ SP':<10} {'TÊN SẢN PHẨM':<30} {'ĐƠN VỊ':<10} {'DANH MỤC':<15} {'ĐƠN GIÁ':>10}")
        print("-"*80)
        for product in self.products:
            print(f"{product.product_id:<10} {product.name:<30} {product.calculation_unit:<10} "
                  f"{product.category:<15} {product.unit_price:>10,.2f}")
        print("="*80)
        print(f"Tổng số: {len(self.products)} sản phẩm")
        print("="*80)
