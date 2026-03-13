<template>
  <div class="max-w-7xl mx-auto animate-in">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="w-2 h-2 rounded-full bg-zinc-500 shadow-[0_0_8px_rgba(113,113,122,0.5)]"></div>
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-text-muted">Fulfillment Archive</span>
        </div>
        <h2 class="text-3xl font-black text-text-primary tracking-tight uppercase">Order History</h2>
        <p class="text-text-secondary text-sm font-medium mt-1">Access completed, cancelled, and historic system protocols.</p>
      </div>
      
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
        <div class="relative min-w-[320px] group">
          <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted group-focus-within:text-primary-500 transition-colors" />
          <input 
            v-model="search" 
            placeholder="Search client, ID or theme..." 
            class="w-full pl-11 pr-4 py-3 bg-surface border border-border rounded-xl text-sm font-medium focus:ring-4 focus:ring-primary-500/10 focus:border-primary-500 outline-none transition-all shadow-sm"
          />
        </div>
        <div class="flex items-center gap-3 px-5 py-3 bg-zinc-100 dark:bg-zinc-800 rounded-xl border border-border">
          <Database class="w-4 h-4 text-text-muted" />
          <span class="text-xs font-black text-text-secondary uppercase tracking-widest">{{ filteredOrders.length }} Records</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="card-triage h-48 p-6 space-y-4 opacity-50 border-dashed">
        <div class="flex justify-between">
          <div class="skeleton h-4 w-20"></div>
          <div class="skeleton h-4 w-24"></div>
        </div>
        <div class="skeleton h-6 w-3/4"></div>
        <div class="skeleton h-4 w-1/2"></div>
        <div class="mt-auto pt-4 border-t border-border flex justify-between">
          <div class="skeleton h-4 w-24"></div>
          <div class="skeleton h-4 w-12"></div>
        </div>
      </div>
    </div>

    <!-- Orders Grid -->
    <div v-else-if="filteredOrders.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div 
        v-for="order in filteredOrders" 
        :key="order.order_id"
        class="history-card transition-all duration-300 hover:grayscale-0 grayscale-[0.2] opacity-90 hover:opacity-100"
      >
        <OrderCard 
          :order="order" 
          @refresh="fetchOrders"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-32 bg-surface rounded-3xl border-2 border-dashed border-border shadow-inner text-text-muted opacity-20">
      <div class="w-24 h-24 bg-bg rounded-full flex items-center justify-center mb-8 border border-border shadow-xl">
        <HistoryIcon class="w-10 h-10" />
      </div>
      <h3 class="text-xl font-black text-text-primary uppercase tracking-widest">Archive Empty</h3>
      <p class="text-text-muted text-sm max-w-xs text-center mt-3 leading-relaxed font-medium">
        No historic protocols found in the database. Completed orders will be archived here.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, History as HistoryIcon, Database } from 'lucide-vue-next';
import api from '../services/api';
import OrderCard from '../components/OrderCard.vue';

const orders = ref<any[]>([]);
const loading = ref(true);
const search = ref('');

const fetchOrders = async () => {
  loading.value = true;
  try {
    const response = await api.get('/historic');
    const rawData = Array.isArray(response.data) ? response.data : [];

    orders.value = rawData
      .filter(order => order && order.order_id)
      .sort((a: any, b: any) => {
        const dateA = new Date(a.selections?.event_date || 0).getTime();
        const dateB = new Date(b.selections?.event_date || 0).getTime();
        return dateB - dateA; 
      });
      
  } catch (err) {
    console.error("Historic API Error:", err);
    orders.value = [];
  } finally {
    loading.value = false;
  }
};

const filteredOrders = computed(() => {
  const term = search.value.toLowerCase();
  return orders.value.filter((o: any) => {
    const name = o.selections?.client_name?.toLowerCase() || '';
    const theme = o.selections?.cake_theme?.toLowerCase() || '';
    const id = o.order_id?.toString() || '';
    return name.includes(term) || theme.includes(term) || id.includes(term);
  });
});

onMounted(fetchOrders);
</script>

<style scoped>
.history-card {
  /* Specific styling for historic items */
}
</style>
