"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


def _latest_observation(prompt: str) -> dict | None:
    """Extract the last structured Observation embedded by the ReAct runner."""
    marker = "Observation:\n"
    marker_index = prompt.rfind(marker)
    if marker_index < 0:
        return None
    raw = prompt[marker_index + len(marker) :].lstrip()
    try:
        observation, _ = json.JSONDecoder().raw_decode(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    return observation if isinstance(observation, dict) else None


def _all_observations(prompt: str) -> list[dict]:
    """Extract structured Observations in the order they entered the trace."""
    marker = "Observation:\n"
    observations: list[dict] = []
    cursor = 0
    decoder = json.JSONDecoder()
    while True:
        marker_index = prompt.find(marker, cursor)
        if marker_index < 0:
            return observations
        raw = prompt[marker_index + len(marker) :].lstrip()
        try:
            observation, consumed = decoder.raw_decode(raw)
        except (json.JSONDecodeError, TypeError):
            cursor = marker_index + len(marker)
            continue
        if isinstance(observation, dict):
            observations.append(observation)
        cursor = marker_index + len(marker) + consumed


def _user_ids(prompt: str) -> list[str]:
    """Return distinct synthetic user IDs while preserving their input order."""
    import re

    found: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"\bU(?:SR)?\d{3}\b", prompt, flags=re.IGNORECASE):
        user_id = match.group(0).upper()
        if user_id not in seen:
            found.append(user_id)
            seen.add(user_id)
    return found


def _date_constraints(prompt: str) -> tuple[str, int]:
    """Extract the deterministic city and maximum budget used by the mock."""
    import re

    text = prompt.casefold()
    if any(alias in text for alias in ("hà nội", "ha noi", "hanoi")):
        city = "Hanoi"
    elif any(alias in text for alias in ("hồ chí minh", "ho chi minh", "tp.hcm")):
        city = "Ho Chi Minh City"
    else:
        city = ""

    budget = 0
    for match in re.finditer(r"\b\d{1,3}(?:[.\s]\d{3})+\b|\b\d{4,}\b", prompt):
        candidate = int(re.sub(r"[.\s]", "", match.group(0)))
        budget = max(budget, candidate)
    return city, budget


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API)"""
    def __init__(self):
        self.model_name = "offline-mock-cupid"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        is_react = "giao thức react" in system_prompt.lower() or "react agent" in system_prompt.lower()
        observation = _latest_observation(prompt)
        observations = _all_observations(prompt)

        if is_react and observation:
            output = observation.get("output") or {}
            data = output.get("data") or {}
            tool_name = observation.get("tool")

            if tool_name == "calculate_compatibility":
                if not data.get("eligible") or not data.get("score_available"):
                    conflicts = ", ".join(data.get("hard_conflicts") or ["không đủ dữ liệu"])
                    return (
                        "Thought: Observation cho thấy cặp hồ sơ không đủ điều kiện để chấm điểm.\n"
                        "Final Answer: Hai hồ sơ hiện không có điểm tương thích hợp lệ. "
                        f"Lý do từ công cụ: {conflicts}. Hệ thống không tự nới lỏng hard constraint."
                    )
                aligned = [
                    name
                    for name, score in (
                        data.get("breakdown") or data.get("dimension_scores") or {}
                    ).items()
                    if score == 100
                ]
                aligned_text = ", ".join(aligned[:3]) or "các tiêu chí đã chia sẻ"
                breakdown = data.get("breakdown") or data.get("dimension_scores") or {}
                breakdown_text = ", ".join(
                    f"{dimension}={score}" for dimension, score in breakdown.items()
                )
                strengths = "; ".join(data.get("strengths") or [aligned_text])
                conflicts = "; ".join(data.get("potential_conflicts") or ["Không có"])
                arguments = observation.get("arguments") or []
                user_id = arguments[0] if arguments else "người dùng"
                candidate_id = data.get("candidate_id") or (
                    arguments[1] if len(arguments) > 1 else "ứng viên"
                )
                return (
                    "Thought: Observation đã có điểm và các chiều tương thích cần thiết.\n"
                    f"Final Answer: Theo dữ liệu từ công cụ, {candidate_id} có score={data.get('score')} "
                    f"với {user_id}, confidence={data.get('confidence')}. "
                    f"Breakdown: {breakdown_text}. "
                    f"Điểm mạnh: {strengths}. "
                    f"Xung đột tiềm ẩn: {conflicts}. "
                    "Đây chỉ là ước lượng từ dữ liệu đã đồng ý chia sẻ, "
                    "không bảo đảm kết quả mối quan hệ."
                )

            if tool_name == "get_shared_interests":
                interests = data.get("shared_interests") or []
                if not interests:
                    return (
                        "Thought: Observation không có sở thích chung để làm căn cứ.\n"
                        "Final Answer: Hiện chưa có sở thích chung đã được xác nhận. "
                        "Tôi không tự tạo dữ liệu thay thế."
                    )
                serialized_interests = json.dumps(interests, ensure_ascii=False)
                city, budget = _date_constraints(prompt)
                if not city or not budget:
                    return (
                        "Thought: Đã có sở thích chung nhưng còn thiếu thành phố hoặc ngân sách.\n"
                        "Final Answer: Vui lòng cung cấp thành phố và ngân sách tối đa để tôi tìm hoạt động phù hợp."
                    )
                return (
                    "Thought: Tôi sẽ dùng đúng sở thích chung từ Observation để tìm hoạt động.\n"
                    f"Action: search_date_activities[{json.dumps(city, ensure_ascii=False)}, "
                    f"{serialized_interests}, {budget}]"
                )

            if tool_name == "search_date_activities":
                activities = data.get("activities") or []
                if not activities:
                    return (
                        "Thought: Observation không tìm thấy hoạt động phù hợp.\n"
                        "Final Answer: Chưa có hoạt động đáp ứng đồng thời địa điểm và ngân sách. "
                        "Bạn có thể điều chỉnh một soft preference."
                    )
                suggestions = "; ".join(
                    (
                        f"{item.get('name')} tại {item.get('city')}, "
                        f"chi phí ước tính {item.get('estimated_cost')} VND"
                    )
                    for item in activities[:2]
                )
                shared_observation = next(
                    (
                        item
                        for item in reversed(observations)
                        if item.get("tool") == "get_shared_interests"
                    ),
                    {},
                )
                shared_data = (shared_observation.get("output") or {}).get("data") or {}
                shared_interests = shared_data.get("shared_interests") or []
                pair_text = " và ".join(
                    filter(
                        None,
                        [
                            shared_data.get("user_a_id"),
                            shared_data.get("user_b_id"),
                        ],
                    )
                )
                shared_text = ", ".join(shared_interests)
                return (
                    "Thought: Observation đã có hoạt động phù hợp để đề xuất.\n"
                    f"Final Answer: {pair_text} có sở thích chung: {shared_text}. "
                    f"Gợi ý từ công cụ: {suggestions}. "
                    "Đây chỉ là đề xuất; hệ thống chưa đặt chỗ, liên hệ hoặc thanh toán."
                )

        if "số điện thoại" in text or "so dien thoai" in text or "matching_consent" in text:
            if not is_react:
                return (
                    "Tôi không thể hỗ trợ tiết lộ thông tin cá nhân hoặc bỏ qua sự đồng ý. "
                    "Bạn có thể gửi lời mời kết nối trong ứng dụng để người kia tự quyết định có chia sẻ thông tin hay không."
                )
            return (
                "Thought: Yêu cầu này liên quan quyền riêng tư hoặc consent nên không thể tiếp tục an toàn.\n"
                "Final Answer: Tôi không thể hỗ trợ tiết lộ thông tin cá nhân hoặc bỏ qua sự đồng ý. "
                "Bạn có thể gửi lời mời kết nối trong ứng dụng để người kia tự quyết định có chia sẻ thông tin hay không."
            )

        user_ids = _user_ids(prompt)
        if len(user_ids) >= 2 and (
            "sở thích chung" in text or "so thich chung" in text or "hoạt động hẹn" in text
        ):
            return (
                "Thought: Cần lấy sở thích chung của hai user trước khi gợi ý hoạt động.\n"
                f"Action: get_shared_interests[{json.dumps(user_ids[0])}, "
                f"{json.dumps(user_ids[1])}]"
            )

        if len(user_ids) >= 2 and (
            "tương thích" in text or "tuong thich" in text or "compatibility" in text
        ):
            return (
                "Thought: Cần gọi công cụ tính tương thích cho đúng hai user ID.\n"
                f"Action: calculate_compatibility[{json.dumps(user_ids[0])}, "
                f"{json.dumps(user_ids[1])}]"
            )

        if "hard constraint" in text and "soft preference" in text:
            return (
                "Hard constraint là điều kiện bắt buộc; nếu vi phạm thì candidate phải bị loại. "
                "Soft preference là sở thích dùng để xếp hạng hoặc cân nhắc giữa các lựa chọn. "
                "Ví dụ hard constraint: người dùng yêu cầu cùng mục tiêu mối quan hệ lâu dài, nên candidate "
                "có relationship goal khác phải bị loại. Ví dụ soft preference: các interests (sở thích) như coffee "
                "hoặc art có thể dùng để ưu tiên xếp hạng. Hệ thống không được tự nới hard constraint "
                "khi thiếu candidate."
            )

        if "điểm tương thích" in text or "diem tuong thich" in text or "compatibility score" in text:
            return (
                "Điểm tương thích không bảo đảm hai người sẽ yêu nhau lâu dài. "
                "Nó chỉ là một ước lượng từ dữ liệu và preference đã cung cấp; kết quả thực tế còn phụ thuộc vào giao tiếp, "
                "ranh giới cá nhân, thời gian và cách hai người tương tác ngoài đời."
            )

        return "Mock Provider: Phản hồi giả lập offline cho bài test Cupid Agent."


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
