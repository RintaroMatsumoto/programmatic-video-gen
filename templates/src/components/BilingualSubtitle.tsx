import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * 日英バイリンガル字幕。
 * 上段: 日本語（大きめ、明朝系）
 * 下段: 英語（細め、セリフ系）
 *
 * フェードイン 8f、フェードアウト 10f。ほのかな下からのスライド付き。
 */
export interface BilingualSubtitleProps {
  ja: string;
  en?: string;
  accent?: string; // 差し色（デフォルト藍色）
}

export const BilingualSubtitle: React.FC<BilingualSubtitleProps> = ({
  ja,
  en,
  accent = "#a8c8e8",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const inP = spring({
    frame,
    fps,
    config: { damping: 200, stiffness: 140, mass: 0.5 },
  });
  const out = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = Math.min(inP, out);
  const translateY = interpolate(inP, [0, 1], [18, 0]);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 80,
        textAlign: "center",
        opacity,
        transform: `translateY(${translateY}px)`,
        pointerEvents: "none",
      }}
    >
      {ja && (
        <div
          style={{
            display: "inline-block",
            padding: "14px 36px",
            fontFamily:
              "'Noto Serif JP', 'Hiragino Mincho ProN', 'Yu Mincho', serif",
            fontSize: 52,
            fontWeight: 500,
            color: "#fafafa",
            background: "rgba(10, 14, 24, 0.72)",
            borderBottom: `3px solid ${accent}`,
            borderRadius: 6,
            letterSpacing: "0.04em",
            lineHeight: 1.35,
            textShadow: "0 2px 8px rgba(0,0,0,0.6)",
            maxWidth: "78%",
          }}
        >
          {ja}
        </div>
      )}
      {en && (
        <div
          style={{
            marginTop: 10,
            display: "inline-block",
            padding: "8px 24px",
            fontFamily:
              "'EB Garamond', 'Times New Roman', Georgia, serif",
            fontSize: 30,
            fontStyle: "italic",
            color: "#e6ecf3",
            background: "rgba(10, 14, 24, 0.55)",
            borderRadius: 4,
            letterSpacing: "0.02em",
            maxWidth: "74%",
          }}
        >
          {en}
        </div>
      )}
    </div>
  );
};
