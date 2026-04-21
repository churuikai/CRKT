<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">API 配置</h2>

    <!-- Profile selector -->
    <div class="flex items-center gap-2">
      <select
        v-model="selectedIndex"
        class="mac-input flex-1"
      >
        <option v-for="(p, i) in profiles" :key="i" :value="i">
          {{ p.name }}
        </option>
      </select>
      <button
        class="px-3 py-[7px] text-[13px] text-blue-500 font-medium rounded-lg hover:bg-blue-500/[0.07] active:bg-blue-500/[0.12] transition-colors"
        @click="addProfile"
      >
        + 添加
      </button>
      <button
        class="px-3 py-[7px] text-[13px] text-red-500/60 font-medium rounded-lg hover:bg-red-500/[0.07] active:bg-red-500/[0.12] transition-colors disabled:opacity-25 disabled:pointer-events-none"
        :disabled="profiles.length <= 1"
        @click="removeProfile"
      >
        删除
      </button>
    </div>

    <!-- Profile form -->
    <div v-if="current" class="mac-card p-5 space-y-4">
      <div>
        <label class="mac-label">名称</label>
        <input v-model="current.name" class="mac-input" @change="emitUpdate" />
      </div>
      <div>
        <label class="mac-label">API Key</label>
        <input v-model="current.api_key" type="password" class="mac-input font-mono" @change="emitUpdate" />
      </div>
      <div>
        <label class="mac-label">Base URL</label>
        <input v-model="current.base_url" class="mac-input font-mono" @change="emitUpdate" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

interface ApiProfile {
  name: string;
  api_key: string;
  base_url: string;
}

const props = defineProps<{ profiles: ApiProfile[]; selectedApi: string }>();
const emit = defineEmits<{
  update: [profiles: ApiProfile[], selectedApi: string];
}>();

const selectedIndex = ref(
  Math.max(
    0,
    props.profiles.findIndex((p) => p.name === props.selectedApi)
  )
);

const current = computed(() => props.profiles[selectedIndex.value]);

function addProfile() {
  props.profiles.push({
    name: `API ${props.profiles.length + 1}`,
    api_key: "",
    base_url: "https://api.openai.com/v1/",
  });
  selectedIndex.value = props.profiles.length - 1;
  emitUpdate();
}

function removeProfile() {
  if (props.profiles.length <= 1) return;
  props.profiles.splice(selectedIndex.value, 1);
  selectedIndex.value = Math.min(selectedIndex.value, props.profiles.length - 1);
  emitUpdate();
}

function emitUpdate() {
  const selected = props.profiles[selectedIndex.value]?.name ?? "";
  emit("update", [...props.profiles], selected);
}
</script>
