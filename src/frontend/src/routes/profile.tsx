import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  User,
  Sparkles,
  Heart,
  ShieldCheck,
  ArrowRight,
  RotateCcw,
  LogOut,
  Mail,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Database,
  Loader2,
} from "lucide-react";

import {
  getAuth,
  getProfile,
  signOut,
  personalityLabel,
  CORE_QUESTIONS,
  DEEP_QUESTIONS,
  type UserProfile,
} from "@/lib/cupid-store";
import { api, type ProfileAnalysis } from "@/lib/api-client";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: "Hồ sơ cá nhân — Cupid Agent" },
      {
        name: "description",
        content: "Trang thông tin hồ sơ và trạng thái dữ liệu matching đã consent.",
      },
      { property: "og:title", content: "Hồ sơ cá nhân — Cupid Agent" },
    ],
  }),
  component: ProfilePage,
});

function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [analysis, setAnalysis] = useState<ProfileAnalysis | null>(null);
  const [analysisError, setAnalysisError] = useState("");

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
    setProfile(p);
    let cancelled = false;
    void api
      .getProfileAnalysis(auth.email)
      .then((result) => {
        if (!cancelled) setAnalysis(result);
      })
      .catch((reason: Error) => {
        if (!cancelled) setAnalysisError(reason.message);
      });
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (!profile) return null;

  const currentYear = new Date().getFullYear();
  const age = currentYear - profile.birthYear;
  const completeness = Math.round((analysis?.completeness.completeness_ratio ?? 0) * 100);
  const missingOptionalFields = analysis?.completeness.missing_optional_fields ?? [];

  const genderLabel =
    profile.gender === "female" ? "Nữ" : profile.gender === "male" ? "Nam" : "Phi nhị nguyên";

  // Build list of all questions & user's answers
  const deepQuestions = profile.personality ? DEEP_QUESTIONS[profile.personality] ?? [] : [];
  const allQuestions = [...CORE_QUESTIONS, ...deepQuestions];

  function handleSignOut() {
    signOut();
    navigate({ to: "/" });
  }

  return (
    <main className="mx-auto max-w-4xl px-6 pb-24 pt-10">
      {/* Header Badge */}
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4 border-b border-border/50 pb-6">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary">
            <Sparkles className="h-3.5 w-3.5" /> Hồ sơ phân tích bởi Profile Agent
          </span>
          <h1 className="mt-3 font-display text-4xl sm:text-5xl">
            Hồ sơ cá nhân của <span className="text-gradient-romance">{profile.name}</span>
          </h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Câu trả lời của bạn và trạng thái dữ liệu matching từ Profile Tools.
          </p>
        </div>

        <button
          onClick={handleSignOut}
          className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-xs font-semibold transition hover:bg-destructive/10 hover:text-destructive"
        >
          <LogOut className="h-3.5 w-3.5" /> Đăng xuất
        </button>
      </div>

      <div className="grid gap-8 md:grid-cols-[1fr_1.8fr]">
        {/* Left Column: User Card */}
        <div className="space-y-6">
          <div className="relative overflow-hidden rounded-3xl border border-border/60 bg-card/90 p-6 shadow-soft backdrop-blur text-center">
            <div className="pointer-events-none absolute -inset-4 bg-gradient-romance opacity-15 blur-2xl" />
            <div className="relative z-10 flex flex-col items-center">
              <div className="mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-primary/10 text-primary shadow-inner">
                <User className="h-12 w-12" />
              </div>

              <h2 className="font-display text-2xl font-bold">{profile.name}</h2>
              <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                <Mail className="h-3.5 w-3.5" /> {profile.email}
              </div>

              <div className="mt-4 flex flex-wrap justify-center gap-2">
                <span className="rounded-full bg-primary/10 border border-primary/20 px-3 py-1 text-xs font-semibold text-primary">
                  {personalityLabel(profile.personality)}
                </span>
                <span className="rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
                  {genderLabel} · {age} tuổi
                </span>
              </div>

              <div className="mt-6 w-full rounded-2xl border border-border/60 bg-background/60 p-4 text-left text-xs space-y-2">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Trạng thái hồ sơ:</span>
                  {analysis ? (
                    <span className="font-semibold text-emerald-600 flex items-center gap-1">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      {analysis.completeness.profile_complete ? "Đủ điều kiện" : "Cần bổ sung"}
                    </span>
                  ) : (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  )}
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Ngày khởi tạo:</span>
                  <span>{new Date(profile.createdAt).toLocaleDateString("vi-VN")}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="space-y-3">
            <Link
              to="/matches"
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3.5 text-sm font-semibold text-primary-foreground shadow-glow transition hover:opacity-95"
            >
              <Heart className="h-4 w-4 fill-current" />
              Xem các kết nối phù hợp
              <ArrowRight className="h-4 w-4" />
            </Link>

            <Link
              to="/onboarding"
              className="flex w-full items-center justify-center gap-2 rounded-2xl border border-border bg-background px-5 py-3 text-sm font-medium transition hover:bg-accent"
            >
              <RotateCcw className="h-4 w-4 text-muted-foreground" />
              Cập nhật lại câu hỏi tính cách
            </Link>
          </div>
        </div>

        {/* Right Column: Detailed Personality & Answers */}
        <div className="space-y-6">
          {/* Profile tool summary */}
          <div className="rounded-3xl border border-border/60 bg-card/80 p-6 shadow-soft backdrop-blur">
            <div className="mb-4 flex items-center gap-2 font-display text-xl">
              <Database className="h-5 w-5 text-primary" />
              <span>Dữ liệu matching đã kiểm tra</span>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Profile Agent dùng <strong>get_match_profile</strong> và{" "}
              <strong>check_profile_completeness</strong>. Giao diện chỉ hiển thị các trường mà
              tools cho phép, không suy diễn vector hoặc thuộc tính chưa có dữ liệu.
            </p>

            <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 text-center">
              <div className="rounded-2xl border border-border/50 bg-background/50 p-3">
                <div className="text-xs text-muted-foreground">Profile ID</div>
                <div className="mt-1 font-semibold text-primary">
                  {analysis?.profileId ?? "Đang tải"}
                </div>
              </div>
              <div className="rounded-2xl border border-border/50 bg-background/50 p-3">
                <div className="text-xs text-muted-foreground">Độ đầy đủ</div>
                <div className="mt-1 font-semibold text-foreground">
                  {analysis ? `${completeness}%` : "Đang tải"}
                </div>
              </div>
              <div className="rounded-2xl border border-border/50 bg-background/50 p-3">
                <div className="text-xs text-muted-foreground">Mức an toàn</div>
                <div className="mt-1 font-semibold text-emerald-600 flex items-center justify-center gap-1">
                  <ShieldCheck className="h-3.5 w-3.5" /> Được bảo vệ
                </div>
              </div>
            </div>

            {analysisError && (
              <div className="mt-4 flex gap-2 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                {analysisError}
              </div>
            )}

            {analysis && missingOptionalFields.length > 0 && (
              <p className="mt-4 text-xs text-muted-foreground">
                Trường tùy chọn còn thiếu: {missingOptionalFields.join(", ")}.
              </p>
            )}
          </div>

          {/* Answers Summary Card */}
          <div className="rounded-3xl border border-border/60 bg-card/80 p-6 shadow-soft backdrop-blur">
            <h3 className="mb-4 font-display text-xl">Chi tiết khảo sát đã trả lời</h3>
            <div className="space-y-4">
              {allQuestions.map((q, idx) => {
                const answerVal = profile.answers[q.id];
                if (!answerVal) return null;
                // find label if option
                const matchedOption = q.options?.find((o) => o.value === answerVal);
                const displayAnswer = matchedOption ? matchedOption.label : answerVal;

                return (
                  <div
                    key={q.id}
                    className="rounded-2xl border border-border/40 bg-background/60 p-4 transition hover:border-primary/30"
                  >
                    <div className="text-xs font-semibold text-muted-foreground mb-1">
                      Câu {idx + 1}: {q.text}
                    </div>
                    <div className="text-sm font-medium text-foreground">{displayAnswer}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
