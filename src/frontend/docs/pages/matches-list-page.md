# Trang Danh Sách Kết Nối Phù Hợp (`matches.index.tsx`)

Trang hiển thị danh sách các hồ sơ đối phương được ghép đôi tối ưu nhất bởi AI Agent.

## 📌 Thông tin tuyến đường (Route Information)
- **File mã nguồn**: [src/routes/matches.index.tsx](file:///d:/vin/lab03/demo/cupid-matchmaker-ai/frontend/src/routes/matches.index.tsx)
- **Đường dẫn**: `/matches`

## 🎯 Chức năng chính
1. **Slideshow / Carousel Thẻ Hồ Sơ (Profile Showcase)**:
   - Cho phép người dùng duyệt qua từng kết nối phù hợp (Previous / Next).
   - Đánh dấu chỉ số phần trăm tương thích (VD: `95% khớp`).
2. **Chi tiết Tương thích & Lý do Ghép đôi (AI Matching Reasons)**:
   - Hiển thị thông tin cơ bản: Tên, Tuổi, Thành phố, Nhóm tính cách.
   - Đoạn Bio tóm tắt tính cách.
   - Danh sách các điểm tương đồng do AI trích xuất (Sở thích chung, điểm chung trong quan niệm sống).
3. **Nút tương tác**:
   - Nút "Trò chuyện & Tìm hiểu" đưa người dùng đến trang trò chuyện chi tiết `/matches/$id`.

## 🔌 Tích hợp với Backend Python
- **`matching_agent.py` & `compatibility_scoring.py`**: Khi trang được tải, gọi API `GET /api/matches?email={userEmail}`.
- Backend chạy thuật toán Cosine Similarity / Vector Search trên database để xếp hạng và trả về Top ứng viên phù hợp nhất kèm giải thích lý do ghép đôi.
