from flask import Flask, flash, request, jsonify, render_template
import sqlite3

from flask import Flask, render_template, request, jsonify, session, redirect
from models.pet_repository import PetRepository
from services.pet_service import PetService
from models.pet_repository import PetRepository
service_pet = PetService()
from services import pet_service
from models import pet_repository
app = Flask(__name__)
app.secret_key = "secret123"

app.secret_key = "petcare_secret"


# DB
# ========================
db = sqlite3.connect("petcare.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS TaiKhoan (
    maTK INTEGER PRIMARY KEY AUTOINCREMENT,
    tenDangNhap TEXT UNIQUE,
    matKhau TEXT,
    vaiTro TEXT,
    trangThai TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS KhachHang (
    maKH INTEGER PRIMARY KEY AUTOINCREMENT,
    maTK INTEGER,
    ten TEXT,
    sdt TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO TaiKhoan (tenDangNhap, matKhau, vaiTro)
VALUES ('admin','123','admin')
""")
# =========================================
# XOA CAC BANG CU
# =========================================
cursor.execute("DROP TABLE IF EXISTS DanhGia")
cursor.execute("DROP TABLE IF EXISTS ThanhToan")
cursor.execute("DROP TABLE IF EXISTS ChiTietHoaDon")
cursor.execute("DROP TABLE IF EXISTS HoaDon")
cursor.execute("DROP TABLE IF EXISTS ChiTietLichHen")
cursor.execute("DROP TABLE IF EXISTS LichHen")
cursor.execute("DROP TABLE IF EXISTS ThuCung")
cursor.execute("DROP TABLE IF EXISTS DichVu")
cursor.execute("DROP TABLE IF EXISTS NhanVien")
cursor.execute("DROP TABLE IF EXISTS KhachHang")

# =========================================
# TAO BANG KHACH HANG
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS KhachHang (
    maKH INTEGER PRIMARY KEY AUTOINCREMENT,
    maTK INTEGER UNIQUE,
    ten VARCHAR(100) NOT NULL,
    sdt VARCHAR(15),
    diaChi VARCHAR(255)
)
""")

# =========================================
# TAO BANG NHAN VIEN
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS NhanVien (
    maNV INTEGER PRIMARY KEY AUTOINCREMENT,
    maTK INTEGER UNIQUE,
    ten VARCHAR(100) NOT NULL,
    sdt VARCHAR(15),
    diaChi VARCHAR(255),
    chucVu VARCHAR(50)
)
""")

# =========================================
# TAO BANG THU CUNG
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ThuCung (
    maTC INTEGER PRIMARY KEY AUTOINCREMENT,
    maKH INTEGER,
    ten VARCHAR(100),
    loai VARCHAR(50),
    tuoi INTEGER,
    trangThai VARCHAR(50)
)
""")

# =========================================
# TAO BANG DICH VU
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS DichVu (
    maDV INTEGER PRIMARY KEY AUTOINCREMENT,
    tenDV VARCHAR(100) NOT NULL,
    gia DECIMAL(10,2) NOT NULL,
    moTa TEXT,
    trangThai VARCHAR(50)
)
""")

# =========================================
# TAO BANG LICH HEN
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS LichHen (
    maLH INTEGER PRIMARY KEY AUTOINCREMENT,
    maKH INTEGER,
    maNV INTEGER,
    maTC INTEGER,
    thoiGian DATETIME,
    trangThai VARCHAR(50)
)
""")

# =========================================
# TAO BANG CHI TIET LICH HEN
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ChiTietLichHen (
    maLH INTEGER,
    maDV INTEGER,
    soLuong INTEGER,
    donGia DECIMAL(10,2),
    thanhTien DECIMAL(10,2),
    PRIMARY KEY(maLH, maDV)
)
""")

# =========================================
# TAO BANG HOA DON
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS HoaDon (
    maHD INTEGER PRIMARY KEY AUTOINCREMENT,
    maLH INTEGER UNIQUE,
    ngayLap DATETIME,
    tongTien DECIMAL(10,2),
    trangThai VARCHAR(50)
)
""")

# =========================================
# TAO BANG CHI TIET HOA DON
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ChiTietHoaDon (
    maHD INTEGER,
    maDV INTEGER,
    soLuong INTEGER,
    donGia DECIMAL(10,2),
    thanhTien DECIMAL(10,2),
    PRIMARY KEY(maHD, maDV)
)
""")

# =========================================
# TAO BANG THANH TOAN
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ThanhToan (
    maTT INTEGER PRIMARY KEY AUTOINCREMENT,
    maHD INTEGER,
    phuongThuc VARCHAR(50),
    soTien DECIMAL(10,2),
    trangThai VARCHAR(50),
    thoiGianThanhToan DATETIME
)
""")

# =========================================
# TAO BANG DANH GIA
# =========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS DanhGia (
    maDG INTEGER PRIMARY KEY AUTOINCREMENT,
    maKH INTEGER,
    maDV INTEGER,
    soSao INTEGER CHECK(soSao >=1 AND soSao <=5),
    noiDung TEXT,
    phanHoi TEXT,
    ngayDanhGia DATETIME
)
""")

# =========================================
# INSERT KHACH HANG
# =========================================
cursor.executemany("""
INSERT INTO KhachHang
(maKH, maTK, ten, sdt, diaChi)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, 2, 'Nguyễn Văn A', '0901234567', 'TP.HCM'),
    (2, 4, 'Trần Thị B', '0912345678', 'Hà Nội'),
    (3, 5, 'Lê Minh C', '0923456789', 'Đà Nẵng')
])

# =========================================
# INSERT NHAN VIEN
# =========================================
cursor.executemany("""
INSERT INTO NhanVien
(maNV, maTK, ten, sdt, diaChi, chucVu)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, 3, 'Bác sĩ Lan', '0988888888', 'TP.HCM', 'Bác sĩ thú y'),
    (2, 6, 'Nguyễn Hoàng', '0977777777', 'Hà Nội', 'Spa'),
    (3, 7, 'Trần Minh', '0966666666', 'Đà Nẵng', 'Chăm sóc thú cưng')
])

# =========================================
# INSERT THU CUNG
# =========================================
cursor.executemany("""
INSERT INTO ThuCung
(maTC, maKH, ten, loai, tuoi, trangThai)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, 1, 'Milu', 'Chó Poodle', 2, 'Khỏe mạnh'),
    (2, 1, 'Coco', 'Mèo Anh', 1, 'Khỏe mạnh'),
    (3, 2, 'Bun', 'Chó Husky', 3, 'Đang điều trị'),
    (4, 3, 'Nabi', 'Mèo Ba Tư', 2, 'Khỏe mạnh')
])

# =========================================
# INSERT DICH VU
# =========================================
cursor.executemany("""
INSERT INTO DichVu
(maDV, tenDV, gia, moTa, trangThai)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, 'Khám tổng quát', 150000, 'Kiểm tra sức khỏe', 'Hoạt động'),
    (2, 'Tiêm phòng', 250000, 'Tiêm vaccine', 'Hoạt động'),
    (3, 'Tắm spa', 180000, 'Spa thư giãn', 'Hoạt động'),
    (4, 'Cắt tỉa lông', 200000, 'Cắt lông chuyên nghiệp', 'Hoạt động'),
    (5, 'Khách sạn thú cưng', 350000, 'Lưu trú qua đêm', 'Hoạt động'),
    (6, 'Khám da liễu', 220000, 'Điều trị da', 'Hoạt động'),
    (7, 'Tẩy giun', 100000, 'Tẩy giun định kỳ', 'Hoạt động'),
    (8, 'Đưa đón thú cưng', 80000, 'Đưa đón tận nơi', 'Hoạt động'),
    (9, 'Khám nha khoa', 270000, 'Vệ sinh răng', 'Hoạt động'),
    (10, 'Spa cao cấp', 450000, 'Combo VIP', 'Hoạt động')
])

# =========================================
# INSERT LICH HEN
# =========================================
cursor.executemany("""
INSERT INTO LichHen
(maLH, maKH, maNV, maTC, thoiGian, trangThai)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, 1, 1, 1, '2026-05-10 09:00:00', 'Đã xác nhận'),
    (2, 2, 2, 3, '2026-05-11 14:00:00', 'Chờ xác nhận'),
    (3, 3, 3, 4, '2026-05-12 10:00:00', 'Hoàn thành')
])

# =========================================
# INSERT CHI TIET LICH HEN
# =========================================
cursor.executemany("""
INSERT INTO ChiTietLichHen
(maLH, maDV, soLuong, donGia, thanhTien)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, 1, 1, 150000, 150000),
    (1, 2, 1, 250000, 250000),
    (2, 3, 1, 180000, 180000),
    (3, 4, 1, 200000, 200000)
])

# =========================================
# INSERT HOA DON
# =========================================
cursor.executemany("""
INSERT INTO HoaDon
(maHD, maLH, ngayLap, tongTien, trangThai)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, 1, '2026-05-10', 400000, 'Đã thanh toán'),
    (2, 3, '2026-05-12', 200000, 'Đã thanh toán')
])

# =========================================
# INSERT CHI TIET HOA DON
# =========================================
cursor.executemany("""
INSERT INTO ChiTietHoaDon
(maHD, maDV, soLuong, donGia, thanhTien)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, 1, 1, 150000, 150000),
    (1, 2, 1, 250000, 250000),
    (2, 4, 1, 200000, 200000)
])

# =========================================
# INSERT THANH TOAN
# =========================================
cursor.executemany("""
INSERT INTO ThanhToan
(maTT, maHD, phuongThuc, soTien, trangThai, thoiGianThanhToan)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, 1, 'Tiền mặt', 400000, 'Đã thanh toán', '2026-05-10 10:00:00'),
    (2, 2, 'Chuyển khoản', 200000, 'Đã thanh toán', '2026-05-12 11:00:00')
])

# =========================================
# INSERT DANH GIA
# =========================================
cursor.executemany("""
INSERT INTO DanhGia
(maDG, maKH, maDV, soSao, noiDung, phanHoi, ngayDanhGia)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    (1, 1, 1, 5, 'Dịch vụ rất tốt', 'Cảm ơn bạn', '2026-05-11'),
    (2, 2, 3, 4, 'Spa sạch sẽ', 'Cảm ơn phản hồi', '2026-05-12'),
    (3, 3, 4, 5, 'Cắt lông đẹp', 'Rất vui được phục vụ', '2026-05-13')
])

db.commit()

# ========================
# LOAD UI
# ========================
@app.route("/")
def home():
    user = session.get("user")
    return render_template("home.html", user=user)
@app.route("/login-page")
def login_page():
    return render_template("index.html")
# ========================
# LOGIN
# ========================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        user = data.get("username")
        pw = data.get("password")

        if not user or not pw:
            return {"message": "Thiếu dữ liệu"}

        cursor.execute(
            "SELECT maTK, vaiTro FROM TaiKhoan WHERE tenDangNhap=? AND matKhau=?",
            (user, pw)
        )
        result = cursor.fetchone()

        if result:
            session["user"] = user
            session["role"] = result[1]

            return {"message": "OK"}
        return {"message": "Sai thông tin"}
    except Exception as e:
        return {"message": "Lỗi server"}

# ========================
# REGISTER
# ========================
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json

        user = data.get("username")
        pw = data.get("password")
        ten = data.get("ten")
        sdt = data.get("sdt")

        # VALIDATE
        if not user or not pw or not ten:
            return {"message": "Thiếu thông tin"}

        # CHECK TRÙNG
        cursor.execute("SELECT * FROM TaiKhoan WHERE tenDangNhap=?", (user,))
        if cursor.fetchone():
            return {"message": "Tài khoản đã tồn tại"}

        # INSERT TK
        cursor.execute(
            "INSERT INTO TaiKhoan (tenDangNhap, matKhau, vaiTro) VALUES (?, ?, ?)",
            (user, pw, "khachhang")
        )
        maTK = cursor.lastrowid

        # INSERT KHÁCH HÀNG
        cursor.execute(
            "INSERT INTO KhachHang (maTK, ten, sdt) VALUES (?, ?, ?)",
            (maTK, ten, sdt)
        )

        db.commit()

        return {"message": "Đăng ký thành công"}

    except Exception as e:
        return {"message": "Lỗi server"}
# TRANG CHỦ
@app.route("/home")
def home_page():
    user = session.get("user")  # có thì lấy, không thì None
    return render_template("home.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
# =========================================
# TRANG DAT LICH
# =========================================
@app.route('/booking')
def booking():
    if 'user' not in session:
        return redirect('/login-page')
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy thông tin khách hàng hiện tại
    cursor.execute("""
        SELECT maKH FROM KhachHang 
        JOIN TaiKhoan ON KhachHang.maTK = TaiKhoan.maTK 
        WHERE TaiKhoan.tenDangNhap = ?
    """, (session['user'],))
    kh = cursor.fetchone()
    
    ds_lich_hen = []
    if kh:
        # Lấy danh sách lịch hẹn kèm tên thú cưng và tên dịch vụ
        cursor.execute("""
            SELECT p.*, tc.ten as tenThuCung, dv.tenDV, dv.gia
            FROM PhieuDatLich p
            JOIN ThuCung tc ON p.maTC = tc.maTC
            JOIN DichVu dv ON p.maDV = dv.maDV
            WHERE tc.maKH = ?
            ORDER BY p.ngayDat DESC
        """, (kh['maKH'],))
        ds_lich_hen = cursor.fetchall()
    
    conn.close()
    return render_template('booking.html', user=session['user'], ds_lich_hen=ds_lich_hen)


# =========================================
# TRANG THU CUNG CUA TOI
# =========================================
@app.route('/my-pets')
def my_pets():
    if 'user' not in session:
        return redirect('/login-page')
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sửa lại câu lệnh SQL: Bỏ TaiKhoan.email nếu bảng TaiKhoan không có cột này
    cursor.execute("""
        SELECT KhachHang.*, TaiKhoan.tenDangNhap
        FROM KhachHang 
        JOIN TaiKhoan ON KhachHang.maTK = TaiKhoan.maTK 
        WHERE TaiKhoan.tenDangNhap = ?
    """, (session['user'],))
    thong_tin_kh = cursor.fetchone()
    
    ds_pets = []
    if thong_tin_kh:
        cursor.execute("SELECT * FROM ThuCung WHERE maKH = ?", (thong_tin_kh['maKH'],))
        ds_pets = cursor.fetchall()
    
    conn.close()
    return render_template('my-pets.html', 
                           user=session['user'], 
                           khach_hang=thong_tin_kh, 
                           ds_pets=ds_pets)

service_pet = PetService() # Khởi tạo Object Duy nhất

@app.route('/my-pets')
def my_pets():
    if 'user' not in session:
        return redirect('/login')
    
    maKH = session['user']['maKH']
    # Luôn lấy dữ liệu mới nhất từ DB
    khach_hang, ds_pets = service_pet.get_profile_data(maKH)
    
    return render_template('my-pets.html', khach_hang=khach_hang, ds_pets=ds_pets)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user' not in session: return redirect('/login')
    
    maKH = session['user']['maKH']
    success, message = service_pet.update_profile(maKH, request.form)
    
    flash(message)
    return redirect('/my-pets')

@app.route('/add-pet', methods=['POST'])
def add_pet():
    if 'user' not in session: return redirect('/login')
    
    maKH = session['user']['maKH']
    success, message = service_pet.add_new_pet(request.form, maKH)
    
    flash(message)
    return redirect('/my-pets')

@app.route('/delete-pet/<int:maTC>', methods=['POST'])
def delete_pet(maTC):
    success, message = service_pet.remove_pet(maTC)
    flash(message)
    return redirect('/my-pets')


# =========================================
# TRANG DICH VU
# =========================================
def get_db_connection():
    conn = sqlite3.connect('petcare.db')
    # DÒNG QUAN TRỌNG NHẤT: Giúp gọi dữ liệu bằng tên cột dv.tenDV
    conn.row_factory = sqlite3.Row 
    return conn
@app.route('/services')
def services():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Lấy danh sách dịch vụ 
    # Lưu ý: Kiểm tra chữ 'Hoạt động' có khớp với chữ trong DB của bạn không
    cursor.execute("SELECT * FROM DichVu WHERE trangThai = 'Hoạt động'")
    ds_dich_vu = cursor.fetchall()

    # 2. Lấy danh sách thú cưng của người dùng (nếu đã đăng nhập)
    ds_thu_cung = []
    user_session = session.get("user")
    
    if user_session:
        # Tìm maKH từ tên đăng nhập trong session
        cursor.execute("""
            SELECT maKH FROM KhachHang 
            JOIN TaiKhoan ON KhachHang.maTK = TaiKhoan.maTK 
            WHERE TaiKhoan.tenDangNhap = ?
        """, (user_session,))
        kh = cursor.fetchone()
        
        if kh:
            cursor.execute("SELECT * FROM ThuCung WHERE maKH = ?", (kh['maKH'],))
            ds_thu_cung = cursor.fetchall()

    conn.close()

    # Trả dữ liệu sang file HTML
    return render_template('services.html', 
                           user=user_session, 
                           ds_dich_vu=ds_dich_vu, 
                           ds_thu_cung=ds_thu_cung)
# # TRANG CHI TIET DICH VU
# =========================================
@app.route("/service_detail/<int:maDV>")
def service_detail(maDV):

    cursor.execute("""
    SELECT * FROM DichVu
    WHERE maDV=?
    """, (maDV,))

    service = cursor.fetchone()

    return render_template(
        "service_detail.html",
        service=service
    )


# 2. Route Xóa Thú Cưng

# =========================================
# TRANG THONG TIN TAI KHOAN
# =========================================
@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login-page")

    return render_template("profile.html")


# =========================================
# TRANG ADMIN
# =========================================
@app.route("/admin")
def admin():

    if "role" not in session:
        return redirect("/login-page")

    if session["role"] != "admin":
        return redirect("/")

    return render_template("admin.html")
# ========================
# RUN
# ========================
if __name__ == "__main__":
    app.run(debug=True)