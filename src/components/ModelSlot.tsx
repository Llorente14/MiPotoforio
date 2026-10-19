import { lazy, Suspense, useEffect, useState } from 'react';
import { getDeviceCapability } from '../lib/device-capability';
import type { ModelId } from './ModelScene';

// three.js is only downloaded when 3D is allowed.
const ModelScene = lazy(() => import('./ModelScene'));

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

  useEffect(() => setMode(getDeviceCapability()), []);

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
      {mode.allow3d ? (
        <div role="img" aria-label={alt} className="absolute inset-0">
          <Suspense fallback={still}>
            <ModelScene id={id} reducedMotion={mode.reducedMotion} />
          </Suspense>
        </div>
      ) : (
        still
      )}
    </div>
  );
}
