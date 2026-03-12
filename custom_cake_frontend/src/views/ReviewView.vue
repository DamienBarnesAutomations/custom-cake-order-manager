<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
      <div>
        <h2 class="text-2xl font-bold text-zinc-900 tracking-tight">Order Triage</h2>
        <p class="text-zinc-500 text-sm mt-1">Review incoming requests, quote prices, and send to customers.</p>
      </div>
      
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
        <div class="relative min-w-[300px]">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input 
            v-model="search" 
            placeholder="Search pending reviews..." 
            class="w-full pl-10 pr-4 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        <div class="flex items-center gap-2 px-4 py-2 bg-amber-50 rounded-lg border border-amber-100">
          <span class="text-xs font-bold text-amber-700 uppercase tracking-wider">{{ filteredOrders.length }} Pending</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24">
      <div class="w-12 h-12 border-4 border-zinc-200 border-t-amber-500 rounded-full animate-spin mb-4"></div>
      <p class="text-zinc-500 font-medium">Fetching orders for review...</p>
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
    <div v-else class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border-2 border-dashed border-zinc-100">
      <div class="w-20 h-20 bg-zinc-50 rounded-full flex items-center justify-center mb-6">
        <ClipboardCheck class="w-10 h-10 text-zinc-300" />
      </div>
      <h3 class="text-lg font-bold text-zinc-900">All caught up!</h3>
      <p class="text-zinc-500 text-sm max-w-xs text-center mt-2 leading-relaxed">
        No orders currently need review. Great job staying on top of your requests! 🍰
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, ClipboardCheck } from 'lucide-vue-next';
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

<style scoped>
/* Review-specific styling */
</style>
