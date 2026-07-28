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

        if "observation" in text and "calculate_compatibility" in text:
            return (
                "Thought: Tôi đã có Observation về điểm tương thích và có thể trả lời dựa trên dữ liệu đó.\n"
                "Final Answer: Theo dữ liệu từ công cụ, U003 có điểm tương thích 86 với U001, độ tin cậy 92. "
                "Điểm mạnh là cùng định hướng mối quan hệ lâu dài và tương đồng về giá trị sống. "
                "Điểm cần lưu ý là khác biệt về mức độ giao tiếp xã hội. Đây chỉ là ước lượng hỗ trợ tham khảo, "
                "không bảo đảm hai người sẽ phù hợp trong quan hệ thực tế."
            )

        if "observation" in text and "search_date_activities" in text:
            return (
                "Thought: Tôi đã có sở thích chung và danh sách hoạt động phù hợp ngân sách.\n"
                "Final Answer: U001 và U003 có sở thích chung gồm photography, coffee và art. "
                "Một gợi ý phù hợp ở Hanoi là Cafe triển lãm ảnh với chi phí ước tính 250000 đồng; "
                "ngoài ra Workshop làm gốm có chi phí 400000 đồng. Đây chỉ là đề xuất, hệ thống chưa đặt chỗ, "
                "chưa liên hệ và chưa thanh toán."
            )

        if "observation" in text and "get_shared_interests" in text:
            return (
                "Thought: Tôi đã có sở thích chung, cần dùng chính danh sách này để tìm hoạt động hẹn phù hợp.\n"
                "Action: search_date_activities[\"Hanoi\", [\"photography\", \"coffee\", \"art\"], 500000]"
            )

        if "u001" in text and "u003" in text and (
            "sở thích chung" in text or "so thich chung" in text or "hoạt động hẹn" in text
        ):
            return (
                "Thought: Cần lấy sở thích chung của hai user trước khi gợi ý hoạt động.\n"
                "Action: get_shared_interests[\"U001\", \"U003\"]"
            )

        if "u001" in text and "u003" in text and (
            "tương thích" in text or "tuong thich" in text or "compatibility" in text
        ):
            return (
                "Thought: Cần gọi công cụ tính tương thích cho đúng hai user ID.\n"
                "Action: calculate_compatibility[\"U001\", \"U003\"]"
            )

        if "hard constraint" in text and "soft preference" in text:
            return (
                "Hard constraint là điều kiện bắt buộc; nếu vi phạm thì candidate phải bị loại. "
                "Soft preference là sở thích dùng để xếp hạng hoặc cân nhắc giữa các lựa chọn. "
                "Ví dụ hard constraint: chỉ ghép với người đã có consent. Ví dụ soft preference: thích cafe hoặc nghệ thuật."
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
