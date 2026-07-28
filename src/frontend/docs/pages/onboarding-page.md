# Trang Khảo Sát & Khởi Tạo Hồ Sơ (`onboarding.tsx`)

Trang bộ câu hỏi tương tác thích ứng giúp AI hiểu rõ tính cách, sở thích và giá trị sống của người dùng.

## 📌 Thông tin tuyến đường (Route Information)
- **File mã nguồn**: [src/routes/onboarding.tsx](file:///d:/vin/lab03/demo/cupid-matchmaker-ai/frontend/src/routes/onboarding.tsx)
- **Đường dẫn**: `/onboarding`

## 🎯 Chức năng chính
1. **Bộ câu hỏi cốt lõi (Core Questions)**:
   - Thu thập Giới tính, Năm sinh, Kiểu tính cách chủ đạo (`introvert`, `extrovert`, `analytical`, `creative`, `adventurous`, v.v.).
2. **Bộ câu hỏi mở rộng thích ứng (Dynamic Deep Questions)**:
   - Dựa trên nhóm tính cách người dùng chọn ở câu hỏi trước, giao diện sẽ mở rộng các câu hỏi chuyên sâu tương ứng (VD: Phong cách làm việc, quan niệm tình yêu, giao tiếp).
3. **Màn hình Xử lý Vector Embedding (`EmbeddingScreen`)**:
   - Sau khi hoàn thành câu hỏi cuối cùng, ứng dụng hiển thị animation chờ AI Agent trích xuất đặc trưng tính cách và tính toán Vector Embeddings.
   - Tự động điều hướng sang trang kết quả `/matches`.

## 🔌 Tích hợp với Backend Python
- **`profile_agent.py` & `profile_graph.py`**: Tiếp nhận dữ liệu khảo sát từ frontend qua API `POST /api/profile`.
- Backend thực hiện Embed văn bản trả lời thành Vector trong DB (Milvus/Qdrant/Pinecone) và trả về kết quả thành công cho frontend.
