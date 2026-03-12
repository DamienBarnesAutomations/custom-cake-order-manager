<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { 
  MessageCircle, 
  Send, 
  ArrowLeft,
  User,
  Bot,
  AlertCircle
} from 'lucide-vue-next';
import api from '../services/api';

const userList = ref<any[]>([]);
const messages = ref<any[]>([]);
const selectedUser = ref<any>(null);
const newMessage = ref('');
const loadingUsers = ref(true);
const isSidebarVisible = ref(true);
const messageBox = ref<HTMLElement | null>(null);

// Timer reference for polling
let pollTimer: number | null = null;

const fetchUsers = async () => {
  try {
    const response = await api.get('/chatSessions');
    userList.value = response.data;
  } catch (err) { 
    console.error('Error fetching users:', err); 
  } finally { 
    loadingUsers.value = false; 
  }
};

const fetchMessages = async (isAutoPoll = false) => {
  if (!selectedUser.value) return;
  
  try {
    const response = await api.get('/chatLogs', { 
      params: { customer_id: selectedUser.value.customer_id } 
    });
    
    // Only update and scroll if the message count actually changed
    if (response.data.length !== messages.value.length) {
      messages.value = response.data;
      
      await nextTick();
      if (messageBox.value) {
        // Smart Scroll: only scroll to bottom if user is close to it
        const threshold = 150; 
        const isNearBottom = messageBox.value.scrollHeight - messageBox.value.scrollTop - messageBox.value.clientHeight < threshold;
        
        if (isNearBottom || !isAutoPoll) {
          messageBox.value.scrollTop = messageBox.value.scrollHeight;
        }
      }
    }
  } catch (err) {
    console.error('Error fetching messages:', err);
  }
};

const startPolling = () => {
  stopPolling(); // Clear existing
  pollTimer = window.setInterval(() => {
    fetchMessages(true);
  }, 3000); // Poll every 3 seconds
};

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
};

const handleSelectUser = async (user: any) => {
  selectedUser.value = user;
  isSidebarVisible.value = false;
  messages.value = []; // Clear current view while loading
  await fetchMessages();
  startPolling(); // Start polling for the new user
};

const handleSendMessage = async () => {
  if (!newMessage.value.trim() || !selectedUser.value) return;
  try {
    await api.post('/sendChatMessage', {
      customer_id: selectedUser.value.customer_id,
      message: newMessage.value,
      source: selectedUser.value.source
    });
    newMessage.value = '';
    await fetchMessages(); // Immediate refresh after sending
  } catch (err) {
    console.error('Error sending message:', err);
  }
};

const formatTime = (dateStr: string) => new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

onMounted(() => {
  fetchUsers();
  // Optional: Poll the user list too if you want to see new incoming chats
  setInterval(fetchUsers, 10000); 
});

onUnmounted(() => {
  stopPolling();
});
</script>

<template>
  <div class="flex h-[calc(100vh-8rem)] lg:h-[calc(100vh-6rem)] -m-4 lg:-m-6">
    <!-- Sidebar - User List -->
    <aside 
      :class="[
        'w-full md:w-72 bg-white border-r border-zinc-200 flex flex-col flex-shrink-0 transition-all duration-300',
        isSidebarVisible ? 'translate-x-0' : '-translate-x-full md:translate-x-0 absolute md:relative h-full z-20',
        !isSidebarVisible && 'hidden md:block'
      ]"
    >
      <div class="p-4 border-b border-zinc-100">
        <h3 class="font-semibold text-zinc-900 flex items-center gap-2">
          <MessageCircle class="w-5 h-5 text-primary-600" />
          Conversations
        </h3>
      </div>

      <div class="flex-1 overflow-y-auto scrollbar-thin">
        <div 
          v-for="user in userList" 
          :key="user.customer_id" 
          :class="[
            'p-4 border-b border-zinc-50 cursor-pointer transition-colors',
            selectedUser?.customer_id === user.customer_id 
              ? 'bg-primary-50 border-l-4 border-l-primary-500' 
              : 'hover:bg-zinc-50'
          ]"
          @click="handleSelectUser(user)"
        >
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-full bg-zinc-100 flex items-center justify-center flex-shrink-0">
              <User class="w-5 h-5 text-zinc-400" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <span class="font-medium text-zinc-900 truncate">{{ user.customer_id.slice(-8) }}</span>
                <span class="text-xs text-zinc-400">{{ formatTime(user.last_interaction) }}</span>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-xs px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-600">
                  {{ user.source }}
                </span>
                <span 
                  v-if="user.current_state === 'TALK_TO_HUMAN'" 
                  class="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 flex items-center gap-1"
                >
                  <AlertCircle class="w-3 h-3" /> Needs Human
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Chat Window -->
    <main 
      :class="[
        'flex-1 flex flex-col bg-zinc-50 transition-all duration-300',
        !isSidebarVisible ? 'translate-x-0' : 'translate-x-0'
      ]"
    >
      <!-- No Selection State -->
      <div v-if="!selectedUser" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="w-16 h-16 rounded-full bg-zinc-100 flex items-center justify-center mx-auto mb-4">
            <MessageCircle class="w-8 h-8 text-zinc-300" />
          </div>
          <p class="text-zinc-500">Select a conversation to start</p>
        </div>
      </div>

      <!-- Chat Content -->
      <template v-else>
        <!-- Chat Header -->
        <header class="bg-white border-b border-zinc-200 px-4 py-3 flex items-center gap-3">
          <button 
            class="md:hidden p-1 hover:bg-zinc-100 rounded-lg"
            @click="isSidebarVisible = true"
          >
            <ArrowLeft class="w-5 h-5 text-zinc-600" />
          </button>
          <div class="flex items-center gap-3 flex-1">
            <div class="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center">
              <User class="w-4 h-4 text-zinc-400" />
            </div>
            <div>
              <h3 class="font-medium text-zinc-900">Customer: {{ selectedUser.customer_id.slice(-8) }}</h3>
              <span 
                :class="[
                  'text-xs px-2 py-0.5 rounded-full',
                  selectedUser.current_state === 'TALK_TO_HUMAN' 
                    ? 'bg-red-100 text-red-700' 
                    : 'bg-green-100 text-green-700'
                ]"
              >
                {{ selectedUser.current_state === 'TALK_TO_HUMAN' ? 'Needs Human' : 'Bot Active' }}
              </span>
            </div>
          </div>
        </header>
        
        <!-- Message List -->
        <div 
          class="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin"
          ref="messageBox"
        >
          <template v-for="log in messages" :key="log.id">
            <!-- Customer Message -->
            <div 
              v-if="log.customer_message && log.customer_message.trim() !== ''" 
              class="flex justify-start"
            >
              <div class="max-w-[75%]">
                <div class="flex items-center gap-2 mb-1">
                  <User class="w-3 h-3 text-zinc-400" />
                  <span class="text-xs text-zinc-400">Customer</span>
                </div>
                <div class="bg-white border border-zinc-200 rounded-2xl rounded-tl-md px-4 py-2 shadow-sm">
                  <p class="text-sm text-zinc-700 whitespace-pre-wrap">{{ log.customer_message }}</p>
                </div>
                <span class="text-xs text-zinc-400 mt-1 block">{{ formatTime(log.created_at) }}</span>
              </div>
            </div>

            <!-- System Response -->
            <div 
              v-if="log.response && log.response.trim() !== ''" 
              class="flex justify-end"
            >
              <div class="max-w-[75%]">
                <div class="flex items-center justify-end gap-2 mb-1">
                  <Bot class="w-3 h-3 text-primary-500" />
                  <span class="text-xs text-primary-500">System</span>
                </div>
                <div class="bg-primary-600 text-white rounded-2xl rounded-tr-md px-4 py-2 shadow-sm">
                  <p class="text-sm whitespace-pre-wrap">{{ log.response }}</p>
                </div>
                <span class="text-xs text-zinc-400 mt-1 block text-right">{{ formatTime(log.created_at) }}</span>
              </div>
            </div>
          </template>
        </div>

        <!-- Chat Input -->
        <div class="bg-white border-t border-zinc-200 p-4">
          <div class="flex gap-3">
            <input 
              v-model="newMessage" 
              @keyup.enter="handleSendMessage" 
              placeholder="Type a message..." 
              class="input flex-1"
            />
            <button 
              @click="handleSendMessage" 
              :disabled="!newMessage.trim()" 
              class="btn btn-primary px-4"
            >
              <Send class="w-4 h-4" />
              <span class="hidden sm:inline">Send</span>
            </button>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
/* Additional styles if needed - most styling is now in Tailwind classes */
</style>
