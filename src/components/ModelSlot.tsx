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
}

export default function ModelSlot({ id, alt, priority = false }: Props) {
  const [mode, setMode] = useState<{ allow3d: boolean; reducedMotion: boolean }>({
    allow3d: false,
    reducedMotion: false,
  });

  useEffect(() => setMode(getDeviceCapability()), []);

  const still = (
    <img
      src={`/renders/${id}.webp`}
      alt={alt}
      width={800}
      height={600}
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
      className="relative flex aspect-[4/3] w-full items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-sakura/50 via-paper/60 to-torii/30 shadow"
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
