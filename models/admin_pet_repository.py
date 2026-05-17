import sqlite3

class AdminPetRepository:
    def __init__(self):
        self.db_path = "petcare.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Lấy toàn bộ thú cưng hệ thống kèm thông tin chủ nuôi (Có hỗ trợ tìm kiếm bộ lọc)
    def get_all_pets_admin(self, search_query=None):
        conn = self.get_connection()
        try:
            sql = """
                SELECT tc.*, kh.ten as tenChuNuoi, kh.sdt as sdtChuNuoi
                FROM ThuCung tc
                LEFT JOIN KhachHang kh ON tc.maKH = kh.maKH
                WHERE 1=1
            """
            params = []
            if search_query:
                sql += " AND (tc.ten LIKE ? OR kh.ten LIKE ? OR tc.giong LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
            
            sql += " ORDER BY tc.maTC DESC"
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()