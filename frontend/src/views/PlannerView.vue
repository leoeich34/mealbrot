<template>
  <div class="space-y-5">
    <div class="flex flex-col justify-between gap-3 md:flex-row md:items-end">
      <div>
        <p class="text-sm font-semibold uppercase text-stone-500">Календарь</p>
        <h2 class="text-2xl font-bold">План питания на месяц</h2>
      </div>
      <div class="flex flex-wrap gap-2">
        <button class="btn" @click="shiftMonth(-1)"><ChevronLeft class="h-4 w-4" />Назад</button>
        <button class="btn" @click="shiftMonth(1)">Вперед<ChevronRight class="h-4 w-4" /></button>
        <button class="btn-primary" @click="generateWeek"><Sparkles class="h-4 w-4" />Сгенерировать неделю</button>
      </div>
    </div>

    <section class="card-pad">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 class="text-lg font-bold">{{ monthTitle }}</h3>
        <input v-model="weekStart" class="field max-w-48" type="date" />
      </div>

      <div class="grid grid-cols-7 border-l border-t border-stone-200 text-center text-xs font-semibold uppercase text-stone-500">
        <div v-for="day in weekdays" :key="day" class="border-b border-r border-stone-200 bg-stone-50 px-2 py-2">{{ day }}</div>
      </div>
      <div class="grid grid-cols-7 border-l border-stone-200">
        <button
          v-for="day in calendarDays"
          :key="day.date"
          class="min-h-28 border-b border-r border-stone-200 bg-white p-2 text-left transition hover:bg-green-50"
          :class="!day.isCurrentMonth && 'bg-stone-50 text-stone-400'"
          @click="openDay(day.date)"
        >
          <span class="text-sm font-semibold">{{ day.day }}</span>
          <div class="mt-2 space-y-1">
            <p v-for="entry in day.entries.slice(0, 3)" :key="entry.id" class="truncate rounded bg-stone-100 px-2 py-1 text-xs text-stone-700">
              {{ mealSlotLabel(entry.meal_slot) }} · {{ entry.recipe.title }}
            </p>
          </div>
        </button>
      </div>
    </section>

    <section v-if="selectedDate" class="card-pad">
      <div class="mb-4 flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-semibold uppercase text-stone-500">Редактор дня</p>
          <h3 class="text-lg font-bold">{{ selectedDate }}</h3>
        </div>
        <button class="icon-btn" title="Закрыть" @click="selectedDate = ''"><X class="h-4 w-4" /></button>
      </div>
      <div class="grid gap-3 md:grid-cols-3">
        <div v-for="slot in slots" :key="slot.value" class="rounded-md border border-stone-200 p-3">
          <label class="label">{{ slot.label }}</label>
          <select v-model.number="dayForm[slot.value]" class="field">
            <option :value="0">Не запланировано</option>
            <option v-for="recipe in recipes" :key="recipe.id" :value="recipe.id">{{ recipe.title }}</option>
          </select>
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <button class="btn-primary" @click="saveDay"><Save class="h-4 w-4" />Сохранить день</button>
        <button class="btn" @click="clearDay"><Trash2 class="h-4 w-4" />Очистить</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ChevronLeft, ChevronRight, Save, Sparkles, Trash2, X } from 'lucide-vue-next';
import { computed, onMounted, reactive, ref } from 'vue';

import { api } from '../api/client';
import { buildMonthGrid, mealSlotLabel } from '../utils/ui';

const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
const slots = [
  { value: 'breakfast', label: 'Завтрак' },
  { value: 'lunch', label: 'Обед' },
  { value: 'dinner', label: 'Ужин' }
];
const current = ref(new Date());
const entries = ref([]);
const recipes = ref([]);
const selectedDate = ref('');
const weekStart = ref(new Date().toISOString().slice(0, 10));
const dayForm = reactive({ breakfast: 0, lunch: 0, dinner: 0 });

const monthTitle = computed(() =>
  current.value.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })
);
const calendarDays = computed(() =>
  buildMonthGrid(current.value.getFullYear(), current.value.getMonth(), entries.value).flat()
);

async function loadMonth() {
  const year = current.value.getFullYear();
  const month = current.value.getMonth() + 1;
  const [planData, recipeData] = await Promise.all([
    api.get(`/planner/month/${year}/${month}`),
    api.get('/recipes')
  ]);
  entries.value = planData.entries;
  recipes.value = recipeData;
}

function shiftMonth(delta) {
  current.value = new Date(current.value.getFullYear(), current.value.getMonth() + delta, 1);
  loadMonth();
}

async function openDay(date) {
  selectedDate.value = date;
  const day = await api.get(`/planner/day/${date}`);
  for (const slot of slots) {
    dayForm[slot.value] = day.entries.find((entry) => entry.meal_slot === slot.value)?.recipe.id ?? 0;
  }
}

async function saveDay() {
  const payload = {
    entries: slots
      .filter((slot) => dayForm[slot.value])
      .map((slot) => ({ meal_slot: slot.value, recipe_id: dayForm[slot.value] }))
  };
  await api.put(`/planner/day/${selectedDate.value}`, payload);
  await loadMonth();
}

async function clearDay() {
  for (const slot of slots) dayForm[slot.value] = 0;
  await saveDay();
}

async function generateWeek() {
  await api.post('/planner/generate-week', { start_date: weekStart.value });
  await loadMonth();
}

onMounted(loadMonth);
</script>
