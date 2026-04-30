<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">翻译</h2>

    <div class="mac-card p-5 space-y-4">
      <div>
        <label class="mac-label">目标语言</label>
        <input
          v-model="targetLang"
          list="target-languages"
          class="mac-input"
          placeholder="可输入或从下拉中选择"
          @change="$emit('update', { targetLanguage: targetLang })"
        />
        <datalist id="target-languages">
          <option value="中文" />
          <option value="英语" />
          <option value="日语" />
          <option value="俄语" />
          <option value="法语" />
          <option value="德语" />
          <option value="韩语" />
          <option value="西班牙语" />
        </datalist>
      </div>
      <div>
        <label class="mac-label">翻译快捷键</label>
        <select
          v-model="translateShortcut"
          class="mac-input font-mono"
          @change="$emit('update', { translateShortcut })"
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
          @change="$emit('update', { appendShortcut })"
        >
          <option value="DoubleTap:Shift">双击 Shift</option>
          <option value="DoubleTap:Ctrl">双击 Ctrl</option>
          <option value="CmdOrCtrl+Shift+A">Ctrl/Cmd+Shift+A</option>
        </select>
        <p
          v-if="hasConflict"
          class="mt-2 text-[11px] text-amber-600 flex items-center gap-1"
        >
          <span>⚠</span>
          <span>翻译和追加快捷键相同,只会触发一个,请选择不同的按键。</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

const props = defineProps<{
  targetLanguage: string;
  translateShortcut: string;
  appendShortcut: string;
}>();

defineEmits<{ update: [partial: Record<string, string>] }>();

const targetLang = ref(props.targetLanguage);
const translateShortcut = ref(props.translateShortcut);
const appendShortcut = ref(props.appendShortcut);

const hasConflict = computed(
  () => translateShortcut.value === appendShortcut.value
);
</script>
