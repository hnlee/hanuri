import { ui } from "./ui";

type Lang = keyof typeof ui;

export function getLangFromUrl(url: URL): Lang {
  const [, lang] = url.pathname.split("/");
  if (lang in ui) return lang as keyof typeof ui;
  return "en";
}

export function useTranslation(lang: Lang): (key: string) => string {
  const localizedUI: Record<string, string> = ui[lang];
  const defaultUI: Record<string, string> = ui["en"];
  return function t(key: string): string {
    return key in localizedUI ? localizedUI[key] : defaultUI[key];
  };
}
