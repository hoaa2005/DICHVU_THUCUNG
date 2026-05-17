import sqlite3

class PetRepository:
    def __init__(self):
        self.db_path = "petcare.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_customer_by_id(self, maKH):
        conn = self.get_connection()
        try:
            return conn.execute("SELECT * FROM KhachHang WHERE maKH = ?", (maKH,)).fetchone()
        finally:
            conn.close()

    def update_customer(self, maKH, ten, sdt, diaChi):
        conn = self.get_connection()
        try:
            conn.execute("""
                UPDATE KhachHang 
                SET ten = ?, sdt = ?, diaChi = ? 
                WHERE maKH = ?
            """, (ten, sdt, diaChi, maKH))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error Update KH: {e}")
            return False
        finally:
            conn.close()

    def get_pets_by_customer(self, maKH):
        conn = self.get_connection()
        try:
            return conn.execute("SELECT * FROM ThuCung WHERE maKH = ?", (maKH,)).fetchall()
        finally:
            conn.close()

    def add_pet(self, ten, loai, tuoi, maKH):
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO ThuCung (maKH, ten, loai, tuoi, trangThai) 
                VALUES (?, ?, ?, ?, ?)
            """, (maKH, ten, loai, tuoi, 'Hoạt động'))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error Add Pet: {e}")
            return False
        finally:
            conn.close()

    def delete_pet(self, maTC):
        conn = self.get_connection()
        try:
            conn.execute("DELETE FROM ThuCung WHERE maTC = ?", (maTC,))
            conn.commit()
            return True
        finally:
            conn.close()