<template>
  <div class="card-container">
    <div 
      class="card-triage group relative overflow-hidden flex flex-col h-full cursor-pointer" 
      @click="isModalOpen = true"
    >
      <!-- Status accent bar -->
      <div 
        :class="['absolute top-0 left-0 w-1 h-full', statusBgClass]"
      ></div>

      <div class="pl-4 pr-4 py-4 flex flex-col h-full">
        <!-- Header: ID & Status -->
        <div class="flex items-center justify-between mb-3">
          <span class="text-technical text-zinc-400">#{{ order.order_id }}</span>
          <span :class="['badge-status', statusTextClass]">
            {{ formatStatus(order.order_status_id) }}
          </span>
        </div>

        <!-- Identity: Client Name -->
        <h3 class="text-base font-bold text-zinc-900 mb-1 group-hover:text-primary-600 transition-colors truncate">
          {{ order.selections?.client_name || 'Anonymous Client' }}
        </h3>

        <!-- Product Summary -->
        <p class="text-[13px] text-zinc-500 mb-4 line-clamp-2 leading-snug">
          <span v-if="order.selections?.order_type === 'cupcakes'" class="flex items-center gap-1.5">
            <Package class="w-3.5 h-3.5" /> {{ order.selections?.num_cupcakes || '?' }} Cupcakes
          </span>
          <span v-else class="flex items-center gap-1.5">
            <Cake class="w-3.5 h-3.5" /> {{ order.selections?.tiers }}-tier Cake
          </span>
          <span v-if="order.selections?.cake_theme && order.selections.cake_theme !== 'None'" class="text-zinc-400">
            · {{ order.selections.cake_theme }}
          </span>
        </p>
        
        <!-- Footer: Date & Price -->
        <div class="mt-auto pt-3 border-t border-zinc-100 flex items-center justify-between">
          <div :class="['flex items-center gap-1.5 text-[13px] font-medium', dateUrgencyClass]">
            <Calendar class="w-3.5 h-3.5" />
            {{ formatDate(order.selections?.event_date) }}
          </div>
          <div class="text-technical font-bold text-zinc-900">
            {{ order.quoted_price > 0 ? `$${order.quoted_price}` : '—' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="isModalOpen" class="fixed inset-0 bg-zinc-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-2 lg:p-8" @click.self="isModalOpen = false">
          <div class="bg-white rounded-xl w-full max-w-4xl max-h-[95vh] overflow-hidden flex flex-col shadow-2xl animate-in">
            <!-- Modal Header -->
            <header class="px-4 lg:px-6 py-4 border-b border-zinc-100 flex items-center justify-between bg-white sticky top-0 z-10">
              <div class="flex items-center gap-3 lg:gap-4 overflow-hidden">
                <div :class="['w-1.5 h-10 rounded-full flex-shrink-0', statusBgClass]"></div>
                <div class="min-w-0">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h2 class="text-lg lg:text-xl font-bold text-zinc-900 truncate">Order #{{ order.order_id }}</h2>
                    <span :class="['badge-status whitespace-nowrap', statusTextClass]">{{ formatStatus(order.order_status_id) }}</span>
                  </div>
                  <p class="text-[10px] lg:text-xs text-zinc-500 font-mono truncate">Customer: {{ order.customer_id }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2 lg:gap-3 flex-shrink-0">
                <a 
                  v-if="fullImagePath" 
                  :href="fullImagePath" 
                  target="_blank" 
                  class="btn btn-secondary py-1.5 px-2 lg:px-4 text-[10px] lg:text-xs"
                >
                  <ImageIcon class="w-3 h-3 lg:w-3.5 lg:h-3.5" /> <span class="hidden sm:inline">Reference</span>
                </a>
                <button @click="isModalOpen = false" class="p-2 hover:bg-zinc-100 rounded-lg transition-colors">
                  <X class="w-5 h-5 text-zinc-400" />
                </button>
              </div>
            </header>

            <!-- Modal Content (Split Layout) -->
            <div class="flex-1 overflow-y-auto p-4 lg:p-6 scrollbar-thin">
              <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
                <!-- Left Column: Specs -->
                <div class="lg:col-span-7 space-y-6 lg:space-y-8">
                  <!-- Section: Core Details -->
                  <section>
                    <h4 class="text-[10px] lg:text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-4">Core Specifications</h4>
                    <div class="grid grid-cols-2 gap-y-4 lg:gap-y-6 gap-x-4">
                      <div class="space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">Event Date</label>
                        <p class="text-sm font-semibold text-zinc-900">{{ formatDate(order.selections?.event_date) }}</p>
                      </div>
                      <div class="space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">Event Type</label>
                        <p class="text-sm font-semibold text-zinc-900">{{ order.selections?.event_type || '—' }}</p>
                      </div>
                      <div class="space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">Celebrant</label>
                        <p class="text-sm font-semibold text-zinc-900">
                          {{ order.selections?.celebrant_name || '—' }}
                          <span v-if="order.selections?.celebrant_age" class="text-zinc-400 font-normal ml-1">({{ order.selections.celebrant_age }} yrs)</span>
                        </p>
                      </div>
                      <div class="space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">AC Venue</label>
                        <p class="text-sm font-semibold text-zinc-900">{{ order.selections?.has_ac ? '✅ Verified' : '❌ Not Verified' }}</p>
                      </div>
                      <div class="col-span-2 space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">Delivery Address</label>
                        <p class="text-sm font-semibold text-zinc-900 break-words">{{ order.selections?.delivery ? order.selections?.delivery_address : '🏠 Pick-up at Bakery' }}</p>
                      </div>
                    </div>
                  </section>

                  <!-- Section: Product Details (Cake Tiers or Cupcakes) -->
                  <section>
                    <h4 class="text-[10px] lg:text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-4">Production Specs</h4>
                    
                    <div v-if="order.selections?.order_type !== 'cupcakes'" class="space-y-3">
                      <div
                        v-for="tier in order.selections?.tier_definitions"
                        :key="tier.tier_index"
                        class="flex items-center gap-3 lg:gap-4 bg-zinc-50 p-3 lg:p-4 rounded-lg border border-zinc-100"
                      >
                        <div class="w-10 h-10 lg:w-12 lg:h-12 rounded bg-white border border-zinc-200 flex items-center justify-center font-mono text-xs font-bold text-zinc-400 flex-shrink-0">
                          T{{ tier.tier_index }}
                        </div>
                        <div class="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-2">
                          <div>
                            <label class="block text-[9px] lg:text-[10px] text-zinc-400 font-bold uppercase">Size</label>
                            <span class="text-technical font-bold text-sm lg:text-base">{{ tier.size }}"</span>
                          </div>
                          <div class="col-span-1 lg:col-span-2">
                            <label class="block text-[9px] lg:text-[10px] text-zinc-400 font-bold uppercase">Flavor/Filling</label>
                            <span class="text-[12px] lg:text-[13px] text-zinc-700 line-clamp-1 block">{{ tier.flavor || 'TBD' }}</span>
                            <span class="text-[10px] text-zinc-400 block">{{ tier.filling || 'No filling' }}</span>
                          </div>
                          <div class="text-right">
                            <label class="block text-[9px] lg:text-[10px] text-zinc-400 font-bold uppercase">Layers</label>
                            <span class="text-technical text-sm lg:text-base">{{ tier.layers || '?' }}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div v-else class="bg-zinc-50 p-4 rounded-lg border border-zinc-100 grid grid-cols-2 gap-4">
                      <div class="space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">Quantity</label>
                        <p class="text-sm font-bold text-zinc-900">{{ order.selections?.num_cupcakes }} Pieces</p>
                      </div>
                      <div class="space-y-1">
                        <label class="text-[10px] lg:text-[11px] font-medium text-zinc-500 uppercase">Flavor</label>
                        <p class="text-sm font-bold text-zinc-900">{{ order.selections?.cupcake_definition?.cupcake_flavor || 'TBD' }}</p>
                      </div>
                    </div>
                  </section>

                  <!-- Section: Special Note -->
                  <section v-if="order.selections?.special_note && order.selections.special_note !== 'None'">
                    <h4 class="text-[10px] lg:text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-2">Instructions</h4>
                    <div class="bg-amber-50/50 p-4 rounded-lg border border-amber-100 text-sm text-amber-900 italic leading-relaxed break-words">
                      "{{ order.selections.special_note }}"
                    </div>
                  </section>
                </div>

                <!-- Right Column: Admin Actions -->
                <div class="lg:col-span-5">
                  <div class="lg:sticky lg:top-0 space-y-6 bg-zinc-50/50 -m-4 lg:m-0 p-4 lg:p-0 rounded-b-xl lg:rounded-none border-t lg:border-t-0 border-zinc-100">
                    <h4 class="text-[10px] lg:text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-4">Admin Dashboard</h4>
                    
                    <!-- Pricing and Deposit Info -->
                    <div class="space-y-4">
                      <div class="flex items-center justify-between p-4 bg-white rounded-lg border border-zinc-200 shadow-sm">
                        <div class="space-y-1">
                          <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Required Deposit (60%)</span>
                          <span class="text-lg lg:text-xl font-mono font-bold text-emerald-600">${{ depositAmount }}</span>
                        </div>
                        <div class="text-right space-y-1">
                          <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Total Quote</span>
                          <span class="text-sm font-bold text-zinc-900">${{ order.quoted_price || editForm.quoted_price }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Form based on status -->
                    <div v-if="order.order_status_id === 'AWAITING_REVIEW'" class="space-y-4">
                      <div class="space-y-2">
                        <label class="text-xs font-bold text-zinc-700">Note to Customer</label>
                        <textarea v-model="editForm.user_note" class="w-full h-24 p-3 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none" placeholder="Explain the pricing to the client..."></textarea>
                      </div>
                      <div class="space-y-2">
                        <label class="text-xs font-bold text-zinc-700 text-zinc-400">Internal Note</label>
                        <textarea v-model="editForm.admin_note" class="w-full h-20 p-3 bg-white/50 border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none" placeholder="Private staff notes..."></textarea>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <div class="space-y-2">
                          <label class="text-xs font-bold text-zinc-700">Set Price ($)</label>
                          <div class="relative">
                            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400">$</span>
                            <input type="number" v-model.number="editForm.quoted_price" step="0.01" class="w-full pl-7 pr-3 py-2.5 bg-white border border-zinc-200 rounded-lg text-sm font-bold focus:ring-2 focus:ring-primary-500 outline-none" />
                          </div>
                        </div>
                        <div class="space-y-2">
                          <label class="text-xs font-bold text-zinc-700">Status</label>
                          <select v-model="editForm.review_status" class="w-full p-2.5 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none">
                            <option value="PENDING">Pending</option>
                            <option value="APPROVED">Approve</option>
                            <option value="REJECTED">Reject</option>
                          </select>
                        </div>
                      </div>
                      <button 
                        @click="handleSave" 
                        class="btn btn-primary w-full py-3.5 shadow-lg shadow-primary-500/20"
                        :disabled="!isFormValid"
                      >
                        Finalize Review
                      </button>
                    </div>

                    <!-- Workflow Actions -->
                    <div v-else class="space-y-4">
                      <div class="space-y-3">
                        <div class="p-3 lg:p-4 bg-white rounded-lg border border-zinc-100">
                          <label class="text-[9px] lg:text-[10px] font-bold text-zinc-400 uppercase block mb-1">Message Sent</label>
                          <p class="text-xs lg:text-sm text-zinc-700 leading-relaxed">{{ order.user_note || 'No message provided.' }}</p>
                        </div>
                      </div>

                      <div v-if="order.order_status_id === 'AWAITING_DEPOSIT'" class="grid grid-cols-1 gap-3">
                        <button @click="handleProcessDeposit('ACCEPTED')" class="btn btn-success w-full py-3">
                          <CheckCircle class="w-4 h-4" /> Verify Deposit & Start
                        </button>
                        <button @click="handleProcessDeposit('CANCELLED')" class="btn btn-danger w-full py-3">
                          <Trash2 class="w-4 h-4" /> Cancel Order
                        </button>
                      </div>

                      <div v-if="order.order_status_id === 'ACCEPTED'" class="grid grid-cols-1 gap-3">
                        <button @click="handleFinalizeOrder('COMPLETED')" class="btn btn-primary w-full py-3">
                          <CheckCircle2 class="w-4 h-4" /> Mark as Finished
                        </button>
                        <button @click="handleFinalizeOrder('CANCELLED')" class="btn btn-danger w-full py-3">
                          <XCircle class="w-4 h-4" /> Terminate Order
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { 
  X, 
  Image as ImageIcon, 
  Calendar, 
  Cake, 
  Package, 
  CheckCircle, 
  CheckCircle2, 
  Trash2, 
  XCircle 
} from 'lucide-vue-next';
import api from '../services/api';

const props = defineProps<{ order: any }>();
const emit = defineEmits(['refresh']);
const isModalOpen = ref(false);

const editForm = reactive({
  user_note: '',
  admin_note: '',
  quoted_price: 0,
  review_status: 'PENDING'
});

// Deposit is 60% of total cost
const depositAmount = computed(() => {
  const total = props.order.quoted_price || editForm.quoted_price || 0;
  return (total * 0.6).toFixed(2);
});

const isFormValid = computed(() => {
  return editForm.user_note.trim() && 
         editForm.admin_note.trim() && 
         editForm.review_status !== 'PENDING' && 
         editForm.quoted_price > 0;
});

const statusBgClass = computed(() => {
  const status = props.order.order_status_id?.toUpperCase() || '';
  if (status.includes('REVIEW')) return 'bg-status-review';
  if (status.includes('DEPOSIT')) return 'bg-status-deposit';
  if (status.includes('COMPLETED')) return 'bg-status-complete';
  if (status.includes('CANCELLED')) return 'bg-status-cancelled';
  if (status.includes('ACCEPTED') || status.includes('UPCOMING')) return 'bg-status-accepted';
  return 'bg-zinc-400';
});

const statusTextClass = computed(() => {
  const status = props.order.order_status_id?.toUpperCase() || '';
  if (status.includes('REVIEW')) return 'text-status-review bg-status-review/10';
  if (status.includes('DEPOSIT')) return 'text-status-deposit bg-status-deposit/10';
  if (status.includes('COMPLETED')) return 'text-status-complete bg-status-complete/10';
  if (status.includes('CANCELLED')) return 'text-status-cancelled bg-status-cancelled/10';
  if (status.includes('ACCEPTED') || status.includes('UPCOMING')) return 'text-status-accepted bg-status-accepted/10';
  return 'text-zinc-500 bg-zinc-100';
});

const dateUrgencyClass = computed(() => {
  if (!props.order.selections?.event_date) return 'text-zinc-500';
  const eventDate = new Date(props.order.selections.event_date);
  const today = new Date();
  const diffDays = Math.ceil((eventDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  
  if (diffDays <= 3) return 'text-red-600 font-bold';
  if (diffDays <= 7) return 'text-amber-600';
  return 'text-zinc-500';
});

const formatStatus = (status: string) => {
  if (!status) return 'PENDING';
  return status.replace(/_/g, ' ');
};

watch(isModalOpen, (isOpen) => {
  if (isOpen) {
    editForm.user_note = props.order.user_note || '';
    editForm.admin_note = props.order.admin_note || '';
    editForm.quoted_price = props.order.quoted_price || 0;
    editForm.review_status = props.order.review_status || 'PENDING';
  }
});

const formatDate = (d: string | undefined) => {
  if (!d) return 'Date Pending';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const handleSave = async () => {
  if (!isFormValid.value) return;
  try {
    await api.post('/performReview', {
      order_id: props.order.order_id,
      user_note: editForm.user_note,
      admin_note: editForm.admin_note,
      quoted_price: editForm.quoted_price,
      review_status: editForm.review_status
    });
    emit('refresh');
  } catch (err) {
    console.error(err);
  } finally {
    isModalOpen.value = false;
  }
};

const handleProcessDeposit = async (status: 'ACCEPTED' | 'CANCELLED') => {
  const confirmMsg = status === 'ACCEPTED' ? 'Accept payment and move to production?' : 'Cancel this order?';
  if (!confirm(confirmMsg)) return;

  try {
    await api.post('/processDeposit', { order_id: props.order.order_id, status });
    emit('refresh');
  } catch (err) {
    console.error(err);
  } finally {
    isModalOpen.value = false;
  }
};

const handleFinalizeOrder = async (status: 'COMPLETED' | 'CANCELLED') => {
  const confirmMsg = status === 'COMPLETED' ? 'Mark as COMPLETED?' : 'Abort this order?';
  if (!confirm(confirmMsg)) return;

  try {
    await api.post('/completeOrder', { order_id: props.order.order_id, status });
    emit('refresh');
  } catch (err) {
    console.error(err);
  } finally {
    isModalOpen.value = false;
  }
};

const IMAGE_BASE_URL = import.meta.env.VITE_IMAGE_BASE_URL || '';
const fullImagePath = computed(() => {
  const path = props.order.selections?.image_reference;
  if (!path || path === 'None') return null;
  if (path.startsWith('http')) return path;
  return `${IMAGE_BASE_URL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
});
</script>

<style scoped>
.card-container {
  height: 100%;
}
</style>