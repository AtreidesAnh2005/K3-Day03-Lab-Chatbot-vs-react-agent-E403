// Client-side auth/onboarding state. Match data always comes from the backend tools.

export type Personality =
  | "introvert"
  | "extrovert"
  | "ambivert"
  | "analytical"
  | "creative"
  | "adventurous";

export interface UserProfile {
  name: string;
  email: string;
  gender: "female" | "male" | "nonbinary";
  birthYear: number;
  personality: Personality;
  answers: Record<string, string>;
  createdAt: string;
}

export interface Candidate {
  id: string;
  name: string;
  age: number;
  city: string;
  careerField: string;
  loveLanguage: string;
  personality: Personality;
  photo: string;
  bio: string;
  interests: string[];
  compatibility: number;
  confidence: "low" | "medium" | "high" | number;
  coverageRatio: number | null;
  reasons: string[];
  dimensions: {
    key: string;
    label: string;
    value: number;
    result: "aligned" | "trade_off" | "hard_conflict" | "unknown";
  }[];
  limitations: string[];
}

const AUTH_KEY = "cupid.auth";
const PROFILE_KEY = "cupid.profile";

export function getAuth(): { email: string; name: string } | null {
  if (typeof window === "undefined") return null;
  try {
    return JSON.parse(localStorage.getItem(AUTH_KEY) || "null");
  } catch {
    return null;
  }
}

export function signIn(email: string, name: string) {
  localStorage.setItem(AUTH_KEY, JSON.stringify({ email, name }));
}

export function signOut() {
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(PROFILE_KEY);
}

export function getProfile(): UserProfile | null {
  if (typeof window === "undefined") return null;
  try {
    return JSON.parse(localStorage.getItem(PROFILE_KEY) || "null");
  } catch {
    return null;
  }
}

export function saveProfile(profile: UserProfile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

// ----- Questions -----

export interface Question {
  id: string;
  text: string;
  type: "single" | "text";
  options?: { value: string; label: string }[];
}

export const CORE_QUESTIONS: Question[] = [
  {
    id: "gender",
    text: "Bạn xác định giới tính của mình là?",
    type: "single",
    options: [
      { value: "female", label: "Nữ" },
      { value: "male", label: "Nam" },
      { value: "nonbinary", label: "Phi nhị nguyên" },
    ],
  },
  {
    id: "birthYear",
    text: "Bạn sinh năm nào?",
    type: "single",
    options: Array.from({ length: 30 }, (_, i) => {
      const y = 2006 - i;
      return { value: String(y), label: String(y) };
    }),
  },
  {
    id: "personality",
    text: "Tính cách nào mô tả bạn đúng nhất?",
    type: "single",
    options: [
      { value: "introvert", label: "Hướng nội — Thích yên tĩnh, sâu lắng" },
      { value: "extrovert", label: "Hướng ngoại — Tràn đầy năng lượng kết nối" },
      { value: "ambivert", label: "Cân bằng — Linh hoạt theo hoàn cảnh" },
      { value: "analytical", label: "Lý trí — Logic, quan sát tỉ mỉ" },
      { value: "creative", label: "Sáng tạo — Nghệ thuật, ý tưởng độc đáo" },
      { value: "adventurous", label: "Phiêu lưu — Thích khám phá, thử thách" },
    ],
  },
];

export const DEEP_QUESTIONS: Record<Personality, Question[]> = {
  introvert: [
    {
      id: "idealEvening",
      text: "Buổi tối lý tưởng của bạn cùng đối phương là?",
      type: "single",
      options: [
        { value: "book_tea", label: "Đọc sách, uống trà tại nhà" },
        { value: "quiet_cafe", label: "Một quán cà phê vắng người" },
        { value: "movie_night", label: "Xem phim tại gia" },
      ],
    },
    {
      id: "deepNote",
      text: "Điều bạn tìm kiếm nhất ở người ấy?",
      type: "text",
    },
  ],
  extrovert: [
    {
      id: "weekendActivity",
      text: "Cuối tuần của bạn thường thế nào?",
      type: "single",
      options: [
        { value: "party_friends", label: "Tụ tập bạn bè đông vui" },
        { value: "outdoor_sports", label: "Tham gia các sự kiện ngoài trời" },
        { value: "workshop", label: "Tham gia workshop / câu lạc bộ mới" },
      ],
    },
    {
      id: "energyNote",
      text: "Bạn muốn cùng người ấy trải nghiệm hoạt động gì tiếp theo?",
      type: "text",
    },
  ],
  ambivert: [
    {
      id: "balanceStyle",
      text: "Bạn nạp năng lượng bằng cách nào?",
      type: "single",
      options: [
        { value: "flexible", label: "Tùy tâm trạng — đôi khi đi chơi, đôi khi ở một mình" },
        { value: "one_on_one", label: "Trò chuyện sâu 1-1 với người thân thiết" },
      ],
    },
    {
      id: "ambivertNote",
      text: "Mô tả một ngày hoàn hảo của bạn?",
      type: "text",
    },
  ],
  analytical: [
    {
      id: "conflictStyle",
      text: "Khi có bất đồng, bạn xử lý thế nào?",
      type: "single",
      options: [
        { value: "logic_discussion", label: "Thảo luận thẳng thắn dựa trên lý trí" },
        { value: "time_reflect", label: "Cần thời gian suy nghĩ kỹ trước khi nói" },
      ],
    },
    {
      id: "analyticNote",
      text: "Chủ đề trí tuệ nào bạn thích thảo luận nhất?",
      type: "text",
    },
  ],
  creative: [
    {
      id: "artExpression",
      text: "Lĩnh vực nghệ thuật bạn yêu thích nhất?",
      type: "single",
      options: [
        { value: "music_indie", label: "Âm nhạc / Indie" },
        { value: "design_art", label: "Hội họa / Thiết kế / Nhiếp ảnh" },
        { value: "writing_reading", label: "Văn học / Viết lách" },
      ],
    },
    {
      id: "creativeNote",
      text: "Dự án cá nhân hoặc đam mê bạn đang theo đuổi?",
      type: "text",
    },
  ],
  adventurous: [
    {
      id: "travelStyle",
      text: "Phong cách du lịch của bạn là?",
      type: "single",
      options: [
        { value: "backpacking", label: "Phượt / Khám phá vùng đất mới" },
        { value: "extreme_sports", label: "Thể thao mạo hiểm / Leo núi" },
        { value: "food_tour", label: "Foodtour văn hóa địa phương" },
      ],
    },
    {
      id: "adventureNote",
      text: "Chuyến đi đáng nhớ nhất của bạn là gì?",
      type: "text",
    },
  ],
};

const PERSONALITY_LABEL: Record<Personality, string> = {
  introvert: "Hướng nội",
  extrovert: "Hướng ngoại",
  ambivert: "Cân bằng",
  analytical: "Lý trí",
  creative: "Sáng tạo",
  adventurous: "Phiêu lưu",
};

export function personalityLabel(p: Personality) {
  return PERSONALITY_LABEL[p];
}
