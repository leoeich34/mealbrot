<template>
  <main class="min-h-screen bg-stone-50 px-4 py-8">
    <section class="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[1fr_420px]">
      <div class="card-pad flex min-h-[520px] flex-col justify-between">
        <div>
          <div class="mb-6 flex h-12 w-12 items-center justify-center rounded-md bg-leaf text-white">
            <ChefHat class="h-6 w-6" />
          </div>
          <h1 class="max-w-2xl text-3xl font-bold leading-tight md:text-4xl">
            Рабочий сервис для домашнего планирования питания
          </h1>
          <p class="mt-4 max-w-2xl text-base leading-7 text-stone-600">
            Ведите продукты дома, собирайте рецепты, планируйте неделю и получайте список покупок без лишних интеграций на первом этапе.
          </p>
        </div>
        <div class="grid gap-3 md:grid-cols-3">
          <div class="rounded-md border border-stone-200 bg-stone-50 p-4">
            <p class="font-semibold">Категории</p>
            <p class="mt-1 text-sm text-stone-600">Овощи, мясо, молочные продукты, крупы и другие группы.</p>
          </div>
          <div class="rounded-md border border-stone-200 bg-stone-50 p-4">
            <p class="font-semibold">Календарь</p>
            <p class="mt-1 text-sm text-stone-600">Месяц на экране, неделя генерируется автоматически.</p>
          </div>
          <div class="rounded-md border border-stone-200 bg-stone-50 p-4">
            <p class="font-semibold">Покупки</p>
            <p class="mt-1 text-sm text-stone-600">Недостающие ингредиенты группируются по категориям.</p>
          </div>
        </div>
      </div>

      <form class="card-pad" @submit.prevent="submit">
        <div class="mb-5 flex rounded-md border border-stone-200 bg-stone-100 p-1">
          <button type="button" class="flex-1 rounded px-3 py-2 text-sm font-semibold" :class="mode === 'login' ? 'bg-white shadow-sm' : 'text-stone-500'" @click="mode = 'login'">
            Вход
          </button>
          <button type="button" class="flex-1 rounded px-3 py-2 text-sm font-semibold" :class="mode === 'register' ? 'bg-white shadow-sm' : 'text-stone-500'" @click="mode = 'register'">
            Регистрация
          </button>
        </div>

        <div v-if="mode === 'register'" class="mb-4">
          <label class="label">Имя</label>
          <input v-model="form.name" class="field" required />
        </div>
        <div class="mb-4">
          <label class="label">Email</label>
          <input v-model="form.email" autocomplete="email" class="field" inputmode="email" required type="text" />
        </div>
        <div class="mb-4">
          <label class="label">Пароль</label>
          <input v-model="form.password" class="field" type="password" required minlength="6" />
        </div>
        <div v-if="mode === 'register'" class="grid gap-4">
          <div>
            <label class="label">Предпочтения</label>
            <textarea v-model="form.preferences" class="field min-h-20" placeholder="простые блюда, курица, крупы"></textarea>
          </div>
          <div>
            <label class="label">Аллергии</label>
            <input v-model="form.allergies" class="field" placeholder="арахис; мед" />
          </div>
          <div>
            <label class="label">Недельный бюджет</label>
            <input v-model.number="form.weekly_budget" class="field" type="number" min="0" />
          </div>
        </div>

        <p v-if="error" class="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
        <button class="btn-primary mt-5 w-full" :disabled="loading">
          <LogIn class="h-4 w-4" />
          {{ mode === 'login' ? 'Войти' : 'Создать аккаунт' }}
        </button>
        <p class="mt-4 text-sm text-stone-500">
          Стартовый admin после seed: admin@example.com / admin123
        </p>
      </form>
    </section>
  </main>
</template>

<script setup>
import { ChefHat, LogIn } from 'lucide-vue-next';
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();
const mode = ref('login');
const loading = ref(false);
const error = ref('');
const form = reactive({
  name: '',
  email: '',
  password: '',
  preferences: '',
  allergies: '',
  weekly_budget: 2500
});

async function submit() {
  loading.value = true;
  error.value = '';
  try {
    if (mode.value === 'login') {
      await auth.login({ email: form.email, password: form.password });
    } else {
      await auth.register({ ...form });
    }
    router.push({ name: 'dashboard' });
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>
