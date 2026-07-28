import { useEffect, useState } from "react";

interface HeartParticle {
  id: number;
  size: number; // in pixels
  left: number; // in percentage (0-100)
  duration: number; // in seconds
  delay: number; // in seconds
  opacity: number;
  rotate: number;
}

export function FloatingHeartsBackground() {
  const [hearts, setHearts] = useState<HeartParticle[]>([]);

  useEffect(() => {
    // Generate a list of particles with random properties
    const particles: HeartParticle[] = Array.from({ length: 24 }, (_, i) => ({
      id: i,
      size: Math.floor(Math.random() * 18) + 10, // 10px to 28px
      left: Math.floor(Math.random() * 96) + 2, // 2% to 98%
      duration: Math.floor(Math.random() * 12) + 14, // 14s to 26s
      delay: Math.floor(Math.random() * 12), // 0s to 12s
      opacity: Math.random() * 0.45 + 0.15, // 0.15 to 0.60
      rotate: Math.floor(Math.random() * 60) - 30, // -30deg to 30deg
    }));
    setHearts(particles);
  }, []);

  return (
    <div
      className="pointer-events-none fixed inset-0 overflow-hidden z-0"
      aria-hidden="true"
    >
      {hearts.map((h) => (
        <div
          key={h.id}
          className="absolute bottom-[-40px] animate-float-heart text-primary/30 fill-primary/20 drop-shadow-sm"
          style={{
            left: `${h.left}%`,
            width: `${h.size}px`,
            height: `${h.size}px`,
            animationDuration: `${h.duration}s`,
            animationDelay: `${h.delay}s`,
            opacity: h.opacity,
            transform: `rotate(${h.rotate}deg)`,
          }}
        >
          <svg
            viewBox="0 0 24 24"
            className="w-full h-full text-rose-500/40 fill-rose-500/20"
          >
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        </div>
      ))}
    </div>
  );
}
