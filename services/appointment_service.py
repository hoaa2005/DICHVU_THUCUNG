from models.appointment_repository import AppointmentRepository

class AppointmentService:
    def __init__(self):
        self.repo = AppointmentRepository()

    def get_admin_appointments(self, status, search):
        return self.repo.get_all_appointments_admin(status, search)

    def change_status(self, ma_lh, status):
        if not ma_lh or not status:
            return {"status": "error", "message": "Dữ liệu yêu cầu không hợp lệ!"}
        
        if self.repo.update_appointment_status(ma_lh, status):
            return {"status": "success", "message": f"Đã cập nhật trạng thái lịch hẹn thành: {status}"}
        return {"status": "error", "message": "Không thể cập nhật, lỗi hệ thống database!"}

    def get_booking_form_data(self, ma_kh):
        # 1. Lấy danh sách thú cưng từ Repo lịch hẹn
        pets = self.repo.get_pets_by_customer(ma_kh)
        
        # 2. Tự tạo kết nối nhanh để lấy danh sách dịch vụ, tránh gọi qua BookingRepository bị thiếu hàm
        import sqlite3
        conn = sqlite3.connect("petcare.db")
        conn.row_factory = sqlite3.Row
        try:
            services = conn.execute("SELECT maDV, tenDV, gia FROM DichVu").fetchall()
        finally:
            conn.close()
            
        return pets, services