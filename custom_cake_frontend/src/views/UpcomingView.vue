<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header Actions -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
        <input 
          v-model="search" 
          placeholder="Search by name or theme..." 
          class="input input-search pl-10"
        />
      </div>
      <div class="flex items-center gap-2">
        <span class="badge badge-info text-sm py-2 px-4">
          {{ filteredOrders.length }} Upcoming
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="spinner mb-4"></div>
      <p class="text-zinc-500">Loading your baking schedule...</p>
    </div>

    <!-- Orders Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
      <OrderCard 
        v-for="order in filteredOrders" 
        :key="order.order_id" 
        :order="order" 
        @refresh="fetchUpcomingOrders"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredOrders.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <Cake class="w-full h-full" />
      </div>
      <h3 class="empty-state-title">No upcoming orders</h3>
      <p class="empty-state-description">
        Enjoy the break! New orders will appear here once they are reviewed.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, Cake } from 'lucide-vue-next';
import api from '../services/api';
import OrderCard from '../components/OrderCard.vue';

const orders = ref<any[]>([]);
const loading = ref(true);
const search = ref('');

const fetchUpcomingOrders = async () => {
  loading.value = true;
  try {
    const response = await api.get('/upcoming');
    const data = Array.isArray(response.data) ? response.data : [];
    orders.value = data.filter(order => order && order.order_id);
  } catch (err) {
    console.error("Error fetching upcoming orders:", err);
    orders.value = [];
  } finally {
    loading.value = false;
  }
};

const filteredOrders = computed(() => {
  const searchTerm = search.value.toLowerCase();
  
  return orders.value
    .filter((o: any) => {
      const name = o.selections?.client_name?.toLowerCase() || '';
      const theme = o.selections?.cake_theme?.toLowerCase() || '';
      return name.includes(searchTerm) || theme.includes(searchTerm);
    })
    .sort((a: any, b: any) => {
      // Primary sort: Date (Soonest first)
      const dateA = new Date(a.selections?.event_date || 0).getTime();
      const dateB = new Date(b.selections?.event_date || 0).getTime();
      return dateA - dateB;
    });
});

onMounted(fetchUpcomingOrders);
</script>

<style scoped>
/* Empty scoped styles - card styling handled in OrderCard */
</style>
