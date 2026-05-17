from flask import Flask, render_template, request, jsonify
from flask import session, redirect, flash, url_for

import sqlite3

from services.pet_service import PetService
from services.booking_service import BookingService
from services.admin_service import AdminService

# =========================================
# FLASK
# =========================================
app = Flask(__name__)

app.secret_key = "petcare_secret_key_123"

# =========================================
# SERVICES
# =========================================
service_pet = PetService()

booking_service = BookingService()

admin_service = AdminService()

# =========================================
# DATABASE
# =========================================
def get_db_connection():

    conn = sqlite3.connect("petcare.db")

    conn.row_factory = sqlite3.Row

    return conn


# =========================================
# HOME
# =========================================
@app.route('/')
def index():
    # Gọi hàm lấy danh sách dịch vụ thực tế từ DB thông qua service hoặc repo trực tiếp
    danh_sach_dv = booking_service.repo.get_all_active_services()
    return render_template('home.html', danh_sach_dv=danh_sach_dv)
@app.route("/home")
def home():

    return render_template(
        "home.html",
        user=session.get("user_name")
    )


# =========================================
# LOGIN PAGE
# =========================================
@app.route("/login-page")
def login_page():

    return render_template("index.html")


# =========================================
# LOGIN
# =========================================
@app.route("/login", methods=["POST"])
def login_action():

    try:

        data = request.json

        username = data.get("username")

        password = data.get("password")

        conn = get_db_connection()

        user = conn.execute("""
            SELECT *
            FROM TaiKhoan
            WHERE tenDangNhap = ?
            AND matKhau = ?
        """, (username, password)).fetchone()

        # =====================================
        # KHÔNG TÌM THẤY
        # =====================================
        if not user:

            conn.close()

            return jsonify({
                "status": "error",
                "message": "Sai tài khoản hoặc mật khẩu"
            })

        # =====================================
        # LƯU SESSION
        # =====================================
        session["user_name"] = user["tenDangNhap"]

        session["role"] = user["vaiTro"]

        # =====================================
        # ADMIN
        # =====================================
        if user["vaiTro"] == "admin":

            session["maKH"] = None

            conn.close()

            return jsonify({
                "status": "success",
                "message": "Đăng nhập admin thành công",
                "redirect": "/admin/dashboard"
            })

        # =====================================
        # KHÁCH HÀNG
        # =====================================
        kh = conn.execute("""
            SELECT maKH
            FROM KhachHang
            WHERE maTK = ?
        """, (user["maTK"],)).fetchone()

        # CHƯA CÓ KHÁCH HÀNG
        if not kh:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO KhachHang
                (maTK, ten, sdt, diaChi)
                VALUES (?, ?, '', '')
            """, (
                user["maTK"],
                username
            ))

            conn.commit()

            session["maKH"] = cursor.lastrowid

        else:

            session["maKH"] = kh["maKH"]

        conn.close()

        return jsonify({
            "status": "success",
            "message": "Đăng nhập thành công",
            "redirect": "/home"
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })


# =========================================
# LOGOUT
# =========================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================================
# ADMIN DASHBOARD
# =========================================
@app.route("/admin/dashboard")
def admin_dashboard():

    # CHƯA LOGIN
    if "user_name" not in session:

        flash("Vui lòng đăng nhập!")

        return redirect(url_for("login_page"))

    # KHÔNG PHẢI ADMIN
    if session.get("role") != "admin":

        return "<h3>Bạn không có quyền truy cập Admin</h3>"

    thong_ke, ds_moi = admin_service.load_admin_dashboard()

    return render_template(
        "admin_dashboard.html",
        thong_ke=thong_ke,
        ds_moi=ds_moi,
        user=session.get("user_name")
    )

@app.route('/api/booking/cancel/<int:ma_lh>', methods=['POST'])
def api_customer_cancel_booking(ma_lh):
    if "user_name" not in session:
        return jsonify({"status": "error", "message": "Vui lòng đăng nhập!"}), 401
        
    ma_kh = session.get("maKH")
    from models.booking_repository import BookingRepository
    repo = BookingRepository()
    
    success, msg = repo.customer_cancel_booking(ma_lh, ma_kh)
    if success:
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg}), 400

from services.admin_account_service import AdminAccountService

account_service = AdminAccountService()

# Trang giao diện quản lý tài khoản chính của Admin
@app.route('/admin/accounts')
def admin_accounts_page():
    if "user_name" not in session or session.get("role").strip().lower() != "admin":
        return "Từ chối truy cập!", 403
    
    search_query = request.args.get('search', '')
    list_accounts = account_service.load_accounts_list(search_query)
    return render_template('admin_accounts.html', accounts=list_accounts, search_query=search_query, user=session["user_name"])

# API Thêm mới
@app.route('/api/admin/accounts', methods=['POST'])
def api_add_account():
    res = account_service.add_new_user(request.json or {})
    return jsonify(res), 200 if res["status"] == "success" else r400 # type: ignore

# API Sửa
@app.route('/api/admin/accounts/<int:ma_tk>', methods=['PUT'])
def api_edit_account(ma_tk):
    res = account_service.edit_user(ma_tk, request.json or {})
    return jsonify(res)

# API Xóa
@app.route('/api/admin/accounts/<int:ma_tk>', methods=['DELETE'])
def api_delete_account(ma_tk):
    res = account_service.remove_user(ma_tk)
    return jsonify(res)

from services.appointment_service import AppointmentService

appointment_service = AppointmentService()

# 1. TRANG ADMIN: Quản lý danh sách lịch hẹn toàn hệ thống
@app.route('/admin/appointments')
def admin_appointments_page():
    if "user_name" not in session or session.get("role").strip().lower() != "admin":
        return "Từ chối truy cập!", 403
        
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    list_lh = appointment_service.get_admin_appointments(status if status != '' else None, search if search != '' else None)
    return render_template('admin_appointments.html', appointments=list_lh, current_status=status, search_query=search, user=session["user_name"])

# API Admin: Cập nhật nhanh trạng thái lịch hẹn công việc
@app.route('/api/admin/appointments/<int:ma_lh>/status', methods=['PUT'])
def api_update_appointment_status(ma_lh):
    data = request.json or {}
    res = appointment_service.change_status(ma_lh, data.get('trangThai'))
    return jsonify(res)

# 2. TRANG NGƯỜI DÙNG: Đặt lịch hẹn mới trực tuyến
@app.route('/booking')
def customer_booking_page():
    if "user_name" not in session:
        return redirect(url_for('login_page'))
        
    ma_kh = session.get("maKH")
    pets, services = appointment_service.get_booking_form_data(ma_kh)
    return render_template('booking.html', pets=pets, services=services, user=session["user_name"])

# API Người dùng: Xử lý submit form đặt lịch hẹn trực tuyến
@app.route('/api/booking', methods=['POST'])
def api_customer_submit_booking():
    if "user_name" not in session:
        return jsonify({"status": "error", "message": "Hết phiên đăng nhập!"}), 401
        
    data = request.json or {}
    ma_kh = session.get("maKH")
    ma_tc = data.get("maTC")
    ma_dv = data.get("maDV")
    don_gia = data.get("donGia")
    thoi_gian = data.get("thoiGian")
    phuong_thuc = data.get("phuongThuc", "Tiền mặt")
    
    from models.booking_repository import BookingRepository
    booking_repo = BookingRepository()
    
    success, err_msg = booking_repo.insert_booking_transaction(ma_kh, ma_tc, ma_dv, don_gia, thoi_gian, phuong_thuc)
    if success:
        return jsonify({"status": "success", "message": "Đặt lịch hẹn PetCare thành công!"})
    return jsonify({"status": "error", "message": f"Đặt lịch thất bại: {err_msg}"}), 400

# Import lớp Service mới thay vì import trực tiếp Repository
from services.admin_pet_service import AdminPetService

admin_pet_service = AdminPetService()

# =======================================================
# ROUTE ADMIN: QUẢN LÝ THÚ CƯNG TOÀN HỆ THỐNG
# =======================================================
@app.route('/admin/pets')
def admin_pets_page():
    if "user_name" not in session or session.get("role").strip().lower() != "admin":
        return "Từ chối truy cập! Đặc quyền này thuộc về Admin.", 403
        
    search = request.args.get('search', '').strip()
    
    # Gửi qua tầng Service xử lý nghiệp vụ
    ds_toan_bo_pet = admin_pet_service.get_all_pets_for_dashboard(search if search != '' else None)
    
    return render_template(
        'admin_pets.html', 
        pets=ds_toan_bo_pet, 
        search_query=search, 
        user=session["user_name"]
    )

# API xóa thú cưng dành riêng cho Admin gọi qua Service
@app.route('/api/admin/pets/<int:ma_tc>', methods=['DELETE'])
def api_admin_delete_pet(ma_tc):
    if "user_name" not in session or session.get("role").strip().lower() != "admin":
        return jsonify({"status": "error", "message": "Từ chối truy cập!"}), 403
        
    # Gọi Service xử lý logic xóa hồ sơ
    success, msg = admin_pet_service.process_admin_delete_pet(ma_tc)
    
    if success:
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg}), 400
# =========================================
# MY PETS
# =========================================
@app.route("/my-pets")
def my_pets():

    if "user_name" not in session:

        flash("Vui lòng đăng nhập!")

        return redirect(url_for("login_page"))

    maKH = session.get("maKH")

    if not maKH:

        flash("Không tìm thấy khách hàng!")

        return redirect(url_for("home"))

    khach_hang, ds_pets = service_pet.get_profile_data(maKH)

    return render_template(
        "my-pets.html",
        khach_hang=khach_hang,
        ds_pets=ds_pets,
        user=session.get("user_name")
    )


# =========================================
# UPDATE PROFILE
# =========================================
@app.route("/update-profile", methods=["POST"])
def update_profile():

    if "maKH" not in session:

        return redirect(url_for("login_page"))

    success, message = service_pet.update_profile(
        session["maKH"],
        request.form
    )

    flash(message)

    return redirect(url_for("my_pets"))


# =========================================
# ADD PET
# =========================================
@app.route("/add-pet", methods=["POST"])
def add_pet():

    if "maKH" not in session:

        return redirect(url_for("login_page"))

    success, message = service_pet.add_new_pet(
        request.form,
        session["maKH"]
    )

    flash(message)

    return redirect(url_for("my_pets"))


# =========================================
# DELETE PET
# =========================================
@app.route("/delete-pet/<int:maTC>", methods=["POST"])
def delete_pet(maTC):

    if "maKH" not in session:

        return redirect(url_for("login_page"))

    success, message = service_pet.remove_pet(maTC)

    flash(message)

    return redirect(url_for("my_pets"))


# =========================================
# SERVICES
# =========================================
@app.route("/services")
def services():

    conn = get_db_connection()

    ds_dich_vu = conn.execute("""
        SELECT *
        FROM DichVu
        WHERE trangThai = 'Hoạt động'
    """).fetchall()

    ds_thu_cung = []

    # LOAD PET NẾU LOGIN
    if session.get("maKH"):

        ds_thu_cung = conn.execute("""
            SELECT *
            FROM ThuCung
            WHERE maKH = ?
        """, (session["maKH"],)).fetchall()

    conn.close()

    return render_template(
        "services.html",
        ds_dich_vu=ds_dich_vu,
        ds_thu_cung=ds_thu_cung,
        user=session.get("user_name")
    )


# =========================================
# BOOKING
# =========================================
@app.route("/booking")
def booking():

    # CHƯA LOGIN
    if "user_name" not in session:

        flash("Bạn cần đăng nhập!")

        return redirect(url_for("login_page"))

    # ADMIN
    if session.get("role") == "admin":

        return redirect(url_for("admin_dashboard"))

    maKH = session.get("maKH")

    # KHÔNG CÓ KHÁCH HÀNG
    if not maKH:

        flash("Không tìm thấy thông tin khách hàng!")

        return redirect(url_for("home"))

    ds_lich_hen = booking_service.get_customer_bookings(maKH)

    return render_template(
        "booking.html",
        ds_lich_hen=ds_lich_hen,
        user=session.get("user_name")
    )


# =========================================
# RUN APP
# =========================================
if __name__ == "__main__":

    app.run(debug=True)