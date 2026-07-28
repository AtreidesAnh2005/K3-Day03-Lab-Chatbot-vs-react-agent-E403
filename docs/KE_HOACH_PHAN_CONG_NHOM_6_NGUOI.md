# KẾ HOẠCH PHÂN CÔNG NHÓM 6 NGƯỜI

## Lab 03 — Chatbot vs ReAct Agent

> **Repository:** `K3-Day03-Lab-Chatbot-vs-react-agent-E403`  
> **Quy mô nhóm:** 6 thành viên  
> **Thời lượng đề xuất:** 240 phút  
> **Mục tiêu:** Xây dựng Chatbot Baseline và ReAct Agent có Tool, Guardrails, Trace Log, cơ chế xử lý lỗi và luồng Hybrid.

---

## 1. Mục tiêu và sản phẩm cần bàn giao

Nhóm cần hoàn thành một hệ thống gồm hai đường xử lý:

1. **Chatbot Baseline:** dùng một lần gọi LLM, không gọi Tool.
2. **ReAct Agent:** hoạt động theo vòng lặp:

```text
Thought → Action → Observation → Thought → ... → Final Answer
```

Các artifact bắt buộc:

- `config/test_cases.json`: bộ 5 test case.
- `src/tools.py`: Tool Registry và các Tool.
- `src/prompts.py`: Baseline Prompt, ReAct Prompt và Guardrails.
- `src/app.py`: ứng dụng chính và vòng lặp ReAct.
- `src/providers.py`: bộ chuyển đổi LLM Provider.
- `docs/trace_eval.md`: Agentic Fit, Trace Log và kết quả đánh giá.
- `docs/hybrid_flowchart.mermaid`: sơ đồ phân luồng Chatbot/ReAct Agent.

### Tiêu chí nghiệm thu chung

- Chatbot Baseline không được gọi Tool.
- ReAct Agent phải gọi đúng Tool theo yêu cầu.
- Mỗi `Action` phải nhận đúng một `Observation` từ ứng dụng.
- `Observation` phải được đưa trở lại lịch sử suy luận.
- Agent không được lặp vô hạn hoặc crash khi Tool lỗi.
- Có ít nhất một success trace và một failed trace.
- Có phân tích nguyên nhân gốc và kết quả sau khi sửa Agent V2.
- Không commit `.env`, API key hoặc thông tin nhạy cảm lên Git.

---

## 2. Cơ cấu nhóm và định nghĩa vai trò

| Thành viên | Vai trò | File sở hữu chính | Trách nhiệm |
|---|---|---|---|
| Thành viên 1 | **Product Architect & Test Designer** | `config/test_cases.json` | Xác định bài toán, hành vi kỳ vọng và thiết kế test |
| Thành viên 2 | **Tool & Spec Engineer** | `src/tools.py` | Xây Tool, Tool Contract, validation và xử lý lỗi |
| Thành viên 3 | **Prompt & Safety Engineer** | `src/prompts.py` | Thiết kế Prompt, Guardrails và cơ chế phục hồi |
| Thành viên 4 | **Core Developer / Integrator** | `src/app.py`, `src/providers.py` | Tích hợp Provider, Parser, Tool Executor và ReAct Loop |
| Thành viên 5 | **Trace & Evaluation Analyst** | `docs/trace_eval.md` | Ghi Trace, chấm điểm, phân tích lỗi và so sánh |
| Thành viên 6 | **QA, Flowchart & Demo Coordinator** | `docs/hybrid_flowchart.mermaid` | Kiểm thử độc lập, Cross-Audit, Flowchart và Demo |

> **Khuyến nghị:** Trưởng nhóm giữ hoặc trực tiếp giám sát Role 4 vì đây là vị trí nằm trên critical path và chịu trách nhiệm tích hợp toàn bộ sản phẩm.

### 2.1. Role 1 — Product Architect & Test Designer

**Mục tiêu:** Đảm bảo nhóm đang giải đúng bài toán và có tiêu chí nghiệm thu rõ ràng.

Nhiệm vụ:

- Viết Problem Statement và mô tả người dùng mục tiêu.
- Xác định khi nào chỉ cần Chatbot, khi nào bắt buộc dùng Agent.
- Thiết kế đúng 5 test case:
  - 2 câu hỏi đơn giản, chỉ cần LLM.
  - 1 câu hỏi cần một Tool.
  - 1 câu hỏi cần hai Tool.
  - 1 Edge Case để kiểm tra Guardrail.
- Viết `expected_behavior` đủ rõ để Role 5 có thể chấm điểm.
- Không sửa test case sau khi đã thấy kết quả chỉ để làm Agent dễ pass hơn.

### 2.2. Role 2 — Tool & Spec Engineer

**Mục tiêu:** Cung cấp các Tool deterministic, có contract rõ ràng và không làm ứng dụng crash.

Nhiệm vụ:

- Xây dựng và kiểm thử các Tool trong `src/tools.py`.
- Với mỗi Tool, xác định:
  - Name.
  - Purpose.
  - Input schema.
  - Output schema.
  - Error semantics.
  - Side effect.
  - Example.
  - Safety.
- Validate kiểu dữ liệu và giá trị đầu vào.
- Khi gặp lỗi nghiệp vụ, trả về thông báo lỗi rõ ràng thay vì ném exception làm dừng chương trình.
- Đăng ký đầy đủ Tool trong `AVAILABLE_TOOLS`.
- Hỗ trợ Role 4 xây Tool Dispatcher.

### 2.3. Role 3 — Prompt & Safety Engineer

**Mục tiêu:** Kiểm soát cách LLM suy luận, sử dụng Tool và dừng an toàn.

Nhiệm vụ:

- Viết `CHATBOT_BASELINE_PROMPT`.
- Viết `REACT_SYSTEM_PROMPT`.
- Quy định định dạng:

```text
Thought: ...
Action: tool_name[arguments]
```

hoặc:

```text
Thought: ...
Final Answer: ...
```

- Chỉ cho phép Final Answer khi đã có đủ bằng chứng.
- Định nghĩa `MAX_ITERATIONS` và timeout.
- Bổ sung recovery rule cho:
  - Unknown Tool.
  - Malformed Arguments.
  - Tool Error.
  - Repeated Action.
  - Final Answer quá sớm.
- Phối hợp với Role 4 để bảo đảm Parser hiểu đúng format Prompt.

### 2.4. Role 4 — Core Developer / Integrator

**Mục tiêu:** Ghép các thành phần thành ứng dụng Chatbot và ReAct Agent hoàn chỉnh.

Nhiệm vụ:

- Setup môi trường và kiểm tra LLM Provider.
- Load toàn bộ test case.
- Xây `run_baseline_chatbot()`.
- Xây vòng lặp ReAct tổng quát:

```text
Gọi LLM
   ↓
Parse Thought/Action
   ↓
Tìm Tool trong AVAILABLE_TOOLS
   ↓
Validate Arguments
   ↓
Execute Tool
   ↓
Append Observation vào lịch sử
   ↓
Gọi LLM ở vòng tiếp theo
```

- Không hard-code riêng một câu hỏi hoặc một thành phố.
- Xử lý Parser Error, Unknown Tool và Tool Exception.
- Theo dõi Action History để nhận biết hành động lặp.
- Dừng bằng Final Answer hoặc Safe Fallback.
- Pull và tích hợp kết quả của các Role khác.
- Chạy full regression trước khi merge vào `main`.

### 2.5. Role 5 — Trace & Evaluation Analyst

**Mục tiêu:** Chứng minh Agent hoạt động đúng bằng evidence, không chỉ dựa trên câu trả lời cuối.

Nhiệm vụ:

- Điền Agentic Fit Scoring Matrix.
- Lưu kết quả Chatbot Baseline trên 5 test case.
- Phân loại kết quả:
  - `correct`
  - `safe fallback`
  - `hallucinated`
- Ghi lại chuỗi `Thought → Action → Observation`.
- Thu thập ít nhất:
  - 1 success trace.
  - 1 failed trace.
- Phân tích Root Cause:
  - Biểu hiện.
  - Nguyên nhân.
  - Cách sửa.
  - Kết quả Agent V2.
- Chấm từng test theo:
  - Factual correctness.
  - Grounding.
  - Tool selection.
  - Termination.

### 2.6. Role 6 — QA, Flowchart & Demo Coordinator

**Mục tiêu:** Đóng vai trò kiểm thử độc lập và bảo đảm sản phẩm sẵn sàng trình bày.

Nhiệm vụ:

- Xây checklist QA và regression test.
- Thực hiện Black-box Testing, không phụ thuộc vào giả định của người viết code.
- Chuẩn bị các câu hỏi Cross-Audit ngoài bộ test chính.
- Kiểm tra:
  - Tool được gọi đúng hay không.
  - Agent có lặp Action không.
  - Agent có trả Final Answer quá sớm không.
  - Guardrail có dừng Agent an toàn không.
- Vẽ `docs/hybrid_flowchart.mermaid`.
- Chuẩn bị kịch bản demo và phân công người trình bày.
- Ghi lại bug, mức độ nghiêm trọng và người chịu trách nhiệm xử lý.

---

## 3. Lịch trình tổng thể

| Thời gian | Giai đoạn | Mục tiêu |
|---|---|---|
| T+00 → T+25 | Pre-flight | Setup, Smoke Test và thống nhất Workflow |
| T+25 → T+45 | Mốc 1 — Agentic Fit | Chứng minh bài toán phù hợp với Agent |
| T+45 → T+75 | Mốc 2 — Baseline & Tool Specs | Hoàn thành Baseline, Test Cases và Tool Contract |
| T+75 → T+135 | Mốc 3 — ReAct Loop | Xây Parser, Executor, Observation Loop và Guardrails |
| T+135 → T+175 | Mốc 4 — Cross-Audit & Hybrid | Kiểm thử tấn công/phòng thủ và Hybrid Routing |
| T+175 → T+215 | Agent V2 & Evaluation | RCA, Recovery và chạy đầy đủ 5 Test Cases |
| T+215 → T+240 | Final QA & Demo | Security Check, Report, Merge và chuẩn bị trình bày |

---

## 4. Kế hoạch chi tiết theo từng mốc

### 4.1. Pre-flight — T+00 đến T+25

**Mục tiêu:** Tất cả thành viên chạy được repository và hiểu phần việc của mình.

| Role | Công việc |
|---|---|
| R1 | Kiểm tra bộ 5 test hiện tại và chốt chủ đề bài toán |
| R2 | Chạy thử độc lập các Tool hiện có |
| R3 | Đọc Prompt và liệt kê các Rule còn thiếu |
| R4 | Tạo môi trường, cài dependencies, cấu hình Mock Provider và chạy `python src/app.py` |
| R5 | Chuẩn bị template báo cáo và bảng scoring |
| R6 | Chuẩn bị checklist QA, demo và danh sách artifact |

**Checkpoint:**

- [ ] Sáu thành viên clone được repository.
- [ ] `python src/app.py` chạy không crash.
- [ ] Mỗi thành viên đã tạo branch riêng.
- [ ] Không có API key trong commit.
- [ ] Nhóm thống nhất giữ hoặc thay đổi chủ đề hiện tại.

---

### 4.2. Mốc 1 — Agentic Fit, T+25 đến T+45

**Mục tiêu:** Chứng minh bài toán cần Agent thay vì chỉ dùng Chatbot.

| Role | Công việc |
|---|---|
| R1 | Viết Problem Statement, actor, nhu cầu và expected workflow |
| R2 | Chốt danh sách Tool và dependency giữa các Tool |
| R3 | Liệt kê Failure Mode và Safety Rule |
| R4 | Xác nhận luồng dữ liệu Test → Agent → Tool → Observation |
| R5 | Điền Agentic Fit Matrix trong `trace_eval.md` |
| R6 | Review tính nhất quán giữa bài toán, Tool và Test Case |

**Checkpoint:**

- [ ] Có Problem Statement thống nhất.
- [ ] Agentic Fit đạt khoảng 14/20 trở lên.
- [ ] Danh sách Tool đã được khóa.
- [ ] Có danh sách Failure Mode.
- [ ] Toàn nhóm đồng ý chuyển sang Mốc 2.

---

### 4.3. Mốc 2 — Baseline & Tool Specs, T+45 đến T+75

**Mục tiêu:** Tạo đường cơ sở công bằng và chuẩn hóa Tool trước khi tích hợp Agent.

| Role | Công việc |
|---|---|
| R1 | Hoàn thiện 5 Test Cases và `expected_behavior` |
| R2 | Hoàn thiện Docstring, Schema, Validation và Error Response |
| R3 | Hoàn thiện `CHATBOT_BASELINE_PROMPT` |
| R4 | Chạy Baseline trên cả 5 Test Cases |
| R5 | Lưu và phân loại Output của Baseline |
| R6 | Xác minh Baseline không gọi Tool và chuẩn bị câu Cross-Audit |

**Checkpoint:**

- [ ] Hai câu đơn giản được Baseline xử lý hợp lý.
- [ ] Câu cần dữ liệu thực tế trả Safe Fallback thay vì bịa đặt.
- [ ] Baseline dùng đúng một LLM Call cho mỗi Test Case.
- [ ] Tool chạy độc lập không crash.
- [ ] Kết quả Baseline đã được lưu vào báo cáo.

---

### 4.4. Mốc 3 — ReAct Loop, T+75 đến T+135

**Mục tiêu:** Xây ReAct Agent thật sự thay vì demo hard-code.

| Role | Công việc |
|---|---|
| R1 | Chạy Test 3–5 và so sánh với `expected_behavior` |
| R2 | Hỗ trợ Tool Dispatcher và kiểm tra Arguments |
| R3 | Hoàn thiện ReAct Format, Guardrails và Recovery Rules |
| R4 | Implement LLM Call, Action Parser, Tool Executor, Observation History và Termination |
| R5 | Thu thập Success Trace và Failed Trace |
| R6 | Black-box Test bằng Input lạ và ghi Bug |

**Checkpoint:**

- [ ] Test 3 gọi đúng một Tool.
- [ ] Test 4 gọi đúng hai Tool.
- [ ] Test 5 không làm ứng dụng crash.
- [ ] Không còn hard-code riêng câu hỏi Hà Nội.
- [ ] Observation thật được đưa vào Prompt vòng sau.
- [ ] Agent dừng bằng Final Answer hoặc Safe Fallback.

---

### 4.5. Mốc 4 — Cross-Audit & Hybrid Flow, T+135 đến T+175

**Mục tiêu:** Kiểm tra khả năng chịu lỗi và thiết kế cơ chế chọn Chatbot/Agent.

| Role | Công việc |
|---|---|
| R1 | Chuẩn bị câu hỏi nghiệp vụ ngoài bộ Test chính |
| R2 | Theo dõi việc gọi sai Tool hoặc truyền Arguments bất thường |
| R3 | Thử Repeated Action, Malformed Format và Prompt Injection đơn giản |
| R4 | Sửa lỗi Integration; khóa Feature sau T+165 |
| R5 | Ghi kết quả Attack/Defense vào Trace Report |
| R6 | Điều phối Cross-Audit và hoàn thiện Hybrid Flowchart |

Hybrid Flow cần thể hiện:

```text
Câu hỏi kiến thức đơn giản
→ Chatbot Baseline

Câu hỏi cần dữ liệu mới, nhiều bước hoặc Tool
→ ReAct Agent

Tool lỗi, Parse lỗi hoặc hết Iteration
→ Safe Fallback
```

**Checkpoint:**

- [ ] Có ít nhất hai câu hỏi Cross-Audit.
- [ ] Có biên bản Attack/Defense.
- [ ] Có `docs/hybrid_flowchart.mermaid`.
- [ ] Agent không lặp vô hạn trước Input từ nhóm khác.

---

### 4.6. Agent V2 & Evaluation — T+175 đến T+215

**Mục tiêu:** Sửa lỗi dựa trên evidence và đánh giá lại phiên bản Agent V2.

| Role | Công việc |
|---|---|
| R1 | Khóa bộ Test; không thay đổi Expected Behavior |
| R2 | Hoàn thiện Invalid Location và Invalid Arguments |
| R3 | Thêm Recovery cho Unknown Tool, Malformed Arguments và Repeated Action |
| R4 | Implement Action History, Parse Recovery và Safe Fallback |
| R5 | Chạy Baseline/Agent trên 5 Test và chấm điểm |
| R6 | Regression Test Agent V2 và xác minh Bug cũ không tái xuất hiện |

**Checkpoint:**

- [ ] Có ít nhất một Failed Trace được phân tích.
- [ ] Có Root Cause và giải pháp tương ứng.
- [ ] Agent V2 không crash ở Edge Case.
- [ ] Bảng so sánh Baseline, Agent V1 và Agent V2 đã hoàn thành.

---

### 4.7. Final QA & Demo — T+215 đến T+240

**Mục tiêu:** Tạo phiên bản cuối có thể nộp và trình bày.

| Role | Công việc |
|---|---|
| R1 | Xác nhận Test và Expected Behavior nhất quán |
| R2 | Chạy lại Smoke Test toàn bộ Tool |
| R3 | Kiểm tra Prompt và Guardrails lần cuối |
| R4 | Merge, chạy Full Demo và tạo Release Candidate |
| R5 | Hoàn thiện Scoring, Trace và RCA |
| R6 | Chuẩn bị Demo Script, Flowchart và phân công trình bày |

**Final Checklist:**

- [ ] Chạy được cả 5 Test Cases.
- [ ] Không có Hard-coded Answer trong ReAct Loop.
- [ ] Không có `.env`, API key hoặc PII trong Git.
- [ ] Có `trace_eval.md` hoàn chỉnh.
- [ ] Có `hybrid_flowchart.mermaid`.
- [ ] Có ít nhất một success trace và một failed trace.
- [ ] Có Root Cause Analysis và kết quả Agent V2.
- [ ] Nhóm đã chạy thử Demo ít nhất một lần.

---

## 5. Git Workflow

### 5.1. Branch của từng Role

```text
role1-product
role2-tools
role3-prompts
role4-integrator
role5-evaluation
role6-qa-demo
```

### 5.2. Quy trình làm việc

Trước khi bắt đầu:

```bash
git switch main
git pull origin main
git switch -c roleX-ten-role
```

Khi hoàn thành một phần:

```bash
git add <file-phu-trach>
git commit -m "Role X: mo ta thay doi"
git push -u origin roleX-ten-role
```

Sau đó tạo Pull Request vào `main`.

### 5.3. Thứ tự tích hợp

```text
Role 1 — Test Cases
        ↓
Role 2 — Tools
        ↓
Role 3 — Prompts
        ↓
Role 4 — Core Integration
        ↓
Role 5 — Evaluation Report
        ↓
Role 6 — QA, Flowchart và Demo
```

### 5.4. Quy tắc tránh conflict

- Mỗi Role chỉ chỉnh sửa file mình sở hữu.
- Nếu cần sửa file của Role khác, phải trao đổi trước.
- Không push trực tiếp vào `main`.
- Không dùng `git push --force` trên branch chung.
- Role 4 chỉ merge khi phần tương ứng chạy độc lập.
- Pull Request phải mô tả:
  - Đã thay đổi gì.
  - Cách kiểm thử.
  - Kết quả.
  - Vấn đề còn tồn tại.

---

## 6. Phân công trình bày

| Nội dung | Người trình bày |
|---|---|
| Problem Statement và Agentic Fit | Role 1 |
| Tool Contract và Tool Demo | Role 2 |
| ReAct Prompt và Guardrails | Role 3 |
| Kiến trúc và Live Demo | Role 4 |
| Kết quả, Trace và Root Cause Analysis | Role 5 |
| Hybrid Flow và Cross-Audit | Role 6 |

### Demo Script đề xuất

1. Giới thiệu bài toán và lý do cần Agent.
2. Chạy một câu hỏi đơn giản bằng Chatbot Baseline.
3. Chạy Test Case cần một Tool.
4. Chạy Test Case cần hai Tool.
5. Chạy Edge Case để kích hoạt Guardrail.
6. Mở Trace Log và giải thích `Thought → Action → Observation`.
7. Trình bày Failed Trace, Root Cause và Agent V2.
8. Kết luận khi nào dùng Chatbot, khi nào dùng ReAct Agent.

---

## 7. Quy tắc điều hành của trưởng nhóm

- Thực hiện checkpoint tối đa 3 phút sau mỗi mốc.
- Không chuyển mốc khi checkpoint hiện tại chưa đạt.
- Role 4 chịu trách nhiệm theo dõi critical path.
- Role 6 là người nghiệm thu độc lập, không tự sửa code của Role 2–4 khi chưa trao đổi.
- Sau T+175 không thêm Feature mới; chỉ sửa Bug, hoàn thiện Evaluation và Demo.
- Không làm Bonus Planning/Memory trước khi 5 Test Cases chính đã pass.
- Ưu tiên theo thứ tự:
  1. ReAct Loop hoạt động thật.
  2. Multi-tool Test pass.
  3. Edge Case dừng an toàn.
  4. Trace và RCA đầy đủ.
  5. Hybrid Flowchart.
  6. Bonus Autonomous Agent.

---

## 8. Bảng điền tên thành viên

| Role | Thành viên | GitHub Username |
|---|---|---|
| Role 1 — Product Architect & Test Designer |  |  |
| Role 2 — Tool & Spec Engineer |  |  |
| Role 3 — Prompt & Safety Engineer |  |  |
| Role 4 — Core Developer / Integrator |  |  |
| Role 5 — Trace & Evaluation Analyst |  |  |
| Role 6 — QA, Flowchart & Demo Coordinator |  |  |

---

## 9. Definition of Done

Bài Lab được xem là hoàn thành khi:

- [ ] Cả Chatbot Baseline và ReAct Agent chạy được.
- [ ] ReAct Agent sử dụng Tool thông qua `AVAILABLE_TOOLS`.
- [ ] Có cơ chế Parser, Executor và Observation History.
- [ ] Test Case cần hai Tool được xử lý đúng.
- [ ] Edge Case không làm chương trình crash hoặc lặp vô hạn.
- [ ] Guardrail `MAX_ITERATIONS` hoạt động.
- [ ] Có Success Trace, Failed Trace và Root Cause Analysis.
- [ ] Agent V2 thể hiện cải thiện so với Agent V1.
- [ ] Có bảng đánh giá định lượng.
- [ ] Có Hybrid Flowchart.
- [ ] Repository không chứa Secret.
- [ ] Nhóm hoàn thành chạy thử Demo.

