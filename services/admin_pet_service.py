from models.admin_pet_repository import AdminPetRepository

class AdminPetService:
    def __init__(self):
        # Khởi tạo kết nối tới lớp hạ tầng dữ liệu của Thú cưng cho Admin
        self.repo = AdminPetRepository()

    def get_all_pets_for_dashboard(self, search_query=None):
        """
        Nghiệp vụ lấy danh sách thú cưng toàn hệ thống.
        Xử lý chuẩn hóa chuỗi tìm kiếm trước khi đẩy xuống tầng Repository.
        """
        if search_query:
            # Chuẩn hóa chuỗi: xóa khoảng trắng thừa ở 2 đầu
            search_query = search_query.strip()
            
        # Gọi xuống repo để lấy dữ liệu thô từ cơ sở dữ liệu
        return self.repo.get_all_pets_admin(search_query)

    def process_admin_delete_pet(self, ma_tc):
        """
        Nghiệp vụ xử lý xóa hồ sơ thú cưng kèm kiểm tra logic.
        Admin chỉ được phép xóa các bé nếu mã thú cưng hợp lệ (lớn hơn 0).
        """
        if not ma_tc or int(ma_tc) <= 0:
            return False, "Mã thú cưng cung cấp không hợp lệ!"
            
        # Ủy quyền cho Repository thực hiện thao tác xóa và kiểm tra ràng buộc khóa ngoại (Lịch hẹn)
        success, message = self.repo.admin_delete_pet(ma_tc)
        return success, message