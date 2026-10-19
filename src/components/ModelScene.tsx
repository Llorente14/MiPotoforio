import { Bounds, ContactShadows, useGLTF } from '@react-three/drei';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Component, Suspense, useEffect, useMemo, useRef, type ReactNode } from 'react';
import {
  BackSide,
  Box3,
  DataTexture,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  MeshToonMaterial,
  NearestFilter,
  RedFormat,
  Vector3,
  type Group,
  type Object3D,
} from 'three';
import { cardProgress } from '../lib/card-progress';

useGLTF.setDecoderPath('/draco/');

export type ModelId = 'untar' | 'temple' | 'akai' | 'kaito';

const INK = '#17140f';

// Three hard tones (shadow, mid, lit): the same cel steps as the Blender stills.
const gradientMap = (() => {
  const tex = new DataTexture(new Uint8Array([100, 172, 232]), 3, 1, RedFormat);
  tex.minFilter = tex.magFilter = NearestFilter;
  tex.needsUpdate = true;
  return tex;
})();

// Inverted hull: back faces only, pushed out along the normal in the vertex shader.
function inkMaterial(thickness: number) {
  const m = new MeshBasicMaterial({ color: INK, side: BackSide });
  m.onBeforeCompile = (shader) => {
    shader.vertexShader = shader.vertexShader.replace(
      '#include <begin_vertex>',
      `#include <begin_vertex>\ntransformed += normalize(normal) * ${thickness.toFixed(4)};`,
    );
  };
  return m;
}

// Swap the glTF PBR materials for toon ones and give every mesh an ink outline.
function toonify(root: Object3D) {
  const size = new Box3().setFromObject(root).getSize(new Vector3());
  const ink = inkMaterial(Math.max(size.x, size.y, size.z) * 0.0042);
  const meshes: Mesh[] = [];
  root.traverse((o) => {
    if ((o as Mesh).isMesh) meshes.push(o as Mesh);
  });
  for (const mesh of meshes) {
    const src = mesh.material as MeshStandardMaterial;
    mesh.material = new MeshToonMaterial({
      color: src.color,
      map: src.map,
      gradientMap,
      transparent: src.transparent,
      alphaTest: src.map ? 0.5 : 0,
    });
    if (mesh.name === 'Card') continue;
    const hull = new Mesh(mesh.geometry, ink);
    hull.name = `${mesh.name}Outline`;
    mesh.add(hull);
  }
}

function Model({ id }: { id: ModelId }) {
  const { scene } = useGLTF(`/models/${id}.glb`);
  const model = useMemo(() => {
    const clone = scene.clone(true);
    toonify(clone);
    return clone;
  }, [scene]);

  // Kaito: the card leaves his fingers as the Card Transition starts; the page card takes over from there.
  useFrame(() => {
    if (id !== 'kaito') return;
    const card = model.getObjectByName('Card');
    if (!card) return;
    // Remember where the fingers hold it; the flick is an offset from there.
    card.userData.rest ??= { x: card.position.x, ry: card.rotation.y };
    const p = Math.min(cardProgress.value / 0.06, 1);
    card.visible = p < 1;
    card.rotation.y = card.userData.rest.ry + p * Math.PI * 0.6;
    card.position.x = card.userData.rest.x - p * 0.1;
  });
  return <primitive object={model} />;
}

// A missing GLB makes useGLTF throw; show nothing rather than a broken scene (the still sits behind).
class MissingModelBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

// Scenes render on demand: a frame only when the pointer moves or the page scrolls (the Card Transition),
// never in an idle loop. Keeps the main thread quiet and the battery cool.
function Wake({ enabled }: { enabled: boolean }) {
  const invalidate = useThree((s) => s.invalidate);
  useEffect(() => {
    if (!enabled) return;
    const wake = () => invalidate();
    window.addEventListener('pointermove', wake, { passive: true });
    window.addEventListener('scroll', wake, { passive: true });
    return () => {
      window.removeEventListener('pointermove', wake);
      window.removeEventListener('scroll', wake);
    };
  }, [enabled, invalidate]);
  return null;
}

// The figure leans a little toward the pointer, easing until it settles. No spins: these are figures on a print.
function Lean({ children, reducedMotion, amount }: { children: ReactNode; reducedMotion: boolean; amount: number }) {
  const ref = useRef<Group>(null);
  useFrame((state, delta) => {
    if (reducedMotion || !ref.current) return;
    const target = state.pointer.x * amount;
    const diff = target - ref.current.rotation.y;
    ref.current.rotation.y += diff * Math.min(delta * 4, 1);
    if (Math.abs(diff) > 0.002) state.invalidate();
  });
  return <group ref={ref}>{children}</group>;
}

const framing: Record<ModelId, { camera: [number, number, number]; fov: number; margin: number; sway: number; ground: boolean }> = {
  kaito: { camera: [-0.45, 0.62, 2.6], fov: 30, margin: 1.02, sway: 0.12, ground: false },
  untar: { camera: [-3, 2.4, 6.5], fov: 34, margin: 1.12, sway: 0.35, ground: true },
  temple: { camera: [3.5, 2.2, 5.5], fov: 34, margin: 1.12, sway: 0.35, ground: true },
  akai: { camera: [2.6, 1.4, 3.4], fov: 34, margin: 1.08, sway: 0.2, ground: true },
};

export default function ModelScene({ id, reducedMotion }: { id: ModelId; reducedMotion: boolean }) {
  const f = framing[id];
  return (
    <Canvas
      dpr={[1, 1.5]}
      frameloop="demand"
      camera={{ position: f.camera, fov: f.fov }}
      gl={{ alpha: true, antialias: true }}
      // Wheel and touch scrolling must always reach the page.
      style={{ touchAction: 'pan-y' }}
    >
      <ambientLight intensity={0.75} />
      <directionalLight position={[-3, 5, 4]} intensity={1.6} />
      <Wake enabled={!reducedMotion} />
      <Suspense fallback={null}>
        <Bounds fit clip margin={f.margin} maxDuration={reducedMotion ? 0 : 0.6}>
          <Lean reducedMotion={reducedMotion} amount={f.sway}>
            <MissingModelBoundary>
              <Model id={id} />
            </MissingModelBoundary>
          </Lean>
        </Bounds>
        {f.ground && <ContactShadows position={[0, 0, 0]} opacity={0.35} scale={6} blur={2.4} far={2} color={INK} frames={1} />}
      </Suspense>
    </Canvas>
  );
}
