# Root Layout & Navigation Systems (`__root.tsx`)

Bố cục tổng thể và khung điều hướng toàn cục cho ứng dụng Cupid Matchmaker AI.

## 📌 Thông tin tuyến đường (Route Information)
- **File mã nguồn**: [src/routes/__root.tsx](file:///d:/vin/lab03/demo/cupid-matchmaker-ai/frontend/src/routes/__root.tsx)
- **Đường dẫn**: Tất cả các trang trong ứng dụng đều nằm trong Layout này.

## 🎯 Chức năng chính
1. **Header & Navigation**:
   - Logo thương hiệu **Cupid Agent** kết hợp icon trái tim.
   - Nút điều hướng linh hoạt dựa trên trạng thái đăng nhập/hồ sơ của người dùng (Trang chủ, Onboarding, Kết nối).
   - Nút **Đăng xuất / Đăng nhập lại**.
2. **Quản lý SEO & Font chữ**:
   - Tải font Google Fonts (`Instrument Serif` & `Inter`).
   - Cấu hình Meta Tags, Open Graph (`og:title`, `og:description`).
3. **Xử lý Lỗi & 404 (Boundary Handling)**:
   - Thành phần `NotFoundComponent`: Hiển thị trang 404 thân thiện khi truy cập sai đường dẫn.
   - Thành phần `ErrorComponent`: Bắt lỗi Runtime với khả năng khôi phục (Reset state, Invalidate router).
   - Tích hợp báo lỗi với Lovable Error Reporting.

## 🔌 Tích hợp với Backend Python
- Header hiển thị thông tin User Authenticated từ Local Storage hoặc Session Token nhận từ backend REST API (`/api/auth/me`).
