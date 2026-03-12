<template>
  <div class="card-container">
    <div 
      class="card cursor-pointer group" 
      @click="isModalOpen = true"
    >
      <!-- Status indicator bar -->
      <div 
        :class="[
          'h-1 rounded-t-xl -mx-4 -mt-4 mb-4',
          statusColorClass
        ]"
      ></div>

      <div class="flex items-start justify-between mb-3">
        <span class="text-xs font-mono text-zinc-400">#{{ order.order_id }}</span>
        <span 
          :class="['badge', statusBadgeClass]"
        >
          {{ formatStatus(order.order_status_id) }}
        </span>
      </div>

      <h3 class="text-lg font-semibold text-zinc-900 mb-1 truncate">
        {{ order.selections?.client_name || 'No Name Provided' }}
      </h3>

      <p class="text-sm text-zinc-500 mb-4 line-clamp-2">
        <span v-if="order.selections?.order_type === 'cupcakes'">
          🧁 {{ order.selections?.num_cupcakes || '?' }} Cupcakes
        </span>
        <span v-else>
          🎂 {{ order.selections?.tiers }}-tier Cake
        </span>
        <span v-if="order.selections?.cake_theme && order.selections.cake_theme !== 'None'">
          — {{ order.selections.cake_theme }}
        </span>
      </p>
      
      <div class="pt-3 border-t border-zinc-100 mt-auto">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-3 text-zinc-500">
            <span class="flex items-center gap-1">
              📅 {{ formatDate(order.selections?.event_date) }}
            </span>
          </div>
          <div 
            :class="[
              'font-bold',
              order.quoted_price > 0 ? 'text-primary-600' : 'text-zinc-400'
            ]"
          >
            {{ order.quoted_price > 0 ? `$${order.quoted_price}` : 'Price Pending' }}
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
          <div class="modal-content animate-in">
            <button class="close-btn" @click="isModalOpen = false">
              <X class="w-5 h-5" />
            </button>
            
            <header class="modal-header">
              <div class="flex items-center gap-3">
                <div :class="['w-2 h-8 rounded-full', statusColorClass]"></div>
                <div>
                  <h2 class="text-xl font-bold text-zinc-900">Order #{{ order.order_id }}</h2>
                  <p class="text-sm text-zinc-500">Customer: {{ order.customer_id }}</p>
                </div>
              </div>
              <a 
                v-if="fullImagePath" 
                :href="fullImagePath" 
                target="_blank" 
                class="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                <Image class="w-4 h-4" /> View Image
              </a>
            </header>

            <div class="modal-body">
              <!-- Order Overview -->
              <section class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div class="info-item">
                    <span class="info-label">Event</span>
                    <span class="info-value">
                      {{ order.selections?.event_type || 'TBD' }}
                      <span v-if="order.selections?.event_date" class="text-zinc-400"> · {{ formatDate(order.selections.event_date) }}</span>
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Celebrant</span>
                    <span class="info-value">
                      {{ order.selections?.celebrant_name || '—' }}
                      <span v-if="order.selections?.celebrant_age" class="text-zinc-400"> (turning {{ order.selections.celebrant_age }})</span>
                    </span>
                  </div>
                  <div class="info-item col-span-2">
                    <span class="info-label">Delivery</span>
                    <span class="info-value">
                      {{ order.selections?.delivery ? order.selections?.delivery_address : 'Bakery Pickup' }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">AC venue</span>
                    <span class="info-value">{{ order.selections?.has_ac ? '✅ Yes' : '❌ No' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Theme</span>
                    <span class="info-value">
                      {{ order.selections?.cake_theme && order.selections.cake_theme !== 'None' ? order.selections.cake_theme : 'None' }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Frosting</span>
                    <span class="info-value">{{ order.selections?.frosting_flavor || 'TBD' }}</span>
                  </div>
                </div>
              </section>

              <!-- Cake: Tier Details -->
              <template v-if="order.selections?.order_type !== 'cupcakes'">
                <label class="section-label">Tiers</label>
                <div class="tier-list">
                  <div
                    v-for="tier in order.selections?.tier_definitions"
                    :key="tier.tier_index"
                    class="tier-row"
                  >
                    <span class="tier-label">{{ tierLabel(tier.tier_index, order.selections.tier_definitions.length) }}</span>
                    <span class="tier-detail">{{ tier.size }}"</span>
                    <span class="tier-detail">{{ tier.flavor || 'flavor TBD' }}</span>
                    <span class="tier-detail">{{ tier.filling || 'filling TBD' }}</span>
                    <span class="tier-detail">{{ tier.layers ? `${tier.layers} layers` : 'layers TBD' }}</span>
                  </div>
                </div>
              </template>

              <!-- Cupcake: Batch Details -->
              <template v-else>
                <label class="section-label">Cupcake Details</label>
                <div class="cupcake-box">
                  <div class="cupcake-row">
                    <span>🧁 Quantity</span>
                    <strong>{{ order.selections?.num_cupcakes || 'TBD' }}</strong>
                  </div>
                  <div class="cupcake-row">
                    <span>Flavor</span>
                    <strong>{{ order.selections?.cupcake_definition?.cupcake_flavor || 'TBD' }}</strong>
                  </div>
                  <div class="cupcake-row">
                    <span>Filling</span>
                    <strong>{{ order.selections?.cupcake_definition?.cupcake_filling || 'None' }}</strong>
                  </div>
                </div>
              </template>

              <!-- Special Note -->
              <div
                v-if="order.selections?.special_note && order.selections.special_note !== 'None'"
                class="special-note-box"
              >
                <label class="section-label">Special Instructions</label>
                <p class="note-text">"{{ order.selections.special_note }}"</p>
              </div>

              <hr class="divider" />

              <!-- Admin Section -->
              <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div class="field-group">
                    <label>Note to Customer</label>
                    <textarea 
                      v-if="order.order_status_id === 'AWAITING_REVIEW'"
                      v-model="editForm.user_note"
                      placeholder="Pricing/pickup details..."
                      class="input"
                    ></textarea>
                    <div v-else class="read-only-display">{{ order.user_note || 'No note to customer.' }}</div>
                  </div>

                  <div class="field-group">
                    <label>Admin Note</label>
                    <textarea 
                      v-if="order.order_status_id === 'AWAITING_REVIEW'"
                      v-model="editForm.admin_note"
                      placeholder="Staff only..."
                      class="input"
                    ></textarea>
                    <div v-else class="read-only-display">{{ order.admin_note || 'No admin notes.' }}</div>
                  </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                  <div class="field-group">
                    <label>Quoted Price ($)</label>
                    <input 
                      v-if="order.order_status_id === 'AWAITING_REVIEW'"
                      type="number" 
                      v-model.number="editForm.quoted_price"
                      step="0.01"
                      class="input"
                    />
                    <div v-else class="read-only-display price-tag-large">
                      {{ order.quoted_price ? `$${order.quoted_price}` : 'No Price' }}
                    </div>
                  </div>

                  <div v-if="order.order_status_id === 'AWAITING_REVIEW'" class="field-group">
                    <label>Review Status</label>
                    <select v-model="editForm.review_status" class="input">
                      <option value="PENDING">Pending</option>
                      <option value="APPROVED">Approved</option>
                      <option value="REJECTED">Rejected</option>
                    </select>
                  </div>
                </div>
                
                <p v-if="order.order_status_id === 'AWAITING_REVIEW' && !isFormValid" class="text-amber-600 text-sm text-center">
                  ⚠️ Fill both notes, Price > 0, and Status != Pending.
                </p>

                <!-- Deposit Management -->
                <div v-if="order.order_status_id === 'AWAITING_DEPOSIT'" class="deposit-management">
                  <hr class="divider" />
                  <label class="section-label">Deposit Management</label>
                  <div class="flex gap-3 mt-2">
                    <button @click="handleProcessDeposit('ACCEPTED')" class="btn btn-success flex-1">
                      💰 Mark as Paid
                    </button>
                    <button @click="handleProcessDeposit('CANCELLED')" class="btn btn-danger flex-1">
                      🚫 Cancel Order
                    </button>
                  </div>
                </div>

                <!-- Completion Management -->
                <div v-if="order.order_status_id === 'ACCEPTED'" class="deposit-management">
                  <hr class="divider" />
                  <label class="section-label">Order Management</label>
                  <div class="flex gap-3 mt-2">
                    <button @click="handleFinalizeOrder('COMPLETED')" class="btn btn-primary flex-1">
                      ✅ Mark as Completed
                    </button>
                    <button @click="handleFinalizeOrder('CANCELLED')" class="btn btn-danger flex-1">
                      🚫 Cancel Order
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <footer class="modal-footer">
              <button 
                v-if="order.order_status_id === 'AWAITING_REVIEW'" 
                @click="handleSave" 
                class="btn btn-primary flex-1"
                :disabled="!isFormValid"
              >
                Save & Finalize
              </button>
              <button @click="isModalOpen = false" class="btn btn-secondary flex-1">
                Close
              </button>
            </footer>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { X, Image } from 'lucide-vue-next';
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

const isFormValid = computed(() => {
  return editForm.user_note.trim() && 
         editForm.admin_note.trim() && 
         editForm.review_status !== 'PENDING' && 
         editForm.quoted_price > 0;
});

const statusColorClass = computed(() => {
  const status = props.order.order_status_id?.toLowerCase() || '';
  if (status.includes('awaiting_review')) return 'bg-amber-500';
  if (status.includes('awaiting_deposit')) return 'bg-red-500';
  if (status.includes('completed')) return 'bg-emerald-500';
  if (status.includes('cancelled')) return 'bg-zinc-400';
  if (status.includes('accepted') || status.includes('upcoming')) return 'bg-primary-500';
  return 'bg-zinc-400';
});

const statusBadgeClass = computed(() => {
  const status = props.order.order_status_id?.toLowerCase() || '';
  if (status.includes('awaiting_review')) return 'badge-warning';
  if (status.includes('awaiting_deposit')) return 'badge-danger';
  if (status.includes('completed')) return 'badge-success';
  if (status.includes('cancelled')) return 'badge-neutral';
  if (status.includes('accepted') || status.includes('upcoming')) return 'badge-info';
  return 'badge-neutral';
});

const formatStatus = (status: string) => {
  if (!status) return 'Pending';
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
  if (!d) return 'TBD';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const tierLabel = (index: number, total: number) => {
  if (total === 1) return 'Base';
  if (total === 2) return index === 1 ? 'Base' : 'Top';
  const labels: Record<number, string> = { 1: 'Base', 2: 'Middle', 3: 'Top' };
  return labels[index] || `Tier ${index}`;
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
  let confirmMsg = '';
  if (status === 'ACCEPTED') confirmMsg = 'Mark this order as PAID and ACCEPTED?';
  else if (status === 'CANCELLED') confirmMsg = 'Are you sure you want to CANCEL this order?';
    
  if (!confirm(confirmMsg)) return;

  try {
    await api.post('/processDeposit', {
      order_id: props.order.order_id,
      status: status
    });
    emit('refresh');
  } catch (err) {
    console.error(err);
  } finally {
    isModalOpen.value = false;
  }
};

const handleFinalizeOrder = async (status: 'COMPLETED' | 'CANCELLED') => {
  const confirmMsg = status === 'COMPLETED' 
    ? 'Mark this order as COMPLETED?' 
    : 'Are you sure you want to CANCEL this accepted order?';
    
  if (!confirm(confirmMsg)) return;

  try {
    await api.post('/completeOrder', {
      order_id: props.order.order_id,
      status: status
    });
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
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-content {
  background-color: white;
  border-radius: 1rem;
  width: 100%;
  max-width: 36rem;
  max-height: 90vh;
  overflow-y: auto;
}

/* Header */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.25rem;
  border-bottom: 1px solid #f4f4f5;
}

.close-btn {
  padding: 0.25rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
  color: #a1a1aa;
  border: none;
  background: transparent;
  cursor: pointer;
}

.close-btn:hover {
  background-color: #f4f4f5;
  color: #52525b;
}

/* Body */
.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Info Items */
.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  color: #3f3f46;
}

/* Section Label */
.section-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.5rem;
}

/* Tier List */
.tier-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tier-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #fafafa;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  flex-wrap: wrap;
}

.tier-label {
  font-weight: 600;
  color: #3f3f46;
  min-width: 50px;
}

.tier-detail {
  color: #71717a;
}

.tier-detail + .tier-detail::before {
  content: '·';
  margin-right: 0.5rem;
  color: #d4d4d8;
}

/* Cupcake Box */
.cupcake-box {
  background-color: #fafafa;
  border-radius: 0.5rem;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cupcake-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #52525b;
  border-bottom: 1px solid #f4f4f5;
  padding-bottom: 0.5rem;
}

.cupcake-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

/* Special Note */
.special-note-box {
  background-color: #fffbeb;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border-left: 4px solid #fbbf24;
}

.note-text {
  font-size: 0.875rem;
  color: #3f3f46;
  font-style: italic;
  margin: 0;
}

.divider {
  border: none;
  border-top: 1px solid #f4f4f5;
  margin: 1rem 0;
}

/* Field Groups */
.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-group label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #71717a;
  text-transform: uppercase;
}

.read-only-display {
  background-color: #fafafa;
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #52525b;
  min-height: 2.5rem;
}

.price-tag-large {
  font-weight: 700;
  color: #8b5cf6;
  font-size: 1rem;
}

/* Footer */
.modal-footer {
  padding: 1.25rem;
  border-top: 1px solid #f4f4f5;
  display: flex;
  gap: 0.75rem;
  position: sticky;
  bottom: 0;
  background-color: white;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
