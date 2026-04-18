import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * Ken Burns-style camera.
 * 浮世絵MVPの中核。SAM/Depthなしで、単一の原画に対してズーム・パン・微傾斜を与える。
 *
 * Props:
 *  - src: public/ukiyoe/<name>/original.jpg の staticFile() 済みURL
 *  - fromZoom/toZoom: 画面占有率の倍率 (1.0 = 画面幅=画像幅)
 *  - fromXY/toXY: 注視点の正規化座標 (0..1, 左上原点)
 *  - tilt: 終端での微小ロール (deg)
 *  - easing: 既定 cubic-ease-out
 */
export interface KenBurnsProps {
  src: string;
  fromZoom?: number;
  toZoom?: number;
  fromXY?: { x: number; y: number };
  toXY?: { x: number; y: number };
  tilt?: number;
}

const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

export const KenBurns: React.FC<KenBurnsProps> = ({
  src,
  fromZoom = 1.0,
  toZoom = 1.08,
  fromXY = { x: 0.5, y: 0.5 },
  toXY = { x: 0.5, y: 0.5 },
  tilt = 0,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();

  const p = easeOut(Math.min(1, frame / Math.max(1, durationInFrames - 1)));

  const zoom = interpolate(p, [0, 1], [fromZoom, toZoom]);
  const fx = interpolate(p, [0, 1], [fromXY.x, toXY.x]);
  const fy = interpolate(p, [0, 1], [fromXY.y, toXY.y]);
  const rot = interpolate(p, [0, 1], [0, tilt]);

  // transform-origin を注視点に合わせ、scale で拡大。
  // 中心(0.5,0.5)に対するオフセットで疑似パンを行う。
  const originX = fx * 100;
  const originY = fy * 100;
  const offsetX = (0.5 - fx) * width * (zoom - 1);
  const offsetY = (0.5 - fy) * height * (zoom - 1);

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transformOrigin: `${originX}% ${originY}%`,
          transform: `translate(${offsetX}px, ${offsetY}px) scale(${zoom}) rotate(${rot}deg)`,
        }}
      >
        <Img
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
