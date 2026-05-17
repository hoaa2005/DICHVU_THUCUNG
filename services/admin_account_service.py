from models.admin_account_repository import AdminAccountRepository

class AdminAccountService:
    def __init__(self):
        self.repo = AdminAccountRepository()

    def load_accounts_list(self, search_query=None):
        return self.repo.get_all_accounts(search_query)

    def add_new_user(self, data):
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "Khách hàng")
        status = data.get("status", "Hoạt động")
        full_name = data.get("full_name", "").strip()

        if not username or not password or not full_name:
            return {"status": "error", "message": "Vui lòng điền các trường bắt buộc!"}
            
        success, msg = self.repo.create_account_transaction(username, password, role, status, full_name)
        return {"status": "success" if success else "error", "message": msg}

    def edit_user(self, ma_tk, data):
        role = data.get("role")
        status = data.get("status")
        password = data.get("password")
        
        if self.repo.update_account(ma_tk, role, status, password):
            return {"status": "success", "message": "Cập nhật tài khoản thành công!"}
        return {"status": "error", "message": "Cập nhật thất bại!"}

    def remove_user(self, ma_tk):
        if self.repo.delete_account_transaction(ma_tk):
            return {"status": "success", "message": "Đã xóa tài khoản vĩnh viễn!"}
        return {"status": "error", "message": "Lỗi hệ thống, không thể xóa tài khoản này!"}