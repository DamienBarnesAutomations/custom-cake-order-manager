<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header Actions -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
        <input 
          v-model="search" 
          placeholder="Search order history by name or ID..." 
          class="input input-search pl-10"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="spinner mb-4"></div>
      <p class="text-zinc-500">Loading archives...</p>
    </div>

    <!-- Orders Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
      <OrderCard 
        v-for="order in filteredOrders" 
        :key="order.order_id" 
        :order="order" 
        @refresh="fetchOrders"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredOrders.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <Archive class="w-full h-full" />
      </div>
      <h3 class="empty-state-title">No historic orders</h3>
      <p class="empty-state-description">
        Completed and cancelled orders will appear here.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, Archive } from 'lucide-vue-next';
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

    // Filter, sanitize, and sort by date descending
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
    // Check selections.client_name and order_id
    const name = o.selections?.client_name?.toLowerCase() || '';
    const id = o.order_id?.toString() || '';
    return name.includes(term) || id.includes(term);
  });
});

onMounted(fetchOrders);
</script>

<style scoped>
/* History-specific styling - grayscale cards */
:deep(.order-card) {
  @apply opacity-80;
}

:deep(.order-card:hover) {
  @apply opacity-100;
}
</style>
