// Resolves on the visitor's first input (pointer, wheel, key, touch or scroll), or after `fallbackMs`.
// Heavy enhancements (the 3D scenes) wait for it so the first seconds of the page stay responsive;
// the still renders cover the gap.
const EVENTS = ['pointermove', 'pointerdown', 'wheel', 'keydown', 'touchstart', 'scroll'] as const;

let pending: Promise<void> | undefined;

export function firstInput(fallbackMs = 8000): Promise<void> {
  pending ??= new Promise((resolve) => {
    const done = () => {
      EVENTS.forEach((e) => window.removeEventListener(e, done));
      window.clearTimeout(timer);
      resolve();
    };
    EVENTS.forEach((e) => window.addEventListener(e, done, { passive: true }));
    const timer = window.setTimeout(done, fallbackMs);
  });
  return pending;
}
