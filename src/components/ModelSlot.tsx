import { Component, lazy, Suspense, useCallback, useEffect, useState, type ReactNode } from 'react';
import { getDeviceCapability } from '../lib/device-capability';
import { firstInput } from '../lib/first-input';
import type { ModelId } from './ModelScene';

// three.js is only downloaded when 3D is allowed.
const ModelScene = lazy(() => import('./ModelScene'));

// A lost WebGL context leaves a blank canvas that a demand-rendered scene never repaints, so the slot
// remounts the scene with a fresh context. After this many losses it settles on the still.
const MAX_LOSSES = 3;

// Width of each full-size still; scripts/responsive-images.mjs writes 480 and 720 wide copies beside it.
const STILL_WIDTH: Record<ModelId, number> = { kaito: 1000, untar: 900, temple: 900 };

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
  // The still stays on screen until the scene has drawn its model: fetching three.js, the GLB and the Draco
  // decode take a second or two, and a bare transparent canvas in that gap reads as the model vanishing.
  const [ready, setReady] = useState(false);
  const onReady = useCallback(() => setReady(true), []);
  const remount = () => {
    setReady(false);
    setSceneKey((n) => n + 1);
  };
  const onContextLost = () => {
    setLosses((n) => n + 1);
    remount();
  };
  // The GPU may still be busy when a fresh context is asked for: wait a moment before the next try.
  const onSceneError = () => {
    setReady(false);
    window.setTimeout(onContextLost, 1000);
  };

  // three.js, the GLB decode and shader compiles are the heaviest work on the page: start them on the
  // visitor's first input rather than during load. The still shows meanwhile.
  useEffect(() => {
    const capability = getDeviceCapability();
    if (!capability.allow3d) return setMode(capability);
    let live = true;
    void firstInput().then(() => live && setMode(capability));
    return () => {
      live = false;
    };
  }, []);

  // Coming back through the back/forward cache: the page is restored as it was, but its GPU contexts
  // may not have survived. Start the scene over.
  useEffect(() => {
    const onShow = (e: PageTransitionEvent) => {
      if (e.persisted) remount();
    };
    window.addEventListener('pageshow', onShow);
    return () => window.removeEventListener('pageshow', onShow);
  }, []);

  const still = (decorative: boolean) => (
    <img
      src={`/renders/${id}.webp`}
      srcSet={`/renders/${id}-480.webp 480w, /renders/${id}-720.webp 720w, /renders/${id}.webp ${STILL_WIDTH[id]}w`}
      sizes="(min-width: 768px) 40vw, 90vw"
      alt={decorative ? '' : alt}
      aria-hidden={decorative || undefined}
      width={1000}
      height={1250}
      loading={priority ? 'eager' : 'lazy'}
      fetchPriority={priority ? 'high' : 'auto'}
      onError={(e) => {
        // No render shipped for this id yet: use the generic placeholder.
        const img = e.currentTarget;
        if (!img.src.endsWith('/renders/placeholder.svg')) {
          img.removeAttribute('srcset');
          img.src = '/renders/placeholder.svg';
        }
      }}
      className="absolute inset-0 size-full object-contain transition-opacity duration-500"
      style={{ opacity: decorative && ready ? 0 : 1 }}
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
          {still(true)}
          <div className="absolute inset-0 transition-opacity duration-500" style={{ opacity: ready ? 1 : 0 }}>
            <SceneBoundary key={sceneKey} fallback={null} onError={onSceneError}>
              <Suspense fallback={null}>
                <ModelScene id={id} reducedMotion={mode.reducedMotion} onContextLost={onContextLost} onReady={onReady} />
              </Suspense>
            </SceneBoundary>
          </div>
        </div>
      ) : (
        still(false)
      )}
    </div>
  );
}
