from models.pet_repository import PetRepository

class PetService:
    def __init__(self):
        self.repo = PetRepository()

    def get_profile_data(self, maKH):
        if not maKH:
            return None, []
        kh = self.repo.get_customer_by_id(maKH)
        pets = self.repo.get_pets_by_customer(maKH)
        return kh, pets

    def update_profile(self, maKH, form_data):
        ten = form_data.get('ten', '').strip()
        sdt = form_data.get('sdt', '').strip()
        diaChi = form_data.get('diaChi', '').strip()
        
        if not ten:
            return False, "Tên khách hàng không được để trống!"
            
        success = self.repo.update_customer(maKH, ten, sdt, diaChi)
        if success:
            return True, "Cập nhật thông tin cá nhân thành công!"
        return False, "Không thể cập nhật hồ sơ."

    def add_new_pet(self, form_data, maKH):
        ten = form_data.get('ten', '').strip()
        loai = form_data.get('loai', 'Khác').strip()
        
        try:
            tuoi = int(form_data.get('tuoi', 0))
        except ValueError:
            tuoi = 0

        if not ten: 
            return False, "Tên của thú cưng không được để trống!"
            
        success = self.repo.add_pet(ten, loai, tuoi, maKH)
        if success:
            return True, "Thêm bé cưng thành công!"
        return False, "Lỗi khi lưu thông tin thú cưng."

    def remove_pet(self, maTC):
        self.repo.delete_pet(maTC)
        return True, "Đã loại bỏ thông tin bé cưng khỏi hệ thống."