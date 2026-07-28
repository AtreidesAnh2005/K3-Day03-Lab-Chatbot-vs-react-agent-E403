import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowLeft, Heart, MapPin, MessageCircle, Sparkles, User, Briefcase, HeartHandshake, Calendar } from "lucide-react";

import {
  findMatches,
  getAuth,
  getProfile,
  personalityLabel,
  type Candidate,
} from "@/lib/cupid-store";
import { DatePlannerModal } from "@/components/date-planner-modal";

export const Route = createFileRoute("/matches/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `Chi tiết kết nối — Cupid Agent` },
      {
        name: "description",
        content: `Thông tin chi tiết về kết nối #${params.id} do Matching Agent gợi ý.`,
      },
      { property: "og:title", content: "Chi tiết kết nối — Cupid Agent" },
    ],
  }),
  component: MatchDetail,
});

function MatchDetail() {
  const { id } = Route.useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [isPlannerOpen, setIsPlannerOpen] = useState(false);

  useEffect(() => {
    if (!getAuth()) {
      navigate({ to: "/" });
      return;
    }
    const p = getProfile();
    if (!p) {
      navigate({ to: "/onboarding" });
      return;
    }
    const list = findMatches(p);
    setCandidate(list.find((c) => c.id === id) ?? null);
  }, [id, navigate]);

  if (!candidate) return null;

  const dims = [
    { label: "Giá trị sống & Định hướng", value: Math.min(99, candidate.compatibility + 2) },
    { label: "Phong cách giao tiếp", value: Math.max(60, candidate.compatibility - 4) },
    { label: "Sở thích & Quan niệm tình yêu", value: Math.max(65, candidate.compatibility - 2) },
    { label: "Nhịp sống & Tính cách (Big Five)", value: Math.max(55, candidate.compatibility - 6) },
  ];

  return (
    <main className="mx-auto max-w-5xl px-6 pb-24 pt-10">
      <Link
        to="/matches"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground transition hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> Về danh sách
      </Link>

      <div className="mt-6 grid gap-8 lg:grid-cols-[1fr_1.1fr]">
        <div className="relative overflow-hidden rounded-3xl border border-border/60 shadow-soft bg-gradient-to-br from-primary/5 via-accent/20 to-rose-500/10 min-h-[380px] flex items-center justify-center p-8">
          {candidate.photo ? (
            <img
              src={candidate.photo}
              alt={`Ảnh của ${candidate.name}`}
              className="aspect-[4/5] w-full object-cover"
            />
          ) : (
            <div className="flex flex-col items-center justify-center text-center">
              <div className="mb-4 flex h-32 w-32 items-center justify-center rounded-full bg-primary/10 text-primary shadow-inner">
                <User className="h-16 w-16" />
              </div>
              <div className="font-display text-4xl font-bold text-foreground">{candidate.name}</div>
              <span className="mt-2 text-sm text-muted-foreground">Hồ sơ giả lập từ Cupid Classification</span>
            </div>
          )}
          <div className="absolute right-4 top-4 rounded-full bg-white/95 px-3.5 py-1.5 text-xs font-bold text-primary shadow-lg backdrop-blur">
            {candidate.compatibility}% khớp
          </div>
        </div>

        <div>
          <h1 className="font-display text-5xl">
            {candidate.name}, {candidate.age}
          </h1>
          <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <span className="inline-flex items-center gap-1">
              <MapPin className="h-4 w-4" /> {candidate.city}
            </span>
            <span>·</span>
            <span>{personalityLabel(candidate.personality)}</span>
            {candidate.careerField && (
              <>
                <span>·</span>
                <span className="inline-flex items-center gap-1">
                  <Briefcase className="h-3.5 w-3.5" /> {candidate.careerField}
                </span>
              </>
            )}
            {candidate.loveLanguage && (
              <>
                <span>·</span>
                <span className="inline-flex items-center gap-1 text-primary font-medium">
                  <HeartHandshake className="h-3.5 w-3.5" /> {candidate.loveLanguage}
                </span>
              </>
            )}
          </div>

          <p className="mt-6 text-base leading-relaxed">{candidate.bio}</p>

          <div className="mt-8">
            <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              <Sparkles className="h-3.5 w-3.5" /> Phân tích tương thích multi-agent
            </div>
            <div className="space-y-3">
              {dims.map((d) => (
                <div key={d.label}>
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="text-muted-foreground">{d.label}</span>
                    <span className="font-semibold">{d.value}%</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full rounded-full bg-gradient-romance"
                      style={{ width: `${d.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Vì sao Matching Agent chọn
            </div>
            <ul className="space-y-2">
              {candidate.reasons.map((r) => (
                <li key={r} className="flex items-start gap-2 text-sm">
                  <Heart className="mt-0.5 h-4 w-4 shrink-0 fill-primary text-primary" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {candidate.interests.map((i) => (
              <span
                key={i}
                className="rounded-full border border-border bg-background px-3 py-1 text-xs"
              >
                #{i}
              </span>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              onClick={() => setIsPlannerOpen(true)}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground shadow-glow transition hover:opacity-95"
            >
              <Calendar className="h-4 w-4" /> Lên kế hoạch hẹn hò với Date Agent
            </button>
            <button className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-6 py-3.5 text-sm font-semibold transition hover:bg-accent">
              <MessageCircle className="h-4 w-4 text-muted-foreground" /> Nhắn tin làm quen
            </button>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Bấm vào nút để **Date Planning Agent** tự động lập lịch trình 3 bước lãng mạn & chủ đề trò chuyện phá băng.
          </p>
        </div>
      </div>

      {/* Date Planning Agent Modal */}
      <DatePlannerModal
        candidate={candidate}
        isOpen={isPlannerOpen}
        onClose={() => setIsPlannerOpen(false)}
      />
    </main>
  );
}
