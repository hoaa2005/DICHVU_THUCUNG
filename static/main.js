// =======================
// LOGIN
// =======================
function login() {
  const email = document.getElementById("loginEmail").value.trim();
  const pass = document.getElementById("loginPass").value.trim();

  // VALIDATE
  if (!email || !pass) {
    showToast("⚠️ Vui lòng nhập đầy đủ thông tin");
    return;
  }

  fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: email,
      password: pass
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.message === "OK") {
      setTimeout(() => {
    window.location.href = "/home";
    }, 1000);

      // phân quyền
      if (data.role === "admin") {
        showToast("👑 Admin");
      } else {
        showToast("🐾 Khách hàng");
      }
    } else {
      showToast("❌ Sai tài khoản hoặc mật khẩu");
    }
  })
  .catch(() => {
    showToast("❌ Lỗi kết nối server");
  });
}

// =======================
// REGISTER
// =======================
function register() {
  const name = document.getElementById("regName").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const phone = document.getElementById("regPhone").value.trim();
  const pass = document.getElementById("regPass").value.trim();

  // VALIDATE
  if (!name || !email || !phone || !pass) {
    showToast("⚠️ Nhập đầy đủ thông tin");
    return;
  }

  if (pass.length < 3) {
    showToast("⚠️ Mật khẩu quá ngắn");
    return;
  }

  fetch("/register", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: email,
      password: pass,
      ten: name,
      sdt: phone
    })
  })
  .then(res => res.json())
  .then(data => {
    showToast(data.message);
  })
  .catch(() => {
    showToast("❌ Lỗi server");
  });
}
// Tự động ẩn các thông báo Flash sau 3 giây
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.animate-fade-in');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            msg.style.transition = 'all 0.5s ease';
            setTimeout(() => msg.remove(), 500);
        }, 3000);
    });
});

// Đảm bảo các icons luôn được load lại khi mở modal
function toggleModal(id) {
    const modal = document.getElementById(id);
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        lucide.createIcons(); // Load lại icons nếu cần
    } else {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }
}