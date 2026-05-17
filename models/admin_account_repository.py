import sqlite3

class AdminAccountRepository:
    def __init__(self):
        self.db_path = "petcare.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # 1. Lấy toàn bộ danh sách tài khoản kèm bộ lọc tìm kiếm
    def get_all_accounts(self, search_query=None):
        conn = self.get_connection()
        try:
            sql = "SELECT maTK, tenDangNhap, vaiTro, trangThai FROM TaiKhoan"
            params = []
            if search_query:
                sql += " WHERE tenDangNhap LIKE ? OR vaiTro LIKE ?"
                params = [f"%{search_query}%", f"%{search_query}%"]
            sql += " ORDER BY maTK DESC"
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    # 2. Thêm mới tài khoản và tự động tạo thực thể liên quan
    def create_account_transaction(self, username, password, role, status, full_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Kiểm tra trùng tên đăng nhập trước
            cursor.execute("SELECT maTK FROM TaiKhoan WHERE tenDangNhap = ?", (username,))
            if cursor.fetchone():
                return False, "Tên đăng nhập đã tồn tại trong hệ thống!"

            # Thêm vào bảng TaiKhoan
            cursor.execute("""
                INSERT INTO TaiKhoan (tenDangNhap, matKhau, vaiTro, trangThai)
                VALUES (?, ?, ?, ?)
            """, (username, password, role, status))
            ma_tk = cursor.lastrowid

            # Dựa vào vai trò để tự động tạo bản ghi ở bảng tương ứng theo DB của bạn
            if role.lower() == 'admin' or role.lower() == 'nhân viên':
                cursor.execute("""
                    INSERT INTO NhanVien (maTK, ten, sdt, diaChi, chucVu)
                    VALUES (?, ?, '', '', ?)
                """, (ma_tk, full_name, role))
            else:
                cursor.execute("""
                    INSERT INTO KhachHang (maTK, ten, sdt, diaChi)
                    VALUES (?, ?, '', '')
                """, (ma_tk, full_name))

            conn.commit()
            return True, "Tạo tài khoản và đồng bộ thực thể thành công!"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    # 3. Cập nhật tài khoản (Vai trò, Trạng thái, Mật khẩu nếu có)
    def update_account(self, ma_tk, role, status, password=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if password and password.strip() != "":
                cursor.execute("""
                    UPDATE TaiKhoan SET vaiTro = ?, trangThai = ?, matKhau = ? WHERE maTK = ?
                """, (role, status, password, ma_tk))
            else:
                cursor.execute("""
                    UPDATE TaiKhoan SET vaiTro = ?, trangThai = ? WHERE maTK = ?
                """, (role, status, ma_tk))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    # 4. Xóa tài khoản (Có ràng buộc cascade bằng tay để không lỗi logic DB)
    def delete_account_transaction(self, ma_tk):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Xóa thực thể phụ thuộc trước để bảo toàn toàn vẹn dữ liệu
            cursor.execute("DELETE FROM KhachHang WHERE maTK = ?", (ma_tk,))
            cursor.execute("DELETE FROM NhanVien WHERE maTK = ?", (ma_tk,))
            cursor.execute("DELETE FROM TaiKhoan WHERE maTK = ?", (ma_tk,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()