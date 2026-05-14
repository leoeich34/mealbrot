<template>
  <div class="space-y-12">
    <!-- Header & Stats -->
    <div>
      <div class="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p class="mb-2 text-sm font-bold uppercase tracking-widest text-stone-400">Сводка</p>
          <h2 class="font-display text-4xl font-bold tracking-tight text-ink">Обзор кухни</h2>
        </div>
        <RouterLink to="/planner" class="btn-primary">
          <CalendarDays class="h-5 w-5" />
          <span>Календарь</span>
        </RouterLink>
      </div>

      <div class="flex flex-wrap items-baseline gap-10 md:gap-16">
        <div>
          <p class="font-display text-6xl font-bold text-ink">{{ inventory.length }}</p>
          <p class="mt-2 text-xs font-bold uppercase tracking-widest text-stone-400">Продукты</p>
        </div>
        <div>
          <p class="font-display text-6xl font-bold text-ink">{{ recipes.length }}</p>
          <p class="mt-2 text-xs font-bold uppercase tracking-widest text-stone-400">Рецепты</p>
        </div>
        <div>
          <p class="font-display text-6xl font-bold text-leaf">{{ todayEntries.length }}</p>
          <p class="mt-2 text-xs font-bold uppercase tracking-widest text-stone-400">Блюда сегодня</p>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid gap-10 xl:grid-cols-[1fr_400px]">
      
      <!-- Menu List -->
      <section class="section-container">
        <div class="mb-6 flex items-baseline justify-between">
          <h3 class="font-display text-2xl font-bold text-ink">Меню на сегодня</h3>
          <span class="text-sm font-medium text-stone-400">{{ today }}</span>
        </div>
        
        <div v-if="todayEntries.length" class="divide-y divide-stone-100">
          <div v-for="entry in todayEntries" :key="entry.id" class="list-item list-item-hoverable">
            <div class="flex items-center gap-5">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-stone-100 text-stone-400">
                <ChefHat class="h-6 w-6" />
              </div>
              <div>
                <p class="text-xs font-bold uppercase tracking-widest text-stone-400">{{ mealSlotLabel(entry.meal_slot) }}</p>
                <p class="mt-0.5 text-lg font-bold text-ink">{{ entry.recipe.title }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-stone-500">{{ entry.recipe.cooking_time }} мин</p>
              <p class="mt-0.5 text-xs text-stone-400">{{ entry.recipe.difficulty }}</p>
            </div>
          </div>
        </div>
        <p v-else class="rounded-3xl bg-stone-50 p-8 text-center text-sm font-medium text-stone-400">
          На сегодня ничего не запланировано.
        </p>
      </section>

      <!-- Inventory List -->
      <section class="section-container">
        <div class="mb-6 flex items-center justify-between">
          <h3 class="font-display text-2xl font-bold text-ink">Продукты</h3>
          <RouterLink to="/inventory" class="text-sm font-bold text-leaf hover:text-leaf-dark">Все</RouterLink>
        </div>
        <div class="space-y-1">
          <div v-for="item in inventory.slice(0, 6)" :key="item.id" class="list-item list-item-hoverable">
            <div class="min-w-0 flex-1">
              <p class="truncate font-bold text-ink">{{ item.ingredient.name }}</p>
              <p class="mt-0.5 text-xs text-stone-400">{{ formatQuantity(item.quantity, item.ingredient.unit) }}</p>
            </div>
            <StatusBadge :status="item.expiration_status" />
          </div>
        </div>
      </section>
    </div>

    <!-- Recommendations -->
    <section>
      <div class="mb-6 flex items-center justify-between">
        <h3 class="font-display text-2xl font-bold text-ink">Рекомендации</h3>
      </div>
      <div class="grid gap-6 md:grid-cols-3">
        <article v-for="recipe in recipes.slice(0, 3)" :key="recipe.id" class="section-container transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-stone-200/50">
          <div class="mb-4 flex h-32 items-center justify-center rounded-2xl bg-stone-100">
            <ChefHat class="h-10 w-10 text-stone-300" />
          </div>
          <p class="font-display text-xl font-bold text-ink">{{ recipe.title }}</p>
          <div class="mt-2 flex items-center justify-between text-sm">
            <span class="font-medium text-stone-500">{{ recipe.cooking_time }} мин</span>
            <span :class="recipe.can_cook ? 'text-leaf font-bold' : 'text-stone-400'">
              {{ recipe.can_cook ? 'Можно готовить' : 'Нет продуктов' }}
            </span>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { CalendarDays } from 'lucide-vue-next';
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge.vue';
import { formatQuantity, mealSlotLabel } from '../utils/ui';

const inventory = ref([]);
const recipes = ref([]);
const todayEntries = ref([]);
const shoppingItems = ref([]);
const today = new Date().toISOString().slice(0, 10);

onMounted(async () => {
  const [inventoryData, recipesData, dayData, shoppingData] = await Promise.all([
    api.get('/inventory'),
    api.get('/recipes'),
    api.get(`/planner/day/${today}`),
    api.get('/shopping-list')
  ]);
  inventory.value = inventoryData;
  recipes.value = recipesData;
  todayEntries.value = dayData.entries;
  shoppingItems.value = shoppingData.items;
});
</script>
