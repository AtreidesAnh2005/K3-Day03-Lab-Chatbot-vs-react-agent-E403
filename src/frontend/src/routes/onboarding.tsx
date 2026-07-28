import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Check, Sparkles } from "lucide-react";

import {
  CORE_QUESTIONS,
  DEEP_QUESTIONS,
  getAuth,
  getProfile,
  saveProfile,
  type Personality,
  type Question,
  type UserProfile,
} from "@/lib/cupid-store";
import { api } from "@/lib/api-client";

export const Route = createFileRoute("/onboarding")({
  head: () => ({
    meta: [
      { title: "Xây dựng hồ sơ — Cupid Agent" },
      {
        name: "description",
        content: "Trả lời bộ câu hỏi tính cách để Cupid Agent hiểu bạn và tìm người phù hợp.",
      },
      { property: "og:title", content: "Xây dựng hồ sơ — Cupid Agent" },
      { property: "og:description", content: "Bộ câu hỏi tính cách thích ứng theo bạn." },
    ],
  }),
  component: Onboarding,
});

function Onboarding() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [embedding, setEmbedding] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    if (!auth) {
      navigate({ to: "/" });
      return;
    }
    const existing = getProfile();
    if (existing) setAnswers(existing.answers);
    setReady(true);
  }, [navigate]);

  const personality = answers.personality as Personality | undefined;

  const questions: Question[] = useMemo(() => {
    const deep = personality ? DEEP_QUESTIONS[personality] : [];
    return [...CORE_QUESTIONS, ...deep];
  }, [personality]);

  if (!ready) return null;

  const current = questions[step];
  const total = questions.length;
  const isLast = step === total - 1;
  const answered = current ? !!answers[current.id]?.trim() : false;

  function handleNext() {
    if (!answered) return;
    if (!isLast) {
      setStep((s) => s + 1);
      return;
    }
    const auth = getAuth()!;
    const profile: UserProfile = {
      name: auth.name,
      email: auth.email,
      gender: answers.gender as UserProfile["gender"],
      birthYear: parseInt(answers.birthYear, 10),
      personality: answers.personality as Personality,
      answers,
      createdAt: new Date().toISOString(),
    };
    setEmbedding(true);
    saveProfile(profile);
    void Promise.all([
      api.submitProfile(profile),
      new Promise((resolve) => setTimeout(resolve, 800)),
    ]).finally(() => {
      navigate({ to: "/profile" });
    });
  }

  function setAnswer(value: string) {
    setAnswers((a) => ({ ...a, [current.id]: value }));
  }

  const progress = ((step + (answered ? 1 : 0)) / total) * 100;

  if (embedding) return <EmbeddingScreen />;

  return (
    <main className="mx-auto max-w-2xl px-6 pb-24 pt-10">
      <div className="mb-6 flex items-center justify-between text-xs text-muted-foreground">
        <span>
          Câu {step + 1} / {total}
        </span>
        <span>
          {step < CORE_QUESTIONS.length ? "Câu hỏi cơ bản" : "Đào sâu tính cách"}
        </span>
      </div>
      <div className="mb-8 h-1.5 overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full bg-gradient-romance transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="rounded-3xl border border-border/60 bg-card/80 p-8 shadow-soft backdrop-blur">
        <h1 className="font-display text-3xl leading-tight sm:text-4xl">{current.text}</h1>

        {current.type === "single" && current.options ? (
          <div className="mt-6 grid gap-2">
            {current.options.map((opt) => {
              const selected = answers[current.id] === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setAnswer(opt.value)}
                  className={`group flex items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition ${
                    selected
                      ? "border-primary bg-primary/5 shadow-glow"
                      : "border-border bg-background hover:border-primary/40 hover:bg-accent/40"
                  }`}
                >
                  <span className="pr-2">{opt.label}</span>
                  <span
                    className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                      selected ? "border-primary bg-primary text-primary-foreground" : "border-input"
                    }`}
                  >
                    {selected && <Check className="h-3 w-3" />}
                  </span>
                </button>
              );
            })}
          </div>
        ) : (
          <textarea
            key={current.id}
            value={answers[current.id] || ""}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Chia sẻ càng nhiều càng tốt — Cupid Agent sẽ hiểu bạn hơn..."
            rows={5}
            className="mt-6 w-full resize-none rounded-xl border border-input bg-background px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
          />
        )}

        <div className="mt-8 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm text-muted-foreground transition hover:text-foreground disabled:opacity-40"
          >
            <ArrowLeft className="h-4 w-4" /> Quay lại
          </button>
          <button
            type="button"
            onClick={handleNext}
            disabled={!answered}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-glow transition hover:opacity-95 disabled:opacity-40 disabled:shadow-none"
          >
            {isLast ? "Hoàn tất & tìm kết nối" : "Tiếp theo"}
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </main>
  );
}

function EmbeddingScreen() {
  const steps = [
    "Profile Agent đang xây dựng hồ sơ...",
    "Đang embed thành vector 1536 chiều...",
    "Matching Agent đang tìm kết nối phù hợp...",
  ];
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % steps.length), 500);
    return () => clearInterval(t);
  }, []);
  return (
    <main className="flex min-h-[70vh] items-center justify-center px-6">
      <div className="text-center">
        <div className="relative mx-auto mb-6 h-20 w-20">
          <div className="absolute inset-0 rounded-full bg-gradient-romance opacity-40 blur-2xl" />
          <div className="relative flex h-full w-full items-center justify-center rounded-full bg-primary/10">
            <Sparkles className="h-8 w-8 animate-pulse text-primary" />
          </div>
        </div>
        <h2 className="font-display text-3xl">Đang phân tích bạn...</h2>
        <p className="mt-2 text-sm text-muted-foreground">{steps[i]}</p>
      </div>
    </main>
  );
}
