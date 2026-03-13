<template>
  <div class="card-container">
    <div 
      class="card-triage group relative flex flex-col h-full cursor-pointer border-l-4" 
      :class="statusBorderClass"
      @click="isModalOpen = true"
    >
      <div class="p-4 flex flex-col h-full">
        <!-- Header: ID & Urgency -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="text-technical text-text-muted font-bold">#{{ order.order_id }}</span>
            <span :class="['badge-status', statusTextClass]">
              {{ formatStatus(order.order_status_id) }}
            </span>
          </div>
          <div :class="['flex items-center gap-1 text-[11px] font-bold uppercase tracking-tight', dateUrgencyClass]">
            <Clock class="w-3 h-3" />
            {{ formatRelativeDate(order.selections?.event_date) }}
          </div>
        </div>

        <!-- Identity: Client Name -->
        <h3 class="text-sm font-bold text-text-primary mb-1 group-hover:text-primary-600 transition-colors truncate">
          {{ order.selections?.client_name || 'Anonymous' }}
        </h3>

        <!-- Product Summary -->
        <div class="flex flex-wrap gap-y-1 gap-x-3 text-[12px] text-text-secondary mb-4 min-h-[1.5rem]">
          <span v-if="order.selections?.order_type === 'cupcakes'" class="flex items-center gap-1.5 font-medium">
            <Package class="w-3.5 h-3.5 text-text-muted" /> {{ order.selections?.num_cupcakes || '?' }} Cupcakes
          </span>
          <span v-else class="flex items-center gap-1.5 font-medium">
            <Cake class="w-3.5 h-3.5 text-text-muted" /> {{ order.selections?.tiers }}-tier Cake
          </span>
          <span v-if="order.selections?.cake_theme && order.selections.cake_theme !== 'None'" class="text-text-muted truncate max-w-[120px]">
            {{ order.selections.cake_theme }}
          </span>
        </div>
        
        <!-- Footer: Date & Price -->
        <div class="mt-auto pt-3 border-t border-border flex items-center justify-between">
          <div class="flex items-center gap-1.5 text-[11px] font-mono text-text-muted">
            <Calendar class="w-3 h-3" />
            {{ formatDate(order.selections?.event_date) }}
          </div>
          <div class="text-technical font-black text-text-primary bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded">
            {{ order.quoted_price > 0 ? `$${order.quoted_price}` : 'TBD' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="isModalOpen" class="fixed inset-0 bg-zinc-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4 lg:p-12" @click.self="isModalOpen = false">
          <div class="bg-surface rounded-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl animate-in border border-border">
            <!-- Modal Header -->
            <header class="px-6 py-5 border-b border-border flex items-center justify-between bg-surface sticky top-0 z-10">
              <div class="flex items-center gap-4 overflow-hidden">
                <div :class="['w-1.5 h-12 rounded-full flex-shrink-0 shadow-lg', statusBgClass]"></div>
                <div class="min-w-0">
                  <div class="flex items-center gap-3 flex-wrap mb-1">
                    <h2 class="text-xl font-black text-text-primary tracking-tight">Order #{{ order.order_id }}</h2>
                    <span :class="['badge-status text-[11px] px-2.5 py-1', statusTextClass]">{{ formatStatus(order.order_status_id) }}</span>
                  </div>
                  <p class="text-[11px] text-text-muted font-mono truncate uppercase tracking-widest">Token: {{ order.customer_id }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 flex-shrink-0">
                <a 
                  v-if="fullImagePath" 
                  :href="fullImagePath" 
                  target="_blank" 
                  class="btn btn-secondary px-4 text-xs shadow-sm"
                >
                  <ImageIcon class="w-4 h-4" /> <span>View Ref</span>
                </a>
                <button @click="isModalOpen = false" class="p-2.5 hover:bg-bg rounded-xl transition-all border border-transparent hover:border-border text-text-muted">
                  <X class="w-6 h-6" />
                </button>
              </div>
            </header>

            <!-- Modal Content (Split Layout) -->
            <div class="flex-1 overflow-y-auto scrollbar-thin">
              <div class="flex flex-col lg:flex-row h-full">
                <!-- Left Column: Specs (Scrollable) -->
                <div class="flex-1 p-6 lg:p-8 space-y-10 border-r border-border bg-bg/30">
                  <!-- Section: Core Context -->
                  <section>
                    <div class="flex items-center gap-2 mb-6">
                      <div class="w-1 h-4 bg-primary-500 rounded-full"></div>
                      <h4 class="text-[11px] font-bold text-text-muted uppercase tracking-[0.2em]">Deployment Context</h4>
                    </div>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-8">
                      <div class="space-y-1.5">
                        <label class="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Target Delivery</label>
                        <div class="flex items-center gap-2 text-text-primary">
                          <Calendar class="w-4 h-4 text-primary-500" />
                          <span class="text-sm font-bold">{{ formatDate(order.selections?.event_date) }}</span>
                        </div>
                      </div>
                      <div class="space-y-1.5">
                        <label class="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Operation Mode</label>
                        <div class="flex items-center gap-2 text-text-primary">
                          <Activity class="w-4 h-4 text-primary-500" />
                          <span class="text-sm font-bold">{{ order.selections?.event_type || 'General' }}</span>
                        </div>
                      </div>
                      <div class="space-y-1.5">
                        <label class="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Climate Control</label>
                        <div class="flex items-center gap-2 text-text-primary">
                          <div :class="['w-2 h-2 rounded-full', order.selections?.has_ac ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-zinc-400']"></div>
                          <span class="text-sm font-bold">{{ order.selections?.has_ac ? 'AC Verified' : 'Ambient' }}</span>
                        </div>
                      </div>
                      <div class="col-span-full space-y-1.5 pt-4 border-t border-border/50">
                        <label class="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Fulfillment Location</label>
                        <p class="text-sm font-medium text-text-primary flex items-start gap-2">
                          <MapPin class="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                          {{ order.selections?.delivery ? order.selections?.delivery_address : 'Local Pickup @ Precious Place HQ' }}
                        </p>
                      </div>
                    </div>
                  </section>

                  <!-- Section: Build Specifications -->
                  <section>
                    <div class="flex items-center gap-2 mb-6">
                      <div class="w-1 h-4 bg-primary-500 rounded-full"></div>
                      <h4 class="text-[11px] font-bold text-text-muted uppercase tracking-[0.2em]">Build Specifications</h4>
                    </div>
                    
                    <div v-if="order.selections?.order_type !== 'cupcakes'" class="space-y-4">
                      <div
                        v-for="tier in order.selections?.tier_definitions"
                        :key="tier.tier_index"
                        class="group/tier p-5 bg-surface rounded-xl border border-border hover:border-primary-200 transition-all shadow-sm flex items-start gap-6"
                      >
                        <div class="w-14 h-14 rounded-xl bg-zinc-100 dark:bg-zinc-800 border border-border flex flex-col items-center justify-center font-mono flex-shrink-0 group-hover/tier:bg-primary-50 dark:group-hover/tier:bg-primary-900/20 transition-colors">
                          <span class="text-[10px] font-bold text-text-muted leading-none mb-1">UNIT</span>
                          <span class="text-lg font-black text-primary-600 leading-none">{{ tier.tier_index }}</span>
                        </div>
                        <div class="flex-1 grid grid-cols-2 md:grid-cols-4 gap-6">
                          <div class="space-y-1">
                            <label class="block text-[9px] text-text-muted font-bold uppercase tracking-widest">Dimension</label>
                            <span class="text-sm font-black font-mono text-text-primary">{{ tier.size }}" Diameter</span>
                          </div>
                          <div class="col-span-2 space-y-1">
                            <label class="block text-[9px] text-text-muted font-bold uppercase tracking-widest">Payload</label>
                            <span class="text-sm font-bold text-text-primary block truncate">{{ tier.flavor || 'Standard' }}</span>
                            <span class="text-[11px] text-text-muted font-medium flex items-center gap-1 italic">
                              <ChevronRight class="w-3 h-3" /> {{ tier.filling || 'No filling' }}
                            </span>
                          </div>
                          <div class="text-right space-y-1">
                            <label class="block text-[9px] text-text-muted font-bold uppercase tracking-widest text-right">Structure</label>
                            <span class="text-sm font-bold text-text-primary">{{ tier.layers || '?' }} Stacked Layers</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div v-else class="bg-surface p-6 rounded-2xl border border-border shadow-sm flex items-center gap-8">
                      <div class="flex flex-col items-center p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-border min-w-[100px]">
                        <span class="text-[10px] font-bold text-text-muted uppercase mb-1">Quantity</span>
                        <span class="text-2xl font-black text-primary-600">{{ order.selections?.num_cupcakes }}</span>
                      </div>
                      <div class="space-y-3 flex-1">
                        <div class="space-y-1">
                          <label class="text-[10px] font-bold text-text-muted uppercase tracking-widest block">Main Component</label>
                          <p class="text-lg font-bold text-text-primary">{{ order.selections?.cupcake_definition?.cupcake_flavor || 'TBD' }}</p>
                        </div>
                        <div class="flex items-center gap-4 text-text-secondary text-sm font-medium italic">
                          <span class="flex items-center gap-1.5"><ChevronRight class="w-3.5 h-3.5 text-primary-500" /> {{ order.selections?.cupcake_definition?.cupcake_filling || 'No internal filling' }}</span>
                        </div>
                      </div>
                    </div>
                  </section>

                  <!-- Section: Special Protocol -->
                  <section v-if="order.selections?.special_note && order.selections.special_note !== 'None'">
                    <div class="flex items-center gap-2 mb-4">
                      <div class="w-1 h-4 bg-amber-500 rounded-full"></div>
                      <h4 class="text-[11px] font-bold text-text-muted uppercase tracking-[0.2em]">Special Protocols</h4>
                    </div>
                    <div class="bg-amber-50/50 dark:bg-amber-900/10 p-5 rounded-xl border border-amber-100 dark:border-amber-900/30 text-sm text-text-primary leading-relaxed font-medium italic">
                      "{{ order.selections.special_note }}"
                    </div>
                  </section>
                </div>

                <!-- Right Column: Admin Actions (Fixed Panel) -->
                <div class="w-full lg:w-96 bg-surface border-l border-border p-6 lg:p-8 flex flex-col shrink-0 overflow-y-auto">
                  <div class="flex items-center gap-2 mb-8">
                    <div class="w-1 h-4 bg-zinc-900 dark:bg-white rounded-full"></div>
                    <h4 class="text-[11px] font-bold text-text-primary uppercase tracking-[0.2em]">Command Center</h4>
                  </div>
                  
                  <!-- Financial Summary Card -->
                  <div class="p-5 bg-zinc-950 text-white rounded-2xl shadow-xl mb-10 overflow-hidden relative group/price">
                    <div class="absolute -right-4 -top-4 w-24 h-24 bg-primary-500/10 rounded-full blur-2xl group-hover/price:bg-primary-500/20 transition-all"></div>
                    <div class="relative z-10 flex flex-col gap-4">
                      <div class="flex justify-between items-start">
                        <span class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Contract Total</span>
                        <div class="text-right">
                          <p class="text-2xl font-black font-mono leading-none tracking-tighter">${{ order.quoted_price || editForm.quoted_price }}</p>
                        </div>
                      </div>
                      <div class="pt-4 border-t border-white/10 flex justify-between items-center">
                        <div class="space-y-0.5">
                          <span class="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">Protocol Deposit (60%)</span>
                          <p class="text-base font-black font-mono text-emerald-400 tracking-tighter leading-none">${{ depositAmount }}</p>
                        </div>
                        <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                          <Activity class="w-4 h-4 text-emerald-400" />
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Workflow State: REVIEW -->
                  <div v-if="order.order_status_id === 'AWAITING_REVIEW'" class="space-y-6 flex-1">
                    <div class="space-y-2">
                      <label class="text-[10px] font-bold text-text-primary uppercase tracking-widest flex items-center gap-2">
                        <MessageSquare class="w-3.5 h-3.5" /> Client Transmission
                      </label>
                      <textarea 
                        v-model="editForm.user_note" 
                        class="w-full h-28 p-4 bg-bg border border-border rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 outline-none transition-all placeholder:text-text-muted/50 font-medium" 
                        placeholder="Price explanation or greeting for the customer..."
                      ></textarea>
                    </div>
                    <div class="space-y-2">
                      <label class="text-[10px] font-bold text-text-muted uppercase tracking-widest flex items-center gap-2">
                        <Lock class="w-3.5 h-3.5" /> Internal Archive
                      </label>
                      <textarea 
                        v-model="editForm.admin_note" 
                        class="w-full h-20 p-4 bg-bg/50 border border-border rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 outline-none transition-all placeholder:text-text-muted/50 font-medium" 
                        placeholder="Technical notes for kitchen staff only..."
                      ></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                      <div class="space-y-2">
                        <label class="text-[10px] font-bold text-text-primary uppercase tracking-widest">Quote Unit ($)</label>
                        <div class="relative">
                          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted font-mono font-bold">$</span>
                          <input type="number" v-model.number="editForm.quoted_price" step="0.01" class="w-full pl-8 pr-4 py-3 bg-bg border border-border rounded-xl text-sm font-black font-mono focus:ring-2 focus:ring-primary-500/20 outline-none" />
                        </div>
                      </div>
                      <div class="space-y-2">
                        <label class="text-[10px] font-bold text-text-primary uppercase tracking-widest">Protocol</label>
                        <select v-model="editForm.review_status" class="w-full p-3 bg-bg border border-border rounded-xl text-sm font-bold focus:ring-2 focus:ring-primary-500/20 outline-none appearance-none cursor-pointer">
                          <option value="PENDING">PENDING</option>
                          <option value="APPROVED">APPROVE</option>
                          <option value="REJECTED">REJECT</option>
                        </select>
                      </div>
                    </div>
                    
                    <button 
                      @click="handleSave" 
                      class="btn btn-primary w-full py-4 text-sm font-black uppercase tracking-[0.15em] shadow-xl shadow-primary-500/20 mt-4 h-auto"
                      :disabled="!isFormValid"
                    >
                      Commit Review
                    </button>
                  </div>

                  <!-- Workflow State: PROGRESSION -->
                  <div v-else class="space-y-8 flex-1 flex flex-col">
                    <div class="p-5 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-border flex-1">
                      <label class="text-[10px] font-bold text-text-muted uppercase tracking-widest block mb-3 border-b border-border pb-2">Last Transmission</label>
                      <p class="text-sm text-text-primary font-medium italic leading-relaxed">{{ order.user_note || 'Standard system prompt issued.' }}</p>
                    </div>

                    <!-- Inline Confirmation Buttons -->
                    <div class="space-y-3 mt-auto">
                      <!-- Deposit Verification -->
                      <template v-if="order.order_status_id === 'AWAITING_DEPOSIT'">
                        <div class="flex flex-col gap-3">
                          <button 
                            v-if="confirmAction !== 'ACCEPTED'"
                            @click="requestConfirm('ACCEPTED')" 
                            class="btn btn-success w-full py-4 text-xs font-black uppercase tracking-widest h-auto"
                          >
                            <CheckCircle class="w-4 h-4" /> Verify Deposit & Start
                          </button>
                          <div v-else class="flex gap-2 animate-in">
                            <button @click="confirmAction = null" class="btn btn-secondary flex-1 py-4 text-xs font-bold h-auto">Cancel</button>
                            <button @click="handleProcessDeposit('ACCEPTED')" class="btn btn-success flex-[2] py-4 text-xs font-black uppercase tracking-widest h-auto">Confirm Verification</button>
                          </div>

                          <button 
                            v-if="confirmAction !== 'CANCEL_DEPOSIT'"
                            @click="requestConfirm('CANCEL_DEPOSIT')" 
                            class="btn btn-danger w-full py-4 text-xs font-black uppercase tracking-widest h-auto"
                          >
                            <Trash2 class="w-4 h-4" /> Abort Order
                          </button>
                          <div v-else class="flex gap-2 animate-in">
                            <button @click="confirmAction = null" class="btn btn-secondary flex-1 py-4 text-xs font-bold h-auto">Back</button>
                            <button @click="handleProcessDeposit('CANCELLED')" class="btn btn-danger flex-[2] py-4 text-xs font-black uppercase tracking-widest h-auto">Confirm Abort</button>
                          </div>
                        </div>
                      </template>

                      <!-- Completion Verification -->
                      <template v-if="order.order_status_id === 'ACCEPTED'">
                        <div class="flex flex-col gap-3">
                          <button 
                            v-if="confirmAction !== 'COMPLETED'"
                            @click="requestConfirm('COMPLETED')" 
                            class="btn btn-primary w-full py-4 text-xs font-black uppercase tracking-widest h-auto"
                          >
                            <CheckSquare class="w-4 h-4" /> Mark as Fulfilled
                          </button>
                          <div v-else class="flex gap-2 animate-in">
                            <button @click="confirmAction = null" class="btn btn-secondary flex-1 py-4 text-xs font-bold h-auto">Back</button>
                            <button @click="handleFinalizeOrder('COMPLETED')" class="btn btn-primary flex-[2] py-4 text-xs font-black uppercase tracking-widest h-auto">Confirm Fulfill</button>
                          </div>

                          <button 
                            v-if="confirmAction !== 'TERMINATE'"
                            @click="requestConfirm('TERMINATE')" 
                            class="btn btn-danger w-full py-4 text-xs font-black uppercase tracking-widest h-auto"
                          >
                            <XCircle class="w-4 h-4" /> Terminate Order
                          </button>
                          <div v-else class="flex gap-2 animate-in">
                            <button @click="confirmAction = null" class="btn btn-secondary flex-1 py-4 text-xs font-bold h-auto">Back</button>
                            <button @click="handleFinalizeOrder('CANCELLED')" class="btn btn-danger flex-[2] py-4 text-xs font-black uppercase tracking-widest h-auto">Confirm Terminate</button>
                          </div>
                        </div>
                      </template>
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
  CheckSquare, 
  Trash2, 
  XCircle,
  Clock,
  ChevronRight,
  MapPin,
  Activity,
  MessageSquare,
  Lock
} from 'lucide-vue-next';
import api from '../services/api';

const props = defineProps<{ order: any }>();
const emit = defineEmits(['refresh']);
const isModalOpen = ref(false);
const confirmAction = ref<string | null>(null);

const editForm = reactive({
  user_note: '',
  admin_note: '',
  quoted_price: 0,
  review_status: 'PENDING'
});

// Financial Calculation
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

// UI System Tokens
const statusBgClass = computed(() => {
  const status = props.order.order_status_id?.toUpperCase() || '';
  if (status.includes('REVIEW')) return 'bg-status-review';
  if (status.includes('DEPOSIT')) return 'bg-status-deposit';
  if (status.includes('COMPLETED')) return 'bg-status-complete';
  if (status.includes('CANCELLED')) return 'bg-status-cancelled';
  if (status.includes('ACCEPTED') || status.includes('UPCOMING')) return 'bg-status-accepted';
  return 'bg-zinc-400';
});

const statusBorderClass = computed(() => {
  const status = props.order.order_status_id?.toUpperCase() || '';
  if (status.includes('REVIEW')) return 'border-status-review';
  if (status.includes('DEPOSIT')) return 'border-status-deposit';
  if (status.includes('COMPLETED')) return 'border-status-complete';
  if (status.includes('CANCELLED')) return 'border-status-cancelled';
  if (status.includes('ACCEPTED') || status.includes('UPCOMING')) return 'border-status-accepted';
  return 'border-zinc-400';
});

const statusTextClass = computed(() => {
  const status = props.order.order_status_id?.toUpperCase() || '';
  if (status.includes('REVIEW')) return 'text-status-review bg-status-review/10';
  if (status.includes('DEPOSIT')) return 'text-status-deposit bg-status-deposit/10';
  if (status.includes('COMPLETED')) return 'text-status-complete bg-status-complete/10';
  if (status.includes('CANCELLED')) return 'text-status-cancelled bg-status-cancelled/10';
  if (status.includes('ACCEPTED') || status.includes('UPCOMING')) return 'text-status-accepted bg-status-accepted/10';
  return 'text-text-muted bg-zinc-100 dark:bg-zinc-800';
});

const dateUrgencyClass = computed(() => {
  if (!props.order.selections?.event_date) return 'text-text-muted';
  const eventDate = new Date(props.order.selections.event_date);
  const today = new Date();
  const diffDays = Math.ceil((eventDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  
  if (diffDays <= 3) return 'text-red-600 dark:text-red-400';
  if (diffDays <= 7) return 'text-amber-600 dark:text-amber-400';
  return 'text-text-muted';
});

// Formatting Logic
const formatStatus = (status: string) => {
  if (!status) return 'INIT';
  return status.replace(/_/g, ' ');
};

const formatDate = (d: string | undefined) => {
  if (!d) return 'TBD';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const formatRelativeDate = (d: string | undefined) => {
  if (!d) return 'Queue';
  const date = new Date(d);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffDays = Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Tomorrow';
  if (diffDays < 0) return 'Expired';
  return `in ${diffDays}d`;
};

// Lifecycle Hooks
watch(isModalOpen, (isOpen) => {
  if (isOpen) {
    editForm.user_note = props.order.user_note || '';
    editForm.admin_note = props.order.admin_note || '';
    editForm.quoted_price = props.order.quoted_price || 0;
    editForm.review_status = props.order.review_status || 'PENDING';
    confirmAction.value = null;
  }
});

// API Operations
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
    isModalOpen.value = false;
  } catch (err) {
    console.error(err);
  }
};

const requestConfirm = (action: string) => {
  confirmAction.value = action;
};

const handleProcessDeposit = async (status: 'ACCEPTED' | 'CANCELLED') => {
  try {
    await api.post('/processDeposit', { order_id: props.order.order_id, status });
    emit('refresh');
    isModalOpen.value = false;
  } catch (err) {
    console.error(err);
  }
};

const handleFinalizeOrder = async (status: 'COMPLETED' | 'CANCELLED') => {
  try {
    await api.post('/completeOrder', { order_id: props.order.order_id, status });
    emit('refresh');
    isModalOpen.value = false;
  } catch (err) {
    console.error(err);
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
