"use client";

import * as RSlider from "@radix-ui/react-slider";

export function Slider({
  label,
  value,
  min,
  max,
  step = 1,
  suffix = "",
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="font-medium text-muted">{label}</span>
        <span className="font-bold text-primary-soft">
          {value}
          {suffix}
        </span>
      </div>
      <RSlider.Root
        className="relative flex h-11 w-full touch-none items-center"
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={([v]) => onChange(v)}
      >
        <RSlider.Track className="relative h-1.5 grow rounded-full bg-border">
          <RSlider.Range className="absolute h-full rounded-full bg-primary" />
        </RSlider.Track>
        {/* Visible thumb stays 16px (proportional to the track); an invisible
            44x44 hit area (WCAG 2.5.5 / Apple HIG minimum) sits behind it via
            `before:` so dragging works comfortably on a phone. */}
        <RSlider.Thumb
          aria-label={label}
          className="relative block h-4 w-4 rounded-full border-2 border-primary bg-white shadow-md outline-none transition before:absolute before:left-1/2 before:top-1/2 before:h-11 before:w-11 before:-translate-x-1/2 before:-translate-y-1/2 before:content-[''] hover:scale-110 focus:ring-2 focus:ring-primary/40"
        />
      </RSlider.Root>
    </div>
  );
}
