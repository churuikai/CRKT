<template>
  <div class="space-y-5">
    <h2 class="text-[17px] font-semibold text-[#1d1d1f] tracking-tight">提示词</h2>

    <div class="flex items-center gap-2">
      <select v-model="selectedIndex" class="mac-input flex-1">
        <option v-for="(s, i) in skills" :key="i" :value="i">
          {{ s.name }}
        </option>
      </select>
      <button
        class="px-3 py-[7px] text-[13px] text-blue-500 font-medium rounded-lg hover:bg-blue-500/[0.07] active:bg-blue-500/[0.12] transition-colors"
        @click="addSkill"
      >
        + 添加
      </button>
      <button
        class="px-3 py-[7px] text-[13px] text-red-500/60 font-medium rounded-lg hover:bg-red-500/[0.07] active:bg-red-500/[0.12] transition-colors disabled:opacity-25 disabled:pointer-events-none"
        :disabled="skills.length <= 1"
        @click="removeSkill"
      >
        删除
      </button>
    </div>

    <div v-if="current" class="mac-card p-5 space-y-4">
      <div>
        <label class="mac-label">名称</label>
        <input v-model="current.name" class="mac-input" @change="emitUpdate" />
      </div>
      <div>
        <label class="mac-label">提示词模板</label>
        <p class="text-[11px] text-black/25 mb-2">
          可用变量: {source_language}, {target_language}, {selected_text}
        </p>
        <textarea
          v-model="current.prompt"
          rows="10"
          class="mac-input font-mono leading-relaxed resize-y"
          style="height: auto"
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
