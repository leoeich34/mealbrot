<template>
  <div class="space-y-5">
    <div>
      <p class="text-sm font-semibold uppercase text-stone-500">Рецепты</p>
      <h2 class="text-2xl font-bold">Подбор по домашним продуктам</h2>
    </div>

    <section class="card-pad grid gap-3 md:grid-cols-[1fr_160px_160px_140px_auto]">
      <input v-model="filters.q" class="field" placeholder="Поиск рецепта" @input="load" />
      <select v-model="filters.meal_type" class="field" @change="load">
        <option value="">Все приемы</option>
        <option value="breakfast">Завтрак</option>
        <option value="lunch">Обед</option>
        <option value="dinner">Ужин</option>
      </select>
      <select v-model="filters.difficulty" class="field" @change="load">
        <option value="">Любая сложность</option>
        <option value="easy">Легко</option>
        <option value="medium">Средне</option>
        <option value="hard">Сложно</option>
      </select>
      <input v-model.number="filters.max_time" class="field" type="number" min="1" placeholder="Минуты" @input="load" />
      <button class="btn" @click="load"><Search class="h-4 w-4" />Найти</button>
    </section>

    <div class="grid gap-4 lg:grid-cols-2">
      <article v-for="recipe in recipes" :key="recipe.id" class="card overflow-hidden">
        <div class="grid md:grid-cols-[180px_1fr]">
          <div class="min-h-44 bg-stone-100">
            <img v-if="recipe.image_url" :src="recipe.image_url" :alt="recipe.title" class="h-full w-full object-cover" />
            <div v-else class="flex h-full min-h-44 items-center justify-center text-stone-400">
              <NotebookTabs class="h-8 w-8" />
            </div>
          </div>
          <div class="p-4">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h3 class="text-lg font-bold">{{ recipe.title }}</h3>
                <p class="mt-1 text-sm text-stone-500">{{ mealSlotLabel(recipe.meal_type) }} · {{ recipe.cooking_time }} мин · {{ recipe.calories || 'ккал не указаны' }}</p>
              </div>
              <span class="rounded-full border px-3 py-1 text-xs font-semibold" :class="recipe.can_cook ? 'border-green-200 bg-green-50 text-leaf' : 'border-orange-200 bg-orange-50 text-orange-700'">
                {{ recipe.can_cook ? 'Готово к приготовлению' : `Не хватает ${recipe.missing_ingredients.length}` }}
              </span>
            </div>
            <p class="mt-3 text-sm leading-6 text-stone-600">{{ recipe.description }}</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span v-for="item in recipe.ingredients" :key="item.ingredient.id" class="rounded-full bg-stone-100 px-2.5 py-1 text-xs text-stone-600">
                {{ item.ingredient.name }} {{ formatQuantity(item.quantity, item.ingredient.unit) }}
              </span>
            </div>
            <div v-if="recipe.missing_ingredients.length" class="mt-3 rounded-md border border-orange-100 bg-orange-50 p-3 text-sm text-orange-800">
              <p class="font-semibold">Нужно докупить: {{ recipe.missing_cost === null ? 'цена неизвестна' : `${recipe.missing_cost} ₽` }}</p>
              <p>{{ recipe.missing_ingredients.map((item) => item.ingredient.name).join(', ') }}</p>
            </div>
            <div class="mt-4 grid gap-2 md:grid-cols-[1fr_150px_auto]">
              <input v-model="planDate" class="field" type="date" />
              <select v-model="planSlot" class="field">
                <option value="breakfast">Завтрак</option>
                <option value="lunch">Обед</option>
                <option value="dinner">Ужин</option>
              </select>
              <button class="btn-primary" @click="addToPlan(recipe)">
                <CalendarPlus class="h-4 w-4" />
                В план
              </button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { CalendarPlus, NotebookTabs, Search } from 'lucide-vue-next';
import { onMounted, reactive, ref } from 'vue';

import { api } from '../api/client';
import { formatQuantity, mealSlotLabel } from '../utils/ui';

const recipes = ref([]);
const planDate = ref(new Date().toISOString().slice(0, 10));
const planSlot = ref('dinner');
const filters = reactive({ q: '', meal_type: '', difficulty: '', max_time: '' });

async function load() {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value);
  }
  const suffix = params.toString() ? `?${params}` : '';
  recipes.value = await api.get(`/recipes${suffix}`);
}

async function addToPlan(recipe) {
  const day = await api.get(`/planner/day/${planDate.value}`);
  const entries = day.entries
    .filter((entry) => entry.meal_slot !== planSlot.value)
    .map((entry) => ({ meal_slot: entry.meal_slot, recipe_id: entry.recipe.id }));
  entries.push({ meal_slot: planSlot.value, recipe_id: recipe.id });
  await api.put(`/planner/day/${planDate.value}`, { entries });
}

onMounted(load);
</script>
