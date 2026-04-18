import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import { KenBurns } from "../components/KenBurns";
import { BilingualSubtitle } from "../components/BilingualSubtitle";

/**
 * 浮世絵解説動画のRemotionコンポジション (MVP)。
 *
 * データは src/data/ukiyoe_scenes/<name>.json。
 * MVPではKen Burnsのみ（ParallaxSceneはPhase 2で切替）。
 *
 * 使い方:
 *   Root.tsx 側で <Composition component={UkiyoeAnimation}
 *     defaultProps={{name: "kanagawa_wave"}} ... />
 *   とデフォルトプロップで作品名を渡すか、動的ロードする。
 *
 * 静的requireだとビルド時に作品追加ができないため、
 * Rootでjsonをimportしてpropsに渡す形にしている。
 */

export interface UkiyoeCamera {
  zoom: number;
  x: number;
  y: number;
  endZoom?: number;
  endX?: number;
  endY?: number;
  tilt?: number;
}

export interface UkiyoeScene {
  id: number;
  section: string;
  duration: number; // seconds
  narration_ja: string;
  subtitle_ja: string;
  narration_en?: string;
  subtitle_en?: string;
  camera: UkiyoeCamera;
  audio_path?: string;
  overlays?: unknown[];
}

export interface UkiyoeMeta {
  title_ja: string;
  title_en: string;
  artist: string;
  year: number;
}

export interface UkiyoeData {
  meta: UkiyoeMeta;
  scenes: UkiyoeScene[];
}

export interface UkiyoeAnimationProps {
  name: string;
  data: UkiyoeData;
}

/**
 * シーン単体のレンダラ。
 */
const SceneView: React.FC<{
  name: string;
  scene: UkiyoeScene;
}> = ({ name, scene }) => {
  const originalSrc = staticFile(`ukiyoe/${name}/original.jpg`);
  const cam = scene.camera;
  const fromZoom = cam.zoom ?? 1.0;
  const toZoom = cam.endZoom ?? Math.max(fromZoom, fromZoom + 0.06);
  const fromXY = { x: cam.x ?? 0.5, y: cam.y ?? 0.5 };
  const toXY = {
    x: cam.endX ?? cam.x ?? 0.5,
    y: cam.endY ?? cam.y ?? 0.5,
  };

  return (
    <AbsoluteFill>
      <KenBurns
        src={originalSrc}
        fromZoom={fromZoom}
        toZoom={toZoom}
        fromXY={fromXY}
        toXY={toXY}
        tilt={cam.tilt ?? 0}
      />
      {/* 上下の黒帯（シネマスコープ風） */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 48,
          background: "linear-gradient(180deg, rgba(0,0,0,0.9), rgba(0,0,0,0))",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 240,
          background: "linear-gradient(0deg, rgba(0,0,0,0.85), rgba(0,0,0,0))",
          pointerEvents: "none",
        }}
      />
      <BilingualSubtitle ja={scene.subtitle_ja} en={scene.subtitle_en} />
    </AbsoluteFill>
  );
};

/**
 * タイトル専用オーバーレイ（section="title" のシーンに重ねる）。
 */
const TitleOverlay: React.FC<{ meta: UkiyoeMeta }> = ({ meta }) => (
  <AbsoluteFill
    style={{
      justifyContent: "center",
      alignItems: "center",
      background:
        "radial-gradient(ellipse at center, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.55) 100%)",
    }}
  >
    <div
      style={{
        textAlign: "center",
        padding: "28px 60px",
        background: "rgba(8, 12, 22, 0.55)",
        border: "1px solid rgba(255,255,255,0.2)",
      }}
    >
      <div
        style={{
          fontFamily:
            "'Noto Serif JP', 'Hiragino Mincho ProN', 'Yu Mincho', serif",
          fontSize: 96,
          color: "#fafafa",
          letterSpacing: "0.12em",
          fontWeight: 600,
          textShadow: "0 4px 12px rgba(0,0,0,0.8)",
        }}
      >
        {meta.title_ja}
      </div>
      <div
        style={{
          marginTop: 14,
          fontFamily: "'EB Garamond', 'Times New Roman', serif",
          fontSize: 38,
          fontStyle: "italic",
          color: "#d8e0ea",
          letterSpacing: "0.08em",
        }}
      >
        {meta.title_en}
      </div>
      <div
        style={{
          marginTop: 28,
          fontFamily:
            "'Noto Serif JP', 'Hiragino Mincho ProN', serif",
          fontSize: 32,
          color: "#c9d2dd",
        }}
      >
        {meta.artist} ・ {meta.year}
      </div>
    </div>
  </AbsoluteFill>
);

/**
 * メインコンポジション。
 */
export const UkiyoeAnimation: React.FC<UkiyoeAnimationProps> = ({
  name,
  data,
}) => {
  const { fps } = useVideoConfig();

  let cursor = 0;
  const seqs = data.scenes.map((scene) => {
    const frames = Math.round(scene.duration * fps);
    const start = cursor;
    cursor += frames;
    return { scene, start, frames };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {seqs.map(({ scene, start, frames }) => (
        <Sequence
          key={scene.id}
          from={start}
          durationInFrames={frames}
          name={`scene-${scene.id}-${scene.section}`}
        >
          <SceneView name={name} scene={scene} />
          {scene.section === "title" && <TitleOverlay meta={data.meta} />}
          {scene.audio_path && (
            <Audio src={staticFile(scene.audio_path)} />
          )}
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

/**
 * durationInFrames 算出ヘルパ。Root.tsx から呼ぶ。
 */
export const computeUkiyoeDuration = (
  data: UkiyoeData,
  fps: number
): number => {
  return data.scenes.reduce(
    (acc, s) => acc + Math.round(s.duration * fps),
    0
  );
};
