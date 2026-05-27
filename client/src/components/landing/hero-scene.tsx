'use client';

import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

/* ── Particle field — responds to mouse ── */
function ParticleField({ mouse }: { mouse: React.MutableRefObject<[number, number]> }) {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const pos = new Float32Array(4000 * 3);
    for (let i = 0; i < 4000; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 24;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 24;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.getElapsedTime();
    const [mx, my] = mouse.current;
    ref.current.rotation.x = t * 0.018 + my * 0.08;
    ref.current.rotation.y = t * 0.025 + mx * 0.08;
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#00D4FF"
        size={0.025}
        sizeAttenuation
        depthWrite={false}
        opacity={0.45}
      />
    </Points>
  );
}

/* ── Secondary violet particle layer ── */
function ParticleField2({ mouse }: { mouse: React.MutableRefObject<[number, number]> }) {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const pos = new Float32Array(2000 * 3);
    for (let i = 0; i < 2000; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 30;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 30;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 22;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.getElapsedTime();
    const [mx, my] = mouse.current;
    ref.current.rotation.x = -t * 0.012 - my * 0.04;
    ref.current.rotation.y = -t * 0.02 - mx * 0.04;
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#A78BFA"
        size={0.02}
        sizeAttenuation
        depthWrite={false}
        opacity={0.25}
      />
    </Points>
  );
}

/* ── Orbiting data rings ── */
function DataRings({ mouse }: { mouse: React.MutableRefObject<[number, number]> }) {
  const r1 = useRef<THREE.Mesh>(null);
  const r2 = useRef<THREE.Mesh>(null);
  const r3 = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    const [mx, my] = mouse.current;
    if (r1.current) {
      r1.current.rotation.x = t * 0.12 + my * 0.15;
      r1.current.rotation.z = t * 0.08;
    }
    if (r2.current) {
      r2.current.rotation.y = t * 0.1 + mx * 0.15;
      r2.current.rotation.x = t * 0.06;
    }
    if (r3.current) {
      r3.current.rotation.z = -t * 0.09 - mx * 0.1;
      r3.current.rotation.y = t * 0.05;
    }
  });

  return (
    <>
      <mesh ref={r1}>
        <torusGeometry args={[4.5, 0.018, 16, 120]} />
        <meshBasicMaterial color="#00D4FF" transparent opacity={0.18} />
      </mesh>
      <mesh ref={r2}>
        <torusGeometry args={[5.8, 0.012, 16, 140]} />
        <meshBasicMaterial color="#A78BFA" transparent opacity={0.12} />
      </mesh>
      <mesh ref={r3}>
        <torusGeometry args={[3.2, 0.015, 16, 100]} />
        <meshBasicMaterial color="#00D4FF" transparent opacity={0.10} />
      </mesh>
    </>
  );
}

/* ── Pulsing core sphere ── */
function CoreSphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.getElapsedTime();
    meshRef.current.scale.setScalar(1 + Math.sin(t * 0.7) * 0.06);
    (meshRef.current.material as THREE.MeshBasicMaterial).opacity = 0.04 + Math.sin(t * 0.5) * 0.02;
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1.2, 32, 32]} />
      <meshBasicMaterial color="#00D4FF" transparent opacity={0.05} />
    </mesh>
  );
}

/* ── Inner canvas scene ── */
function Scene({ mouse }: { mouse: React.MutableRefObject<[number, number]> }) {
  const { camera } = useThree();

  useFrame(() => {
    const [mx, my] = mouse.current;
    camera.position.x += (mx * 0.3 - camera.position.x) * 0.04;
    camera.position.y += (-my * 0.2 - camera.position.y) * 0.04;
    camera.lookAt(0, 0, 0);
  });

  return (
    <>
      <ambientLight intensity={0.2} />
      <ParticleField mouse={mouse} />
      <ParticleField2 mouse={mouse} />
      <DataRings mouse={mouse} />
      <CoreSphere />
    </>
  );
}

export function HeroScene() {
  const mouse = useRef<[number, number]>([0, 0]);

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      mouse.current = [
        (e.clientX / window.innerWidth - 0.5) * 2,
        (e.clientY / window.innerHeight - 0.5) * 2,
      ];
    };
    window.addEventListener('mousemove', handleMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  return (
    <div className="absolute inset-0 z-0" aria-hidden="true">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 52 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        style={{ background: 'transparent' }}
        dpr={[1, 2]}
      >
        <Scene mouse={mouse} />
      </Canvas>
    </div>
  );
}
