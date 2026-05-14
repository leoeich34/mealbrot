<template>
  <div class="min-h-screen text-ink pb-20 lg:pb-0">
    <aside class="fixed inset-y-0 left-0 z-20 hidden w-64 bg-white px-6 py-8 lg:block">
      <div class="mb-10 flex items-center gap-4">
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-ink text-white">
          <ChefHat class="h-6 w-6" />
        </div>
        <div>
          <h1 class="text-xl font-display font-bold tracking-tight">SpiceUp</h1>
          <p class="text-[10px] font-bold uppercase tracking-widest text-stone-400">Meal Planner</p>
        </div>
      </div>

      <nav class="space-y-2">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          <component :is="item.icon" class="h-4 w-4" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <div class="lg:pl-64">
      <header class="sticky top-0 z-10 bg-surface-subtle/80 px-6 py-4 backdrop-blur-xl md:px-10">
        <div class="flex items-center justify-between gap-4">
          <div class="min-w-0">
            <p class="font-display text-lg font-bold">{{ auth.user?.name || 'Пользователь' }}</p>
            <p class="truncate text-xs text-stone-500">{{ auth.user?.email }}</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="rounded-full bg-white px-4 py-1.5 text-[10px] font-bold uppercase tracking-widest text-stone-600">
              {{ auth.user?.role }}
            </span>
            <button class="icon-btn bg-white" title="Выйти" @click="logout">
              <LogOut class="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      <main class="mx-auto max-w-7xl px-6 py-8 md:px-10">
        <slot />
      </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="fixed bottom-0 left-0 z-50 flex w-full justify-around bg-white/90 px-2 py-3 backdrop-blur-xl lg:hidden shadow-[0_-10px_40px_rgba(0,0,0,0.03)]">
      <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="mobile-nav-link">
        <component :is="item.icon" class="h-6 w-6 mb-1" />
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import {
  CalendarDays,
  ChefHat,
  ClipboardList,
  Home,
  LogOut,
  NotebookTabs,
  Settings,
  ShoppingCart
} from 'lucide-vue-next';
import { computed } from 'vue';
import { RouterLink, useRouter } from 'vue-router';

import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();

const navItems = computed(() => {
  const items = [
    { to: '/', label: 'Обзор', icon: Home },
    { to: '/inventory', label: 'Продукты', icon: ClipboardList },
    { to: '/recipes', label: 'Рецепты', icon: NotebookTabs },
    { to: '/planner', label: 'Календарь', icon: CalendarDays },
    { to: '/shopping-list', label: 'Покупки', icon: ShoppingCart }
  ];
  if (auth.isAdmin) {
    items.push({ to: '/admin', label: 'Admin', icon: Settings });
  }
  return items;
});

async function logout() {
  await auth.logout();
  router.push({ name: 'login' });
}
</script>
