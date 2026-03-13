<template>
  <div class="max-w-7xl mx-auto animate-in">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div>
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-text-muted">Inbound Triage</span>
        </div>
        <h2 class="text-3xl font-black text-text-primary tracking-tight uppercase">Order Triage</h2>
        <p class="text-text-secondary text-sm font-medium mt-1">Review incoming requests, quote prices, and commit to schedule.</p>
      </div>
      
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
        <div class="relative min-w-[320px] group">
          <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted group-focus-within:text-amber-500 transition-colors" />
          <input 
            v-model="search" 
            placeholder="Search pending reviews..." 
            class="w-full pl-11 pr-4 py-3 bg-surface border border-border rounded-xl text-sm font-medium focus:ring-4 focus:ring-amber-500/10 focus:border-amber-500 outline-none transition-all shadow-sm"
          />
        </div>
        <div class="flex items-center gap-3 px-5 py-3 bg-amber-50 dark:bg-amber-900/10 rounded-xl border border-amber-100 dark:border-amber-900/30">
          <ClipboardList class="w-4 h-4 text-amber-600" />
          <span class="text-xs font-black text-amber-700 dark:text-amber-400 uppercase tracking-widest">{{ filteredOrders.length }} Pending</span>
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
      <OrderCard 
        v-for="order in filteredOrders" 
        :key="order.order_id" 
        :order="order" 
        @refresh="fetchOrders"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-32 bg-surface rounded-3xl border-2 border-dashed border-border shadow-inner">
      <div class="w-24 h-24 bg-bg rounded-full flex items-center justify-center mb-8 border border-border shadow-xl text-text-muted opacity-20">
        <ClipboardCheck class="w-10 h-10" />
      </div>
      <h3 class="text-xl font-black text-text-primary uppercase tracking-widest">All Clear</h3>
      <p class="text-text-muted text-sm max-w-xs text-center mt-3 leading-relaxed font-medium">
        No orders currently require protocol review. Your triage queue is empty.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, ClipboardList, ClipboardCheck } from 'lucide-vue-next';
import api from '../services/api';
import OrderCard from '../components/OrderCard.vue';

const orders = ref<any[]>([]);
const loading = ref(true);
const search = ref('');

const fetchOrders = async () => {
  loading.value = true;
  try {
    const response = await api.get('/review');
    const rawData = Array.isArray(response.data) ? response.data : [];
    orders.value = rawData.filter(order => order && Object.keys(order).length > 0 && order.order_id);
  } catch (err) {
    console.error("API Error:", err);
    orders.value = [];
  } finally {
    loading.value = false;
  }
};

const filteredOrders = computed(() => {
  const searchTerm = search.value.toLowerCase();
  return orders.value.filter((o: any) => {
    const name = o.selections?.client_name?.toLowerCase() || '';
    const theme = o.selections?.cake_theme?.toLowerCase() || '';
    const id = o.order_id?.toString() || '';
    return name.includes(searchTerm) || theme.includes(searchTerm) || id.includes(searchTerm);
  });
});

onMounted(fetchOrders);
</script>
