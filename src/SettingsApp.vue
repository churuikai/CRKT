<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <nav class="w-48 bg-black/[0.025] border-r border-black/[0.05] pt-10 pb-4 px-3 space-y-0.5 select-none"
         data-tauri-drag-region>
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="w-full text-left px-3 py-[7px] text-[13px] rounded-lg transition-all duration-150"
        :class="
          activeTab === tab.id
            ? 'bg-blue-500 text-white font-medium shadow-sm shadow-blue-500/20'
            : 'text-[#1d1d1f]/55 hover:text-[#1d1d1f]/80 hover:bg-black/[0.04]'
        "
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </nav>

    <!-- Content -->
    <main class="flex-1 overflow-auto px-8 py-8">
      <div v-if="!config" class="text-gray-300 text-sm animate-pulse">加载中...</div>
      <template v-else>
        <ApiSettings
          v-if="activeTab === 'api'"
          :profiles="config.api_profiles"
          :selected-api="config.selected_api"
          @update="onApiUpdate"
        />
        <ModelSettings
          v-if="activeTab === 'models'"
          :models="config.models"
          :selected-model="config.selected_model"
          @update="onModelUpdate"
        />
        <PromptSettings
          v-if="activeTab === 'prompts'"
          :skills="config.skills"
          :selected-skill="config.selected_skill"
          @update="onPromptUpdate"
        />
        <TranslationSettings
          v-if="activeTab === 'translation'"
          :target-language="config.target_language"
          :translate-shortcut="config.translate_shortcut"
          :append-shortcut="config.append_shortcut"
          @update="onTranslationUpdate"
        />
        <GeneralSettings
          v-if="activeTab === 'general'"
          :start-on-boot="config.start_on_boot"
          @update="onGeneralUpdate"
        />
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSettings, type AppConfig } from "./composables/useSettings";
import ApiSettings from "./components/settings/ApiSettings.vue";
import ModelSettings from "./components/settings/ModelSettings.vue";
import PromptSettings from "./components/settings/PromptSettings.vue";
import TranslationSettings from "./components/settings/TranslationSettings.vue";
import GeneralSettings from "./components/settings/GeneralSettings.vue";

const tabs = [
  { id: "api", label: "API" },
  { id: "models", label: "模型" },
  { id: "prompts", label: "提示词" },
  { id: "translation", label: "翻译" },
  { id: "general", label: "通用" },
];

const activeTab = ref("api");
const { config, loadConfig, saveConfig } = useSettings();

onMounted(() => loadConfig());

function save() {
  if (config.value) {
    saveConfig({ ...config.value });
  }
}

function onApiUpdate(profiles: AppConfig["api_profiles"], selectedApi: string) {
  if (!config.value) return;
  config.value.api_profiles = profiles;
  config.value.selected_api = selectedApi;
  save();
}

function onModelUpdate(models: string[], selected: string) {
  if (!config.value) return;
  config.value.models = models;
  config.value.selected_model = selected;
  save();
}

function onPromptUpdate(skills: AppConfig["skills"], selectedSkill: string) {
  if (!config.value) return;
  config.value.skills = skills;
  config.value.selected_skill = selectedSkill;
  save();
}

function onTranslationUpdate(partial: Record<string, string>) {
  if (!config.value) return;
  Object.assign(config.value, {
    target_language: partial.targetLanguage ?? config.value.target_language,
    translate_shortcut:
      partial.translateShortcut ?? config.value.translate_shortcut,
    append_shortcut: partial.appendShortcut ?? config.value.append_shortcut,
  });
  save();
}

function onGeneralUpdate(partial: Record<string, boolean>) {
  if (!config.value) return;
  if (partial.startOnBoot !== undefined) {
    config.value.start_on_boot = partial.startOnBoot;
  }
  save();
}
</script>
