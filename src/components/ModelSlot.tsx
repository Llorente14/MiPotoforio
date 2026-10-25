import { Component, lazy, Suspense, useEffect, useState, type ReactNode } from 'react';
import { getDeviceCapability } from '../lib/device-capability';
import type { ModelId } from './ModelScene';

// three.js is only downloaded when 3D is allowed.
const ModelScene = lazy(() => import('./ModelScene'));

// A lost WebGL context leaves a blank canvas that a demand-rendered scene never repaints, so the slot
// remounts the scene with a fresh context. After this many losses it settles on the still.
const MAX_LOSSES = 3;

// A scene that throws (no usable WebGL context yet, for one) shows the still instead of taking the slot
// down, and reports it so the slot can try again.
class SceneBoundary extends Component<
  { fallback: ReactNode; onError: () => void; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    this.props.onError();
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}

interface Props {
  id: ModelId;
  alt: string;
  // Above-the-fold slot: load its still immediately and at high priority.
  priority?: boolean;
  // CSS aspect-ratio of the slot; the figure stands in it with no frame.
  aspect?: string;
}

export default function ModelSlot({ id, alt, priority = false, aspect = '4 / 3' }: Props) {
  const [mode, setMode] = useState<{ allow3d: boolean; reducedMotion: boolean }>({
    allow3d: false,
    reducedMotion: false,
  });

  // Bumping the key remounts the scene; only real context losses count toward giving up.
  const [sceneKey, setSceneKey] = useState(0);
  const [losses, setLosses] = useState(0);
  const remount = () => setSceneKey((n) => n + 1);
  const onContextLost = () => {
    setLosses((n) => n + 1);
    remount();
  };
  // The GPU may still be busy when a fresh context is asked for: wait a moment before the next try.
  const onSceneError = () => window.setTimeout(onContextLost, 1000);

  useEffect(() => setMode(getDeviceCapability()), []);

  // Coming back through the back/forward cache: the page is restored as it was, but its GPU contexts
  // may not have survived. Start the scene over.
  useEffect(() => {
    const onShow = (e: PageTransitionEvent) => {
      if (e.persisted) remount();
    };
    window.addEventListener('pageshow', onShow);
    return () => window.removeEventListener('pageshow', onShow);
  }, []);

  const still = (
    <img
      src={`/renders/${id}.webp`}
      alt={alt}
      width={1000}
      height={1250}
      loading={priority ? 'eager' : 'lazy'}
      fetchPriority={priority ? 'high' : 'auto'}
      onError={(e) => {
        // No render shipped for this id yet: use the generic placeholder.
        const img = e.currentTarget;
        if (!img.src.endsWith('/renders/placeholder.svg')) img.src = '/renders/placeholder.svg';
      }}
      className="size-full object-contain"
    />
  );

  return (
    <div
      data-model-slot={id}
      className="relative flex w-full items-center justify-center"
      style={{ aspectRatio: aspect }}
    >
      {mode.allow3d && losses <= MAX_LOSSES ? (
        <div role="img" aria-label={alt} className="absolute inset-0">
          <SceneBoundary key={sceneKey} fallback={still} onError={onSceneError}>
            <Suspense fallback={still}>
              <ModelScene id={id} reducedMotion={mode.reducedMotion} onContextLost={onContextLost} />
            </Suspense>
          </SceneBoundary>
        </div>
      ) : (
        still
      )}
    </div>
  );
}
