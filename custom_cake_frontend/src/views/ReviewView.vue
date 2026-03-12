<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header Actions -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
        <input 
          v-model="search" 
          placeholder="Search pending reviews..." 
          class="input input-search pl-10"
        />
      </div>
      <div class="flex items-center gap-2">
        <span class="badge badge-warning text-sm py-2 px-4">
          {{ filteredOrders.length }} Pending
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="spinner mb-4"></div>
      <p class="text-zinc-500">Loading reviews...</p>
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
        <ClipboardCheck class="w-full h-full" />
      </div>
      <h3 class="empty-state-title">All caught up!</h3>
      <p class="empty-state-description">
        No orders currently need review. 🍰
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
    return name.includes(searchTerm) || theme.includes(searchTerm);
  });
});

onMounted(fetchOrders);
</script>

<style scoped>
/* Review-specific styling */
</style>
