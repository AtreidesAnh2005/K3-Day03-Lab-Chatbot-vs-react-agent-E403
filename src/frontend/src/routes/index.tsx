import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Heart, Sparkles, ArrowRight, Shield, Brain } from "lucide-react";

import hero from "@/assets/hero.jpg";
import { signIn, getAuth, getProfile } from "@/lib/cupid-store";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Cupid Agent — Trợ lý ghép đôi & phân tích tương thích bằng AI" },
      {
        name: "description",
        content:
          "Đăng nhập Cupid Agent để trả lời bộ câu hỏi tính cách và tìm những kết nối tương thích nhất với bạn.",
      },
      { property: "og:title", content: "Cupid Agent — Trợ lý ghép đôi AI" },
      {
        property: "og:description",
        content: "Phân tích tính cách, embed hồ sơ, tìm nửa kia phù hợp.",
      },
    ],
  }),
  component: Landing,
});

function Landing() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(true);
    const auth = getAuth();
    if (auth) {
      const p = getProfile();
      navigate({ to: p ? "/profile" : "/onboarding" });
    }
  }, [navigate]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !name.trim()) return;
    signIn(email.trim(), name.trim());
    navigate({ to: "/onboarding" });
  }

  if (!ready) return null;

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24 pt-10">
      <section className="grid gap-12 lg:grid-cols-[1.1fr_1fr] lg:items-center">
        <div className="space-y-6">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary">
            <Sparkles className="h-3.5 w-3.5" /> Trợ lý ghép đôi bằng AI
          </span>
          <h1 className="font-display text-5xl leading-[1.05] sm:text-6xl">
            Tìm người phù hợp <br />
            bằng <span className="text-gradient-romance">phân tích tính cách</span> thay vì chỉ hình
            ảnh.
          </h1>
          <p className="max-w-xl text-base text-muted-foreground sm:text-lg">
            Cupid Agent hỏi bạn vài câu hỏi tinh tế, embed hồ sơ thành vector, rồi ghép bạn với
            những người có độ tương thích cao nhất trong kho dữ liệu của chúng tôi.
          </p>

          <div className="grid gap-3 sm:grid-cols-3">
            <Feature icon={<Brain className="h-4 w-4" />} title="Hồ sơ sâu">
              Câu hỏi mở rộng theo tính cách bạn chọn.
            </Feature>
            <Feature icon={<Sparkles className="h-4 w-4" />} title="Vector matching">
              Embed và xếp hạng theo độ tương thích.
            </Feature>
            <Feature icon={<Shield className="h-4 w-4" />} title="Riêng tư">
              Dữ liệu được bảo vệ bởi Safety Critic Agent.
            </Feature>
          </div>
        </div>

        <div className="relative">
          <div className="pointer-events-none absolute -inset-6 rounded-[2rem] bg-gradient-romance opacity-30 blur-3xl" />
          <form
            onSubmit={handleSubmit}
            className="relative overflow-hidden rounded-3xl border border-border/60 bg-card/90 shadow-soft backdrop-blur"
          >
            <img
              src={hero}
              alt="Hai bóng người kết nối bằng sợi chỉ vàng và những trái tim"
              width={1024}
              height={1024}
              className="aspect-[5/4] w-full object-cover"
            />
            <div className="space-y-4 p-6">
              <div>
                <h2 className="font-display text-2xl">Bắt đầu hành trình</h2>
                <p className="text-sm text-muted-foreground">
                  Đăng nhập nhanh để lưu hồ sơ và xem những kết nối phù hợp.
                </p>
              </div>
              <div className="space-y-3">
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Tên của bạn"
                  className="w-full rounded-xl border border-input bg-background px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  required
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full rounded-xl border border-input bg-background px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  required
                />
              </div>
              <button
                type="submit"
                className="group flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-glow transition hover:opacity-95"
              >
                <Heart className="h-4 w-4 fill-current" />
                Đăng nhập & bắt đầu
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </button>
              <p className="text-center text-xs text-muted-foreground">
                Không cần mật khẩu — bản demo, dữ liệu lưu trên trình duyệt.
              </p>
            </div>
          </form>
        </div>
      </section>
    </main>
  );
}

function Feature({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card/60 p-4 backdrop-blur">
      <div className="mb-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-primary">
        {icon}
      </div>
      <div className="text-sm font-semibold">{title}</div>
      <div className="text-xs text-muted-foreground">{children}</div>
    </div>
  );
}
