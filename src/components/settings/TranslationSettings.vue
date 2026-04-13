<template>
  <div class="space-y-4">
    <div>
      <label class="block text-sm text-gray-600 mb-1">目标语言</label>
      <select
        v-model="targetLang"
        class="border border-gray-300 rounded px-2 py-1 text-sm"
        @change="$emit('update', { targetLanguage: targetLang })"
      >
        <option value="中文">中文</option>
        <option value="英语">英语 / English</option>
        <option value="日语">日语 / 日本語</option>
        <option value="俄语">俄语 / Русский</option>
      </select>
    </div>
    <div>
      <label class="block text-sm text-gray-600 mb-1">翻译快捷键</label>
      <input
        v-model="translateShortcut"
        class="border border-gray-300 rounded px-2 py-1 text-sm font-mono"
        readonly
        @change="$emit('update', { translateShortcut: translateShortcut })"
      />
      <p class="text-xs text-gray-400 mt-1">例: CmdOrCtrl+Shift+T</p>
    </div>
    <div>
      <label class="block text-sm text-gray-600 mb-1">追加快捷键</label>
      <input
        v-model="appendShortcut"
        class="border border-gray-300 rounded px-2 py-1 text-sm font-mono"
        readonly
        @change="$emit('update', { appendShortcut: appendShortcut })"
      />
      <p class="text-xs text-gray-400 mt-1">例: CmdOrCtrl+Shift+A</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  targetLanguage: string;
  translateShortcut: string;
  appendShortcut: string;
}>();

defineEmits<{ update: [partial: Record<string, string>] }>();

const targetLang = ref(props.targetLanguage);
const translateShortcut = ref(props.translateShortcut);
const appendShortcut = ref(props.appendShortcut);
</script>
