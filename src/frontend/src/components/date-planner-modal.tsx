import { useState, useEffect } from "react";
import {
  Sparkles,
  Calendar,
  Clock,
  MapPin,
  Heart,
  MessageSquare,
  X,
  Send,
  Check,
  Copy,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";

import type { Candidate } from "@/lib/cupid-store";
import { api, type DatePlanResponse } from "@/lib/api-client";

interface DatePlannerModalProps {
  candidate: Candidate;
  isOpen: boolean;
  onClose: () => void;
}

export function DatePlannerModal({ candidate, isOpen, onClose }: DatePlannerModalProps) {
  const [loading, setLoading] = useState(true);
  const [datePlan, setDatePlan] = useState<DatePlanResponse | null>(null);
  const [customPrompt, setCustomPrompt] = useState("");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchPlan();
    }
  }, [isOpen, candidate.id]);

  async function fetchPlan(prompt?: string) {
    setLoading(true);
    setError("");
    try {
      const plan = await api.generateDatePlan(candidate.id, prompt);
      setDatePlan(plan);
    } catch (err) {
      setDatePlan(null);
      setError(err instanceof Error ? err.message : "Không tạo được kế hoạch.");
    } finally {
      setLoading(false);
    }
  }

  function handleReplan(e: React.FormEvent) {
    e.preventDefault();
    if (!customPrompt.trim()) return;
    fetchPlan(customPrompt.trim());
    setCustomPrompt("");
  }

  function handleCopy() {
    if (!datePlan) return;
    const text = `🗓️ ${datePlan.theme}\n\n` +
      datePlan.items.map((it) => `📍 [${it.time}] ${it.title}\n   - Địa điểm: ${it.location}\n   - Mô tả: ${it.description}`).join("\n\n") +
      `\n\n💡 Câu hỏi phá băng gợi ý:\n` + datePlan.icebreakerQuestions.map((q, i) => `${i + 1}. ${q}`).join("\n");
    
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-border/80 bg-card p-6 sm:p-8 shadow-2xl backdrop-blur">
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Đóng"
          className="absolute right-5 top-5 rounded-full p-2 text-muted-foreground transition hover:bg-accent hover:text-foreground"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-6">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            <Sparkles className="h-3.5 w-3.5" /> Date Planning Agent AI
          </span>
          <h2 className="mt-2 font-display text-3xl font-bold">
            Kế hoạch hẹn hò cùng <span className="text-gradient-romance">{candidate.name}</span>
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Lịch trình dùng sở thích chung đã consent, thành phố và ngân sách từ Profile Tools.
          </p>
        </div>

        {/* Content Body */}
        {loading ? (
          <div className="my-12 flex flex-col items-center justify-center text-center space-y-4">
            <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Loader2 className="h-8 w-8 animate-spin" />
              <Heart className="absolute h-4 w-4 fill-primary text-primary animate-ping" />
            </div>
            <div>
              <div className="font-semibold text-base">Date Planning Agent đang suy nghĩ...</div>
              <p className="text-xs text-muted-foreground mt-1">
                Phân tích điểm tương đồng về địa điểm tại {candidate.city} & chủ đề trò chuyện
              </p>
            </div>
          </div>
        ) : error ? (
          <div className="my-10 text-center">
            <AlertCircle className="mx-auto h-9 w-9 text-destructive" />
            <h3 className="mt-3 font-semibold">Không tạo được kế hoạch</h3>
            <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">{error}</p>
            <button
              onClick={() => fetchPlan()}
              className="mt-5 inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              <RefreshCw className="h-4 w-4" /> Thử lại
            </button>
          </div>
        ) : datePlan ? (
          <div className="space-y-6">
            {datePlan.appliedChanges?.length ? (
              <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4">
                <div className="text-xs font-semibold uppercase tracking-wider text-primary flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5" /> Dieu chinh cua agent
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {datePlan.appliedChanges.map((change) => (
                    <span
                      key={change}
                      className="rounded-full border border-primary/20 bg-background px-2.5 py-1 text-[11px] font-medium text-foreground/80"
                    >
                      {change}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            {/* Itinerary Timeline */}
            <div className="space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-primary" /> Lịch trình hẹn hò chi tiết
              </div>

              <div className="relative space-y-4 pl-4 border-l-2 border-primary/20">
                {datePlan.items.map((item) => (
                  <div key={item.step} className="relative group">
                    {/* Timeline Dot */}
                    <div className="absolute -left-[23px] top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-primary-foreground text-[10px] font-bold shadow-glow">
                      {item.step}
                    </div>

                    <div className="rounded-2xl border border-border/60 bg-background/70 p-4 transition hover:border-primary/40">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                        <span className="text-xs font-bold text-primary flex items-center gap-1">
                          <Clock className="h-3 w-3" /> {item.time}
                        </span>
                        <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-medium text-accent-foreground">
                          {item.tag}
                        </span>
                      </div>
                      <h4 className="font-semibold text-base">{item.title}</h4>
                      <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                        <MapPin className="h-3.5 w-3.5 shrink-0 text-rose-500" />
                        <span>{item.location}</span>
                        {item.durationMinutes ? <span>- {item.durationMinutes} phut</span> : null}
                      </div>
                      <p className="mt-2 text-xs leading-relaxed text-foreground/80">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Icebreaker Questions Section */}
            <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4 space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-primary flex items-center gap-1.5">
                <MessageSquare className="h-3.5 w-3.5" /> Gợi ý 3 câu hỏi phá băng (Icebreaker Topics)
              </div>
              <ul className="space-y-1.5 text-xs text-foreground/90">
                {datePlan.icebreakerQuestions.map((q, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="font-bold text-primary">{idx + 1}.</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Re-prompt Form */}
            <form onSubmit={handleReplan} className="flex gap-2">
              <input
                type="text"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Yêu cầu thay đổi (VD: Hẹn buổi tối, đổi sang không gian ngoài trời)..."
                className="flex-1 rounded-xl border border-input bg-background px-4 py-2.5 text-xs outline-none focus:border-primary focus:ring-1 focus:ring-primary/20"
              />
              <button
                type="submit"
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground shadow-glow transition hover:opacity-95"
              >
                <Send className="h-3.5 w-3.5" /> Điều chỉnh
              </button>
            </form>

            {/* Modal Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border/50 pt-4">
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-4 py-2 text-xs font-semibold transition hover:bg-accent"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                {copied ? "Đã sao chép lịch trình" : "Sao chép kế hoạch"}
              </button>

              <button
                onClick={onClose}
                className="rounded-full bg-primary px-6 py-2 text-xs font-semibold text-primary-foreground shadow-glow transition hover:opacity-95"
              >
                Đóng
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
