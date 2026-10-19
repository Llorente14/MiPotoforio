// Single source of truth for "may this visitor get 3D?". Client-side only.

export interface DeviceCapability {
  allow3d: boolean;
  reducedMotion: boolean;
}

const NARROW = '(max-width: 767px)';
const COARSE = '(pointer: coarse)';
const REDUCED = '(prefers-reduced-motion: reduce)';

function hasWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return Boolean(canvas.getContext('webgl2') ?? canvas.getContext('webgl'));
  } catch {
    return false;
  }
}

export function getDeviceCapability(): DeviceCapability {
  const reducedMotion = window.matchMedia(REDUCED).matches;
  const phoneOrTablet = window.matchMedia(NARROW).matches || window.matchMedia(COARSE).matches;
  // Never probe WebGL on phones/tablets: not even creating a context.
  return { allow3d: !phoneOrTablet && hasWebGL(), reducedMotion };
}
