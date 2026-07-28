import type { Candidate, UserProfile } from "./cupid-store";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(
      "Không kết nối được backend. Hãy kiểm tra FastAPI đang chạy tại cổng 8000.",
      0,
    );
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail;
    const message =
      (typeof detail === "object" && detail?.message) ||
      (typeof detail === "string" && detail) ||
      `Backend trả về lỗi HTTP ${response.status}.`;
    throw new ApiError(message, response.status);
  }
  return payload as T;
}

export interface ProfileAnalysis {
  success: boolean;
  profileId: string;
  mode: string;
  profile: {
    user_id?: string;
    display_name?: string;
    age?: number;
    city?: string;
    relationship_goal?: string;
    interests?: string[];
    values?: string[];
    communication_style?: string;
  };
  completeness: {
    profile_complete?: boolean;
    completeness_ratio?: number;
    missing_required_fields?: string[];
    missing_optional_fields?: string[];
    recommended_action?: string;
  };
  requestId: string;
}

export interface ChatResponse {
  reply: string;
  suggestedTopics?: string[];
  safetyApproved: boolean;
  requestId: string;
}

export interface DatePlanItem {
  step: number;
  time: string;
  title: string;
  location: string;
  description: string;
  tag: string;
}

export interface DatePlanResponse {
  candidateName: string;
  theme: string;
  items: DatePlanItem[];
  icebreakerQuestions: string[];
  requestId: string;
}

export const api = {
  submitProfile(profile: UserProfile): Promise<ProfileAnalysis> {
    return requestJson<ProfileAnalysis>("/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    });
  },

  getProfileAnalysis(userEmail: string): Promise<ProfileAnalysis> {
    return requestJson<ProfileAnalysis>(
      `/profile?email=${encodeURIComponent(userEmail)}`,
    );
  },

  getMatches(userEmail: string): Promise<Candidate[]> {
    return requestJson<Candidate[]>(
      `/matches?email=${encodeURIComponent(userEmail)}`,
    );
  },

  generateDatePlan(candidateId: string, customPrompt?: string): Promise<DatePlanResponse> {
    return requestJson<DatePlanResponse>("/date-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidateId, customPrompt }),
    });
  },

  sendMessage(candidateId: string, message: string): Promise<ChatResponse> {
    return requestJson<ChatResponse>("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidateId, message }),
    });
  },
};
