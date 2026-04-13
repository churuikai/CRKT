<template>
  <div class="flex h-screen bg-white text-gray-900">
    <!-- Tab sidebar -->
    <nav class="w-40 bg-gray-50 border-r border-gray-200 p-2 space-y-1">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="w-full text-left px-3 py-2 text-sm rounded"
        :class="
          activeTab === tab.id
            ? 'bg-purple-100 text-purple-700'
            : 'hover:bg-gray-100 text-gray-600'
        "
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </nav>

    <!-- Tab content -->
    <div class="flex-1 p-6 overflow-auto">
      <div v-if="!config" class="text-gray-400">加载中...</div>
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
    </div>
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
  { id: "api", label: "API 设置" },
  { id: "models", label: "模型管理" },
  { id: "prompts", label: "技能/提示词" },
  { id: "translation", label: "翻译设置" },
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
