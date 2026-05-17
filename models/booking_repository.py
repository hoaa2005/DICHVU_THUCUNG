import sqlite3
from datetime import datetime

class BookingRepository:

    def __init__(self):
        self.db_path = "petcare.db"

    # =========================================
    # KẾT NỐI DB
    # =========================================
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================
    # LOGIN
    # =========================================
    def find_account_by_credentials(self, username, password):
        conn = self.get_connection()
        try:
            user = conn.execute("""
                SELECT *
                FROM TaiKhoan
                WHERE tenDangNhap = ? AND matKhau = ?
            """, (username, password)).fetchone()
            return user
        finally:
            conn.close()

    # =========================================
    # LẤY MÃ KHÁCH HÀNG THEO MÃ TÀI KHOẢN
    # =========================================
    def get_customer_by_account(self, maTK):
        conn = self.get_connection()
        try:
            row = conn.execute("""
                SELECT maKH
                FROM KhachHang
                WHERE maTK = ?
            """, (maTK,)).fetchone()
            if row:
                return row["maKH"]
            return None
        finally:
            conn.close()

    # =========================================
    # TẠO KHÁCH HÀNG MỚI
    # =========================================
    def create_customer(self, maTK, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO KhachHang (maTK, ten, sdt, diaChi)
                VALUES (?, ?, '', '')
            """, (maTK, username))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    # =========================================
    # NGHIỆP VỤ ĐẶT LỊCH HẸN
    # =========================================
    def insert_booking_transaction(self, maKH, maTC, maDV, donGia, thoiGian, phuongThuc):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 1. Thêm vào bảng Lịch Hẹn
            cursor.execute("""
                INSERT INTO LichHen (maKH, maNV, maTC, thoiGian, trangThai)
                VALUES (?, NULL, ?, ?, 'Chờ xử lý')
            """, (maKH, maTC, thoiGian))
            maLH = cursor.lastrowid

            # 2. Thêm vào Chi Tiết Lịch Hẹn
            cursor.execute("""
                INSERT INTO ChiTietLichHen (maLH, maDV, soLuong, donGia, thanhTien)
                VALUES (?, ?, 1, ?, ?)
            """, (maLH, maDV, donGia, donGia))

            # 3. Tạo Hóa Đơn đi kèm
            ngay_lap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO HoaDon (maLH, ngayLap, tongTien, trangThai)
                VALUES (?, ?, ?, 'Chưa thanh toán')
            """, (maLH, ngay_lap, donGia))
            maHD = cursor.lastrowid

            # 4. Ghi nhận giao dịch Thanh Toán
            cursor.execute("""
                INSERT INTO ThanhToan (maHD, phuongThuc, soTien, trangThai, thoiGianThanhToan)
                VALUES (?, ?, ?, 'Thành công', ?)
            """, (maHD, phuongThuc, donGia, ngay_lap))

            conn.commit()
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    # =========================================
    # LỊCH SỬ ĐẶT LỊCH KHÁCH HÀNG
    # =========================================
    def get_bookings_by_customer(self, maKH):
        conn = self.get_connection()
        try:
            return conn.execute("""
                SELECT 
                    lh.maLH, 
                    lh.thoiGian, 
                    lh.trangThai as trangThaiLH,
                    tc.ten as tenThuCung, 
                    tc.loai as loaiThuCung,
                    dv.tenDV,
                    COALESCE(hd.tongTien, 0) as tongTien,
                    tt.phuongThuc,
                    tt.trangThai as trangThaiTT
                FROM LichHen lh
                LEFT JOIN ThuCung tc ON lh.maTC = tc.maTC
                LEFT JOIN ChiTietLichHen ctlh ON lh.maLH = ctlh.maLH
                LEFT JOIN DichVu dv ON ctlh.maDV = dv.maDV
                LEFT JOIN HoaDon hd ON lh.maLH = hd.maLH
                LEFT JOIN ThanhToan tt ON hd.maHD = tt.maHD
                WHERE lh.maKH = ?
                ORDER BY lh.maLH DESC
            """, (maKH,)).fetchall()
        finally:
            conn.close()

    # =========================================
    # HỦY LỊCH HẸN (TỪ PHÍA USER)
    # =========================================
    def customer_cancel_booking(self, ma_lh, ma_kh):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT trangThai FROM LichHen WHERE maLH = ? AND maKH = ?", (ma_lh, ma_kh))
            row = cursor.fetchone()
            if not row:
                return False, "Lịch hẹn không tồn tại!"
            if row["trangThai"] != "Chờ xử lý":
                return False, "Chỉ có thể hủy lịch hẹn khi trạng thái là 'Chờ xử lý'!"

            cursor.execute("UPDATE LichHen SET trangThai = 'Đã hủy' WHERE maLH = ?", (ma_lh,))
            cursor.execute("UPDATE HoaDon SET trangThai = 'Đã hủy' WHERE maLH = ?", (ma_lh,))
            conn.commit()
            return True, "Đã hủy lịch hẹn thành công!"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    # =========================================
    # LẤY TOÀN BỘ DỊCH VỤ ĐANG HOẠT ĐỘNG
    # =========================================
    # Đã sửa lỗi căn lề (Thụt lề 4 dấu cách) để hàm thuộc về Class
    def get_all_active_services(self):
        conn = self.get_connection()
        try:
            return conn.execute("""
                SELECT maDV, tenDV, gia, moTa, trangThai 
                FROM DichVu 
                ORDER BY maDV DESC
            """).fetchall()
        finally:
            conn.close()