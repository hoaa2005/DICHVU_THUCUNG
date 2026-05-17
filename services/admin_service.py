from models.admin_repository import AdminRepository

class AdminService:
    def __init__(self):
        self.repo = AdminRepository()

    def load_admin_dashboard(self):
        thong_ke = self.repo.get_admin_stats()
        ds_moi = self.repo.get_recent_bookings()
        return thong_ke, ds_moi