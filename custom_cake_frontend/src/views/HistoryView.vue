<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
      <div>
        <h2 class="text-2xl font-bold text-zinc-900 tracking-tight">Order Archive</h2>
        <p class="text-zinc-500 text-sm mt-1">Access completed, cancelled, and historic order data.</p>
      </div>
      
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
        <div class="relative min-w-[300px]">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input 
            v-model="search" 
            placeholder="Search by client, ID or theme..." 
            class="w-full pl-10 pr-4 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        <div class="flex items-center gap-2 px-4 py-2 bg-zinc-100 rounded-lg border border-zinc-200">
          <span class="text-xs font-bold text-zinc-500 uppercase tracking-wider">{{ filteredOrders.length }} Records</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24">
      <div class="w-12 h-12 border-4 border-zinc-200 border-t-zinc-400 rounded-full animate-spin mb-4"></div>
      <p class="text-zinc-500 font-medium">Accessing the archives...</p>
    </div>

    <!-- Orders Grid -->
    <div v-else-if="filteredOrders.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div 
        v-for="order in filteredOrders" 
        :key="order.order_id"
        class="history-card transition-opacity duration-300"
      >
        <OrderCard 
          :order="order" 
          @refresh="fetchOrders"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border-2 border-dashed border-zinc-100">
      <div class="w-20 h-20 bg-zinc-50 rounded-full flex items-center justify-center mb-6">
        <HistoryIcon class="w-10 h-10 text-zinc-300" />
      </div>
      <h3 class="text-lg font-bold text-zinc-900">No historic orders</h3>
      <p class="text-zinc-500 text-sm max-w-xs text-center mt-2 leading-relaxed">
        Your order history is currently empty. Completed and cancelled orders will be archived here.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, History as HistoryIcon } from 'lucide-vue-next';
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
  opacity: 0.85;
}
.history-card:hover {
  opacity: 1;
}
</style>
