from models.booking_repository import BookingRepository


class BookingService:

    def __init__(self):
        self.repo = BookingRepository()

    # =========================================
    # ĐĂNG NHẬP
    # =========================================
    def authenticate_user_session(self, username, password):

        # KIỂM TRA RỖNG
        if not username or not password:
            return {
                "status": "error",
                "message": "Vui lòng nhập tài khoản và mật khẩu!"
            }

        # TÌM USER
        user_row = self.repo.find_account_by_credentials(
            username,
            password
        )

        # SAI TK MK
        if not user_row:
            return {
                "status": "error",
                "message": "Sai tài khoản hoặc mật khẩu!"
            }

        maTK = user_row["maTK"]
        role = user_row["vaiTro"]

        # =====================================
        # ADMIN
        # =====================================
        if role == "admin":

            return {
                "status": "success",

                "message": "Đăng nhập thành công!",

                "session_data": {
                    "user_name": username,
                    "role": role,
                    "maKH": None
                },

                "redirect_url": "/admin/dashboard"
            }

        # =====================================
        # KHÁCH HÀNG
        # =====================================

        maKH = self.repo.get_customer_by_account(maTK)

        # CHƯA CÓ KHÁCH HÀNG
        if maKH is None:

            maKH = self.repo.create_customer(
                maTK,
                username
            )

        return {

            "status": "success",

            "message": "Đăng nhập thành công!",

            "session_data": {

                "user_name": username,

                "role": role,

                "maKH": maKH
            },

            "redirect_url": "/home"
        }

    # =========================================
    # ĐẶT LỊCH
    # =========================================
    def process_new_booking(self, maKH, form_data):

        maDV = form_data.get("maDV")
        donGia = form_data.get("donGia")
        maTC = form_data.get("maTC")
        thoiGian = form_data.get("thoiGian")
        phuongThuc = form_data.get("phuongThuc")

        # VALIDATE
        if not all([
            maDV,
            donGia,
            maTC,
            thoiGian,
            phuongThuc
        ]):

            return False, "Thiếu dữ liệu!"

        try:

            maDV = int(maDV)
            maTC = int(maTC)
            donGia = float(donGia)

            # FORMAT DATETIME
            thoiGian = thoiGian.replace("T", " ")

            if len(thoiGian) == 16:
                thoiGian += ":00"

            # INSERT
            success, error_msg = self.repo.insert_booking_transaction(

                maKH=maKH,

                maTC=maTC,

                maDV=maDV,

                donGia=donGia,

                thoiGian=thoiGian,

                phuongThuc=phuongThuc
            )

            if success:
                return True, "Đặt lịch thành công!"

            return False, error_msg

        except Exception as e:
            return False, str(e)

    # =========================================
    # LẤY DANH SÁCH BOOKING
    # =========================================
    def get_customer_bookings(self, maKH):

        if not maKH:
            return []

        return self.repo.get_bookings_by_customer(maKH)