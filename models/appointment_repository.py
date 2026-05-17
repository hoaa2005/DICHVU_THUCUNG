import sqlite3
from datetime import datetime

class AppointmentRepository:
    def __init__(self):
        self.db_path = "petcare.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ==========================================
    # CÁC NGHIỆP VỤ DÀNH CHO ADMIN
    # ==========================================
    
    # 1. Lấy toàn bộ danh sách lịch hẹn hệ thống kèm bộ lọc
    def get_all_appointments_admin(self, status_filter=None, search_query=None):
        conn = self.get_connection()
        try:
            sql = """
                SELECT lh.maLH, lh.thoiGian, lh.trangThai as trangThaiLH,
                       kh.ten as tenKH, kh.sdt, tc.ten as tenThuCung, tc.loai as loaiThuCung,
                       dv.tenDV, hd.tongTien
                FROM LichHen lh
                LEFT JOIN KhachHang kh ON lh.maKH = kh.maKH
                LEFT JOIN ThuCung tc ON lh.maTC = tc.maTC
                LEFT JOIN ChiTietLichHen ctlh ON lh.maLH = ctlh.maLH
                LEFT JOIN DichVu dv ON ctlh.maDV = dv.maDV
                LEFT JOIN HoaDon hd ON lh.maLH = hd.maLH
                WHERE 1=1
            """
            params = []
            if status_filter:
                sql += " AND lh.trangThai = ?"
                params.append(status_filter)
            if search_query:
                sql += " AND (kh.ten LIKE ? OR tc.ten LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
                
            sql += " ORDER BY lh.thoiGian DESC"
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    # 2. Cập nhật trạng thái lịch hẹn xử lý nhanh
    def update_appointment_status(self, ma_lh, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE LichHen SET trangThai = ? WHERE maLH = ?", (status, ma_lh))
            # Nếu lịch hẹn bị hủy, tự động cập nhật trạng thái hóa đơn liên quan
            if status == 'Đã hủy':
                cursor.execute("UPDATE HoaDon SET trangThai = 'Đã hủy' WHERE maLH = ?", (ma_lh,))
            elif status == 'Đã xác nhận':
                cursor.execute("UPDATE HoaDon SET trangThai = 'Đã thanh toán' WHERE maLH = ?", (ma_lh,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==========================================
    # CÁC NGHIỆP VỤ DÀNH CHO KHÁCH HÀNG
    # ==========================================

    # 1. Lấy danh sách thú cưng của riêng khách hàng đó để nạp vào thẻ Select
    def get_pets_by_customer(self, ma_kh):
        conn = self.get_connection()
        try:
            return conn.execute("SELECT maTC, ten, loai FROM ThuCung WHERE maKH = ?", (ma_kh,)).fetchall()
        finally:
            conn.close()