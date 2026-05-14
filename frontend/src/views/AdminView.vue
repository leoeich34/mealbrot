<template>
  <div class="space-y-5">
    <div>
      <p class="text-sm font-semibold uppercase text-stone-500">Admin</p>
      <h2 class="text-2xl font-bold">Каталоги и роли</h2>
    </div>

    <div class="flex gap-2 overflow-x-auto">
      <button v-for="tab in tabs" :key="tab.key" class="btn shrink-0" :class="activeTab === tab.key && 'border-leaf bg-green-50 text-leaf'" @click="activeTab = tab.key">
        {{ tab.label }}
      </button>
    </div>

    <section v-if="activeTab === 'categories'" class="grid gap-4 lg:grid-cols-[360px_1fr]">
      <form class="card-pad space-y-3" @submit.prevent="saveCategory">
        <h3 class="text-lg font-bold">{{ categoryForm.id ? 'Редактировать категорию' : 'Новая категория' }}</h3>
        <input v-model="categoryForm.name" class="field" placeholder="овощи" required />
        <label class="flex items-center gap-2 text-sm">
          <input v-model="categoryForm.is_active" type="checkbox" class="h-4 w-4 accent-leaf" />
          Активна
        </label>
        <div class="flex gap-2">
          <button class="btn-primary"><Save class="h-4 w-4" />Сохранить</button>
          <button type="button" class="btn" @click="resetCategory">Сброс</button>
        </div>
      </form>
      <div class="card overflow-hidden">
        <table class="w-full">
          <thead class="table-head"><tr><th class="px-3 py-3">Название</th><th class="px-3 py-3">Статус</th><th class="px-3 py-3 text-right">Действия</th></tr></thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td class="table-cell font-semibold">{{ category.name }}</td>
              <td class="table-cell">{{ category.is_active ? 'активна' : 'скрыта' }}</td>
              <td class="table-cell">
                <div class="flex justify-end gap-2">
                  <button class="icon-btn" @click="categoryForm = { ...category }"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn text-red-700" @click="deleteCategory(category.id)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="activeTab === 'ingredients'" class="grid gap-4 lg:grid-cols-[420px_1fr]">
      <form class="card-pad space-y-3" @submit.prevent="saveIngredient">
        <h3 class="text-lg font-bold">{{ ingredientForm.id ? 'Редактировать ингредиент' : 'Новый ингредиент' }}</h3>
        <input v-model="ingredientForm.name" class="field" placeholder="томаты" required />
        <select v-model="ingredientForm.unit" class="field">
          <option value="g">g</option>
          <option value="ml">ml</option>
          <option value="pcs">pcs</option>
        </select>
        <select v-model.number="ingredientForm.category_id" class="field" required>
          <option disabled value="">Категория</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
        </select>
        <div class="flex gap-2">
          <button class="btn-primary"><Save class="h-4 w-4" />Сохранить</button>
          <button type="button" class="btn" @click="resetIngredient">Сброс</button>
        </div>
      </form>
      <div class="card overflow-hidden">
        <table class="w-full">
          <thead class="table-head"><tr><th class="px-3 py-3">Ингредиент</th><th class="px-3 py-3">Категория</th><th class="px-3 py-3">Ед.</th><th class="px-3 py-3 text-right">Действия</th></tr></thead>
          <tbody>
            <tr v-for="ingredient in ingredients" :key="ingredient.id">
              <td class="table-cell font-semibold">{{ ingredient.name }}</td>
              <td class="table-cell">{{ ingredient.category.name }}</td>
              <td class="table-cell">{{ ingredient.unit }}</td>
              <td class="table-cell">
                <div class="flex justify-end gap-2">
                  <button class="icon-btn" @click="editIngredient(ingredient)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn text-red-700" @click="remove('/admin/ingredients', ingredient.id)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="activeTab === 'stores'" class="grid gap-4 lg:grid-cols-[360px_1fr]">
      <form class="card-pad space-y-3" @submit.prevent="saveStore">
        <h3 class="text-lg font-bold">{{ storeForm.id ? 'Редактировать магазин' : 'Новый магазин' }}</h3>
        <input v-model="storeForm.name" class="field" placeholder="Домашний магазин" required />
        <label class="flex items-center gap-2 text-sm"><input v-model="storeForm.is_active" type="checkbox" class="h-4 w-4 accent-leaf" />Активен</label>
        <button class="btn-primary"><Save class="h-4 w-4" />Сохранить</button>
      </form>
      <div class="card-pad grid gap-2 md:grid-cols-2">
        <div v-for="store in stores" :key="store.id" class="rounded-md border border-stone-200 p-3">
          <p class="font-semibold">{{ store.name }}</p>
          <p class="text-sm text-stone-500">{{ store.is_active ? 'активен' : 'скрыт' }}</p>
          <div class="mt-3 flex gap-2">
            <button class="icon-btn" @click="storeForm = { ...store }"><Pencil class="h-4 w-4" /></button>
            <button class="icon-btn text-red-700" @click="remove('/admin/stores', store.id)"><Trash2 class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'prices'" class="grid gap-4 lg:grid-cols-[420px_1fr]">
      <form class="card-pad space-y-3" @submit.prevent="savePrice">
        <h3 class="text-lg font-bold">{{ priceForm.id ? 'Редактировать цену' : 'Новая цена' }}</h3>
        <select v-model.number="priceForm.ingredient_id" class="field" required>
          <option disabled value="">Ингредиент</option>
          <option v-for="ingredient in ingredients" :key="ingredient.id" :value="ingredient.id">{{ ingredient.name }}</option>
        </select>
        <select v-model.number="priceForm.store_id" class="field" required>
          <option disabled value="">Магазин</option>
          <option v-for="store in stores" :key="store.id" :value="store.id">{{ store.name }}</option>
        </select>
        <input v-model.number="priceForm.price_per_unit" class="field" type="number" min="0" step="0.01" placeholder="Цена за кг/л/шт" required />
        <button class="btn-primary"><Save class="h-4 w-4" />Сохранить</button>
      </form>
      <div class="card overflow-hidden">
        <table class="w-full">
          <thead class="table-head"><tr><th class="px-3 py-3">Ингредиент</th><th class="px-3 py-3">Магазин</th><th class="px-3 py-3">Цена</th><th class="px-3 py-3 text-right">Действия</th></tr></thead>
          <tbody>
            <tr v-for="price in prices" :key="price.id">
              <td class="table-cell">{{ price.ingredient.name }}</td>
              <td class="table-cell">{{ price.store.name }}</td>
              <td class="table-cell">{{ price.price_per_unit }} ₽</td>
              <td class="table-cell">
                <div class="flex justify-end gap-2">
                  <button class="icon-btn" @click="editPrice(price)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn text-red-700" @click="remove('/admin/prices', price.id)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="activeTab === 'recipes'" class="grid gap-4 xl:grid-cols-[520px_1fr]">
      <form class="card-pad space-y-3" @submit.prevent="saveRecipe">
        <h3 class="text-lg font-bold">{{ recipeForm.id ? 'Редактировать рецепт' : 'Новый рецепт' }}</h3>
        <input v-model="recipeForm.title" class="field" placeholder="Название" required />
        <textarea v-model="recipeForm.description" class="field min-h-20" placeholder="Описание"></textarea>
        <textarea v-model="recipeForm.steps" class="field min-h-24" placeholder="Шаги приготовления" required></textarea>
        <div class="grid gap-3 md:grid-cols-3">
          <input v-model.number="recipeForm.cooking_time" class="field" type="number" min="1" placeholder="мин" required />
          <select v-model="recipeForm.difficulty" class="field"><option value="easy">easy</option><option value="medium">medium</option><option value="hard">hard</option></select>
          <select v-model="recipeForm.meal_type" class="field"><option value="breakfast">Завтрак</option><option value="lunch">Обед</option><option value="dinner">Ужин</option></select>
        </div>
        <div class="grid gap-3 md:grid-cols-2">
          <input v-model.number="recipeForm.calories" class="field" type="number" min="0" placeholder="ккал" />
          <input v-model="recipeForm.image_url" class="field" placeholder="URL изображения" />
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <p class="font-semibold">Ингредиенты</p>
            <button type="button" class="btn" @click="recipeForm.ingredients.push({ ingredient_id: '', quantity: 1 })"><Plus class="h-4 w-4" />Строка</button>
          </div>
          <div v-for="(line, index) in recipeForm.ingredients" :key="index" class="grid gap-2 md:grid-cols-[1fr_120px_40px]">
            <select v-model.number="line.ingredient_id" class="field" required>
              <option disabled value="">Ингредиент</option>
              <option v-for="ingredient in ingredients" :key="ingredient.id" :value="ingredient.id">{{ ingredient.name }}</option>
            </select>
            <input v-model.number="line.quantity" class="field" type="number" min="0" step="0.1" required />
            <button type="button" class="icon-btn text-red-700" @click="recipeForm.ingredients.splice(index, 1)"><Trash2 class="h-4 w-4" /></button>
          </div>
        </div>
        <button class="btn-primary"><Save class="h-4 w-4" />Сохранить рецепт</button>
      </form>
      <div class="space-y-3">
        <article v-for="recipe in recipes" :key="recipe.id" class="card-pad">
          <div class="flex items-start justify-between gap-3">
            <div>
              <h3 class="font-bold">{{ recipe.title }}</h3>
              <p class="text-sm text-stone-500">{{ recipe.cooking_time }} мин · {{ recipe.meal_type }} · {{ recipe.difficulty }}</p>
            </div>
            <div class="flex gap-2">
              <button class="icon-btn" @click="editRecipe(recipe)"><Pencil class="h-4 w-4" /></button>
              <button class="icon-btn text-red-700" @click="remove('/admin/recipes', recipe.id)"><Trash2 class="h-4 w-4" /></button>
            </div>
          </div>
          <p class="mt-2 text-sm text-stone-600">{{ recipe.ingredients.map((item) => item.ingredient.name).join(', ') }}</p>
        </article>
      </div>
    </section>

    <section v-if="activeTab === 'users'" class="card overflow-hidden">
      <table class="w-full">
        <thead class="table-head"><tr><th class="px-3 py-3">Пользователь</th><th class="px-3 py-3">Email</th><th class="px-3 py-3">Роль</th><th class="px-3 py-3 text-right">Сохранить</th></tr></thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="table-cell font-semibold">{{ user.name }}</td>
            <td class="table-cell">{{ user.email }}</td>
            <td class="table-cell">
              <select v-model="user.role" class="field max-w-36">
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </td>
            <td class="table-cell text-right">
              <button class="btn" @click="saveRole(user)"><Save class="h-4 w-4" />Сохранить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <p v-if="error" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
  </div>
</template>

<script setup>
import { Pencil, Plus, Save, Trash2 } from 'lucide-vue-next';
import { onMounted, reactive, ref } from 'vue';

import { api } from '../api/client';

const tabs = [
  { key: 'categories', label: 'Категории' },
  { key: 'ingredients', label: 'Ингредиенты' },
  { key: 'stores', label: 'Магазины' },
  { key: 'prices', label: 'Цены' },
  { key: 'recipes', label: 'Рецепты' },
  { key: 'users', label: 'Пользователи' }
];

const activeTab = ref('categories');
const error = ref('');
const categories = ref([]);
const ingredients = ref([]);
const stores = ref([]);
const prices = ref([]);
const recipes = ref([]);
const users = ref([]);

let categoryForm = ref({ id: null, name: '', is_active: true });
const ingredientForm = reactive({ id: null, name: '', unit: 'g', category_id: '' });
let storeForm = ref({ id: null, name: '', is_active: true });
const priceForm = reactive({ id: null, ingredient_id: '', store_id: '', price_per_unit: 0 });
const recipeForm = reactive({
  id: null,
  title: '',
  description: '',
  steps: '',
  cooking_time: 30,
  difficulty: 'easy',
  calories: null,
  meal_type: 'dinner',
  image_url: '',
  ingredients: [{ ingredient_id: '', quantity: 1 }]
});

async function load() {
  [categories.value, ingredients.value, stores.value, prices.value, recipes.value, users.value] = await Promise.all([
    api.get('/admin/categories'),
    api.get('/admin/ingredients'),
    api.get('/admin/stores'),
    api.get('/admin/prices'),
    api.get('/admin/recipes'),
    api.get('/admin/users')
  ]);
}

async function withErrors(action) {
  error.value = '';
  try {
    await action();
    await load();
  } catch (err) {
    error.value = err.message;
  }
}

function resetCategory() {
  categoryForm.value = { id: null, name: '', is_active: true };
}

async function saveCategory() {
  await withErrors(async () => {
    if (categoryForm.value.id) {
      await api.put(`/admin/categories/${categoryForm.value.id}`, categoryForm.value);
    } else {
      await api.post('/admin/categories', categoryForm.value);
    }
    resetCategory();
  });
}

async function deleteCategory(id) {
  await withErrors(() => api.delete(`/admin/categories/${id}`));
}

function resetIngredient() {
  Object.assign(ingredientForm, { id: null, name: '', unit: 'g', category_id: '' });
}

function editIngredient(ingredient) {
  Object.assign(ingredientForm, {
    id: ingredient.id,
    name: ingredient.name,
    unit: ingredient.unit,
    category_id: ingredient.category.id
  });
}

async function saveIngredient() {
  await withErrors(async () => {
    const payload = {
      name: ingredientForm.name,
      unit: ingredientForm.unit,
      category_id: ingredientForm.category_id
    };
    if (ingredientForm.id) {
      await api.put(`/admin/ingredients/${ingredientForm.id}`, payload);
    } else {
      await api.post('/admin/ingredients', payload);
    }
    resetIngredient();
  });
}

async function saveStore() {
  await withErrors(async () => {
    if (storeForm.value.id) {
      await api.put(`/admin/stores/${storeForm.value.id}`, storeForm.value);
    } else {
      await api.post('/admin/stores', storeForm.value);
    }
    storeForm.value = { id: null, name: '', is_active: true };
  });
}

function editPrice(price) {
  Object.assign(priceForm, {
    id: price.id,
    ingredient_id: price.ingredient.id,
    store_id: price.store.id,
    price_per_unit: price.price_per_unit
  });
}

async function savePrice() {
  await withErrors(async () => {
    const payload = {
      ingredient_id: priceForm.ingredient_id,
      store_id: priceForm.store_id,
      price_per_unit: priceForm.price_per_unit
    };
    if (priceForm.id) {
      await api.put(`/admin/prices/${priceForm.id}`, payload);
    } else {
      await api.post('/admin/prices', payload);
    }
    Object.assign(priceForm, { id: null, ingredient_id: '', store_id: '', price_per_unit: 0 });
  });
}

function editRecipe(recipe) {
  Object.assign(recipeForm, {
    id: recipe.id,
    title: recipe.title,
    description: recipe.description || '',
    steps: recipe.steps,
    cooking_time: recipe.cooking_time,
    difficulty: recipe.difficulty,
    calories: recipe.calories,
    meal_type: recipe.meal_type,
    image_url: recipe.image_url || '',
    ingredients: recipe.ingredients.map((item) => ({
      ingredient_id: item.ingredient.id,
      quantity: item.quantity
    }))
  });
}

function resetRecipe() {
  Object.assign(recipeForm, {
    id: null,
    title: '',
    description: '',
    steps: '',
    cooking_time: 30,
    difficulty: 'easy',
    calories: null,
    meal_type: 'dinner',
    image_url: '',
    ingredients: [{ ingredient_id: '', quantity: 1 }]
  });
}

async function saveRecipe() {
  await withErrors(async () => {
    const payload = {
      ...recipeForm,
      image_url: recipeForm.image_url || null,
      calories: recipeForm.calories || null,
      ingredients: recipeForm.ingredients.filter((line) => line.ingredient_id && line.quantity > 0)
    };
    if (recipeForm.id) {
      await api.put(`/admin/recipes/${recipeForm.id}`, payload);
    } else {
      await api.post('/admin/recipes', payload);
    }
    resetRecipe();
  });
}

async function saveRole(user) {
  await withErrors(() => api.patch(`/admin/users/${user.id}/role`, { role: user.role }));
}

async function remove(basePath, id) {
  await withErrors(() => api.delete(`${basePath}/${id}`));
}

onMounted(load);
</script>
