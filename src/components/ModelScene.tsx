import { Bounds, useGLTF } from '@react-three/drei';
import { Canvas, useFrame } from '@react-three/fiber';
import { Component, Suspense, useRef, type ReactNode } from 'react';
import type { Group } from 'three';
import { cardProgress } from '../lib/card-progress';

useGLTF.setDecoderPath('/draco/');

export type ModelId = 'untar' | 'temple' | 'akai' | 'kaito';

const SAKURA = '#f4b6c2';
const TORII = '#c8362b';
const WOOD = '#8d6e63';
const STONE = '#b0a99f';

function Mesh({ position, children }: { position: [number, number, number]; children: ReactNode }) {
  return <mesh position={position}>{children}</mesh>;
}

// Primitive stand-ins, used only when /models/<id>.glb is missing.
function Placeholder({ id }: { id: ModelId }) {
  if (id === 'temple') {
    return (
      <group>
        {[0, 1, 2].map((i) => (
          <group key={i}>
            <Mesh position={[0, i * 1.1, 0]}>
              <cylinderGeometry args={[0.9 - i * 0.2, 0.9 - i * 0.2, 0.7, 6]} />
              <meshStandardMaterial color={WOOD} flatShading />
            </Mesh>
            <Mesh position={[0, i * 1.1 + 0.55, 0]}>
              <coneGeometry args={[1.5 - i * 0.3, 0.5, 6]} />
              <meshStandardMaterial color={TORII} flatShading />
            </Mesh>
          </group>
        ))}
      </group>
    );
  }
  if (id === 'kaito') {
    return (
      <group>
        <Mesh position={[0, 0.7, 0]}>
          <capsuleGeometry args={[0.4, 0.9, 4, 6]} />
          <meshStandardMaterial color="#f5f5f5" flatShading />
        </Mesh>
        <Mesh position={[0, 0.6, -0.3]}>
          <coneGeometry args={[0.9, 1.6, 5]} />
          <meshStandardMaterial color="#e8e8f0" flatShading />
        </Mesh>
        <Mesh position={[0, 1.75, 0]}>
          <sphereGeometry args={[0.3, 6, 4]} />
          <meshStandardMaterial color={SAKURA} flatShading />
        </Mesh>
        <Mesh position={[0, 2.15, 0]}>
          <cylinderGeometry args={[0.22, 0.26, 0.45, 6]} />
          <meshStandardMaterial color="#f5f5f5" flatShading />
        </Mesh>
        <Mesh position={[0.6, 1.2, 0.3]}>
          <boxGeometry args={[0.35, 0.5, 0.03]} />
          <meshStandardMaterial color="#ffffff" flatShading />
        </Mesh>
      </group>
    );
  }
  if (id === 'akai') {
    return (
      <group>
        <Mesh position={[0, 0.6, 0]}>
          <capsuleGeometry args={[0.35, 0.8, 4, 6]} />
          <meshStandardMaterial color="#263238" flatShading />
        </Mesh>
        <Mesh position={[0, 1.6, 0]}>
          <sphereGeometry args={[0.3, 6, 4]} />
          <meshStandardMaterial color={SAKURA} flatShading />
        </Mesh>
      </group>
    );
  }
  return (
    <group>
      {[0, 1, 2].map((i) => (
        <Mesh key={i} position={[0, i * 0.8, 0]}>
          <boxGeometry args={[2.4 - i * 0.4, 0.8, 1.2]} />
          <meshStandardMaterial color={i === 2 ? TORII : STONE} flatShading />
        </Mesh>
      ))}
    </group>
  );
}

function Model({ id }: { id: ModelId }) {
  const { scene } = useGLTF(`/models/${id}.glb`);
  // The Hero card flies as a page overlay once the transition starts; hide the in-scene copy then.
  useFrame(() => {
    if (id !== 'kaito') return;
    const card = scene.getObjectByName('Card');
    if (card) card.visible = cardProgress.value < 0.02;
  });
  return <primitive object={scene} />;
}

// A missing GLB makes useGLTF throw; swap in the primitive placeholder instead.
class MissingModelBoundary extends Component<{ id: ModelId; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? <Placeholder id={this.props.id} /> : this.props.children;
  }
}

function Spinner({ id, children, reducedMotion }: { id: ModelId; children: ReactNode; reducedMotion: boolean }) {
  const ref = useRef<Group>(null);
  const t = useRef(0);
  useFrame((_, delta) => {
    if (reducedMotion || !ref.current) return;
    if (id === 'kaito') {
      // Kaito faces the camera: sway instead of a full turn.
      t.current += delta;
      ref.current.rotation.y = Math.sin(t.current * 0.6) * 0.35;
    } else {
      ref.current.rotation.y += delta * 0.4;
    }
  });
  return <group ref={ref}>{children}</group>;
}

export default function ModelScene({ id, reducedMotion }: { id: ModelId; reducedMotion: boolean }) {
  return (
    <Canvas
      dpr={[1, 1.5]}
      frameloop={reducedMotion ? 'demand' : 'always'}
      camera={{ position: [4, 3, 6], fov: 40 }}
      // Wheel and touch scrolling must always reach the page.
      style={{ touchAction: 'pan-y' }}
    >
      <ambientLight intensity={0.8} />
      <directionalLight position={[5, 8, 5]} intensity={1.6} />
      <Suspense fallback={null}>
        <Bounds fit observe margin={1.25}>
          <Spinner id={id} reducedMotion={reducedMotion}>
            <MissingModelBoundary id={id}>
              <Model id={id} />
            </MissingModelBoundary>
          </Spinner>
        </Bounds>
      </Suspense>
    </Canvas>
  );
}
