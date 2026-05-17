'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function ParticleField() {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const pos = new Float32Array(3000 * 3);
    for (let i = 0; i < 3000; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = state.clock.getElapsedTime() * 0.02;
    ref.current.rotation.y = state.clock.getElapsedTime() * 0.03;
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#00D4FF"
        size={0.03}
        sizeAttenuation
        depthWrite={false}
        opacity={0.6}
      />
    </Points>
  );
}

function DataRings() {
  const ringRef = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (ringRef.current) {
      ringRef.current.rotation.x = t * 0.15;
      ringRef.current.rotation.z = t * 0.1;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.y = t * 0.12;
      ring2Ref.current.rotation.x = t * 0.08;
    }
  });

  return (
    <>
      <mesh ref={ringRef} position={[0, 0, 0]}>
        <torusGeometry args={[3.5, 0.02, 16, 100]} />
        <meshBasicMaterial color="#00D4FF" transparent opacity={0.2} />
      </mesh>
      <mesh ref={ring2Ref} position={[0, 0, 0]}>
        <torusGeometry args={[4.2, 0.015, 16, 100]} />
        <meshBasicMaterial color="#A78BFA" transparent opacity={0.15} />
      </mesh>
    </>
  );
}

function GlowSphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.getElapsedTime();
    meshRef.current.scale.setScalar(1 + Math.sin(t * 0.5) * 0.05);
  });

  return (
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <sphereGeometry args={[0.8, 32, 32]} />
      <meshBasicMaterial color="#00D4FF" transparent opacity={0.06} />
    </mesh>
  );
}

export function HeroScene() {
  return (
    <div className="absolute inset-0 z-0">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 55 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.3} />
        <ParticleField />
        <DataRings />
        <GlowSphere />
      </Canvas>
    </div>
  );
}
