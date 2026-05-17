import sqlite3

class AdminRepository:
    def __init__(self):
        self.db_path = "petcare.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # 1. Tính toán các chỉ số thống kê tài chính & thực thể trên hệ thống
    def get_admin_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        try:
            # Thống kê tổng doanh thu thực nhận từ hóa đơn
            cursor.execute("SELECT SUM(tongTien) FROM HoaDon")
            res_money = cursor.fetchone()[0]
            stats['doanh_thu'] = res_money if res_money else 0

            # Đếm số lượng lịch hẹn cần phê duyệt
            cursor.execute("SELECT COUNT(*) FROM LichHen WHERE trangThai = 'Chờ xử lý'")
            stats['lich_cho'] = cursor.fetchone()[0]

            # Thống kê tổng số tài khoản người dùng
            cursor.execute("SELECT COUNT(*) FROM TaiKhoan")
            stats['tong_kh'] = cursor.fetchone()[0]

            # Thống kê tổng số thú cưng đã đăng ký
            cursor.execute("SELECT COUNT(*) FROM ThuCung")
            stats['tong_tc'] = cursor.fetchone()[0]
            return stats
        finally:
            conn.close()

    # 2. Truy xuất danh sách 5 yêu cầu đặt lịch mới nhất để đẩy ra bảng duyệt
    def get_recent_bookings(self):
        conn = self.get_connection()
        try:
            return conn.execute("""
                SELECT lh.maLH, lh.thoiGian, lh.trangThai, 
                       tc.ten as tenThuCung, tc.loai as loaiThuCung,
                       dv.tenDV, kh.ten as tenKH
                FROM LichHen lh
                LEFT JOIN ThuCung tc ON lh.maTC = tc.maTC
                LEFT JOIN ChiTietLichHen ctlh ON lh.maLH = ctlh.maLH
                LEFT JOIN DichVu dv ON ctlh.maDV = dv.maDV
                LEFT JOIN KhachHang kh ON lh.maKH = kh.maKH
                WHERE lh.trangThai = 'Chờ xử lý'
                ORDER BY lh.maLH DESC LIMIT 5
            """).fetchall()
        finally:
            conn.close()