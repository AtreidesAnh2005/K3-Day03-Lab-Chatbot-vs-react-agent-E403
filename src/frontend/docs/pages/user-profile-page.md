# Trang Hồ Sơ Cá Nhân Người Dùng (`profile-page.md`)

Trang hiển thị đầy đủ thông tin cá nhân, kết quả khảo sát tính cách và trạng thái Vector Embedding do **Profile Agent** tạo ra.

## 📌 Thông tin tuyến đường (Route Information)
- **File mã nguồn**: [src/routes/profile.tsx](file:///d:/vin/lab03/demo/cupid-matchmaker-ai/frontend/src/routes/profile.tsx)
- **Đường dẫn**: `/profile`

## 🎯 Chức năng chính
1. **Thông tin tổng quan (User Profile Card)**:
   - Tên người dùng, Email, Giới tính, Tuổi.
   - Nhãn nhóm tính cách chủ đạo (Hướng nội, Hướng ngoại, Sáng tạo, Phiêu lưu,...).
   - Trạng thái Vector Embedding (Đã mã hóa 512 chiều).
2. **Thẻ phân tích Vector Profile Agent**:
   - Tóm tắt đặc trưng tính cách và chỉ số độ mở cá nhân.
   - Trạng thái bảo mật thông tin được kiểm duyệt bởi Safety Critic Agent.
3. **Danh sách câu hỏi & câu trả lời đã thực hiện**:
   - Hiển thị lại toàn bộ bộ câu hỏi cốt lõi và câu hỏi mở rộng cùng câu trả lời của người dùng.
4. **Nút chuyển hướng**:
   - **"Xem các kết nối phù hợp"**: Đưa người dùng đến trang `/matches`.
   - **"Cập nhật lại câu hỏi tính cách"**: Quay lại trang khảo sát `/onboarding`.
   - **"Đăng xuất"**: Đăng xuất tài khoản và đưa người dùng về Trang chủ `/`.

## 🔌 Tích hợp với Backend Python
- **`profile_agent.py` & `profile_graph.py`**: Nơi lưu giữ và truy xuất thông tin vector profile của người dùng qua API `GET /api/profile/me`.
