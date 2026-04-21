<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">翻译</h2>

    <div class="mac-card p-5 space-y-4">
      <div>
        <label class="mac-label">目标语言</label>
        <select
          v-model="targetLang"
          class="mac-input"
          @change="$emit('update', { targetLanguage: targetLang })"
        >
          <option value="中文">中文</option>
          <option value="英语">英语 / English</option>
          <option value="日语">日语 / 日本語</option>
          <option value="俄语">俄语 / Русский</option>
        </select>
      </div>
      <div>
        <label class="mac-label">翻译快捷键</label>
        <select
          v-model="translateShortcut"
          class="mac-input font-mono"
          @change="$emit('update', { translateShortcut: translateShortcut })"
        >
          <option value="DoubleTap:Ctrl">双击 Ctrl</option>
          <option value="DoubleTap:Shift">双击 Shift</option>
          <option value="CmdOrCtrl+Shift+T">Ctrl/Cmd+Shift+T</option>
        </select>
      </div>
      <div>
        <label class="mac-label">追加快捷键</label>
        <select
          v-model="appendShortcut"
          class="mac-input font-mono"
          @change="$emit('update', { appendShortcut: appendShortcut })"
        >
          <option value="DoubleTap:Shift">双击 Shift</option>
          <option value="DoubleTap:Ctrl">双击 Ctrl</option>
          <option value="CmdOrCtrl+Shift+A">Ctrl/Cmd+Shift+A</option>
        </select>
      </div>
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
