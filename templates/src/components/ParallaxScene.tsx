import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * レイヤー分解済みの浮世絵に対する 2.5D パララックス表現。
 * Phase 2 用。MVP では未使用で、SAM2 + Depth の出力が揃ってから有効化する。
 *
 * 各レイヤーは public/ukiyoe/<name>/layers/*.png（RGBA、背景透明）。
 * z は 0..1 で、0 が最奥、1 が手前。
 */
export interface Layer {
  src: string;
  z: number;
  offsetX?: number; // 初期ずれ (px)
  offsetY?: number;
  scale?: number;
}

export interface ParallaxSceneProps {
  layers: Layer[];
  fromZoom?: number;
  toZoom?: number;
  fromXY?: { x: number; y: number };
  toXY?: { x: number; y: number };
  /** パララックス強度。奥ほど動かない (1 - z) で乗じる。 */
  parallaxStrength?: number;
}

const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

export const ParallaxScene: React.FC<ParallaxSceneProps> = ({
  layers,
  fromZoom = 1.0,
  toZoom = 1.08,
  fromXY = { x: 0.5, y: 0.5 },
  toXY = { x: 0.5, y: 0.5 },
  parallaxStrength = 40,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const p = easeOut(Math.min(1, frame / Math.max(1, durationInFrames - 1)));

  const zoom = interpolate(p, [0, 1], [fromZoom, toZoom]);
  const fx = interpolate(p, [0, 1], [fromXY.x, toXY.x]);
  const fy = interpolate(p, [0, 1], [fromXY.y, toXY.y]);

  const sorted = [...layers].sort((a, b) => a.z - b.z);

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", overflow: "hidden" }}>
      {sorted.map((layer, idx) => {
        const parallax = 1 - layer.z; // 奥ほど小さく、手前ほど大きく動く
        const lx = (0.5 - fx) * width * (zoom - 1) * (1 + parallax);
        const ly = (0.5 - fy) * height * (zoom - 1) * (1 + parallax);
        const pxOffset = (parallax - 0.5) * parallaxStrength * (p - 0.5) * 2;
        return (
          <div
            key={idx}
            style={{
              position: "absolute",
              inset: 0,
              transformOrigin: `${fx * 100}% ${fy * 100}%`,
              transform: `translate(${lx + (layer.offsetX ?? 0) + pxOffset}px, ${
                ly + (layer.offsetY ?? 0)
              }px) scale(${zoom * (layer.scale ?? 1)})`,
            }}
          >
            <Img
              src={layer.src}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
