# Cupid Matchmaker AI — Monorepo Architecture

Dự án Cupid Matchmaker AI hỗ trợ ghép đôi thông minh bằng AI Agent. Tất cả giao diện Web đã được đóng gói vào thư mục `frontend/`.

## 📁 Cấu trúc Thư mục Dự án

```text
cupid-matchmaker-ai/
├── frontend/                               <-- Giao diện Web (React, TanStack Start, Tailwind v4)
│   ├── src/
│   │   ├── components/                     <-- UI components & shadcn/ui
│   │   ├── routes/                         <-- Pages & Routing (Onboarding, Matches, Chat)
│   │   ├── lib/
│   │   │   ├── cupid-store.ts              <-- Types & State management
│   │   │   └── api-client.ts               <-- REST API Client gửi request tới Backend
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.ts
│
└── src/                                    <-- Backend Python (Multi-Agent System)
    ├── app.py                              <-- Main FastAPI server
    ├── providers.py
    ├── multi_agent/                        <-- Supervisor, Dispatcher, Router & Builder
    ├── agents/                             <-- Profile, Matching, Date Planning, Safety Agents
    ├── subgraphs/                          <-- LangGraph Workflows
    ├── tools/                              <-- Profile, Matching, Date Tools
    ├── services/                           <-- Compatibility Scoring & Filtering
    └── observability/                      <-- Langfuse Logging & Monitoring
```

## 🚀 Khởi chạy Frontend

```bash
cd frontend
npm install
npm run dev
```

Ứng dụng web sẽ chạy tại `http://localhost:3000` (hoặc `http://localhost:5173`).

## 🔌 Kết nối với Backend Python FastAPI

Frontend gọi API tới Backend mặc định tại `http://localhost:8000/api`. Bạn có thể tùy chỉnh URL backend bằng file `.env` trong folder `frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Các Endpoint chính do Backend phục vụ:
- `POST /api/profile`: Tiếp nhận hồ sơ & câu trả lời khảo sát từ `profile_agent.py`.
- `GET /api/matches`: Lấy danh sách ghép đôi tương thích từ `matching_agent.py` & `compatibility_scoring.py`.
- `POST /api/chat`: Gửi câu hỏi / trò chuyện thông qua `safety_critic_agent.py` & `response_agent.py`.
