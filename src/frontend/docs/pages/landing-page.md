# Trang Chủ / Landing Page (`index.tsx`)

Trang đầu tiên khi người dùng truy cập Cupid Agent, giới thiệu mô hình ghép đôi bằng AI và hỗ trợ đăng nhập nhanh.

## 📌 Thông tin tuyến đường (Route Information)
- **File mã nguồn**: [src/routes/index.tsx](file:///d:/vin/lab03/demo/cupid-matchmaker-ai/frontend/src/routes/index.tsx)
- **Đường dẫn**: `/`

## 🎯 Chức năng chính
1. **Hero Section & Giới thiệu Giá trị**:
   - Tiêu đề nổi bật: "Tìm người phù hợp bằng phân tích tính cách thay vì chỉ hình ảnh."
   - 3 điểm nổi bật: Hồ sơ sâu (Personality profiling), Vector matching (Độ tương thích AI), Riêng tư (Bảo vệ bởi Safety Critic Agent).
2. **Form Đăng Nhập Nhanh (Quick Authentication)**:
   - Nhập tên và Email.
   - Tự động điều hướng:
     - Nếu chưa có hồ sơ -> chuyển tới `/onboarding`.
     - Nếu đã hoàn thành hồ sơ -> chuyển tới `/matches`.

## 📸 Thành phần Giao diện (UI Components)
- `Feature Card`: Thẻ mô tả các tính năng chính của hệ thống Multi-Agent.
- Background Gradient Romance & Hình ảnh Hero nghệ thuật đại diện cho sự kết nối tình yêu qua AI.

## 🔌 Tích hợp với Backend Python
- Khi submit Form Đăng nhập: Gọi API Backend `POST /api/auth/login` (hoặc gửi thông tin sang `profile_agent.py`) để khởi tạo Session.
