<template>
  <div class="space-y-5">
    <div>
      <p class="text-sm font-semibold uppercase text-stone-500">Покупки</p>
      <h2 class="text-2xl font-bold">Список покупок по категориям</h2>
    </div>

    <section class="card-pad grid gap-3 md:grid-cols-[180px_120px_auto]">
      <input v-model="generateForm.start_date" class="field" type="date" />
      <input v-model.number="generateForm.days" class="field" type="number" min="1" max="31" />
      <button class="btn-primary" @click="generate">
        <RefreshCw class="h-4 w-4" />
        Сформировать из плана
      </button>
    </section>

    <form class="card-pad grid gap-3 md:grid-cols-[1fr_130px_120px_auto]" @submit.prevent="addManual">
      <input v-model="manual.title" class="field" placeholder="Добавить вручную" required />
      <input v-model.number="manual.quantity" class="field" type="number" min="0" step="0.1" required />
      <select v-model="manual.unit" class="field">
        <option value="g">g</option>
        <option value="ml">ml</option>
        <option value="pcs">pcs</option>
      </select>
      <button class="btn"><Plus class="h-4 w-4" />Добавить</button>
    </form>

    <div class="grid gap-4 lg:grid-cols-2">
      <section v-for="group in groups" :key="group.name" class="card-pad">
        <h3 class="mb-3 text-lg font-bold">{{ group.name }}</h3>
        <div class="space-y-2">
          <label v-for="item in group.items" :key="item.id" class="flex items-center justify-between gap-3 rounded-md border border-stone-100 px-3 py-2">
            <span class="flex min-w-0 items-center gap-3">
              <input type="checkbox" :checked="item.is_purchased" class="h-4 w-4 accent-leaf" @change="toggle(item)" />
              <span class="min-w-0">
                <span class="block truncate font-semibold" :class="item.is_purchased && 'text-stone-400 line-through'">{{ item.title }}</span>
                <span class="text-xs text-stone-500">{{ formatQuantity(item.quantity, item.unit) }} · {{ item.source === 'auto' ? 'из плана' : 'вручную' }}</span>
              </span>
            </span>
            <button class="icon-btn text-red-700" title="Удалить" @click.prevent="remove(item.id)">
              <Trash2 class="h-4 w-4" />
            </button>
          </label>
        </div>
      </section>
    </div>
    <p v-if="!items.length" class="card-pad text-sm text-stone-500">Список покупок пока пуст.</p>
  </div>
</template>

<script setup>
import { Plus, RefreshCw, Trash2 } from 'lucide-vue-next';
import { computed, onMounted, reactive, ref } from 'vue';

import { api } from '../api/client';
import { formatQuantity, groupShoppingItems } from '../utils/ui';

const items = ref([]);
const generateForm = reactive({
  start_date: new Date().toISOString().slice(0, 10),
  days: 7
});
const manual = reactive({ title: '', quantity: 1, unit: 'pcs' });
const groups = computed(() => groupShoppingItems(items.value));

async function load() {
  items.value = (await api.get('/shopping-list')).items;
}

async function generate() {
  items.value = (await api.post('/shopping-list/generate', generateForm)).items;
}

async function addManual() {
  await api.post('/shopping-list', manual);
  manual.title = '';
  manual.quantity = 1;
  manual.unit = 'pcs';
  await load();
}

async function toggle(item) {
  await api.patch(`/shopping-list/${item.id}`, { is_purchased: !item.is_purchased });
  await load();
}

async function remove(id) {
  await api.delete(`/shopping-list/${id}`);
  await load();
}

onMounted(load);
</script>
