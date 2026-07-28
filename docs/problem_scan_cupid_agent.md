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

## Khảo sát phương pháp và giải pháp hiện tại

> Phạm vi khảo sát cập nhật đến **28/07/2026**, gồm hai lớp: (1) các phương pháp kỹ thuật thường dùng trong recommender system cho hẹn hò; (2) các giải pháp sản phẩm đang được công bố chính thức. Phân tích ưu/nhược điểm dựa trên thông tin công khai, không suy đoán thuật toán độc quyền bên trong từng nền tảng.

### 1. Các phương pháp ghép đôi hiện có

| Phương pháp | Cách thực hiện | Ưu điểm | Nhược điểm / khoảng trống |
|---|---|---|---|
| **See-and-screen + hard filter** | Người dùng đặt các điều kiện như độ tuổi, khoảng cách, mục tiêu quan hệ; sau đó tự xem hồ sơ và swipe/chọn | Minh bạch, dễ hiểu, người dùng có quyền kiểm soát cao; hard constraint được áp dụng chắc chắn; dễ xây dựng và kiểm thử | Gây choice overload; thiên về thuộc tính bề mặt; người dùng phải biết chính xác mình muốn gì; không biểu diễn được trade-off hoặc mức độ chưa chắc chắn |
| **Questionnaire/psychometric matching** | Thu thập câu trả lời về tính cách, giá trị, lối sống và kỳ vọng; tính similarity hoặc weighted compatibility | Có dữ liệu explicit ngay cả với người dùng mới; dễ giải thích theo từng câu hỏi/chiều; phù hợp với người tìm quan hệ nghiêm túc | Onboarding dài; phụ thuộc self-report; câu trả lời có thể thay đổi theo thời gian; similarity không đồng nghĩa với chemistry hoặc thành công dài hạn |
| **Content-based/semantic matching** | Biểu diễn bio, prompt, sở thích và mục tiêu thành feature/embedding; tìm hồ sơ có nội dung phù hợp với preference profile | Hoạt động khi chưa có nhiều lịch sử tương tác; tận dụng được văn bản tự do; có thể chỉ ra chủ đề hoặc giá trị chung | Hồ sơ thường ngắn, được “tối ưu hình ảnh” và thiếu dữ liệu; semantic similarity chủ yếu là một chiều; dễ suy luận quá mức từ văn bản hoặc làm lộ thuộc tính nhạy cảm |
| **Collaborative filtering/behavioral ranking** | Học từ like, skip, match, message và pattern của những người có hành vi tương tự | Học được revealed preference; thích ứng theo hành vi thực tế; không buộc người dùng trả lời một questionnaire dài | Cold start; popularity bias và feedback loop; hành vi số đông có thể lấn át nhóm thiểu số; click/match/response không phải ground truth của tương thích dài hạn |
| **Reciprocal recommender** | Ước lượng đồng thời khả năng A quan tâm B và B quan tâm A; xếp hạng theo mutual score hoặc stable matching | Đúng với bản chất hai phía của hẹn hò; giảm gợi ý một chiều và khả năng bị từ chối; tối ưu cơ hội tương tác thực tế | Cần đủ dữ liệu của cả hai phía; dễ ưu tiên hồ sơ vốn đã phổ biến; “có khả năng nhắn lại” vẫn khác “phù hợp để xây dựng quan hệ” |
| **Conversational recommender/LLM Agent** | Agent hỏi nhiều lượt để elicitation preference, duy trì hồ sơ ngôn ngữ tự nhiên, truy xuất ứng viên và tạo giải thích | Giảm độ cứng của form; hỏi thích ứng theo điều còn thiếu; xử lý nuance và feedback tự do; hỗ trợ giải thích dễ đọc | Có thể hallucinate hoặc tự mâu thuẫn; khó calibration; có nguy cơ người dùng quá tin lời Agent; hội thoại chứa dữ liệu nhạy cảm và cần consent chặt chẽ |
| **Human matchmaker** | Chuyên gia phỏng vấn, lập hồ sơ nhu cầu, chọn ứng viên và phản hồi sau mỗi lần giới thiệu | Hiểu được ngữ cảnh khó cấu trúc; có thể hỏi sâu và chịu trách nhiệm giải thích; phù hợp khi dữ liệu số còn ít | Chi phí cao, chậm và khó mở rộng; chất lượng phụ thuộc từng matchmaker; có thể mang thiên kiến chủ quan; khó audit nhất quán |
| **Safety rule + ML moderation + human review** | Xác minh ảnh/ID, rule về hành vi, classifier phát hiện scam/harassment, block/report và moderator xử lý | Giảm một phần tài khoản giả và nội dung nguy hiểm; rule xử lý nhanh case rõ ràng; human review phù hợp với case hậu quả cao | False negative vẫn để lọt rủi ro; false positive có thể gắn cờ oan; không trực tiếp đo độ tương thích; consent, khiếu nại và lưu dữ liệu làm hệ thống phức tạp hơn |

Nghiên cứu về recommender hai chiều nhấn mạnh rằng dating khác recommendation hàng hóa: hệ thống phải xét khả năng **hai người cùng quan tâm và có khả năng tương tác**, không chỉ tối ưu sở thích của một phía. Các thử nghiệm trong nghiên cứu của Xia và cộng sự cũng cho thấy collaborative filtering có thể cải thiện precision/recall so với content-based trong bộ dữ liệu được nghiên cứu, nhưng metric vẫn thiên về khả năng tương tác chứ chưa chứng minh kết quả quan hệ dài hạn ([Xia et al., Reciprocal Recommendation System for Online Dating](https://arxiv.org/abs/1501.06247)).

Với conversational recommender, LLM mở ra khả năng hiểu preference bằng ngôn ngữ tự nhiên, quản lý hội thoại và tạo explanation; đồng thời nghiên cứu cũng nêu các khó khăn về kiểm soát hội thoại phức tạp, retrieval trên tập ứng viên biến động và thiếu dữ liệu hội thoại huấn luyện ([Friedman et al., Leveraging Large Language Models in Conversational Recommender Systems](https://arxiv.org/abs/2305.07961)). Vì vậy, LLM phù hợp với lớp **hỏi–làm rõ–giải thích**, nhưng không nên là nguồn duy nhất tính eligibility, safety hay mutual ranking.

### 2. Các giải pháp sản phẩm đang có

| Giải pháp | Cách tiếp cận đang công bố | Ưu điểm hiện tại | Nhược điểm / khoảng trống còn lại |
|---|---|---|---|
| **OkCupid Match Questions** | Có khoảng 500 câu hỏi; khuyến nghị trả lời 50–100 câu để bắt đầu; hiển thị Match % và cho phép so sánh các câu mà hai bên cùng trả lời công khai ([OkCupid Match Questions](https://okcupid-app.zendesk.com/hc/en-us/articles/22770910347803-Match-Questions)) | Preference explicit phong phú; người dùng có thể xem câu trả lời cụ thể phía sau Match %; hỗ trợ cold start tốt hơn chỉ dùng hành vi | Khối lượng câu hỏi lớn; phụ thuộc sự trung thực và tự nhận thức; câu hỏi cố định khó thích ứng; một Match % có thể che mất unknown và trade-off giữa các chiều |
| **eharmony Compatibility System** | Dùng Compatibility Quiz về tính cách, sở thích, giao tiếp và động lực; trang giới thiệu hiện mô tả 80 câu, khoảng 20 phút, tạo Personality Profile ([eharmony Compatibility Quiz](https://www.eharmony.com/tour/what-is-the-compatibility-quiz/)). Hệ thống hiển thị Compatibility Score theo từng cặp trên thang 60–140 ([eharmony Compatibility Score](https://www.eharmony.com/tour/what-is-compatibility-system/)) | Phân tích sâu hơn bộ lọc bề mặt; có profile và phân tích theo đặc điểm; định vị rõ cho quan hệ nghiêm túc | Onboarding tương đối dài; thuật toán chấm điểm độc quyền nên khó audit; profile chủ yếu dựa trên snapshot tự khai; con số đơn có thể tạo cảm giác chính xác hơn mức bằng chứng thực tế |
| **Hinge Most Compatible** | Đề xuất một hồ sơ nổi bật dựa trên mutual preferences, hoạt động gần đây và pattern trong những người mà người dùng/những người tương tự thường like ([Hinge Most Compatible](https://help.hinge.co/hc/en-us/articles/360011233073-What-is-Most-Compatible)) | Có tính hai chiều và sử dụng hành vi cập nhật; giảm số hồ sơ cần xem; phù hợp với reciprocal ranking | Tài liệu công khai chưa cho biết evidence chi tiết cho từng đề xuất; implicit feedback có thể mang bias; mô hình có xu hướng tối ưu khả năng connect hơn là chứng minh tương thích dài hạn |
| **Hinge automated profiling** | Dùng thông tin khai báo và hành vi như like, skip, match hoặc trao đổi số điện thoại để đề xuất; đồng thời dùng automated profiling cho moderation và chống bot ([Hinge Automated Decision-Making](https://help.hinge.co/hc/en-us/articles/360010956733-Automated-Decision-Making-and-Profiling-at-Hinge)) | Kết hợp explicit và implicit signals; cập nhật theo hành vi; hỗ trợ cả matching và an toàn | Người dùng khó biết từng hành vi tác động thế nào đến ranking; nguy cơ feedback loop và inferred preference; matching và moderation cùng dựa vào profiling làm yêu cầu audit/consent cao hơn |
| **Bumble Dates, powered by Bee** | Bee hỏi về relationship preferences, values và điều thực sự quan trọng ở một đối tác, sau đó tìm người phù hợp và gửi thông báo mà không cần swipe. Tính đến 28/07/2026, tính năng vẫn là pilot cho một nhóm người dùng được mời tại NYC ([Bumble Dates, powered by Bee](https://support.bumble.com/hc/en-us/articles/34865026348701-Using-Dates-powered-by-Bee)) | Là đối thủ gần nhất với ý tưởng Cupid Agent; giảm swipe fatigue; onboarding hội thoại tự nhiên; tập trung vào giá trị và nhu cầu thay vì chỉ hồ sơ bề mặt | Phạm vi pilot còn hẹp; tài liệu công khai chưa mô tả cách tính tương thích, evidence, uncertainty, fairness hoặc consent hai phía; chưa đủ dữ liệu công khai để kết luận hiệu quả |
| **Bumble safety stack** | Photo/ID verification, in-app voice/video, Private Detector, block/report, Deception Detector và human moderation ([Bumble Safety Features](https://support.bumble.com/hc/en-us/articles/28537051467293-Our-safety-features)) | Cho thấy safety cần là một pipeline nhiều lớp chứ không phải một model; giữ con người trong vòng xử lý; cung cấp công cụ kiểm soát trực tiếp cho người dùng | Xác minh không bảo đảm ý định tốt; classifier không hiểu toàn bộ bối cảnh quan hệ; false positive/negative và quy trình khiếu nại vẫn là vấn đề riêng, không thể thay bằng compatibility score |

### 3. Hạn chế chung của các giải pháp hiện tại

**1. Tối ưu interaction chưa đồng nghĩa tối ưu compatibility.**  
Like, match, message hoặc trao đổi số điện thoại là tín hiệu dễ đo, nhưng chủ yếu phản ánh sự chú ý và khả năng phản hồi ở giai đoạn đầu. Một tổng quan về matching algorithm chỉ ra rằng mô hình khó dự đoán chắc chắn hai người cụ thể có “hợp nhau ngoài đời” hay không, vì kết quả quan hệ còn hình thành từ tương tác giữa hai người sau khi gặp ([Sharabi, Finding Love on a First Data](https://hdsr.mitpress.mit.edu/pub/i4eb4e8b/release/3)).

**2. Stated preference và revealed preference có thể không trùng nhau.**  
Questionnaire giả định người dùng biết rõ điều mình muốn; behavioral ranking lại học từ hành vi có thể bị chi phối bởi ảnh, vị trí hiển thị hoặc thói quen swipe. Nếu chỉ chọn một nguồn, hệ thống dễ hiểu sai người dùng. Cupid Agent cần đối chiếu cả hai và hỏi lại khi có mâu thuẫn, không âm thầm ghi đè tiêu chí.

**3. Điểm số tổng làm mất evidence và uncertainty.**  
Một con số như Match % hoặc Compatibility Score thuận tiện để xếp hạng nhưng không cho biết phần nào là hard conflict, phần nào chỉ là preference nhẹ và phần nào chưa có dữ liệu. Điểm số còn có thể tạo expectation effect: người dùng tin vào nhãn “tương thích cao” và đánh giá đối tượng tích cực hơn dù bằng chứng chưa chắc mạnh.

**4. Đa số hệ thống chưa đặt user control ngang với sức mạnh thuật toán.**  
Nghiên cứu về thiết kế online dating phân biệt ba dạng see-and-screen, algorithmic và blended; kết quả cho thấy blended design có lợi thế khi vừa giữ quyền chọn của người dùng vừa cung cấp algorithmic validation ([Tong, Hancock & Slatcher, Online Dating System Design and Relational Decision-Making](https://socialmedialab.sites.stanford.edu/sites/g/files/sbiybj22976/files/media/file/tong-pr-online-dating.pdf)). Điều này ủng hộ việc Cupid Agent đưa ra shortlist và giải thích, nhưng quyết định kết nối vẫn thuộc về con người.

**5. Fairness không thể suy ra từ accuracy chung.**  
Một recommender có precision tốt toàn hệ thống vẫn có thể phân phối cơ hội không đồng đều giữa các nhóm hoặc loại bỏ nhóm ít dữ liệu. Nghiên cứu trên online dating ghi nhận quantity imbalance và calibration imbalance theo nhóm preference, đồng thời đề xuất re-weighting/re-ranking để cải thiện fairness mà vẫn giữ utility ([Zhao et al., AAAI 2024](https://arxiv.org/abs/2402.12541)). Do đó Cupid Agent cần audit exposure, recall và calibration theo nhóm đủ điều kiện thống kê.

**6. Safety thường đứng cạnh matching thay vì nằm trong matching workflow.**  
Verification và moderation giúp loại tài khoản giả/nội dung nguy hiểm, nhưng recommendation vẫn có thể đẩy người dùng đến một kết nối rủi ro nếu consent, PII và safety status không trở thành eligibility gate trước ranking.

### 4. Khoảng trống mà Cupid Agent sẽ tập trung giải quyết

Cupid Agent **không cạnh tranh bằng việc tạo thêm một compatibility score**. Hệ thống được định vị là một pipeline lai, ghép ưu điểm của rule-based filter, reciprocal recommendation và conversational Agent:

```text
[Consent + eligibility + hard safety rules]
→ [Agent làm rõ hard constraint / soft preference / uncertainty]
→ [Tạo preference profile đã được người dùng xác nhận]
→ [Lọc ứng viên hai chiều theo hard constraint]
→ [Reciprocal ranking theo nhiều chiều]
→ [Giải thích bằng evidence + conflict + unknown]
→ [Người dùng quyết định kết nối]
→ [Feedback có lý do để cập nhật preference profile]
```

| Vấn đề được giải quyết | Cupid Agent xử lý như thế nào | Kết quả kỳ vọng |
|---|---|---|
| Người dùng không biết hoặc diễn đạt chưa rõ mình cần gì | Hội thoại thích ứng, forced choice khi cần và tóm tắt lại thành `bắt buộc`, `ưu tiên`, `có thể thỏa hiệp`, `chưa chắc` để người dùng xác nhận | Preference profile rõ ràng hơn mà không bắt mọi người đi qua cùng một bộ 80–100 câu hỏi |
| Questionnaire dài và tĩnh | Chọn câu hỏi tiếp theo theo information gain và chỉ hỏi tại chiều có ảnh hưởng lớn nhưng confidence thấp | Giảm onboarding burden, tránh hỏi những điều không liên quan |
| Swipe/filter tạo quá nhiều lựa chọn | Hard filter trước, sau đó tạo shortlist nhỏ thay vì feed vô hạn | Giảm thời gian sàng lọc và decision fatigue |
| Matching chỉ tối ưu một phía | Tính eligibility và preference ở cả A→B và B→A; chỉ xếp hạng ứng viên có khả năng phù hợp hai chiều | Giảm gợi ý không khả thi và giảm kỳ vọng một chiều |
| Điểm tương thích khó giải thích | Không ưu tiên một số tổng duy nhất; hiển thị theo chiều: mục tiêu quan hệ, giá trị, lối sống, giao tiếp, practical constraint | Người dùng biết vì sao nên tìm hiểu, xung đột nào cần cân nhắc và điều gì chưa biết |
| Hệ thống suy diễn quá mức từ hồ sơ ngắn | Mọi nhận định phải gắn với evidence được consent; thiếu dữ liệu thì abstain hoặc tạo câu hỏi xác minh | Giảm hallucination và cảm giác “AI biết chắc con người” |
| Stated preference mâu thuẫn với hành vi | Phát hiện chênh lệch nhưng hỏi người dùng xác nhận trước khi cập nhật; lưu phiên bản và cho phép hoàn tác | Preference model thích ứng nhưng vẫn do người dùng kiểm soát |
| Tối ưu match/click thay vì chất lượng quyết định | Bổ sung metric về explanation helpfulness, time-to-shortlist, regret sau quyết định, tỷ lệ phát hiện sớm deal-breaker và calibration | Đánh giá hệ thống theo giá trị cho người dùng thay vì chỉ tăng engagement |
| Safety/privacy tách rời recommendation | Consent gate, PII rule, verification/safety status và human-review requirement được kiểm tra trước khi hồ sơ vào ranking | Không đề xuất hồ sơ vi phạm eligibility; giảm rủi ro dùng dữ liệu ngoài phạm vi cho phép |
| Popularity bias và bất bình đẳng cơ hội | Audit exposure, recall và calibration; re-ranking có ràng buộc fairness; cho phép reset/điều chỉnh preference model | Hạn chế feedback loop và việc một nhóm hồ sơ bị hệ thống “ẩn” kéo dài |

### 5. Giá trị khác biệt và giới hạn cam kết

**Giá trị khác biệt đề xuất:**

1. **Adaptive thay vì questionnaire cố định:** hỏi ít nhưng đúng chỗ còn mơ hồ.
2. **Reciprocal thay vì recommendation một chiều:** xét nhu cầu và ranh giới của cả hai phía.
3. **Evidence + uncertainty thay vì một điểm tuyệt đối:** phân biệt rõ `match`, `trade-off`, `conflict` và `unknown`.
4. **User-controlled learning:** hành vi không tự động trở thành preference nếu người dùng chưa xác nhận.
5. **Safety-by-design:** consent, eligibility và risk gate nằm trước ranking, không phải lớp xử lý sau sự cố.

**Hệ thống không cam kết giải quyết:**

- Không dự đoán chắc chắn một mối quan hệ sẽ thành công hoặc kéo dài.
- Không đánh giá “giá trị” của một con người, chẩn đoán tính cách hay gắn nhãn một người là tốt/xấu.
- Không thay thế trải nghiệm trò chuyện, gặp gỡ và xây dựng sự tin cậy giữa hai người.
- Không tự gửi tin nhắn, tự tiết lộ thông tin liên hệ hoặc tự sắp xếp cuộc gặp.
- Không thay thế moderator, chuyên gia an toàn hoặc cơ chế báo cáo/kháng nghị trong case hậu quả cao.

### 6. Vì sao sản phẩm này thực sự cần Agent?

#### 6.1. Điểm yếu trong cách định nghĩa hiện tại

Nếu Cupid chỉ thực hiện chuỗi:

```text
[Thu thập form]
→ [Lọc hard constraint]
→ [Tính compatibility score]
→ [Xếp hạng]
→ [Trả shortlist]
```

thì đây là một **workflow có AI component**, chưa phải Agent. Việc dùng LLM để diễn đạt câu hỏi hoặc viết explanation cũng không tự làm hệ thống trở thành Agent. Workflow trên có đường đi được xác định trước, đầu vào–đầu ra rõ và không cần hệ thống tự lựa chọn hành động tiếp theo.

Agent chỉ trở nên cần thiết khi bài toán được chuyển từ:

> “Tính điểm tương thích giữa người dùng và một tập hồ sơ”

thành:

> “Chủ động giúp một người tìm ra những kết nối phù hợp trong khi mục tiêu, tiêu chí, dữ liệu và mức sẵn sàng thỏa hiệp của họ còn chưa đầy đủ hoặc thay đổi.”

Khác biệt nằm ở **decision-making loop**, không nằm ở giao diện chat.

#### 6.2. Phân biệt Rule, Workflow và Agent trong Cupid

| Khía cạnh | Rule-based | Workflow | Agent |
|---|---|---|---|
| Đường đi | Một điều kiện kích hoạt một hành động cố định | Chuỗi bước và nhánh đã thiết kế trước | Tự chọn hành động tiếp theo dựa trên state và mục tiêu |
| Đầu vào | Có cấu trúc, tương đối đầy đủ | Có thể thiếu nhưng biết trước loại dữ liệu cần hỏi | Mơ hồ, thiếu, mâu thuẫn hoặc thay đổi theo hội thoại |
| State | Ít hoặc không có | Lưu trạng thái tiến trình | Duy trì belief state về mục tiêu, preference, uncertainty và lịch sử |
| Câu hỏi | Cố định hoặc kích hoạt bằng rule | Theo questionnaire/decision tree | Chọn câu hỏi có giá trị thông tin cao nhất tại thời điểm đó |
| Tool use | Gọi tool khi điều kiện đúng | Gọi tool theo thứ tự định trước | Quyết định gọi tool nào, khi nào, với tham số nào và có cần gọi tiếp hay không |
| Khi không có kết quả | Trả danh sách rỗng hoặc lỗi | Đi theo fallback đã viết sẵn | Chẩn đoán nguyên nhân, đề xuất trade-off và hỏi người dùng trước khi đổi chiến lược |
| Học từ feedback | Cập nhật field hoặc weight theo rule | Chạy lại pipeline | Diễn giải feedback, kiểm tra giả thuyết và cập nhật preference sau xác nhận |
| Điều kiện dừng | Rule đã đặt | Kết thúc workflow | Dừng khi đủ evidence, đạt mục tiêu, người dùng yêu cầu hoặc rủi ro vượt ngưỡng |

Nói cách khác, `age ≥ 25`, `distance ≤ 10 km`, kiểm tra consent hay chặn hồ sơ vi phạm là **rule**; tính reciprocal score là **model/tool**; còn quyết định nên hỏi thêm, tìm lại, so sánh, đề nghị nới tiêu chí hay dừng là trách nhiệm của **Agent**.

#### 6.3. Bảy khía cạnh khiến Agent có giá trị thực sự

**1. Preference của con người là latent, không phải một form đã hoàn chỉnh.**  
Người dùng thường diễn đạt bằng mục tiêu mơ hồ như “người trưởng thành”, “hợp tính” hoặc “nghiêm túc nhưng không quá vội”. Những khái niệm này không ánh xạ trực tiếp thành filter. Agent cần hình thành và liên tục cập nhật một belief state gồm:

- Điều đã biết và đã được người dùng xác nhận.
- Điều đang là giả thuyết của hệ thống.
- Điều còn thiếu nhưng ít ảnh hưởng.
- Điều còn thiếu và có thể làm thay đổi toàn bộ shortlist.

Một workflow có thể hỏi hết mọi câu; Agent phải quyết định **câu nào đáng hỏi ngay và câu nào không cần hỏi**.

**2. Câu hỏi tiếp theo phụ thuộc vào cả người dùng và candidate pool.**  
Nếu toàn bộ ứng viên đều ở xa, câu hỏi về mức sẵn sàng yêu xa/di chuyển có information gain lớn. Nếu mọi ứng viên đều ở cùng thành phố, câu hỏi đó gần như vô ích. Agent phải quan sát kết quả retrieval rồi mới chọn hành động tiếp theo; trình tự không thể tối ưu bằng một questionnaire cố định cho mọi phiên.

**3. Matching là bài toán multi-objective có trade-off, không phải sorting một score.**  
Người dùng có thể đồng thời muốn gần địa lý, cùng mục tiêu gia đình, lịch sống phù hợp và tương đồng giá trị. Candidate A mạnh ở giá trị nhưng xa; candidate B gần nhưng còn unknown về mục tiêu. Agent phải:

1. Nhận ra hai lựa chọn không thể so sánh chỉ bằng một score.
2. Xác định trade-off nào đang quyết định thứ hạng.
3. Hỏi người dùng hoặc đề xuất một comparison phù hợp.
4. Chỉ thay đổi trọng số sau khi người dùng xác nhận.

Đây là quá trình ra quyết định nhiều lượt, không phải một lần inference.

**4. Agent có thể phục hồi khi không tìm được kết quả.**  
Rule-based filter thường trả về `0 candidate`. Một Agent có thể kiểm tra nguyên nhân: pool quá nhỏ, một hard constraint loại toàn bộ ứng viên, dữ liệu của đối tượng còn thiếu hay safety gate đang chặn kết quả. Sau đó Agent chọn giữa:

- Hỏi người dùng xem tiêu chí nào thực sự là hard constraint.
- Đề nghị mở rộng phạm vi tìm kiếm nhưng không tự thay đổi.
- Giữ nguyên tiêu chí và chờ candidate pool cập nhật.
- Dừng vì không có lựa chọn đáp ứng an toàn.

Khả năng chẩn đoán–lập kế hoạch lại này là một trong những lý do mạnh nhất để dùng Agent.

**5. Agent điều phối nhiều công cụ có bản chất khác nhau.**  
Cupid không nên để LLM tự tính mọi thứ. Agent đóng vai trò orchestrator cho các tool có thể kiểm thử độc lập:

| Tool | Trách nhiệm |
|---|---|
| Consent & Eligibility Tool | Kiểm tra dữ liệu nào được phép sử dụng và hồ sơ nào được phép xuất hiện |
| Preference State Tool | Lưu hard constraint, soft preference, confidence và phiên bản xác nhận |
| Candidate Retrieval Tool | Truy vấn ứng viên theo constraint hiện tại |
| Reciprocal Ranking Tool | Tính khả năng phù hợp hai chiều |
| Compatibility Analysis Tool | So sánh theo từng chiều, trả evidence/conflict/unknown |
| Safety Tool | Áp dụng rule, risk classifier và yêu cầu human review |
| Explanation Tool | Chuyển kết quả có cấu trúc thành giải thích dễ hiểu, không thêm suy luận ngoài evidence |

Agent quyết định tool nào cần gọi tiếp sau khi đọc kết quả tool trước. Hard rule và scoring vẫn deterministic; Agent không được phép override.

**6. Agent theo đuổi mục tiêu qua nhiều phiên, không chỉ tối ưu một lần swipe.**  
Sau mỗi shortlist hoặc cuộc trò chuyện, feedback như “không phù hợp vì lịch sống” chưa chắc đồng nghĩa với “loại tất cả người làm ca tối”. Agent phải tạo giả thuyết preference mới, hỏi xác nhận và cập nhật state có phiên bản. Nhờ đó hệ thống có thể học từ **lý do** của lựa chọn thay vì chỉ từ like/skip, đồng thời cho phép người dùng xem và hoàn tác thay đổi.

**7. Agent biết khi nào không nên hành động.**  
Trong domain giàu cảm xúc và dữ liệu nhạy cảm, năng lực quan trọng không chỉ là autonomy mà còn là `DEFER`, `ABSTAIN` và `ESCALATE`. Agent phải dừng khi thiếu consent, evidence quá yếu, phát hiện rủi ro hoặc hành động có thể làm thay người dùng một quyết định quan hệ.

#### 6.4. Agent loop đề xuất

```text
[Nhận goal hoặc feedback mới]
→ [Đọc preference state + consent + history]
→ [Đánh giá missing/conflict/uncertainty]
→ [Chọn next-best action]
     ├─ ASK: hỏi làm rõ
     ├─ RETRIEVE: tìm ứng viên
     ├─ FILTER: áp dụng hard constraint
     ├─ COMPARE: phân tích trade-off
     ├─ REQUEST_RELAXATION: xin phép nới một tiêu chí
     ├─ RECOMMEND: tạo shortlist
     ├─ EXPLAIN: đưa evidence/conflict/unknown
     ├─ DEFER/ESCALATE: chờ hoặc chuyển human review
     └─ STOP: kết thúc khi đạt mục tiêu hoặc không thể tiếp tục an toàn
→ [Gọi tool tương ứng]
→ [Quan sát kết quả]
→ [Cập nhật state sau khi người dùng xác nhận]
→ [Lặp hoặc dừng]
```

Có thể biểu diễn state tại lượt \(t\) dưới dạng:

\[
s_t = \{G_t, H_t, P_t, U_t, C_t, R_t, M_t\}
\]

trong đó:

- \(G_t\): mục tiêu quan hệ hiện tại.
- \(H_t\): hard constraints đã xác nhận.
- \(P_t\): soft preferences và trọng số.
- \(U_t\): uncertainty/conflict trong preference profile.
- \(C_t\): candidate pool và kết quả tool gần nhất.
- \(R_t\): trạng thái consent, safety và risk.
- \(M_t\): memory từ hội thoại và feedback trước.

Agent chọn hành động dựa trên utility kỳ vọng:

\[
a_t = \arg\max_a \left(
\mathbb{E}[\Delta Utility]
+ \lambda \Delta InformationGain
- \mu InteractionCost
- \nu Risk
\right)
\]

Công thức này không nhất thiết phải được triển khai bằng reinforcement learning trong MVP. Nó trước hết là nguyên tắc thiết kế: Agent ưu tiên hành động giúp cải thiện quyết định hoặc giảm uncertainty, nhưng phải trừ chi phí làm phiền người dùng và rủi ro an toàn.

#### 6.5. Ví dụ cho thấy workflow cố định là chưa đủ

**Yêu cầu ban đầu:**  
“Mình muốn tìm một mối quan hệ nghiêm túc, ưu tiên sự nghiệp và có thể chuyển nơi sống nếu thực sự phù hợp.”

**Nếu dùng workflow/rule:**

```text
[Form cố định]
→ [Distance filter = giá trị mặc định]
→ [Tính score]
→ [Trả top 5]
```

Hệ thống không biết “có thể chuyển” là hard constraint, soft preference hay một khả năng rất thấp.

**Nếu dùng Agent:**

```text
1. Phát hiện relocation có uncertainty cao và ảnh hưởng lớn đến candidate pool.
2. Hỏi: “Trong 2 năm tới, bạn sẵn sàng chuyển nơi sống, yêu xa tạm thời,
   hay chỉ muốn tìm người ở cùng thành phố?”
3. Cập nhật preference sau xác nhận.
4. Gọi retrieval + reciprocal ranking.
5. Không tìm được candidate thỏa toàn bộ hard constraint.
6. Chẩn đoán constraint gây empty result.
7. Hỏi người dùng có muốn mở rộng khoảng cách hay giữ tiêu chí và chờ.
8. Với candidate mới, phát hiện mục tiêu con cái chưa có dữ liệu.
9. Hỏi người dùng đây có phải deal-breaker cần biết trước hay có thể tìm hiểu sau.
10. Trả shortlist kèm evidence, trade-off và unknown.
```

Giá trị của Agent nằm ở việc **tự xác định bước 2, 6, 7 và 9 là cần thiết trong ngữ cảnh này**, không phải ở việc viết câu hỏi bằng ngôn ngữ tự nhiên.

#### 6.6. Agent hai phía — hướng tạo khác biệt mạnh hơn

Ở giai đoạn sau, mỗi người dùng có thể có một Preference Agent riêng. Hai Agent không tự nhắn tin tình cảm hay thay chủ thể “thương lượng”, mà chỉ thực hiện privacy-preserving compatibility check:

```text
[Agent A: preference đã consent]
          ↘
        [Mutual constraint check]
          ↗
[Agent B: preference đã consent]

Kết quả chỉ trả:
- compatible dimension;
- hard conflict;
- information cần hai bên tự nguyện bổ sung;
- trạng thái đủ/không đủ consent.
```

Cách này có ba lợi ích:

- Tương thích được đánh giá hai chiều ngay cả khi mỗi người có preference khác nhau.
- Không cần hiển thị toàn bộ preference nhạy cảm của B cho A hoặc ngược lại.
- Một người thay đổi tiêu chí sẽ kích hoạt đánh giá lại có kiểm soát, thay vì giữ một score tĩnh.

Đây là phần mang tính Agent rõ hơn reciprocal ranking thông thường, nhưng chỉ nên triển khai sau khi single-user Agent, consent model và deterministic tools đã ổn định.

#### 6.7. Những phần không nên “agent hóa”

Để tránh dùng Agent chỉ vì xu hướng, các phần sau vẫn nên là rule/model/tool:

- Kiểm tra tuổi tối thiểu, trạng thái consent và eligibility.
- Thực thi hard constraint đã được xác nhận.
- Truy vấn cơ sở dữ liệu ứng viên.
- Tính reciprocal score, calibration và fairness metric.
- Phát hiện vi phạm safety có rule rõ.
- Ghi log, versioning và audit.
- Gửi tin nhắn, chia sẻ liên hệ hoặc đặt lịch: chỉ thực hiện sau thao tác xác nhận trực tiếp của người dùng.

Agent **không thay thế** các thành phần này; Agent chỉ quyết định khi nào cần dùng chúng và cách tiếp tục từ kết quả.

#### 6.8. Điều kiện để khẳng định “Agent là cần thiết”

Lập luận kiến trúc chưa đủ; cần chứng minh bằng thực nghiệm so sánh ba baseline:

| Phiên bản | Mô tả |
|---|---|
| Baseline A | Form cố định + hard filter + weighted score |
| Baseline B | Chat UI nhưng theo decision tree/workflow cố định |
| Cupid Agent | Dynamic state + next-action policy + tool orchestration + feedback loop |

**Metric cần đo:**

- Số câu hỏi và thời gian để đạt cùng mức preference completeness.
- Mức giảm uncertainty sau mỗi câu hỏi.
- Tỷ lệ câu hỏi bị người dùng đánh giá là không liên quan/lặp lại.
- Utility của shortlist do người dùng pairwise-rate.
- Tỷ lệ phát hiện hard conflict trước khi bắt đầu trò chuyện.
- Tỷ lệ đề xuất vi phạm hard constraint hoặc consent — mục tiêu bắt buộc bằng 0.
- Calibration của `match/trade-off/unknown`.
- Khả năng phục hồi từ empty result mà không tự ý nới constraint.
- Mức regret của người dùng sau khi xem lại quyết định.
- Số thay đổi preference do Agent đề xuất nhưng bị người dùng từ chối.

**Tiêu chí kết luận:**

- Nếu mọi người dùng gần như đi qua cùng một chuỗi hành động, Agent không cần thiết; nên quay về workflow để giảm chi phí và rủi ro.
- Nếu Agent chọn được các câu hỏi/hành động khác nhau theo state, giảm đáng kể số câu hỏi hoặc thời gian nhưng vẫn cải thiện shortlist utility và không làm tăng vi phạm an toàn, việc dùng Agent mới được chứng minh.

#### 6.9. Lập luận pitch ngắn gọn

> Cupid Agent không được xây dựng để thay một compatibility formula bằng LLM. Hệ thống cần Agent vì quá trình ghép đôi bắt đầu từ preference chưa đầy đủ, có nhiều mục tiêu xung đột và candidate pool luôn thay đổi. Agent duy trì trạng thái về điều người dùng muốn và mức độ chắc chắn, tự chọn giữa hỏi thêm, truy xuất, so sánh, giải thích, xin phép điều chỉnh phạm vi hoặc dừng; trong khi rule và model chuyên biệt vẫn chịu trách nhiệm lọc, chấm điểm và kiểm soát an toàn. Nhờ đó, sản phẩm chuyển từ một pipeline “nhập dữ liệu–nhận kết quả” thành một trợ lý theo đuổi mục tiêu cùng người dùng qua nhiều lượt nhưng không thay người dùng ra quyết định.

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
