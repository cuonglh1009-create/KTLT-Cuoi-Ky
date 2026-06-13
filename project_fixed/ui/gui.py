"""
Giao diện đồ họa (GUI) cho Hệ thống Quản lý Hóa đơn, sử dụng Tkinter.

Module này cung cấp giao diện đồ họa chính của ứng dụng, bao gồm:
- Lớp InvoiceAppGUI: Giao diện chính với tabs cho sản phẩm, hóa đơn và thống kê
- Chức năng quản lý sản phẩm: thêm, sửa, xóa, hiển thị danh sách
- Chức năng quản lý hóa đơn: tạo mới, xem chi tiết, xóa
- Chức năng thống kê: doanh thu, sản phẩm bán chạy, khách hàng VIP
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import io
import sys
from collections import defaultdict

from core.product_manager import ProductManager
from core.customer_manager import CustomerManager
from core.invoice_manager import InvoiceManager
from core.statistics_manager import StatisticsManager

class InvoiceAppGUI:
    """
    Lớp giao diện đồ họa chính cho ứng dụng quản lý hóa đơn.
    
    Lớp này tạo và quản lý giao diện người dùng với các tab khác nhau
    để quản lý sản phẩm, hóa đơn và xem thống kê.
    
    Thuộc tính:
        root: Cửa sổ gốc Tkinter
        product_manager: Đối tượng quản lý sản phẩm
        invoice_manager: Đối tượng quản lý hóa đơn
        statistics_manager: Đối tượng quản lý thống kê
    """
    
    def __init__(self, root):
        """
        Khởi tạo giao diện ứng dụng quản lý hóa đơn.
        
        Tham số:
            root: Cửa sổ gốc Tkinter
            
        Ném ra:
            Exception: Nếu không thể khởi tạo các trình quản lý
        """
        self.root = root
        self.root.title("Hệ thống Quản lý Hóa đơn")
        self.root.geometry("900x700")

        try:
            # Khởi tạo các trình quản lý
            self.product_manager = ProductManager()
            self.customer_manager = CustomerManager()
            self.invoice_manager = InvoiceManager(self.product_manager)
            self.statistics_manager = StatisticsManager(self.invoice_manager, self.product_manager)
        except Exception as e:
            messagebox.showerror("Lỗi khởi tạo", f"Không thể khởi tạo trình quản lý: {str(e)}")
            self.root.destroy()
            return

        # Tạo Notebook (giao diện tab)
        self.notebook = ttk.Notebook(root)
        self.product_tab = ttk.Frame(self.notebook)
        self.customer_tab = ttk.Frame(self.notebook)
        self.invoice_tab = ttk.Frame(self.notebook)
        self.statistics_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.product_tab, text='Quản lý Sản phẩm')
        self.notebook.add(self.customer_tab, text='Quản lý Khách hàng')
        self.notebook.add(self.invoice_tab, text='Quản lý Hóa đơn')
        self.notebook.add(self.statistics_tab, text='Thống kê')
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Điền nội dung cho mỗi tab
        self._create_product_tab()
        self._create_customer_tab()
        self._create_invoice_tab()
        self._create_statistics_tab()

    def _create_product_tab(self):
        """
        Tạo tab quản lý sản phẩm với danh sách và các chức năng CRUD.
        
        Tab này bao gồm:
        - Treeview hiển thị danh sách sản phẩm
        - Các nút thêm, sửa, xóa sản phẩm
        - Chức năng tải lại dữ liệu
        
        Trả về:
            None
        """
        # Frame chứa danh sách sản phẩm
        list_frame = ttk.LabelFrame(self.product_tab, text="Danh sách sản phẩm")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview để hiển thị sản phẩm
        columns = ("ID", "Tên", "Đơn giá", "Đơn vị tính", "Danh mục")
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        self.product_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame chứa các nút
        button_frame = ttk.Frame(self.product_tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Tải lại", command=self.load_products).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Thêm", command=self.add_product_dialog).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_product_dialog).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_product).pack(side="left", padx=5)
        
        # Tải dữ liệu ban đầu
        self.load_products()

    def load_products(self):
        """Tải lại danh sách sản phẩm từ manager và cập nhật Treeview."""
        try:
            success, message = self.product_manager.load_products()
            if not success:
                messagebox.showerror("Lỗi", f"Không thể tải danh sách sản phẩm: {message}")
                return

            # Xóa dữ liệu cũ
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)

            # Hiển thị dữ liệu mới
            for product in self.product_manager.products:
                self.product_tree.insert("", "end", values=(
                    product.product_id,
                    product.name,
                    f"{product.unit_price:,.0f}",
                    product.calculation_unit,
                    product.category
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sản phẩm: {str(e)}")

    def add_product_dialog(self):
        """
        Hiển thị hộp thoại để thêm sản phẩm mới.
        
        Tạo một cửa sổ popup với các trường nhập liệu để người dùng
        nhập thông tin sản phẩm mới. Sau khi xác thực, sản phẩm sẽ
        được thêm vào database.
        
        Trả về:
            None
        
        Ném ra:
            ValueError: Nếu đơn giá không hợp lệ
            Exception: Nếu không thể thêm sản phẩm
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Thêm sản phẩm mới")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        input_frame = ttk.Frame(dialog, padding=10)
        input_frame.pack(fill="both", expand=True)
        
        fields = ["Mã sản phẩm", "Tên sản phẩm", "Đơn giá", "Đơn vị tính", "Danh mục"]
        entries = {}
        for i, field in enumerate(fields):
            ttk.Label(input_frame, text=f"{field}:", font=("Cambria", 12)).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(input_frame, width=30, font=("Cambria", 12))
            entry.grid(row=i, column=1, pady=5)
            entries[field] = entry

        entries["Đơn vị tính"].insert(0, "cái")
        entries["Danh mục"].insert(0, "Chung")

        def on_add():
            try:
                price_str = entries["Đơn giá"].get().strip()
                price = float(price_str) if price_str else 0.0

                success, message = self.product_manager.add_product(
                    product_id=entries["Mã sản phẩm"].get().strip(),
                    name=entries["Tên sản phẩm"].get().strip(),
                    unit_price=price,
                    calculation_unit=entries["Đơn vị tính"].get().strip(),
                    category=entries["Danh mục"].get().strip()
                )
                if success:
                    messagebox.showinfo("Thành công", message)
                    self.load_products()
                    dialog.destroy()
                else:
                    messagebox.showerror("Lỗi", message)
            except ValueError:
                messagebox.showerror("Lỗi", "Đơn giá phải là một con số.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm sản phẩm: {str(e)}")
        
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Thêm", command=on_add).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Hủy", command=dialog.destroy).pack(side="right", padx=5)

    def update_product_dialog(self):
        """
        Hiển thị hộp thoại để cập nhật thông tin sản phẩm đã chọn.
        
        Kiểm tra xem có sản phẩm nào được chọn không, sau đó hiển thị
        cửa sổ popup với thông tin hiện tại để người dùng chỉnh sửa.
        
        Trả về:
            None
        
        Ném ra:
            ValueError: Nếu đơn giá không hợp lệ
            Exception: Nếu không thể cập nhật sản phẩm
        """
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một sản phẩm để cập nhật.")
            return
        
        product_id = self.product_tree.item(selected[0], "values")[0]
        product = self.product_manager.find_product(product_id)
        if not product:
            messagebox.showerror("Lỗi", f"Không tìm thấy sản phẩm với mã {product_id}.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Cập nhật sản phẩm - {product_id}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        input_frame = ttk.Frame(dialog, padding=10)
        input_frame.pack(fill="both", expand=True)
        
        fields = {"Tên sản phẩm": product.name, "Đơn giá": str(product.unit_price), 
                  "Đơn vị tính": product.calculation_unit, "Danh mục": product.category}
        entries = {}
        for i, (field, value) in enumerate(fields.items()):
            ttk.Label(input_frame, text=f"{field}:", font=("Cambria", 12)).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(input_frame, width=30, font=("Cambria", 12))
            entry.grid(row=i, column=1, pady=5)
            entry.insert(0, value)
            entries[field] = entry

        def on_update():
            try:
                price_str = entries["Đơn giá"].get().strip()
                price = float(price_str) if price_str else product.unit_price

                success, message = self.product_manager.update_product(
                    product_id=product_id,
                    name=entries["Tên sản phẩm"].get().strip(),
                    unit_price=price,
                    calculation_unit=entries["Đơn vị tính"].get().strip(),
                    category=entries["Danh mục"].get().strip()
                )
                if success:
                    messagebox.showinfo("Thành công", message)
                    self.load_products()
                    dialog.destroy()
                else:
                    messagebox.showerror("Lỗi", message)
            except ValueError:
                messagebox.showerror("Lỗi", "Đơn giá phải là một con số.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật sản phẩm: {str(e)}")
        
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Cập nhật", command=on_update).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Hủy", command=dialog.destroy).pack(side="right", padx=5)

    def delete_product(self):
        """
        Xóa sản phẩm đã chọn sau khi xác nhận với người dùng.
        
        Kiểm tra xem có sản phẩm nào được chọn không, sau đó hiển thị
        hộp thoại xác nhận trước khi xóa sản phẩm khỏi database.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không thể xóa sản phẩm
        """
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một sản phẩm để xóa.")
            return
        
        product_id = self.product_tree.item(selected[0], "values")[0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa sản phẩm '{product_id}'? Hành động này không thể hoàn tác."):
            try:
                success, message = self.product_manager.delete_product(product_id)
                if success:
                    messagebox.showinfo("Thành công", message)
                    self.load_products()
                else:
                    messagebox.showerror("Lỗi", message)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa sản phẩm: {str(e)}")


    def _create_customer_tab(self):
        """Tạo tab Quản lý Khách hàng."""
        list_frame = ttk.LabelFrame(self.customer_tab, text="Danh sách khách hàng")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Tên", "Điện thoại", "Địa chỉ")
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        col_widths = {"ID": 80, "Tên": 180, "Điện thoại": 110, "Địa chỉ": 160}
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=col_widths.get(col, 120))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.customer_tree.pack(fill="both", expand=True)

        button_frame = ttk.Frame(self.customer_tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(button_frame, text="Tải lại",  command=self.load_customers).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Thêm",     command=self.add_customer_dialog).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_customer_dialog).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xóa",      command=self.delete_customer).pack(side="left", padx=5)

        self.load_customers()

    def load_customers(self):
        """Tải danh sách khách hàng lên Treeview."""
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        self.customer_manager.load_customers()
        for c in self.customer_manager.customers:
            self.customer_tree.insert("", "end", iid=c.customer_id, values=(
                c.customer_id, c.name, c.phone, c.address
            ))

    def _get_selected_customer(self):
        """Lấy khách hàng đang chọn trong Treeview."""
        sel = self.customer_tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một khách hàng.")
            return None
        return self.customer_manager.find_customer(sel[0])

    def add_customer_dialog(self):
        """Pop-up thêm khách hàng mới."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Thêm khách hàng")
        dialog.geometry("380x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        fields = [("Mã KH *:", "id"), ("Họ tên *:", "name"),
                  ("Điện thoại:", "phone"), ("Địa chỉ:", "address")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=4, padx=(0,10))
            e = ttk.Entry(frame, width=28)
            e.grid(row=i, column=1, sticky="ew", pady=4)
            entries[key] = e

        def on_add():
            success, msg = self.customer_manager.add_customer(
                entries["id"].get(), entries["name"].get(),
                entries["phone"].get(), entries["address"].get()
            )
            if success:
                messagebox.showinfo("Thành công", msg, parent=dialog)
                self.load_customers()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=dialog)

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Thêm", command=on_add).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Hủy",  command=dialog.destroy).pack(side="left", padx=6)

    def update_customer_dialog(self):
        """Pop-up cập nhật khách hàng."""
        c = self._get_selected_customer()
        if not c:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Cập nhật khách hàng")
        dialog.geometry("380x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        fields = [("Mã KH:", "id"), ("Họ tên *:", "name"),
                  ("Điện thoại:", "phone"), ("Địa chỉ:", "address")]
        entries = {}
        values = {"id": c.customer_id, "name": c.name, "phone": c.phone,
                  "address": c.address}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=4, padx=(0,10))
            e = ttk.Entry(frame, width=28)
            e.insert(0, values[key])
            if key == "id":
                e.config(state="disabled")
            e.grid(row=i, column=1, sticky="ew", pady=4)
            entries[key] = e

        def on_update():
            success, msg = self.customer_manager.update_customer(
                c.customer_id, entries["name"].get(),
                entries["phone"].get(), entries["address"].get()
            )
            if success:
                messagebox.showinfo("Thành công", msg, parent=dialog)
                self.load_customers()
                dialog.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=dialog)

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Cập nhật", command=on_update).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Hủy",      command=dialog.destroy).pack(side="left", padx=6)

    def delete_customer(self):
        """Xóa khách hàng đã chọn."""
        c = self._get_selected_customer()
        if not c:
            return
        if messagebox.askyesno("Xác nhận", f"Xóa khách hàng '{c.name}'?"):
            success, msg = self.customer_manager.delete_customer(c.customer_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_customers()
            else:
                messagebox.showerror("Lỗi", msg)

    def _create_invoice_tab(self):
        """
        Tạo tab quản lý hóa đơn với danh sách và các chức năng quản lý.
        
        Tab này bao gồm:
        - Treeview hiển thị danh sách hóa đơn
        - Các nút xem chi tiết, tạo mới, xóa hóa đơn
        - Chức năng tải lại dữ liệu
        
        Trả về:
            None
        """
        list_frame = ttk.LabelFrame(self.invoice_tab, text="Danh sách hóa đơn")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("ID", "Khách hàng", "Ngày", "Tổng tiền", "Số mặt hàng")
        self.invoice_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=120)
        self.invoice_tree.column("ID", width=50, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        self.invoice_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(self.invoice_tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Tải lại", command=self.load_invoices).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xem chi tiết", command=self.view_invoice_details).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Tạo hóa đơn", command=self.create_new_invoice).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xóa hóa đơn", command=self.delete_invoice).pack(side="left", padx=5)
        
        self.load_invoices()

    def load_invoices(self):
        """Tải lại danh sách hóa đơn từ manager và cập nhật Treeview."""
        try:
            success, message = self.invoice_manager.load_invoices()
            if not success:
                messagebox.showerror("Lỗi", f"Không thể tải danh sách hóa đơn: {message}")
                return

            for item in self.invoice_tree.get_children():
                self.invoice_tree.delete(item)

            for invoice in self.invoice_manager.invoices:
                self.invoice_tree.insert("", "end", values=(
                    invoice.invoice_id,
                    invoice.customer_name,
                    invoice.date,
                    f"{invoice.total_amount:,.0f}",
                    invoice.total_items
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách hóa đơn: {str(e)}")

    def view_invoice_details(self):
        """
        Hiển thị chi tiết hóa đơn đã chọn trong cửa sổ mới.
        
        Kiểm tra xem có hóa đơn nào được chọn không, sau đó tạo
        cửa sổ popup hiển thị thông tin chi tiết của hóa đơn bao gồm
        thông tin khách hàng và danh sách các mặt hàng.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không tìm thấy hóa đơn
        """
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một hóa đơn để xem chi tiết.")
            return
        
        invoice_id = self.invoice_tree.item(selected[0], "values")[0]
        invoice = self.invoice_manager.find_invoice(invoice_id)
        if not invoice:
            messagebox.showerror("Lỗi", f"Không tìm thấy hóa đơn #{invoice_id}.")
            return
            
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Chi tiết hóa đơn #{invoice_id}")
        detail_window.geometry("800x600")
        detail_window.transient(self.root)
        
        info_frame = ttk.LabelFrame(detail_window, text="Thông tin hóa đơn")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Mã hóa đơn: {invoice.invoice_id}", font=("Cambria", 11)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(info_frame, text=f"Ngày: {invoice.date}", font=("Cambria", 11)).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        ttk.Label(info_frame, text=f"Khách hàng: {invoice.customer_name}", font=("Cambria", 11)).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        items_frame = ttk.LabelFrame(detail_window, text="Danh sách mặt hàng")
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("STT", "Mã SP", "Tên", "Số lượng", "Đơn giá", "Thành tiền")
        items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        
        for col in columns:
            items_tree.heading(col, text=col)
        
        items_tree.column("STT", width=40, anchor='center')
        items_tree.column("Mã SP", width=100)
        items_tree.column("Tên", width=250)
        
        for idx, item in enumerate(invoice.items, 1):
            product = self.product_manager.find_product(item.product_id)
            product_name = product.name if product else "[Sản phẩm không tồn tại]"
            items_tree.insert("", "end", values=(
                idx, item.product_id, product_name, item.quantity,
                f"{item.unit_price:,.0f}", f"{item.total_price:,.0f}"
            ))
        
        items_tree.pack(fill='both', expand=True)
        
        summary_frame = ttk.Frame(detail_window)
        summary_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(summary_frame, text=f"Tổng tiền: {invoice.total_amount:,.0f} VND", font=("Cambria", 12, "bold")).pack(side="right")
        
        ttk.Button(detail_window, text="Đóng", command=detail_window.destroy).pack(pady=10)

    def delete_invoice(self):
        """Xóa hóa đơn đã chọn sau khi xác nhận."""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một hóa đơn để xóa.")
            return

        # Lấy thông tin hóa đơn được chọn
        invoice_id = self.invoice_tree.item(selected[0], "values")[0]
        invoice = self.invoice_manager.find_invoice(invoice_id)
        if not invoice:
            messagebox.showerror("Lỗi", f"Không tìm thấy hóa đơn #{invoice_id}.")
            return

        # Xác nhận xóa với thông tin chi tiết
        confirm_message = (
            f"Bạn có chắc chắn muốn xóa hóa đơn này?\n\n"
            f"Mã hóa đơn: #{invoice.invoice_id}\n"
            f"Khách hàng: {invoice.customer_name}\n"
            f"Ngày: {invoice.date}\n"
            f"Tổng tiền: {invoice.total_amount:,.0f} VND\n"
            f"Số mặt hàng: {invoice.total_items}\n\n"
            f"⚠️ Hành động này không thể hoàn tác!"
        )

        result = messagebox.askyesno(
            "Xác nhận xóa hóa đơn",
            confirm_message,
            icon='warning'
        )

        if result:
            try:
                success, message = self.invoice_manager.delete_invoice(invoice_id)
                if success:
                    messagebox.showinfo("Thành công", message)
                    self.load_invoices()  # Tải lại danh sách hóa đơn
                else:
                    messagebox.showerror("Lỗi", message)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa hóa đơn: {str(e)}")

    def create_new_invoice(self):
        """
        Hiển thị hộp thoại để tạo hóa đơn mới.
        
        Tạo cửa sổ popup phức tạp cho phép người dùng:
        - Nhập thông tin khách hàng
        - Chọn sản phẩm và số lượng
        - Xem tổng tiền tạm tính
        - Tạo hóa đơn mới
        
        Trả về:
            None
        
        Ném ra:
            ValueError: Nếu số lượng không hợp lệ
            Exception: Nếu không thể tạo hóa đơn
        """
        if not self.product_manager.products:
            messagebox.showinfo("Thông báo", "Không có sản phẩm nào. Vui lòng thêm sản phẩm trước.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Tạo hóa đơn mới")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # --- Phần thông tin khách hàng ---
        info_frame = ttk.LabelFrame(dialog, text="Thông tin hóa đơn")
        info_frame.pack(fill="x", padx=10, pady=5, side='top')
        
        ttk.Label(info_frame, text="Khách hàng:", font=("Cambria", 12)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(info_frame, textvariable=customer_var, width=38,
                                      state="readonly", font=("Cambria", 12))
        customer_combo["values"] = [c.display_name() for c in self.customer_manager.customers]
        customer_combo.grid(row=0, column=1, pady=5, padx=5)
        
        # --- Phần mặt hàng ---
        items_container_frame = ttk.Frame(dialog)
        items_container_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Frame chứa danh sách các mặt hàng đã thêm
        items_frame = ttk.LabelFrame(items_container_frame, text="Mặt hàng đã thêm")
        items_frame.pack(fill="both", expand=True, side="top", pady=(0, 5))
        
        current_items = []
        columns = ("Mã SP", "Tên", "Số lượng", "Đơn giá", "Thành tiền")
        items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        for col in columns:
            items_tree.heading(col, text=col)
        items_tree.pack(side="left", fill="both", expand=True)
        
        # --- Phần thêm/xóa mặt hàng ---
        add_item_frame = ttk.LabelFrame(items_container_frame, text="Thao tác")
        add_item_frame.pack(fill="x", side="bottom", pady=(5, 0))

        # Dropdown chọn sản phẩm
        ttk.Label(add_item_frame, text="Sản phẩm:", font=("Cambria", 12)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(add_item_frame, textvariable=product_var, width=35, state="readonly", font=("Cambria", 12))
        product_combo['values'] = [f"{p.product_id} - {p.name}" for p in self.product_manager.products]
        product_combo.grid(row=0, column=1, padx=5, pady=5)

        # Ô nhập số lượng
        ttk.Label(add_item_frame, text="Số lượng:", font=("Cambria", 12)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        quantity_entry = tk.Entry(add_item_frame, width=10, font=("Cambria", 12))
        quantity_entry.grid(row=0, column=3, padx=5, pady=5)
        quantity_entry.insert(0, "1")
        
        total_label = ttk.Label(dialog, text="Tổng tiền: 0 VND", font=("Cambria", 12, "bold"))
        
        def update_items_list():
            for i in items_tree.get_children():
                items_tree.delete(i)
            total_amount = 0
            for item_data in current_items:
                product = self.product_manager.find_product(item_data['product_id'])
                if product:
                    total_price = item_data['quantity'] * product.unit_price
                    total_amount += total_price
                    items_tree.insert("", "end", values=(
                        product.product_id, product.name, item_data['quantity'],
                        f"{product.unit_price:,.0f}", f"{total_price:,.0f}"
                    ))
            total_label.config(text=f"Tổng tiền: {total_amount:,.0f} VND")

        def add_item():
            if not product_var.get(): return
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0: return
                product_id = product_var.get().split(" - ")[0]

                existing_item = next((item for item in current_items if item['product_id'] == product_id), None)
                if existing_item:
                    existing_item['quantity'] += quantity
                else:
                    current_items.append({'product_id': product_id, 'quantity': quantity})
                update_items_list()
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng phải là số nguyên.")
        
        def remove_item():
            selected = items_tree.selection()
            if not selected: return
            product_id = items_tree.item(selected[0], "values")[0]
            current_items[:] = [item for item in current_items if item['product_id'] != product_id]
            update_items_list()

        # Nút thêm và xóa
        button_container = ttk.Frame(add_item_frame)
        button_container.grid(row=0, column=4, padx=10, pady=5)

        ttk.Button(button_container, text="Thêm", command=add_item).pack(side="left", padx=2)
        ttk.Button(button_container, text="Xóa", command=remove_item).pack(side="left", padx=2)

        # Đảm bảo các cột có thể mở rộng
        add_item_frame.grid_columnconfigure(1, weight=1)

        total_label.pack(pady=10, side='top')

        # --- Phần nút cuối cùng ---
        def on_create():
            selected = customer_var.get()
            if not selected:
                messagebox.showinfo("Thông báo", "Vui lòng chọn khách hàng.")
                return
            customer_id = selected.split(" - ")[0]
            customer = self.customer_manager.find_customer(customer_id)
            customer_name = customer.name if customer else selected
            if not current_items:
                messagebox.showinfo("Thông báo", "Hóa đơn phải có ít nhất một mặt hàng.")
                return
            
            try:
                new_invoice, message = self.invoice_manager.create_invoice(customer_id=customer_id, customer_name=customer_name, items_data=current_items)
                if new_invoice:
                    messagebox.showinfo("Thành công", message)
                    self.load_invoices()
                    dialog.destroy()
                else:
                    messagebox.showerror("Lỗi", message)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo hóa đơn: {str(e)}")

        button_frame = ttk.Frame(dialog)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        ttk.Button(button_frame, text="Tạo hóa đơn", command=on_create).pack(side="left")
        ttk.Button(button_frame, text="Hủy", command=dialog.destroy).pack(side="right")
        
    def _create_statistics_tab(self):
        """
        Tạo tab thống kê với các loại báo cáo khác nhau.
        
        Tab này bao gồm:
        - Sub-tab doanh thu (theo sản phẩm, theo thời gian)
        - Sub-tab sản phẩm (bán chạy nhất, phân loại)
        - Sub-tab khách hàng (khách hàng thân thiết)
        
        Trả về:
            None
        """
        # Tạo các frame cho các loại thống kê
        stats_notebook = ttk.Notebook(self.statistics_tab)
        stats_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tạo các tab thống kê
        revenue_tab = ttk.Frame(stats_notebook)
        product_tab = ttk.Frame(stats_notebook)
        customer_tab = ttk.Frame(stats_notebook)
        
        # Thêm các tab vào notebook
        stats_notebook.add(revenue_tab, text="Doanh thu")
        stats_notebook.add(product_tab, text="Sản phẩm")
        stats_notebook.add(customer_tab, text="Khách hàng")
        
        # Tab Doanh thu
        revenue_frame = ttk.LabelFrame(revenue_tab, text="Thống kê doanh thu")
        revenue_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tạo các nút chức năng cho thống kê doanh thu
        revenue_buttons = ttk.Frame(revenue_frame)
        revenue_buttons.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(revenue_buttons, text="Doanh thu theo sản phẩm", 
                  command=self.show_revenue_by_product).pack(side="left", padx=5)
        
        ttk.Button(revenue_buttons, text="Doanh thu theo thời gian", 
                  command=self.show_revenue_by_time).pack(side="left", padx=5)
        
        # Khu vực hiển thị kết quả thống kê doanh thu
        self.revenue_result = tk.Text(revenue_frame, height=20, width=80, font=("Cambria", 12))
        self.revenue_result.pack(fill="both", expand=True, padx=5, pady=5)
        self.revenue_result.insert("1.0", "Chọn loại thống kê doanh thu để xem kết quả")
        self.revenue_result.config(state="disabled")
        
        # Tab Sản phẩm
        product_frame = ttk.LabelFrame(product_tab, text="Thống kê sản phẩm")
        product_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tạo các nút chức năng cho thống kê sản phẩm
        product_buttons = ttk.Frame(product_frame)
        product_buttons.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(product_buttons, text="Sản phẩm bán chạy nhất", 
                  command=self.show_top_products).pack(side="left", padx=5)
        
        ttk.Button(product_buttons, text="Phân loại sản phẩm", 
                  command=self.show_product_categories).pack(side="left", padx=5)
        
        # Khu vực hiển thị kết quả thống kê sản phẩm
        self.product_result = tk.Text(product_frame, height=20, width=80, font=("Cambria", 12))
        self.product_result.pack(fill="both", expand=True, padx=5, pady=5)
        self.product_result.insert("1.0", "Chọn loại thống kê sản phẩm để xem kết quả")
        self.product_result.config(state="disabled")
        
        # Tab Khách hàng
        customer_frame = ttk.LabelFrame(customer_tab, text="Thống kê khách hàng")
        customer_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tạo các nút chức năng cho thống kê khách hàng
        customer_buttons = ttk.Frame(customer_frame)
        customer_buttons.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(customer_buttons, text="Khách hàng thân thiết", 
                  command=self.show_top_customers).pack(side="left", padx=5)
        
        # Khu vực hiển thị kết quả thống kê khách hàng
        self.customer_result = tk.Text(customer_frame, height=20, width=80, font=("Cambria", 12))
        self.customer_result.pack(fill="both", expand=True, padx=5, pady=5)
        self.customer_result.insert("1.0", "Chọn loại thống kê khách hàng để xem kết quả")
        self.customer_result.config(state="disabled")

    def show_revenue_by_product(self):
        """
        Hiển thị thống kê doanh thu theo từng sản phẩm.
        
        Thu thập dữ liệu từ statistics_manager và hiển thị trong
        khu vực văn bản của tab doanh thu. Sử dụng chuyển hướng
        stdout để bắt output từ hàm thống kê.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không thể tạo báo cáo thống kê
        """
        try:
            if self.statistics_manager is None:
                messagebox.showwarning("Cảnh báo", "Trình quản lý thống kê chưa được khởi tạo")
                return
            
            # Kiểm tra xem có hóa đơn nào không
            if not self.invoice_manager or not self.invoice_manager.invoices:
                messagebox.showinfo("Thông báo", "Không có dữ liệu hóa đơn để thống kê!")
                return
                
            # Thông báo đang xử lý
            self.revenue_result.config(state="normal")
            self.revenue_result.delete("1.0", tk.END)
            self.revenue_result.insert("1.0", "Đang xử lý dữ liệu...")
            self.revenue_result.config(state="disabled")
            self.root.update()  # Cập nhật giao diện để hiển thị thông báo
            
            # Chuyển hướng stdout để bắt kết quả in ra
            old_stdout = sys.stdout
            result = io.StringIO()
            sys.stdout = result
            
            # Gọi phương thức thống kê
            self.statistics_manager.revenue_by_product()
            
            # Khôi phục stdout và lấy kết quả
            sys.stdout = old_stdout
            output = result.getvalue()
            
            # Hiển thị kết quả trong tab Doanh thu
            self.revenue_result.config(state="normal")
            self.revenue_result.delete("1.0", tk.END)
            self.revenue_result.insert("1.0", output)
            self.revenue_result.config(state="disabled")
            
            if not output.strip():
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để hiển thị!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị thống kê doanh thu theo sản phẩm: {str(e)}")

    def show_revenue_by_time(self):
        """
        Hiển thị thống kê doanh thu theo thời gian.
        
        Thu thập dữ liệu từ statistics_manager và hiển thị trong
        khu vực văn bản của tab doanh thu. Sử dụng chuyển hướng
        stdout để bắt output từ hàm thống kê.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không thể tạo báo cáo thống kê
        """
        try:
            if self.statistics_manager is None:
                messagebox.showwarning("Cảnh báo", "Trình quản lý thống kê chưa được khởi tạo")
                return
            
            # Kiểm tra xem có hóa đơn nào không
            if not self.invoice_manager or not self.invoice_manager.invoices:
                messagebox.showinfo("Thông báo", "Không có dữ liệu hóa đơn để thống kê!")
                return
                
            # Thông báo đang xử lý
            self.revenue_result.config(state="normal")
            self.revenue_result.delete("1.0", tk.END)
            self.revenue_result.insert("1.0", "Đang xử lý dữ liệu...")
            self.revenue_result.config(state="disabled")
            self.root.update()  # Cập nhật giao diện để hiển thị thông báo
            
            # Chuyển hướng stdout để bắt kết quả in ra
            old_stdout = sys.stdout
            result = io.StringIO()
            sys.stdout = result
            
            # Gọi phương thức thống kê
            self.statistics_manager.revenue_by_date()
            
            # Khôi phục stdout và lấy kết quả
            sys.stdout = old_stdout
            output = result.getvalue()
            
            # Hiển thị kết quả
            self.revenue_result.config(state="normal")
            self.revenue_result.delete("1.0", tk.END)
            self.revenue_result.insert("1.0", output)
            self.revenue_result.config(state="disabled")
            
            if not output.strip():
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để hiển thị!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị thống kê doanh thu theo thời gian: {str(e)}")

    def show_top_products(self):
        """
        Hiển thị thống kê các sản phẩm bán chạy nhất.
        
        Tính toán số lượng bán ra của từng sản phẩm dựa trên dữ liệu
        hóa đơn, sắp xếp theo thứ tự giảm dần và hiển thị báo cáo.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không thể tạo báo cáo thống kê
        """
        try:
            if self.statistics_manager is None:
                messagebox.showwarning("Cảnh báo", "Trình quản lý thống kê chưa được khởi tạo")
                return
            
            # Kiểm tra xem có hóa đơn nào không
            if not self.invoice_manager or not self.invoice_manager.invoices:
                messagebox.showinfo("Thông báo", "Không có dữ liệu hóa đơn để thống kê!")
                return
            
            # Thông báo đang xử lý
            self.product_result.config(state="normal")
            self.product_result.delete("1.0", tk.END)
            self.product_result.insert("1.0", "Đang xử lý dữ liệu...")
            self.product_result.config(state="disabled")
            self.root.update()  # Cập nhật giao diện để hiển thị thông báo
            
            # Tính toán số lượng sản phẩm bán ra
            product_quantity = defaultdict(int)
            for invoice in self.invoice_manager.invoices:
                for item in invoice.items:
                    product_quantity[item.product_id] += item.quantity
            
            if not product_quantity:
                messagebox.showinfo("Thông báo", "Không có dữ liệu sản phẩm bán ra để hiển thị!")
                return
            
            # Sắp xếp theo số lượng bán ra (cao nhất trước)
            sorted_products = sorted(
                product_quantity.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Tạo báo cáo
            report = io.StringIO()
            report.write("\n" + "="*80 + "\n")
            report.write("TOP SẢN PHẨM BÁN CHẠY NHẤT (THEO SỐ LƯỢNG)\n")
            report.write("="*80 + "\n")
            report.write(f"{'MÃ SP':<10} {'TÊN SẢN PHẨM':<30} {'SỐ LƯỢNG':<10} {'ĐƠN GIÁ':<15} {'DOANH THU':<15}\n")
            report.write("-"*80 + "\n")
            
            for product_id, quantity in sorted_products:
                product = self.product_manager.find_product(product_id)
                if product:
                    product_name = product.name
                    unit_price = product.unit_price
                    revenue = quantity * unit_price
                    report.write(f"{product_id:<10} {product_name:<30} {quantity:>10} {unit_price:>15,.2f} {revenue:>15,.2f}\n")
                else:
                    report.write(f"{product_id:<10} {'[Sản phẩm không tồn tại]':<30} {quantity:>10} {'N/A':>15} {'N/A':>15}\n")
            
            total_quantity = sum(product_quantity.values())
            report.write("-"*80 + "\n")
            report.write(f"{'TỔNG CỘNG:':<40} {total_quantity:>10}\n")
            report.write("="*80 + "\n")
            
            # Hiển thị kết quả
            self.product_result.config(state="normal")
            self.product_result.delete("1.0", tk.END)
            self.product_result.insert("1.0", report.getvalue())
            self.product_result.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị thống kê sản phẩm bán chạy: {str(e)}")

    def show_product_categories(self):
        """
        Hiển thị thống kê sản phẩm theo danh mục.
        
        Nhóm các sản phẩm theo danh mục và hiển thị thông tin
        chi tiết về từng danh mục bao gồm số lượng và tỷ lệ phần trăm.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không thể tạo báo cáo thống kê
        """
        try:
            if self.product_manager is None:
                messagebox.showwarning("Cảnh báo", "Trình quản lý sản phẩm chưa được khởi tạo")
                return
            
            # Nhóm sản phẩm theo danh mục
            categories = {}
            for product in self.product_manager.products:
                category = product.category if product.category else "Chưa phân loại"
                if category not in categories:
                    categories[category] = []
                categories[category].append(product)
            
            # Tạo báo cáo
            report = io.StringIO()
            report.write("=" * 80 + "\n")
            report.write("THỐNG KÊ SẢN PHẨM THEO DANH MỤC\n")
            report.write("=" * 80 + "\n")
            
            total_products = len(self.product_manager.products)
            
            # Sắp xếp danh mục theo thứ tự bảng chữ cái
            for category in sorted(categories.keys()):
                products = categories[category]
                percentage = (len(products) / total_products * 100) if total_products > 0 else 0
                
                report.write(f"\nDANH MỤC: {category} ({len(products)} sản phẩm - {percentage:.2f}%)\n")
                report.write("-" * 80 + "\n")
                report.write(f"{'MÃ SP':<10} {'TÊN SẢN PHẨM':<30} {'ĐƠN VỊ':<10} {'ĐƠN GIÁ':>15}\n")
                report.write("-" * 80 + "\n")
                
                # Sắp xếp sản phẩm theo tên
                for product in sorted(products, key=lambda p: p.name):
                    report.write(f"{product.product_id:<10} {product.name:<30} {product.calculation_unit:<10} {product.unit_price:>15,.2f}\n")
            
            report.write("\n" + "=" * 80 + "\n")
            report.write(f"TỔNG SỐ: {total_products} sản phẩm trong {len(categories)} danh mục\n")
            report.write("=" * 80 + "\n")
            
            # Hiển thị kết quả
            self.product_result.config(state="normal")
            self.product_result.delete("1.0", tk.END)
            self.product_result.insert("1.0", report.getvalue())
            self.product_result.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị thống kê sản phẩm theo danh mục: {str(e)}")

    def show_top_customers(self):
        """
        Hiển thị thống kê khách hàng thân thiết.
        
        Hiển thị hộp thoại để người dùng chọn số lượng khách hàng
        muốn xem, sau đó gọi statistics_manager để tạo báo cáo
        và hiển thị kết quả.
        
        Trả về:
            None
        
        Ném ra:
            Exception: Nếu không thể tạo báo cáo thống kê
        """
        try:
            if self.statistics_manager is None:
                messagebox.showwarning("Cảnh báo", "Trình quản lý thống kê chưa được khởi tạo")
                return
                
            # Kiểm tra xem có hóa đơn nào không
            if not self.invoice_manager or not self.invoice_manager.invoices:
                messagebox.showinfo("Thông báo", "Không có dữ liệu hóa đơn để thống kê!")
                return
            
            # Hỏi người dùng về số lượng khách hàng hàng đầu muốn xem
            while True:
                limit = simpledialog.askinteger(
                    "Số lượng khách hàng",
                    "Nhập số lượng khách hàng tiềm năng muốn xem:",
                    initialvalue=5
                )

                if limit is None:
                    return

                if limit <= 0:
                    messagebox.showerror("Lỗi", "Số lượng khách hàng phải lớn hơn 0. Vui lòng thử lại.")
                    continue
                elif limit > 20:
                    messagebox.showerror("Lỗi", "Số lượng khách hàng không được vượt quá 20. Vui lòng thử lại.")
                    continue

                break
                
            # Thông báo đang xử lý
            self.customer_result.config(state="normal")
            self.customer_result.delete("1.0", tk.END)
            self.customer_result.insert("1.0", "Đang xử lý dữ liệu...")
            self.customer_result.config(state="disabled")
            self.root.update()  # Cập nhật giao diện để hiển thị thông báo
            
            # Chuyển hướng stdout để bắt kết quả in ra
            old_stdout = sys.stdout
            result = io.StringIO()
            sys.stdout = result
            
            # Gọi phương thức thống kê
            self.statistics_manager.top_customers(limit=limit)
            
            # Khôi phục stdout và lấy kết quả
            sys.stdout = old_stdout
            output = result.getvalue()
            
            # Hiển thị kết quả
            self.customer_result.config(state="normal")
            self.customer_result.delete("1.0", tk.END)
            self.customer_result.insert("1.0", output)
            self.customer_result.config(state="disabled")
            
            if not output.strip():
                print("Cảnh báo: Kết quả trống!")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị thống kê khách hàng tiềm năng: {str(e)}")

def start_gui():
    """
    Hàm khởi động giao diện đồ họa chính của ứng dụng.
    
    Tạo cửa sổ Tkinter root và khởi tạo lớp InvoiceAppGUI,
    sau đó bắt đầu vòng lặp sự kiện chính. Xử lý các lỗi
    nghiêm trọng bằng cách hiển thị hộp thoại lỗi.
    
    Trả về:
        None
    
    Ném ra:
        Exception: Nếu không thể khởi tạo giao diện
        tk.TclError: Nếu có lỗi với Tkinter
    """
    try:
        root = tk.Tk()
        app = InvoiceAppGUI(root)
        root.mainloop()
    except Exception as e:
        try:
            error_root = tk.Tk()
            error_root.title("Lỗi nghiêm trọng")
            error_root.geometry("400x200")
            error_label = ttk.Label(error_root, text=f"Đã xảy ra lỗi không thể phục hồi:\n{str(e)}", wraplength=380)
            error_label.pack(padx=20, pady=20)
            ttk.Button(error_root, text="Đóng", command=error_root.destroy).pack(pady=10)
            error_root.mainloop()
        except tk.TclError:
            pass
