<template>
  <div class="space-y-4">
    <div class="flex gap-2">
      <select
        v-model="selectedIndex"
        class="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
      >
        <option v-for="(p, i) in profiles" :key="i" :value="i">
          {{ p.name }}
        </option>
      </select>
      <button
        class="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        @click="addProfile"
      >
        添加
      </button>
      <button
        class="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
        :disabled="profiles.length <= 1"
        @click="removeProfile"
      >
        删除
      </button>
    </div>
    <div v-if="current" class="space-y-3">
      <div>
        <label class="block text-sm text-gray-600 mb-1">名称</label>
        <input
          v-model="current.name"
          class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          @change="emitUpdate"
        />
      </div>
      <div>
        <label class="block text-sm text-gray-600 mb-1">API Key</label>
        <input
          v-model="current.api_key"
          type="password"
          class="w-full border border-gray-300 rounded px-2 py-1 text-sm font-mono"
          @change="emitUpdate"
        />
      </div>
      <div>
        <label class="block text-sm text-gray-600 mb-1">Base URL</label>
        <input
          v-model="current.base_url"
          class="w-full border border-gray-300 rounded px-2 py-1 text-sm font-mono"
          @change="emitUpdate"
        />
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
