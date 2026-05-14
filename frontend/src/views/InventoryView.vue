<template>
  <div class="space-y-5">
    <div>
      <p class="text-sm font-semibold uppercase text-stone-500">Продукты</p>
      <h2 class="text-2xl font-bold">Единый список продуктов дома</h2>
    </div>

    <form class="card-pad grid gap-3 md:grid-cols-[1fr_140px_180px_auto]" @submit.prevent="save">
      <div>
        <label class="label">Продукт</label>
        <select v-model.number="form.ingredient_id" class="field" required>
          <option disabled value="">Выберите ингредиент</option>
          <option v-for="ingredient in ingredients" :key="ingredient.id" :value="ingredient.id">
            {{ ingredient.name }} · {{ ingredient.category.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="label">Количество</label>
        <input v-model.number="form.quantity" class="field" min="0" step="0.1" type="number" required />
      </div>
      <div>
        <label class="label">Срок годности</label>
        <input v-model="form.expiration_date" class="field" type="date" />
      </div>
      <div class="flex items-end">
        <button class="btn-primary w-full">
          <Plus class="h-4 w-4" />
          {{ editingId ? 'Сохранить' : 'Добавить' }}
        </button>
      </div>
    </form>

    <section class="card overflow-hidden">
      <table class="w-full min-w-[760px] border-collapse">
        <thead class="table-head">
          <tr>
            <th class="px-3 py-3">Продукт</th>
            <th class="px-3 py-3">Категория</th>
            <th class="px-3 py-3">Количество</th>
            <th class="px-3 py-3">Срок</th>
            <th class="px-3 py-3">Статус</th>
            <th class="px-3 py-3 text-right">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventory" :key="item.id">
            <td class="table-cell font-semibold">{{ item.ingredient.name }}</td>
            <td class="table-cell">{{ item.ingredient.category.name }}</td>
            <td class="table-cell">{{ formatQuantity(item.quantity, item.ingredient.unit) }}</td>
            <td class="table-cell">{{ item.expiration_date || 'без срока' }}</td>
            <td class="table-cell"><StatusBadge :status="item.expiration_status" /></td>
            <td class="table-cell">
              <div class="flex justify-end gap-2">
                <button class="icon-btn" title="Редактировать" @click="edit(item)">
                  <Pencil class="h-4 w-4" />
                </button>
                <button class="icon-btn text-red-700" title="Удалить" @click="remove(item.id)">
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!inventory.length" class="p-6 text-sm text-stone-500">Список продуктов пока пуст.</p>
    </section>
  </div>
</template>

<script setup>
import { Pencil, Plus, Trash2 } from 'lucide-vue-next';
import { onMounted, reactive, ref } from 'vue';

import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge.vue';
import { formatQuantity } from '../utils/ui';

const ingredients = ref([]);
const inventory = ref([]);
const editingId = ref(null);
const form = reactive({ ingredient_id: '', quantity: 1, expiration_date: '' });

async function load() {
  const [ingredientData, inventoryData] = await Promise.all([
    api.get('/catalog/ingredients'),
    api.get('/inventory')
  ]);
  ingredients.value = ingredientData;
  inventory.value = inventoryData;
}

function resetForm() {
  editingId.value = null;
  form.ingredient_id = '';
  form.quantity = 1;
  form.expiration_date = '';
}

async function save() {
  const payload = {
    ingredient_id: form.ingredient_id,
    quantity: form.quantity,
    expiration_date: form.expiration_date || null
  };
  if (editingId.value) {
    await api.put(`/inventory/${editingId.value}`, payload);
  } else {
    await api.post('/inventory', payload);
  }
  resetForm();
  await load();
}

function edit(item) {
  editingId.value = item.id;
  form.ingredient_id = item.ingredient.id;
  form.quantity = item.quantity;
  form.expiration_date = item.expiration_date || '';
}

async function remove(id) {
  await api.delete(`/inventory/${id}`);
  await load();
}

onMounted(load);
</script>
