import { Config } from "@remotion/cli/config";

// Remotion 4.x config.
// 詳細: https://www.remotion.dev/docs/config

Config.setVideoImageFormat("jpeg");
Config.setConcurrency(1);
Config.setEntryPoint("src/index.ts");
// JSON import を strict TS で通すため
Config.overrideWebpackConfig((cfg) => {
  return {
    ...cfg,
    resolve: {
      ...cfg.resolve,
      extensions: [...(cfg.resolve?.extensions ?? []), ".json"],
    },
  };
});
