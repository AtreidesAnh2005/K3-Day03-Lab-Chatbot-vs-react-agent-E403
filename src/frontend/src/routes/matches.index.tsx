import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Heart, MapPin, Sparkles, User, Briefcase, HeartHandshake, Calendar } from "lucide-react";

import {
  findMatches,
  getAuth,
  getProfile,
  personalityLabel,
  type Candidate,
} from "@/lib/cupid-store";
import { api } from "@/lib/api-client";
import { DatePlannerModal } from "@/components/date-planner-modal";

export const Route = createFileRoute("/matches/")({
  head: () => ({
    meta: [
      { title: "Kết nối phù hợp — Cupid Agent" },
      {
        name: "description",
        content: "Danh sách những người có độ tương thích cao nhất với hồ sơ của bạn.",
      },
      { property: "og:title", content: "Kết nối phù hợp — Cupid Agent" },
      { property: "og:description", content: "Danh sách matching cá nhân hoá cho bạn." },
    ],
  }),
  component: Matches,
});

function Matches() {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState<Candidate[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [isPlannerOpen, setIsPlannerOpen] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    if (!auth) {
      navigate({ to: "/" });
      return;
    }
    const p = getProfile();
    if (!p) {
      navigate({ to: "/onboarding" });
      return;
    }
    const localCandidates = findMatches(p);
    setCandidates(localCandidates);

    let cancelled = false;
    void api.getMatches(auth.email).then((remoteCandidates) => {
      if (!cancelled && remoteCandidates.length > 0) {
        setCandidates(remoteCandidates);
        setIdx(0);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  const active = candidates?.[idx];

  const dots = useMemo(() => candidates?.map((_, i) => i) ?? [], [candidates]);

  if (!candidates || !active) return null;

  function prev() {
    setIdx((i) => (i - 1 + candidates!.length) % candidates!.length);
  }
  function next() {
    setIdx((i) => (i + 1) % candidates!.length);
  }

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-10">
      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary">
            <Sparkles className="h-3.5 w-3.5" /> Kết quả từ Cupid Classification Algorithm
          </span>
          <h1 className="mt-3 font-display text-4xl sm:text-5xl">
            Những người <span className="text-gradient-romance">phù hợp</span> với bạn
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {candidates.length} kết nối từ dataset giả lập (phần hình ảnh để trống).
          </p>
        </div>
      </div>

      {/* Slideshow */}
      <div className="relative">
        <div className="pointer-events-none absolute -inset-8 rounded-[2.5rem] bg-gradient-romance opacity-20 blur-3xl" />
        <div className="relative overflow-hidden rounded-3xl border border-border/60 bg-card/80 shadow-soft backdrop-blur">
          <div className="grid gap-0 md:grid-cols-[1.1fr_1fr]">
            <div className="relative aspect-[4/5] min-h-[340px] md:aspect-auto">
              {active.photo ? (
                <img
                  src={active.photo}
                  alt={`Ảnh của ${active.name}`}
                  className="absolute inset-0 h-full w-full object-cover"
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-primary/10 via-accent/30 to-rose-500/10 p-6 text-center">
                  <div className="mb-3 flex h-24 w-24 items-center justify-center rounded-full bg-primary/10 text-primary shadow-inner">
                    <User className="h-12 w-12" />
                  </div>
                  <div className="font-display text-3xl text-foreground font-semibold">{active.name}</div>
                  <span className="mt-1 text-xs font-medium text-muted-foreground">
                    Chưa cập nhật ảnh đại diện
                  </span>
                </div>
              )}
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-6 text-white md:hidden">
                <div className="font-display text-3xl">
                  {active.name}, {active.age}
                </div>
                <div className="flex items-center gap-1 text-sm opacity-90">
                  <MapPin className="h-3.5 w-3.5" /> {active.city}
                </div>
              </div>
              <div className="absolute right-4 top-4 rounded-full bg-white/95 px-3 py-1.5 text-xs font-bold text-primary shadow-lg backdrop-blur">
                {active.compatibility}% khớp
              </div>
            </div>

            <div className="flex flex-col p-8">
              <div className="hidden md:block">
                <div className="font-display text-4xl">
                  {active.name}, {active.age}
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                  <span className="inline-flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5" /> {active.city}
                  </span>
                  {active.careerField && (
                    <span className="inline-flex items-center gap-1">
                      <Briefcase className="h-3.5 w-3.5" /> {active.careerField}
                    </span>
                  )}
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <span className="inline-flex w-fit items-center gap-1 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
                  {personalityLabel(active.personality)}
                </span>
                {active.loveLanguage && (
                  <span className="inline-flex w-fit items-center gap-1 rounded-full bg-primary/10 border border-primary/20 px-3 py-1 text-xs font-medium text-primary">
                    <HeartHandshake className="h-3.5 w-3.5" /> {active.loveLanguage}
                  </span>
                )}
              </div>

              <p className="mt-4 text-sm leading-relaxed text-foreground/90">{active.bio}</p>

              <div className="mt-6">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Lý do khớp (Phân tích Cupid AI)
                </div>
                <ul className="mt-2 space-y-1.5">
                  {active.reasons.map((r) => (
                    <li key={r} className="flex items-start gap-2 text-sm">
                      <Heart className="mt-0.5 h-3.5 w-3.5 shrink-0 fill-primary text-primary" />
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-6 flex flex-wrap gap-2">
                {active.interests.map((i) => (
                  <span
                    key={i}
                    className="rounded-full border border-border bg-background px-3 py-1 text-xs"
                  >
                    #{i}
                  </span>
                ))}
              </div>

              <div className="mt-auto flex flex-wrap gap-3 pt-8">
                <button
                  onClick={() => setIsPlannerOpen(true)}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-full bg-primary px-5 py-3 text-xs font-semibold text-primary-foreground shadow-glow transition hover:opacity-95"
                >
                  <Calendar className="h-4 w-4" /> Lên kế hoạch hẹn hò với Date Agent
                </button>
                <Link
                  to="/matches/$id"
                  params={{ id: active.id }}
                  className="inline-flex items-center justify-center gap-1.5 rounded-full border border-border bg-background px-5 py-3 text-xs font-semibold transition hover:bg-accent"
                >
                  Xem chi tiết
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>

          {/* Nav arrows */}
          <button
            onClick={prev}
            aria-label="Trước"
            className="absolute left-3 top-1/2 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-background/90 shadow-lg backdrop-blur transition hover:scale-105"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={next}
            aria-label="Sau"
            className="absolute right-3 top-1/2 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-background/90 shadow-lg backdrop-blur transition hover:scale-105"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        {/* Dots */}
        <div className="mt-6 flex justify-center gap-1.5">
          {dots.map((i) => (
            <button
              key={i}
              onClick={() => setIdx(i)}
              aria-label={`Đến kết nối ${i + 1}`}
              className={`h-1.5 rounded-full transition-all ${
                i === idx ? "w-8 bg-primary" : "w-1.5 bg-border hover:bg-primary/40"
              }`}
            />
          ))}
        </div>
      </div>

      {/* Thumbnails */}
      <div className="mt-10">
        <h2 className="mb-4 font-display text-2xl">Tất cả kết nối ({candidates.length})</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {candidates.map((c, i) => (
            <button
              key={c.id}
              onClick={() => setIdx(i)}
              className={`group overflow-hidden rounded-2xl border text-left transition ${
                i === idx
                  ? "border-primary shadow-glow"
                  : "border-border/60 hover:border-primary/40"
              }`}
            >
              <div className="relative aspect-[4/5] bg-gradient-to-br from-primary/5 to-rose-500/10 flex flex-col items-center justify-center p-4 text-center">
                {c.photo ? (
                  <img
                    src={c.photo}
                    alt={c.name}
                    loading="lazy"
                    className="absolute inset-0 h-full w-full object-cover transition group-hover:scale-105"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center">
                    <div className="mb-2 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <User className="h-8 w-8" />
                    </div>
                    <span className="font-display text-lg font-semibold">{c.name}</span>
                  </div>
                )}
                <div className="absolute right-2 top-2 rounded-full bg-white/95 px-2 py-0.5 text-[10px] font-bold text-primary shadow">
                  {c.compatibility}%
                </div>
              </div>
              <div className="p-3">
                <div className="text-sm font-semibold">
                  {c.name}, {c.age}
                </div>
                <div className="text-xs text-muted-foreground">
                  {personalityLabel(c.personality)} · {c.city}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Date Planning Agent Modal */}
      {active && (
        <DatePlannerModal
          candidate={active}
          isOpen={isPlannerOpen}
          onClose={() => setIsPlannerOpen(false)}
        />
      )}
    </main>
  );
}
