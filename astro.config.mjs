// @ts-check
import { unified } from "@astrojs/markdown-remark";
import { defineConfig } from "astro/config";
import icon from "astro-icon";
import rehypeExternalLinks from "rehype-external-links";

const isProd = import.meta.env.MODE === "production";

// https://astro.build/config
export default defineConfig({
  site: isProd
    ? "https://hanurikoreanschoool.org"
    : "https://storage.googleapis.com/hanuri-staging",
  integrations: [icon()],
  markdown: {
    processor: unified({
      rehypePlugins: [
        [
          rehypeExternalLinks,
          {
            target: "_blank",
            rel: ["nofollow", "noopener", "noreferrer"],
          },
        ],
      ],
    }),
  },
  i18n: {
    locales: ["en", "ko"],
    defaultLocale: "en",
    routing: {
      prefixDefaultLocale: true,
    },
  },
  build: {
    assetsPrefix: isProd
      ? "https://hanurikoreanschoool.org"
      : "https://storage.googleapis.com/hanuri-staging",
  },
});
