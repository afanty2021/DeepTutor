"use client";

import { Languages } from "lucide-react";
import { useGlobal } from "@/context/GlobalContext";

export default function LanguageSwitcher() {
  const { uiSettings, setUiSettings } = useGlobal();
  const currentLang = uiSettings.language;

  const toggleLanguage = () => {
    setUiSettings({
      ...uiSettings,
      language: currentLang === "en" ? "zh" : "en",
    });
  };

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors text-sm font-medium text-slate-700 dark:text-slate-200"
      title={currentLang === "en" ? "切换到中文" : "Switch to English"}
    >
      <Languages className="w-4 h-4" />
      <span className="min-w-[20px]">{currentLang === "en" ? "EN" : "中文"}</span>
    </button>
  );
}
