import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  AlertCircle,
  ArrowLeft,
  Briefcase,
  Calendar,
  Heart,
  HeartHandshake,
  Loader2,
  MapPin,
  MessageCircle,
  Send,
  Sparkles,
  User,
  X,
} from "lucide-react";

import {
  getAuth,
  getProfile,
  personalityLabel,
  type Candidate,
} from "@/lib/cupid-store";
import { api } from "@/lib/api-client";
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isPlannerOpen, setIsPlannerOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [chatError, setChatError] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    if (!auth) {
      navigate({ to: "/" });
      return;
    }
    if (!getProfile()) {
      navigate({ to: "/onboarding" });
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError("");
    void api
      .getMatches(auth.email)
      .then((remoteCandidates) => {
        if (!cancelled) {
          setCandidate(remoteCandidates.find((item) => item.id === id) ?? null);
          setLoading(false);
        }
      })
      .catch((reason: Error) => {
        if (!cancelled) {
          setError(reason.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id, navigate]);

  async function handleChatSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!candidate || !message.trim()) return;
    setChatLoading(true);
    setChatError("");
    try {
      const response = await api.sendMessage(candidate.id, message.trim());
      setChatReply(response.reply);
    } catch (reason) {
      setChatError(reason instanceof Error ? reason.message : "Không gửi được tin nhắn.");
    } finally {
      setChatLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-[65vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </main>
    );
  }

  if (error || !candidate) {
    return (
      <main className="flex min-h-[65vh] items-center justify-center px-6">
        <div className="max-w-md text-center">
          <AlertCircle className="mx-auto h-9 w-9 text-destructive" />
          <h1 className="mt-3 font-display text-2xl">Không tìm thấy kết nối</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {error || "Ứng viên này không còn trong danh sách consented hiện tại."}
          </p>
          <Link to="/matches" className="mt-5 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground">
            Về danh sách
          </Link>
        </div>
      </main>
    );
  }

  const dims = candidate.dimensions;

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
              <span className="mt-2 text-sm text-muted-foreground">
                Ảnh không nằm trong dữ liệu được đồng ý chia sẻ
              </span>
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
              {dims.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  Tool chưa có đủ dữ liệu để công bố điểm theo từng chiều.
                </p>
              )}
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
            <button
              onClick={() => setIsChatOpen(true)}
              className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-6 py-3.5 text-sm font-semibold transition hover:bg-accent"
            >
              <MessageCircle className="h-4 w-4 text-muted-foreground" /> Nhắn tin làm quen
            </button>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Kế hoạch và phản hồi chỉ dùng dữ liệu đã được consent; hệ thống không tự đặt chỗ hay chia sẻ thông tin liên hệ.
          </p>
        </div>
      </div>

      {/* Date Planning Agent Modal */}
      <DatePlannerModal
        candidate={candidate}
        isOpen={isPlannerOpen}
        onClose={() => setIsPlannerOpen(false)}
      />

      {isChatOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
          <div className="relative w-full max-w-lg rounded-lg border border-border bg-card p-6 shadow-2xl">
            <button
              onClick={() => setIsChatOpen(false)}
              aria-label="Đóng"
              className="absolute right-4 top-4 rounded-md p-2 text-muted-foreground hover:bg-accent"
            >
              <X className="h-4 w-4" />
            </button>
            <h2 className="font-display text-2xl">Response Agent</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Hỏi cách bắt đầu cuộc trò chuyện an toàn với {candidate.name}.
            </p>

            {chatReply && (
              <div className="mt-5 rounded-md border border-primary/20 bg-primary/5 p-4 text-sm leading-relaxed">
                {chatReply}
              </div>
            )}
            {chatError && (
              <div className="mt-5 flex gap-2 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                {chatError}
              </div>
            )}

            <form onSubmit={handleChatSubmit} className="mt-5 space-y-3">
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Ví dụ: Tôi nên mở đầu cuộc trò chuyện về sở thích chung thế nào?"
                rows={4}
                className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:border-primary"
              />
              <button
                type="submit"
                disabled={chatLoading || !message.trim()}
                className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground disabled:opacity-50"
              >
                {chatLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                Gửi tới agent
              </button>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
