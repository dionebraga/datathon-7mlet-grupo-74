"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

// WebGL can't run during SSR -- load the Canvas client-side only. This also
// keeps three.js/R3F out of the initial server-rendered bundle entirely.
const CaracolScene = dynamic(() => import("./CaracolScene"), { ssr: false });

gsap.registerPlugin(useGSAP);

/**
 * Mounts the animated 3D caracol as a fixed full-viewport backdrop and fades
 * it in once ready. The static hero-bg.png (already in globals.css) stays as
 * the paint-immediately fallback underneath, so there's never a blank flash
 * while the WebGL scene boots.
 */
export default function Hero3D() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mq.matches);
    setMounted(true);
    const onChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  useGSAP(
    () => {
      if (!mounted) return;
      gsap.fromTo(
        wrapRef.current,
        { autoAlpha: 0 },
        { autoAlpha: 1, duration: reducedMotion ? 0.6 : 1.8, ease: "power2.out" }
      );
    },
    { dependencies: [mounted], scope: wrapRef }
  );

  if (!mounted) return null;

  return (
    <div ref={wrapRef} aria-hidden="true">
      <CaracolScene reducedMotion={reducedMotion} />
    </div>
  );
}
