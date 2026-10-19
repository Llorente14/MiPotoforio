import { useEffect, useRef } from 'react';
import { getDeviceCapability } from '../lib/device-capability';

interface Petal {
  x: number;
  y: number;
  size: number;
  speed: number;
  drift: number;
  phase: number;
  rot: number;
  spin: number;
  // Seconds spent resting on the meadow; null while falling.
  rest: number | null;
}

const REST_SECONDS = 4;
const FADE_SECONDS = 2;
const MAX_DPR = 1.5;

export default function SakuraParticles() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const reducedQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    let petals: Petal[] = [];
    let width = 0;
    let height = 0;
    let raf = 0;
    let last = 0;

    const spawn = (anywhere: boolean): Petal => ({
      x: Math.random() * width,
      y: anywhere ? Math.random() * height : -20,
      size: 5 + Math.random() * 5,
      speed: 25 + Math.random() * 30,
      drift: 15 + Math.random() * 25,
      phase: Math.random() * Math.PI * 2,
      rot: Math.random() * Math.PI * 2,
      spin: (Math.random() - 0.5) * 2,
      rest: null,
    });

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // Fewer petals when 3D is off (phones/tablets) and on small screens.
      const base = getDeviceCapability().allow3d ? 40 : 18;
      const count = Math.round(base * Math.min(1, width / 1200 + 0.4));
      petals = Array.from({ length: count }, () => spawn(true));
    };

    const draw = (p: Petal, alpha: number) => {
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.fillStyle = '#f4b6c2';
      ctx.beginPath();
      ctx.ellipse(0, 0, p.size, p.size * 0.55, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    };

    const frame = (now: number) => {
      const dt = Math.min((now - last) / 1000, 0.05);
      last = now;
      ctx.clearRect(0, 0, width, height);

      // The meadow's top edge, in viewport coordinates. Only a landing surface while on screen.
      const edge = document.getElementById('meadow-top')?.getBoundingClientRect().top;
      const ground = edge !== undefined && edge < height ? edge : Infinity;

      petals.forEach((p, i) => {
        if (p.rest === null) {
          p.y += p.speed * dt;
          p.x += Math.sin(now / 1000 + p.phase) * p.drift * dt;
          p.rot += p.spin * dt;
          if (p.y >= ground) p.rest = 0;
          else if (p.y > height + 20) petals[i] = spawn(false);
          draw(p, 0.85);
        } else {
          p.rest += dt;
          p.y = Math.min(p.y, ground); // follow the edge while scrolling
          const fade = 1 - Math.max(0, p.rest - REST_SECONDS) / FADE_SECONDS;
          if (fade <= 0) petals[i] = spawn(false);
          else draw(p, 0.85 * fade);
        }
      });
      raf = requestAnimationFrame(frame);
    };

    const stop = () => {
      cancelAnimationFrame(raf);
      raf = 0;
    };
    const start = () => {
      if (raf || reducedQuery.matches || document.hidden) return;
      last = performance.now();
      raf = requestAnimationFrame(frame);
    };
    const sync = () => {
      stop();
      if (reducedQuery.matches) ctx.clearRect(0, 0, width, height);
      else start();
    };

    resize();
    sync();
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', sync);
    reducedQuery.addEventListener('change', sync);
    return () => {
      stop();
      window.removeEventListener('resize', resize);
      document.removeEventListener('visibilitychange', sync);
      reducedQuery.removeEventListener('change', sync);
    };
  }, []);

  return (
    <canvas
      ref={ref}
      data-sakura
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 size-full"
      style={{ zIndex: -1 }}
    />
  );
}
