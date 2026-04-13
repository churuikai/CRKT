import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";

interface AppConfig {
  skills: { name: string; prompt: string }[];
  selected_skill: string;
  api_profiles: { name: string; api_key: string; base_url: string }[];
  selected_api: string;
  models: string[];
  selected_model: string;
  translate_shortcut: string;
  append_shortcut: string;
  start_on_boot: boolean;
  target_language: string;
  show_source_comparison: boolean;
}

export type { AppConfig };

export function useSettings() {
  const config = ref<AppConfig | null>(null);
  const loading = ref(false);

  async function loadConfig() {
    loading.value = true;
    try {
      config.value = await invoke<AppConfig>("get_config");
    } finally {
      loading.value = false;
    }
  }

  async function saveConfig(newConfig: AppConfig) {
    await invoke("update_config", { newConfig });
    config.value = newConfig;
  }

  return { config, loading, loadConfig, saveConfig };
}
