import React from "react";
import { Composition } from "remotion";
import {
  UkiyoeAnimation,
  UkiyoeData,
  computeUkiyoeDuration,
} from "./compositions/UkiyoeAnimation";

// ---------------------------------------------------------------------------
// 浮世絵シーン登録
// ---------------------------------------------------------------------------
// 作品ごとに
//   1. src/data/ukiyoe_scenes/<slug>.json を追加
//   2. ここで import → registerUkiyoe() を呼ぶ
// の 2 ステップで足りるようにしている。
//
// strict TS では JSON import に型が付かないため、いったん unknown を経由して
// UkiyoeData に流し込む。スキーマの整合は generate_script.py 側が担保する。

import kanagawaWave from "./data/ukiyoe_scenes/kanagawa_wave.json";

const FPS = 30;
const WIDTH = 1920;
const HEIGHT = 1080;

const registerUkiyoe = (slug: string, data: UkiyoeData) => {
  const parts = slug.split("_").map((p) => p.charAt(0).toUpperCase() + p.slice(1));
  const id = "Ukiyoe" + parts.join("");
  return (
    <Composition
      id={id}
      component={UkiyoeAnimation}
      durationInFrames={computeUkiyoeDuration(data, FPS)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      defaultProps={{ name: slug, data }}
    />
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {registerUkiyoe("kanagawa_wave", kanagawaWave as unknown as UkiyoeData)}
      {/*
        新しい作品を足すときは、上と同じ形で並べる：
        {registerUkiyoe("gaifu_kaisei", gaifuKaisei as unknown as UkiyoeData)}
      */}
    </>
  );
};
