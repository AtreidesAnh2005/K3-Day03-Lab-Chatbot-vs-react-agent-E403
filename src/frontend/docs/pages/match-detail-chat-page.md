# Trang Chi Tiết & Trò Chuyện Ghép Đôi (`matches.$id.tsx`)

Trang hiển thị thông tin chuyên sâu của một đối phương cụ thể và tích hợp khung chat tương tác trực tiếp được kiểm duyệt bởi AI.

## 📌 Thông tin tuyến đường (Route Information)
- **File mã nguồn**: [src/routes/matches.$id.tsx](file:///d:/vin/lab03/demo/cupid-matchmaker-ai/frontend/src/routes/matches.$id.tsx)
- **Đường dẫn**: `/matches/$id` (Ví dụ: `/matches/c1`, `/matches/c2`)

## 🎯 Chức năng chính
1. **Phân tích Đa chiều (Multi-dimensional Compatibility Analysis)**:
   - Hiển thị biểu đồ thanh tiến trình phân tích chi tiết theo 4 khía cạnh:
     - Giá trị sống (% Compatibility)
     - Phong cách giao tiếp
     - Sở thích chung
     - Nhịp sống & thói quen
2. **Khung Trò Chuyện & Gợi Ý Chủ Đề (Interactive Chat Box & Topic Starters)**:
   - Gợi ý sẵn các câu mở lời phá băng (Icebreakers) thông minh.
   - Nhập tin nhắn và trò chuyện tương tác trực quan.
   - Thông báo về sự hiện diện của **Safety Critic Agent** (giữ gìn môi trường trò chuyện văn minh, an toàn & riêng tư).

## 🔌 Tích hợp với Backend Python
- **`date_planning_agent.py` & `date_tools.py`**: Gợi ý các ý tưởng hẹn hò / chủ đề trò chuyện phù hợp dựa trên điểm chung của 2 người.
- **`safety_critic_agent.py` & `response_agent.py`**: Nhận tin nhắn chat từ frontend via `POST /api/chat`, lọc nội dung nhạy cảm / không an toàn và phản hồi câu trả lời tự nhiên.
