"""
Gói chính của Hệ thống Quản lý Hóa đơn.

Gói này chứa tất cả các module chính của ứng dụng quản lý hóa đơn
bao gồm models, core logic, utilities, database và UI.
"""


"""
Gói ứng dụng chính cho Hệ thống Quản lý Hóa đơn.
"""

# Đảm bảo các submodule có thể được truy cập
from . import ui
from . import core
from . import models
from . import utils
from . import data
from . import database

# Định nghĩa các module sẽ được import khi dùng "from invoicemanager import *"
__all__ = ['ui', 'core', 'models', 'utils', 'data', 'database']