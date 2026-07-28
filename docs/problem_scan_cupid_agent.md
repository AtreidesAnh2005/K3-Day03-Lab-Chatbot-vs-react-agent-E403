# 01 — Individual Problem Scan

> **Bối cảnh giả định:** Cupid Agent phục vụ người trưởng thành đang tìm kiếm mối quan hệ trên một nền tảng ghép đôi. Agent chỉ sử dụng hồ sơ, câu trả lời và dữ liệu hội thoại mà các bên **chủ động cho phép**; không thu thập dữ liệu ngoài nền tảng, không tự nhắn tin thay người dùng và không xem “điểm tương thích” là kết luận tuyệt đối. Các mốc thời gian và mục tiêu dưới đây là **giả thuyết cho pilot**, cần được kiểm chứng bằng phỏng vấn, usability test và log sử dụng trước khi trở thành cam kết sản phẩm.

## Scan rộng

| # | Lăng kính | Problem quan sát được | Ai chịu ảnh hưởng? | Dấu hiệu thật / cách kiểm chứng tiếp |
|---|---|---|---|---|
| 1 | Tốn thời gian | Người dùng phải đọc nhiều hồ sơ nhưng vẫn khó nhận ra ai thực sự phù hợp về mục tiêu quan hệ, giá trị sống và lối sống | Người dùng ứng dụng hẹn hò, đặc biệt là người tìm mối quan hệ nghiêm túc | Đo số hồ sơ đã xem, thời gian đến shortlist đầu tiên và tỷ lệ bỏ phiên; phỏng vấn 8–12 người dùng |
| 2 | Lặp lại | Những câu hỏi cơ bản như mục tiêu quan hệ, lịch sinh hoạt, sở thích hoặc quan điểm gia đình phải được hỏi lại trong nhiều cuộc trò chuyện | Người dùng đang đồng thời tìm hiểu nhiều đối tượng | Diary study trong 1–2 tuần để thống kê câu hỏi lặp lại và thời gian dành cho giai đoạn làm quen |
| 3 | AI có thể tốt hơn | Các bộ lọc hiện tại thường dựa trên thuộc tính bề mặt, trong khi tương thích dài hạn còn phụ thuộc vào giá trị, cách giao tiếp, ranh giới và ưu tiên tương lai | Người tìm mối quan hệ lâu dài | So sánh độ hữu ích của bộ lọc truyền thống với phân tích đa chiều trên các cặp đã được người dùng tự đánh giá |
| 4 | Tốn công nhận thức | Người dùng khó phân biệt “điều bắt buộc”, “điều mong muốn” và “điều có thể thỏa hiệp”, nên tiêu chí thay đổi trong quá trình chọn | Người dùng mới hoặc chưa xác định rõ nhu cầu | Quan sát think-aloud khi người dùng lập tiêu chí; đo số lần đổi filter và lý do loại/chọn hồ sơ |
| 5 | Pain từ người khác | Ý định quan hệ không rõ ràng hoặc không nhất quán khiến hai bên đầu tư thời gian và cảm xúc trước khi nhận ra không cùng kỳ vọng | Cả hai người trong một kết nối tiềm năng | Khảo sát lý do unmatch/dừng trò chuyện; mã hóa nhóm nguyên nhân liên quan đến mismatch ý định |
| 6 | AI có thể tốt hơn | Dữ liệu hồ sơ ngắn và tự khai dễ khiến hệ thống suy diễn quá mức, tạo ra điểm tương thích có vẻ chính xác nhưng thiếu bằng chứng | Người dùng nhận gợi ý, đội sản phẩm | Đánh giá calibration, tỷ lệ “không đủ dữ liệu”, độ hữu ích của phần giải thích và mức người dùng hiểu đúng độ bất định |
| 7 | Pain từ người khác | Lừa đảo, quấy rối, ép buộc, giả mạo hoặc cố gắng chuyển nền tảng quá sớm có thể chỉ lộ ra qua nhiều tín hiệu nhỏ | Người dùng, moderator, trust & safety team | Phân tích các case đã được moderator xác nhận; đo recall/false-positive của rule và model trên tập dữ liệu đã ẩn danh |
| 8 | Rủi ro riêng tư và công bằng | Phân tích tương thích có thể làm lộ dữ liệu nhạy cảm, suy luận thuộc tính người dùng chưa cung cấp hoặc khuếch đại thiên lệch trong xếp hạng | Tất cả người dùng, đội pháp lý và trust & safety | Data-flow review, consent test, fairness audit theo exposure/outcome; kiểm tra khả năng xóa và thu hồi dữ liệu |

## Top 3

| Rank | Problem | Vì sao chọn | Điều còn chưa chắc |
|---|---|---|---|
| 1 | Khó đánh giá mức độ tương thích một cách có cấu trúc và có thể giải thích | Đây là pain trung tâm của đề bài; có workflow rõ từ khai báo nhu cầu đến shortlist và quyết định kết nối | “Tương thích” phải được định nghĩa theo từng người; chưa biết các chiều nào dự báo tốt nhất cho trải nghiệm thực tế |
| 2 | Người dùng chưa làm rõ tiêu chí, ưu tiên và ranh giới của chính mình | Nếu đầu vào mơ hồ, mọi thuật toán ghép đôi phía sau đều dễ đưa ra gợi ý sai hoặc quá tự tin | Người dùng có sẵn sàng trả lời sâu không; cần bao nhiêu câu hỏi để đủ thông tin mà không gây mệt |
| 3 | Tín hiệu an toàn, riêng tư và consent chưa được kiểm soát xuyên suốt | Sai ở card này có hậu quả lớn hơn một gợi ý không phù hợp; đây là điều kiện bắt buộc trước khi Agent được sử dụng | Dữ liệu nhãn rủi ro thường mất cân bằng; model có thể bỏ sót nguy hiểm hoặc gắn cờ oan |

---

## Problem Card #1 — Cupid Compatibility Agent

**Problem 1 câu:**  
Người dùng phải tự tổng hợp thông tin rời rạc từ nhiều hồ sơ và cuộc trò chuyện để đánh giá mục tiêu quan hệ, giá trị sống, lối sống, cách giao tiếp và ranh giới; quá trình này tốn thời gian, dễ bị cảm tính chi phối và vẫn không chỉ ra rõ điểm phù hợp, điểm xung đột hay thông tin còn thiếu.

**Actor:**  
Người trưởng thành đang chủ động tìm kiếm một mối quan hệ và muốn sàng lọc các kết nối tiềm năng có chất lượng.

**Thời điểm / bối cảnh:**  
Sau khi người dùng đã khai báo nhu cầu cơ bản và cần lựa chọn một shortlist từ các hồ sơ có quyền hiển thị cho họ; hoặc trước khi quyết định tiếp tục tìm hiểu một kết nối đã có.

**Current workflow:**

```text
1. Tự xác định tiêu chí và ưu tiên                         ~10–20'
2. Đặt filter cơ bản trên ứng dụng                         ~5'
3. Lướt và đọc nhiều hồ sơ                                ~20–40'
4. Ghi nhớ/so sánh các đối tượng bằng cảm tính            ~10–20'
5. Trò chuyện để tìm hiểu mục tiêu và giá trị             ~2–7 ngày  <-- bottleneck
6. Tự đánh giá điểm phù hợp, xung đột và quyết định tiếp tục
```

> Thời gian trên chỉ là ước lượng từ kịch bản sản phẩm. Pilot cần đo riêng “thời gian đến shortlist” và “thời gian đến khi phát hiện deal-breaker” thay vì cộng cơ học phút và ngày.

**Bottleneck:**  
Thông tin quyết định mức độ phù hợp không nằm trong một trường dữ liệu duy nhất. Người dùng phải vừa làm rõ nhu cầu của mình, vừa đối chiếu nhiều chiều giữa các hồ sơ, đồng thời phân biệt dữ kiện được cung cấp với suy đoán cá nhân.

**Impact:**  
Người dùng mất nhiều thời gian cho các kết nối có xung đột nền tảng, gặp decision fatigue và có thể bỏ qua đối tượng phù hợp vì một ấn tượng bề mặt. Một điểm số không minh bạch còn có thể tạo niềm tin giả, biến gợi ý thành “phán quyết” thay vì công cụ hỗ trợ quyết định.

**Success metric:**

- Đo median thời gian từ khi bắt đầu tìm kiếm đến khi tạo được shortlist 3–5 hồ sơ; mục tiêu pilot là giảm ít nhất 40% so với workflow không có Agent.
- Ít nhất 80% kết quả phải hiển thị được bằng chứng cho từng nhận định từ dữ liệu mà người dùng đã cho phép, đồng thời tách rõ `phù hợp`, `có thể xung đột` và `chưa đủ dữ liệu`.
- Đo precision@k hoặc nDCG theo shortlist do chính người dùng đánh giá, nhưng không dùng click/match đơn lẻ làm proxy duy nhất cho “tương thích”.
- Đo tỷ lệ người dùng xác nhận phần giải thích “đúng với ưu tiên của tôi” và “giúp tôi ra quyết định”, thay vì chỉ đo số lượt match.
- Theo dõi calibration: khi thiếu dữ liệu, Agent phải chọn `không đủ cơ sở` thay vì tạo một điểm số chắc chắn.
- Mọi hành động chia sẻ hồ sơ, mở kết nối hoặc gửi tin nhắn phải do người dùng xác nhận; tỷ lệ Agent tự thực hiện ngoài consent phải bằng 0.

**Non-AI alternative:**  
Bảng câu hỏi có cấu trúc, filter theo hard constraint và ma trận rule-based có trọng số do người dùng tự đặt. Phương án này minh bạch, dễ kiểm soát và nên là baseline bắt buộc; hạn chế là khó xử lý câu trả lời tự do, tiêu chí mơ hồ và nhu cầu thay đổi theo ngữ cảnh.

**AI hypothesis:**  
Một Agent hội thoại có thể hỏi làm rõ tiêu chí còn mơ hồ, chuẩn hóa câu trả lời tự do thành các chiều tương thích, sau đó so sánh hồ sơ trên dữ liệu được consent và giải thích bằng evidence. Agent chỉ đề xuất shortlist, trade-off và câu hỏi cần tìm hiểu thêm; không tự liên hệ, không suy luận thuộc tính nhạy cảm chưa được cung cấp và không khẳng định khả năng thành công của mối quan hệ.

**Quick gut:**  
`[ ] No AI / process fix  [ ] Rule  [ ] Workflow  [x] Agent  [ ] Chưa biết`

### Draft current workflow

```text
CURRENT STATE — nhiều thao tác thủ công, tiêu chí thay đổi trong quá trình chọn

[Tự nghĩ tiêu chí]
→ [Đặt filter bề mặt]
→ [Lướt nhiều hồ sơ]
→ [Tự ghi nhớ và so sánh]
→ [Trò chuyện nhiều ngày để phát hiện mục tiêu/giá trị]  <-- bottleneck
→ [Quyết định tiếp tục hoặc dừng]
```

### Draft future workflow

```text
FUTURE STATE — Agent hỗ trợ, người dùng giữ quyền quyết định

[Người dùng khai báo mục tiêu, ranh giới và dữ liệu được phép dùng]
→ [Rule loại hard constraint không phù hợp]                         -- Rule
→ [Agent hỏi 3–5 câu làm rõ tại điểm có độ bất định cao]            -- AI
→ [Phân tích theo từng chiều + trích evidence + hiển thị unknown]    -- AI
→ [Shortlist kèm điểm phù hợp, trade-off và câu hỏi cần xác minh]    -- AI/UI
→ [Người dùng xem hồ sơ gốc và quyết định kết nối]                   -- human boundary
→ [Chỉ mở liên hệ khi hai bên cùng consent]                          -- platform rule

Fallback: dữ liệu ít, mâu thuẫn hoặc confidence thấp
→ không tạo điểm tổng; hiển thị “chưa đủ dữ liệu”, cho phép dùng filter rule-based
hoặc đề nghị người dùng bổ sung thông tin.
```

**Vì sao có impact:**  
Card này xử lý đúng khoảng trống giữa “nhiều lựa chọn” và “một lựa chọn có căn cứ”. Giá trị của Cupid Agent không nằm ở việc đoán ai là “định mệnh”, mà ở việc giúp người dùng nhìn rõ tiêu chí của mình, so sánh nhất quán và hiểu cả bằng chứng lẫn độ bất định trước khi tự quyết định.

---

## Problem Card #2 — Preference Clarification & Match Criteria

**Problem 1 câu:**  
Nhiều người dùng bắt đầu ghép đôi với các tiêu chí chung chung hoặc mâu thuẫn, nên hệ thống không phân biệt được điều bắt buộc, điều ưu tiên và điều có thể thỏa hiệp, dẫn đến gợi ý thiếu nhất quán.

**Actor:**  
Người dùng mới, người chưa có kinh nghiệm với ứng dụng hẹn hò hoặc người có nhu cầu thay đổi theo từng giai đoạn.

**Thời điểm / bối cảnh:**  
Trong onboarding, khi kết quả ghép đôi liên tục không phù hợp hoặc khi người dùng muốn điều chỉnh mục tiêu quan hệ.

**Current workflow:**

```text
1. Chọn vài filter nhân khẩu học và sở thích
2. Viết mô tả ngắn về người mong muốn
3. Nhận danh sách gợi ý
4. Loại/chọn bằng cảm giác
5. Liên tục sửa filter sau các trải nghiệm không phù hợp
```

**Bottleneck:**  
Người dùng phải tự chuyển một mong muốn trừu tượng thành tiêu chí có thể so sánh. Hệ thống hiện khó biết một tiêu chí là hard constraint, soft preference hay chỉ là phản ứng tạm thời sau một trải nghiệm.

**Impact:**  
Đầu vào kém làm giảm chất lượng toàn bộ pipeline ghép đôi. Agent có thể tối ưu rất tốt cho một bộ tiêu chí nhưng vẫn đưa ra gợi ý sai vì tiêu chí đó không đại diện cho nhu cầu thật của người dùng.

**Success metric:**

- Hoàn thành preference profile trong tối đa 5 phút ở median, với tỷ lệ bỏ onboarding không tăng quá ngưỡng baseline của pilot.
- Ít nhất 90% người dùng phân loại được các tiêu chí chính thành `bắt buộc`, `ưu tiên`, `có thể thỏa hiệp` hoặc `chưa chắc`.
- Giảm số lần thay đổi hard filter ngay sau khi nhận kết quả; mọi thay đổi phải được ghi nhận theo phiên bản để người dùng có thể xem và hoàn tác.
- Đo test–retest consistency sau 7–14 ngày, nhưng không coi thay đổi quan điểm là lỗi của người dùng.

**Non-AI alternative:**  
Form có cấu trúc, forced ranking, pairwise comparison và ví dụ tình huống. Đây là baseline đủ mạnh cho MVP và giúp dữ liệu đầu vào dễ kiểm soát.

**AI hypothesis:**  
Agent dùng câu hỏi thích ứng để chỉ hỏi tại các tiêu chí có ảnh hưởng lớn nhưng độ chắc chắn thấp. AI tóm tắt preference profile để người dùng xác nhận, không tự chuyển một câu trả lời mơ hồ thành hard constraint và không suy luận thuộc tính nhạy cảm.

**Quick gut:**  
`[ ] No AI / process fix  [ ] Rule  [x] Workflow  [ ] Agent  [ ] Chưa biết`

### Draft current workflow

```text
[Chọn filter cơ bản]
→ [Viết mong muốn tự do]
→ [Nhận gợi ý]
→ [Loại/chọn theo cảm giác]
→ [Sửa filter sau mỗi lần không phù hợp]
```

### Draft future workflow

```text
[Form ngắn về mục tiêu và ranh giới]
→ [Rule phát hiện câu trả lời thiếu hoặc mâu thuẫn]
→ [AI hỏi làm rõ tại điểm có giá trị thông tin cao]
→ [Tóm tắt: bắt buộc / ưu tiên / thỏa hiệp / chưa chắc]
→ [Người dùng sửa và xác nhận profile]  <-- human boundary
→ [Lưu phiên bản tiêu chí để dùng cho matching]

Fallback: người dùng không muốn trả lời sâu
→ chỉ sử dụng filter đã chọn, không tự điền hoặc suy luận phần còn thiếu.
```

**Vì sao có impact:**  
Card này là dependency trực tiếp của Card #1. Khi tiêu chí được làm rõ và xác nhận, phần phân tích tương thích mới có thể giải thích đúng “phù hợp với ai, theo điều gì” thay vì áp dụng một chuẩn chung cho mọi người.

---

## Problem Card #3 — Safety, Privacy & Consent Gate

**Problem 1 câu:**  
Người dùng khó tự tổng hợp các tín hiệu lừa đảo, quấy rối, ép buộc hoặc vi phạm ranh giới trong khi dữ liệu phục vụ phân tích tương thích lại rất nhạy cảm; nếu thiếu lớp consent và kiểm soát an toàn, Agent có thể khuếch đại rủi ro thay vì giảm rủi ro.

**Actor:**  
Người dùng ứng dụng hẹn hò, moderator, trust & safety team và đội vận hành dữ liệu.

**Thời điểm / bối cảnh:**  
Từ khi tạo hồ sơ, nhận gợi ý, bắt đầu trò chuyện đến trước khi chia sẻ thông tin liên hệ hoặc gặp mặt trực tiếp.

**Current workflow:**

```text
1. Người dùng đọc hồ sơ và tự đánh giá độ tin cậy
2. Trò chuyện để nhận biết dấu hiệu bất thường
3. Tự quyết định khi nào chia sẻ thông tin cá nhân
4. Block/report sau khi sự cố đã xảy ra
5. Moderator đọc case và xử lý thủ công
```

**Bottleneck:**  
Các tín hiệu rủi ro thường phân tán theo thời gian, trong khi người dùng không biết hệ thống đang lưu, suy luận hoặc chia sẻ những dữ liệu nào để tạo phân tích tương thích.

**Impact:**  
False negative có thể khiến người dùng tiếp xúc với hành vi nguy hiểm; false positive có thể gắn nhãn oan và làm mất cơ hội kết nối. Việc dùng dữ liệu không có consent còn phá vỡ niềm tin ngay cả khi gợi ý ghép đôi có vẻ chính xác.

**Success metric:**

- 100% nguồn dữ liệu được hiển thị trong consent screen, có mục đích sử dụng, thời hạn lưu và cơ chế thu hồi/xóa.
- Đo recall, precision và false-positive rate trên tập case đã được moderator xác nhận; ngưỡng triển khai do trust & safety team phê duyệt theo mức độ rủi ro.
- Cảnh báo nghiêm trọng phải có đường dẫn report/block rõ ràng và SLA xử lý; AI không tự kết luận một người “nguy hiểm” khi chưa có review phù hợp.
- Không cho phép Agent tự gửi tin, tự chia sẻ số điện thoại/vị trí hoặc tự đặt lịch gặp mặt.
- Audit chênh lệch false-positive/false-negative giữa các nhóm đủ điều kiện thống kê; dừng triển khai nếu sai lệch vượt ngưỡng đã phê duyệt.

**Non-AI alternative:**  
Xác minh tài khoản, rate limit, block/report, keyword/rule list, checklist an toàn, cảnh báo khi chia sẻ PII và quy trình moderator review. Các cơ chế này phải tồn tại trước khi thêm AI.

**AI hypothesis:**  
Classifier có thể hỗ trợ gom các tín hiệu scam/harassment và ưu tiên case cho moderator. AI chỉ tạo cảnh báo theo cấp độ và nêu tín hiệu quan sát được; không chẩn đoán tính cách, không tự trừng phạt người dùng và không thay thế quy trình khiếu nại.

**Quick gut:**  
`[ ] No AI / process fix  [ ] Rule  [x] Workflow  [ ] Agent  [ ] Chưa biết`

### Draft current workflow

```text
[Đọc hồ sơ]
→ [Trò chuyện]
→ [Tự phát hiện tín hiệu bất thường]
→ [Sự cố hoặc nghi ngờ]
→ [Block/report]
→ [Moderator xử lý]
```

### Draft future workflow

```text
[Consent rõ nguồn dữ liệu và mục đích sử dụng]
→ [Rule kiểm tra tài khoản, rate limit, PII và hành vi đã biết]
→ [AI gom tín hiệu rủi ro, kèm evidence và confidence]
→ [Cảnh báo người dùng hoặc ưu tiên hàng đợi review]
→ [Người dùng block/report; moderator quyết định xử lý]  <-- human boundary
→ [Cơ chế khiếu nại, xóa dữ liệu và audit]

Fallback: model không chắc chắn hoặc dữ liệu ngoài phạm vi consent
→ không suy luận; áp dụng rule an toàn cơ bản và chuyển moderator khi cần.
```

**Vì sao có impact:**  
Độ tin cậy là điều kiện để người dùng chia sẻ dữ liệu cần thiết cho phân tích tương thích. Card này không phải tính năng phụ mà là lớp kiểm soát xuyên suốt của Cupid Agent, đặc biệt khi hệ thống xử lý thông tin cá nhân và tác động đến quyết định giàu cảm xúc.

## Ghi chú khi pitch/challenge với nhóm

- Câu hỏi cần đặt cho Card #1: “Tương thích” được định nghĩa theo đánh giá chủ quan của từng người hay theo một nhãn chung? Nếu không có ground truth đáng tin, không nên pitch Agent như một mô hình dự đoán thành công của mối quan hệ.
- Câu hỏi cần đặt cho dữ liệu: ứng viên có biết hồ sơ hoặc hội thoại của họ đang được dùng để phân tích không? Consent phải áp dụng cho **cả hai phía**, không chỉ người yêu cầu Agent.
- Câu hỏi cần đặt cho ranking: hệ thống có đang tối ưu click/match và vô tình khuếch đại popularity bias hay loại bỏ các hồ sơ ít dữ liệu không?
- Câu hỏi cần đặt cho safety: false negative nào có hậu quả nghiêm trọng nhất, case nào bắt buộc moderator review và người dùng có cơ chế khiếu nại hay không?
- Nhận định hiện tại: Card #1 phù hợp nhất để deep-dive vì bám trực tiếp vào giá trị ghép đôi và có workflow đo được; Card #2 là dependency đầu vào, còn Card #3 là điều kiện an toàn bắt buộc. MVP nên bắt đầu bằng form + rule-based matching có giải thích, sau đó mới thêm Agent hỏi làm rõ và phân tích dữ liệu tự do.
