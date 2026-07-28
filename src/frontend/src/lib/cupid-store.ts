// Client-side store & synthetic candidate dataset generated from cupid-classification algorithm dataset.
// Photo fields are intentionally left blank ("") as requested.

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
  photo: string; // Trống ("") theo yêu cầu
  bio: string;
  interests: string[];
  compatibility: number;
  reasons: string[];
  bigFive?: {
    openness: number;
    extraversion: number;
    agreeableness: number;
    conscientiousness: number;
  };
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

// ----- Candidate Dataset (Gia lập từ Cupid Classification Dataset, photo: "") -----

const NAMES_F = ["Thu Hà", "Phương Anh", "Bích Ngọc", "Khánh Linh", "Thanh Mai", "Hải Yến", "Tố Uyên", "Quỳnh Chi"];
const NAMES_M = ["Nhật Minh", "Hoàng Nam", "Gia Khoa", "Thành Duy", "Hải Phong", "Quốc Bảo", "Đăng Long", "Quang Huy"];
const CITIES = ["Hà Nội", "TP.HCM", "Đà Nẵng", "Huế", "Nha Trang", "Đà Lạt"];
const CAREER_FIELDS = [
  "Tech", "Finance", "Healthcare", "Marketing", "Engineering",
  "Creative Arts", "Entrepreneurship", "Education", "Law", "Science"
];
const LOVE_LANGUAGES = [
  "Quality Time", "Words of Affirmation", "Physical Touch", "Acts of Service", "Receiving Gifts"
];

const INTERESTS = [
  "cà phê", "sách", "leo núi", "nhiếp ảnh", "âm nhạc indie",
  "nấu ăn", "du lịch", "yoga", "gaming", "phim nghệ thuật",
  "vẽ tranh", "chạy bộ", "podcast", "startup", "thiên văn",
];

function seeded(i: number) {
  return Math.abs(Math.sin(i * 9301 + 49297) * 233280) % 1;
}

function pick<T>(arr: T[], i: number): T {
  return arr[Math.floor(seeded(i) * arr.length)];
}

function pickMany<T>(arr: T[], count: number, seed: number): T[] {
  const out: T[] = [];
  const used = new Set<number>();
  let k = 0;
  while (out.length < count && k < 50) {
    const idx = Math.floor(seeded(seed + k) * arr.length);
    if (!used.has(idx)) {
      used.add(idx);
      out.push(arr[idx]);
    }
    k++;
  }
  return out;
}

const PERSONALITIES: Personality[] = [
  "introvert", "extrovert", "ambivert", "analytical", "creative", "adventurous",
];

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

const COMPAT: Record<Personality, Partial<Record<Personality, number>>> = {
  introvert: { introvert: 0.88, creative: 0.92, analytical: 0.85, ambivert: 0.78, extrovert: 0.58, adventurous: 0.64 },
  extrovert: { extrovert: 0.86, adventurous: 0.94, ambivert: 0.84, creative: 0.78, analytical: 0.62, introvert: 0.58 },
  ambivert: { ambivert: 0.88, introvert: 0.82, extrovert: 0.85, creative: 0.82, analytical: 0.8, adventurous: 0.78 },
  analytical: { analytical: 0.86, introvert: 0.85, creative: 0.8, ambivert: 0.8, extrovert: 0.62, adventurous: 0.72 },
  creative: { creative: 0.9, introvert: 0.92, adventurous: 0.88, ambivert: 0.82, extrovert: 0.78, analytical: 0.8 },
  adventurous: { adventurous: 0.89, extrovert: 0.94, creative: 0.88, ambivert: 0.78, analytical: 0.72, introvert: 0.64 },
};

export function findMatches(profile: UserProfile): Candidate[] {
  const targetGender: UserProfile["gender"] =
    profile.gender === "female" ? "male" : profile.gender === "male" ? "female" : "nonbinary";
  const namePool = targetGender === "male" ? NAMES_M : NAMES_F;

  const candidates: Candidate[] = Array.from({ length: 8 }, (_, i) => {
    const seed = i * 17 + profile.birthYear;
    const personality = pick(PERSONALITIES, seed + 3);
    const baseScore = COMPAT[profile.personality][personality] ?? 0.65;
    const jitter = (seeded(seed + 7) - 0.5) * 0.08;
    const score = Math.min(0.99, Math.max(0.6, baseScore + jitter));
    const age = new Date().getFullYear() - profile.birthYear + Math.floor((seeded(seed + 11) - 0.5) * 6);

    const careerField = pick(CAREER_FIELDS, seed + 2);
    const loveLanguage = pick(LOVE_LANGUAGES, seed + 4);
    const reasons = buildReasons(profile.personality, personality, careerField, loveLanguage);

    return {
      id: `cand-${i + 1}`,
      name: pick(namePool, seed),
      age: Math.max(21, age),
      city: pick(CITIES, seed + 1),
      careerField,
      loveLanguage,
      personality,
      photo: "", // ĐỂ TRỐNG PHẦN HÌNH ẢNH THEO YÊU CẦU
      bio: bioFor(personality, careerField, seed),
      interests: pickMany(INTERESTS, 4, seed + 5),
      compatibility: Math.round(score * 100),
      reasons,
      bigFive: {
        openness: Math.round((seeded(seed + 12) * 0.4 + 0.6) * 100) / 100,
        extraversion: Math.round((seeded(seed + 13) * 0.5 + 0.5) * 100) / 100,
        agreeableness: Math.round((seeded(seed + 14) * 0.3 + 0.7) * 100) / 100,
        conscientiousness: Math.round((seeded(seed + 15) * 0.4 + 0.6) * 100) / 100,
      },
    };
  });

  return candidates.sort((a, b) => b.compatibility - a.compatibility);
}

function bioFor(p: Personality, career: string, seed: number): string {
  const bios: Record<Personality, string[]> = {
    introvert: [
      `Làm việc trong lĩnh vực ${career}. Thích buổi tối yên tĩnh với một cuốn sách và tách trà nóng.`,
      `Chuyên viên ${career}. Thích những cuộc trò chuyện sâu lắng hơn là những buổi tiệc náo nhiệt.`,
    ],
    extrovert: [
      `Hoạt động trong ngành ${career}. Luôn tràn đầy năng lượng và có kế hoạch trải nghiệm mới cuối tuần.`,
      `Làm ${career}. Tôi tin rằng mọi tình bạn và tình yêu đẹp đều bắt đầu từ một cuộc gặp gỡ tình cờ.`,
    ],
    ambivert: [
      `Làm việc trong lĩnh vực ${career}. Thích sự cân bằng giữa tập trung công việc và tận hưởng cuộc sống.`,
      `Chuyên môn ${career}. Cân bằng giữa không gian riêng tư và thời gian chất lượng bên người thân.`,
    ],
    analytical: [
      `Làm việc trong ngành ${career}. Đam mê logic, giải quyết vấn đề và tìm kiếm sự đồng điệu trí tuệ.`,
      `Nhà phân tích trong lĩnh vực ${career}. Tin vào sự thật khách quan và sự chân thành trong tình cảm.`,
    ],
    creative: [
      `Làm việc trong ngành ${career}. Yêu nghệ thuật, âm nhạc và những ý tưởng đột phá trong cuộc sống.`,
      `Sáng tạo nội dung / thiết kế trong ngành ${career}. Luôn nhìn thế giới qua lăng kính nhiều màu sắc.`,
    ],
    adventurous: [
      `Làm việc trong lĩnh vực ${career}. Đã đi qua nhiều nơi và luôn sẵn sàng cho chuyến đi tiếp theo.`,
      `Theo đuổi sự nghiệp ${career}. Đam mê khám phá văn hóa, ẩm thực và trải nghiệm điều mới lạ.`,
    ],
  };
  return bios[p][Math.floor(seeded(seed) * bios[p].length)];
}

function buildReasons(a: Personality, b: Personality, career: string, loveLang: string): string[] {
  const reasons: string[] = [];
  if (a === b) reasons.push("Cùng nhóm tính cách — dễ dàng thấu hiểu suy nghĩ của nhau");
  if (loveLang === "Quality Time") reasons.push("Ngôn ngữ tình yêu 'Quality Time' — coi trọng thời gian bên nhau");
  if (loveLang === "Words of Affirmation") reasons.push("Ngôn ngữ tình yêu 'Words of Affirmation' — thích giao tiếp tích cực");
  if (career) reasons.push(`Nền tảng nghề nghiệp thuộc lĩnh vực ${career} với góc nhìn rộng mở`);
  reasons.push("Độ tương thích cao từ chỉ số phân tích thuật toán Cupid Classification");
  reasons.push("Sở thích và giá trị sống có nhiều điểm đồng điệu");
  return reasons.slice(0, 3);
}
