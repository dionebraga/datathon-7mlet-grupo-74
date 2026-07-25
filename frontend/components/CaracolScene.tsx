"use client";

import { useMemo, useRef } from "react";
import * as THREE from "three";
import { Canvas, useFrame } from "@react-three/fiber";
import { Bloom, EffectComposer } from "@react-three/postprocessing";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, useGSAP);

/**
 * The "caracol" (snail) — the project's brand visual: a glowing neon tube
 * that loops and coils, matching the baked hero image used on the Streamlit
 * dashboard. Here it's a REAL animated 3D scene instead of a static PNG:
 * the tube glows via emissive + bloom, and a bright pulse of light travels
 * along its length (uTime-driven UV wave) — a visual metaphor for reward
 * flowing through the bandit's arms.
 *
 * Kept deliberately simple per the perf budget (well under 100 draw calls /
 * 1M triangles): one TubeGeometry, one shader material, one Bloom pass.
 */

const TUBE_VERTEX = /* glsl */ `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vViewDir;

  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vViewDir = normalize(cameraPosition - worldPos.xyz);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const TUBE_FRAGMENT = /* glsl */ `
  uniform float uTime;
  uniform vec3 uColorA;   // deep base (VIOLET)
  uniform vec3 uColorB;   // bright rim/pulse (CYAN)
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vViewDir;

  void main() {
    // Fresnel: edges of the tube read brighter than the center -- classic
    // "energy conduit" look (see threejs-r3f/references/shaders.md).
    float fresnel = pow(1.0 - max(dot(vNormal, vViewDir), 0.0), 2.6);

    // A soft pulse of brightness travels along the tube's length (vUv.x runs
    // along the path). Two overlapping waves at different speeds/widths
    // avoid a too-mechanical, single-metronome feel.
    float wave1 = smoothstep(0.85, 1.0, sin((vUv.x * 6.0 - uTime * 0.9) * 3.14159));
    float wave2 = smoothstep(0.9, 1.0, sin((vUv.x * 6.0 - uTime * 1.6 + 2.0) * 3.14159)) * 0.6;
    float pulse = wave1 + wave2;

    vec3 base = mix(uColorA, uColorB, fresnel * 0.6 + 0.12);
    vec3 color = base + uColorB * pulse * 1.4;

    gl_FragColor = vec4(color, 1.0);
  }
`;

/** Control points forming a loose double-coil, echoing the baked hero image. */
function buildCurve(): THREE.CatmullRomCurve3 {
  const pts = [
    [-5.2, 0.6, -1.0],
    [-3.0, 1.4, 0.4],
    [-1.4, -0.6, 0.8],
    [-0.4, 1.2, -0.3],
    [0.6, -1.0, 0.2],
    [1.6, 0.4, 0.6],
    [2.6, 1.6, -0.4],
    [4.2, 0.2, 0.3],
    [5.4, -0.8, -0.6],
  ].map(([x, y, z]) => new THREE.Vector3(x, y, z));
  return new THREE.CatmullRomCurve3(pts, false, "catmullrom", 0.6);
}

function NeonTube({ reducedMotion }: { reducedMotion: boolean }) {
  const matRef = useRef<THREE.ShaderMaterial>(null!);
  const groupRef = useRef<THREE.Group>(null!);

  const curve = useMemo(() => buildCurve(), []);
  const geometry = useMemo(
    () => new THREE.TubeGeometry(curve, 220, 0.16, 20, false),
    [curve]
  );
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uColorA: { value: new THREE.Color("#0033CC") },
      uColorB: { value: new THREE.Color("#1A6FFF") },
    }),
    []
  );

  // Per-frame: mutate refs directly, never setState (threejs-r3f/SKILL.md).
  useFrame((state, delta) => {
    matRef.current.uniforms.uTime.value = state.clock.elapsedTime;
    groupRef.current.rotation.y += delta * 0.045;
    groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.08) * 0.08;
  });

  // Scroll-linked parallax: ties the tube to reading progress down the page.
  // Drives position (x/y) and rotation.z only -- useFrame above already owns
  // rotation.x/y for the idle spin, so the two never fight over a property.
  useGSAP(
    () => {
      if (reducedMotion || !groupRef.current) return;
      const st = {
        trigger: document.documentElement,
        start: "top top",
        end: "bottom bottom",
        scrub: 1.2,
      };
      gsap.to(groupRef.current.position, { x: -0.6, y: 1.1, ease: "none", scrollTrigger: st });
      gsap.to(groupRef.current.rotation, { z: 0.35, ease: "none", scrollTrigger: st });
    },
    { dependencies: [reducedMotion] }
  );

  return (
    <group ref={groupRef}>
      <mesh geometry={geometry}>
        <shaderMaterial
          ref={matRef}
          vertexShader={TUBE_VERTEX}
          fragmentShader={TUBE_FRAGMENT}
          uniforms={uniforms}
        />
      </mesh>
    </group>
  );
}

export default function CaracolScene({ reducedMotion = false }: { reducedMotion?: boolean }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 8.5], fov: 42 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
      frameloop={reducedMotion ? "demand" : "always"}
      style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none" }}
    >
      <NeonTube reducedMotion={reducedMotion} />
      <EffectComposer>
        <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.4} intensity={reducedMotion ? 0.5 : 0.9} mipmapBlur />
      </EffectComposer>
    </Canvas>
  );
}
