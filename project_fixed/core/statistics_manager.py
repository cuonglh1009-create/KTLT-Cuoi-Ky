"""
Quản lý thống kê và báo cáo cho Hệ thống Quản lý Hóa đơn.

Module này cung cấp các chức năng phân tích và tạo báo cáo từ dữ liệu
hóa đơn và sản phẩm, bao gồm thống kê doanh thu, sản phẩm bán chạy
và khách hàng thân thiết. Tất cả báo cáo được xuất ra console
với định dạng bảng dễ đọc.
"""

from collections import defaultdict
from typing import Dict, List, Tuple
from .invoice_manager import InvoiceManager
from .product_manager import ProductManager

class StatisticsManager:
    """
    Quản lý các thao tác thống kê và báo cáo trong Hệ thống Quản lý Hóa đơn.
    
    Lớp này cung cấp các chức năng phân tích và báo cáo bao gồm:
    - Thống kê doanh thu theo ngày
    - Thống kê doanh thu theo sản phẩm
    - Xếp hạng khách hàng thân thiết
    
    Thuộc tính:
        invoice_manager (InvoiceManager): Trình quản lý hóa đơn
        product_manager (ProductManager): Trình quản lý sản phẩm
        
    Ghi chú:
        Tất cả các phương thức thống kê in kết quả trực tiếp ra console
        và không trả về dữ liệu. Điều này thiết kế cho việc sử dụng
        trong giao diện dòng lệnh và giao diện đồ họa.
    """
    
    def __init__(self, invoice_manager: InvoiceManager, product_manager: ProductManager):
        """
        Khởi tạo trình quản lý thống kê.
        
        Tham số:
            invoice_manager (InvoiceManager): Trình quản lý hóa đơn để truy cập
                                              dữ liệu hóa đơn và các mặt hàng.
            product_manager (ProductManager): Trình quản lý sản phẩm để lấy
                                              thông tin chi tiết sản phẩm.
        
        Ném ra:
            TypeError: Nếu các tham số không đúng kiểu
        """
        self.invoice_manager = invoice_manager
        self.product_manager = product_manager
    
    def revenue_by_date(self) -> None:
        """
        Hiển thị báo cáo doanh thu theo từng ngày.
        
        Phân tích tất cả hóa đơn và tính tổng doanh thu cho mỗi ngày,
        sau đó hiển thị dưới dạng bảng được sắp xếp theo
        thời gian (mới nhất trước).
        
        Trả về:
            None: Kết quả được in trực tiếp ra console
            
        Ghi chú:
            - Nếu không có hóa đơn nào, hiển thị thông báo
            - Sử dụng định dạng tiền tệ việt nam
        """
        if not self.invoice_manager.invoices:
            print("Không có dữ liệu hóa đơn để thống kê!")
            return
        
        # Nhóm doanh thu theo ngày
        date_revenue: Dict[str, float] = defaultdict(float)
        for invoice in self.invoice_manager.invoices:
            date_revenue[invoice.date] += invoice.total_amount

        if not date_revenue:
            print("Không có dữ liệu doanh thu để hiển thị!")
            return

        # Sắp xếp theo ngày (mới nhất trước)
        sorted_dates = sorted(date_revenue.items(), reverse=True)

        # Hiển thị báo cáo
        print("\n" + "="*60)
        print("THỐNG KÊ DOANH THU THEO NGÀY")
        print("="*60)
        print(f"{'NGÀY':<15} {'DOANH THU':<20} {'TỈ LỆ':<10}")
        print("-"*60)
        
        total_revenue = sum(date_revenue.values())
        for date, revenue in sorted_dates:
            percentage = (revenue / total_revenue) * 100 if total_revenue > 0 else 0
            print(f"{date:<15} {revenue:>20,.2f} {percentage:>9.2f}%")
        
        print("-"*60)
        print(f"{'TỔNG CỘNG:':<15} {total_revenue:>20,.2f}")
        print("="*60)
    
    def revenue_by_product(self) -> None:
        """
        Hiển thị báo cáo doanh thu chi tiết theo từng sản phẩm.
        
        Phân tích tất cả hóa đơn và tính toán:
        - Tổng doanh thu của mỗi sản phẩm
        - Tổng số lượng bán ra của mỗi sản phẩm
        - Tỷ lệ phần trăm đóng góp vào tổng doanh thu
        
        Kết quả được sắp xếp theo doanh thu giảm dần.
        
        Trả về:
            None: Kết quả được in trực tiếp ra console
            
        Ghi chú:
            - Nếu sản phẩm đã bị xóa, hiển thị "[Sản phẩm không tồn tại]"
            - Sử dụng định dạng tiền tệ việt nam
        """
        if not self.invoice_manager.invoices:
            print("Không có dữ liệu hóa đơn để thống kê!")
            return
        
        # Tính toán doanh thu và số lượng theo sản phẩm
        product_stats: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
        for invoice in self.invoice_manager.invoices:
            for item in invoice.items:
                current_revenue, current_quantity = product_stats[item.product_id]
                product_stats[item.product_id] = (
                    current_revenue + item.total_price,
                    current_quantity + item.quantity
                )

        if not product_stats:
            print("Không có dữ liệu doanh thu theo sản phẩm để hiển thị!")
            return

        # Sắp xếp theo doanh thu (cao nhất trước)
        sorted_products = sorted(
            product_stats.items(),
            key=lambda x: x[1][0],
            reverse=True
        )
        
        # Hiển thị báo cáo
        print("\n" + "="*80)
        print("THỐNG KÊ DOANH THU THEO SẢN PHẨM")
        print("="*80)
        print(f"{'MÃ SP':<10} {'TÊN SẢN PHẨM':<30} {'SỐ LƯỢNG':<10} {'DOANH THU':<15} {'TỈ LỆ':<10}")
        print("-"*80)
        
        total_revenue = sum(revenue for revenue, _ in product_stats.values())
        for product_id, (revenue, quantity) in sorted_products:
            product = self.product_manager.find_product(product_id)
            product_name = product.name if product else "[Sản phẩm không tồn tại]"
            percentage = (revenue / total_revenue) * 100 if total_revenue > 0 else 0
            print(f"{product_id:<10} {product_name:<30} {quantity:>10} {revenue:>15,.2f} {percentage:>9.2f}%")
        
        print("-"*80)
        print(f"{'TỔNG CỘNG:':<50} {total_revenue:>15,.2f}")
        print("="*80)
    
    def top_customers(self, limit: int = 5) -> None:
        """
        Hiển thị báo cáo khách hàng thân thiết (chi tiêu nhiều nhất).
        
        Phân tích tất cả hóa đơn và tính tổng số tiền mà mỗi khách hàng
        đã chi tiêu, sau đó hiển thị danh sách khách hàng hàng đầu
        cùng với tỷ lệ đóng góp của họ.
        
        Tham số:
            limit (int): Số lượng khách hàng hàng đầu cần hiển thị.
                        Mặc định là 5. Phải là số dương.
        
        Trả về:
            None: Kết quả được in trực tiếp ra console
            
        Ghi chú:
            - Kết quả được sắp xếp theo tổng chi tiêu giảm dần
            - Hiển thị tỷ lệ phần trăm so với tổng doanh thu
            - Nếu không có dữ liệu, hiển thị thông báo tương ứng
        """
        if not self.invoice_manager.invoices:
            print("Không có dữ liệu hóa đơn để thống kê!")
            return
        
        # Tính toán chi tiêu theo khách hàng
        customer_spending: Dict[str, float] = defaultdict(float)
        for invoice in self.invoice_manager.invoices:
            customer_spending[invoice.customer_name] += invoice.total_amount

        if not customer_spending:
            print("Không có dữ liệu khách hàng để hiển thị!")
            return

        # Sắp xếp theo chi tiêu (cao nhất trước) và giới hạn kết quả
        sorted_customers = sorted(
            customer_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Hiển thị báo cáo
        print("\n" + "="*60)
        print(f"TOP {limit} KHÁCH HÀNG TIỀM NĂNG")
        print("="*60)
        print(f"{'KHÁCH HÀNG':<30} {'TỔNG CHI TIÊU':<20} {'TỈ LỆ':<10}")
        print("-"*60)
        
        total_spending = sum(customer_spending.values())
        for customer_name, spending in sorted_customers:
            percentage = (spending / total_spending) * 100 if total_spending > 0 else 0
            print(f"{customer_name:<30} {spending:>20,.2f} {percentage:>9.2f}%")
        
        print("-"*60)
        print(f"{'TỔNG CỘNG:':<30} {total_spending:>20,.2f}")
        print("="*60) 