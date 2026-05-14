import { createRouter, createWebHistory } from 'vue-router';

import { useAuthStore } from '../stores/auth';
import AdminView from '../views/AdminView.vue';
import DashboardView from '../views/DashboardView.vue';
import InventoryView from '../views/InventoryView.vue';
import LoginView from '../views/LoginView.vue';
import PlannerView from '../views/PlannerView.vue';
import RecipesView from '../views/RecipesView.vue';
import ShoppingListView from '../views/ShoppingListView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { auth: true } },
    { path: '/inventory', name: 'inventory', component: InventoryView, meta: { auth: true } },
    { path: '/recipes', name: 'recipes', component: RecipesView, meta: { auth: true } },
    { path: '/planner', name: 'planner', component: PlannerView, meta: { auth: true } },
    { path: '/shopping-list', name: 'shopping-list', component: ShoppingListView, meta: { auth: true } },
    { path: '/admin', name: 'admin', component: AdminView, meta: { auth: true, admin: true } }
  ]
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.loaded) {
    await auth.fetchMe();
  }
  if (to.meta.auth && !auth.isAuthenticated) {
    return { name: 'login' };
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' };
  }
  if (to.meta.admin && !auth.isAdmin) {
    return { name: 'dashboard' };
  }
  return true;
});

export default router;
