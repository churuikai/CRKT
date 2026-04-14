<template>
  <div class="space-y-4">
    <div class="flex gap-2">
      <select
        v-model="selectedIndex"
        class="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
      >
        <option v-for="(s, i) in skills" :key="i" :value="i">
          {{ s.name }}
        </option>
      </select>
      <button
        class="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        @click="addSkill"
      >
        添加
      </button>
      <button
        class="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
        :disabled="skills.length <= 1"
        @click="removeSkill"
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
        <label class="block text-sm text-gray-600 mb-1">
          提示词模板
          <span class="text-gray-400">
            (可用变量: {source_language}, {target_language}, {selected_text})
          </span>
        </label>
        <textarea
          v-model="current.prompt"
          rows="10"
          class="w-full border border-gray-300 rounded px-2 py-1 text-sm font-mono"
          @change="emitUpdate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

interface Skill {
  name: string;
  prompt: string;
}

const props = defineProps<{ skills: Skill[]; selectedSkill: string }>();
const emit = defineEmits<{
  update: [skills: Skill[], selected: string];
}>();

const selectedIndex = ref(
  Math.max(
    0,
    props.skills.findIndex((s) => s.name === props.selectedSkill)
  )
);
const current = computed(() => props.skills[selectedIndex.value]);

function addSkill() {
  props.skills.push({ name: `技能 ${props.skills.length + 1}`, prompt: "" });
  selectedIndex.value = props.skills.length - 1;
  emitUpdate();
}

function removeSkill() {
  if (props.skills.length <= 1) return;
  props.skills.splice(selectedIndex.value, 1);
  selectedIndex.value = Math.min(selectedIndex.value, props.skills.length - 1);
  emitUpdate();
}

function emitUpdate() {
  const selected = props.skills[selectedIndex.value]?.name ?? "";
  emit("update", [...props.skills], selected);
}
</script>
