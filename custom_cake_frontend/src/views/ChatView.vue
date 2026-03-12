<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { 
  MessageCircle, 
  Send, 
  ArrowLeft,
  User,
  Bot,
  AlertCircle,
  Clock,
  Search
} from 'lucide-vue-next';
import api from '../services/api';

const userList = ref<any[]>([]);
const messages = ref<any[]>([]);
const selectedUser = ref<any>(null);
const newMessage = ref('');
const loadingUsers = ref(true);
const isSidebarVisible = ref(true);
const messageBox = ref<HTMLElement | null>(null);
const searchUser = ref('');

// Timer reference for polling
let pollTimer: number | null = null;

const fetchUsers = async () => {
  try {
    const response = await api.get('/chatSessions');
    // Sort: TALK_TO_HUMAN first, then by last interaction date
    userList.value = response.data.sort((a: any, b: any) => {
      if (a.current_state === 'TALK_TO_HUMAN' && b.current_state !== 'TALK_TO_HUMAN') return -1;
      if (a.current_state !== 'TALK_TO_HUMAN' && b.current_state === 'TALK_TO_HUMAN') return 1;
      return new Date(b.last_interaction).getTime() - new Date(a.last_interaction).getTime();
    });
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
    
    if (response.data.length !== messages.value.length) {
      messages.value = response.data;
      
      await nextTick();
      if (messageBox.value) {
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
  stopPolling();
  pollTimer = window.setInterval(() => {
    fetchMessages(true);
  }, 3000);
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
  messages.value = [];
  await fetchMessages();
  startPolling();
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
    await fetchMessages();
  } catch (err) {
    console.error('Error sending message:', err);
  }
};

const formatTime = (dateStr: string) => new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

onMounted(() => {
  fetchUsers();
  setInterval(fetchUsers, 10000); 
});

onUnmounted(() => {
  stopPolling();
});
</script>

<template>
  <div class="flex h-[calc(100vh-8rem)] lg:h-[calc(100vh-6rem)] -m-4 lg:-m-6 overflow-hidden">
    <!-- Sidebar - User List -->
    <aside 
      :class="[
        'w-full md:w-80 bg-white border-r border-zinc-200 flex flex-col flex-shrink-0 transition-all duration-300',
        isSidebarVisible ? 'translate-x-0' : '-translate-x-full md:translate-x-0 absolute md:relative h-full z-20',
        !isSidebarVisible && 'hidden md:block'
      ]"
    >
      <div class="p-4 border-b border-zinc-100 space-y-4">
        <h3 class="font-bold text-zinc-900 flex items-center gap-2">
          <MessageCircle class="w-5 h-5 text-primary-600" />
          Conversations
        </h3>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input 
            v-model="searchUser"
            placeholder="Search customers..." 
            class="w-full pl-9 pr-3 py-2 bg-zinc-50 border border-zinc-200 rounded-lg text-xs outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto scrollbar-thin">
        <div 
          v-for="user in userList" 
          :key="user.customer_id" 
          :class="[
            'p-4 border-b border-zinc-50 cursor-pointer transition-all relative',
            selectedUser?.customer_id === user.customer_id 
              ? 'bg-primary-50/50' 
              : 'hover:bg-zinc-50'
          ]"
          @click="handleSelectUser(user)"
        >
          <!-- Active Indicator -->
          <div v-if="selectedUser?.customer_id === user.customer_id" class="absolute left-0 top-0 w-1 h-full bg-primary-600"></div>

          <div class="flex items-start gap-3">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 border', user.current_state === 'TALK_TO_HUMAN' ? 'bg-red-50 border-red-100 shadow-[0_0_10px_rgba(239,68,68,0.2)] animate-pulse' : 'bg-zinc-50 border-zinc-100']">
              <User :class="['w-5 h-5', user.current_state === 'TALK_TO_HUMAN' ? 'text-red-500' : 'text-zinc-400']" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-sm text-zinc-900 truncate">ID: {{ user.customer_id.slice(-8) }}</span>
                <span class="text-[10px] text-zinc-400 flex items-center gap-1 font-mono">
                  <Clock class="w-3 h-3" /> {{ formatTime(user.last_interaction) }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider bg-zinc-100 text-zinc-500">
                  {{ user.source }}
                </span>
                <span 
                  v-if="user.current_state === 'TALK_TO_HUMAN'" 
                  class="text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider bg-red-600 text-white flex items-center gap-1"
                >
                  <AlertCircle class="w-2.5 h-2.5" /> Action Needed
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Chat Window -->
    <main class="flex-1 flex flex-col bg-zinc-50">
      <div v-if="!selectedUser" class="flex-1 flex items-center justify-center p-8 text-center">
        <div class="max-w-xs">
          <div class="w-20 h-20 rounded-2xl bg-white border border-zinc-200 flex items-center justify-center mx-auto mb-6 shadow-sm">
            <MessageCircle class="w-10 h-10 text-zinc-200" />
          </div>
          <h4 class="text-zinc-900 font-bold mb-2">Select a Conversation</h4>
          <p class="text-zinc-500 text-sm">Real-time triage of customer requests from Telegram and WhatsApp.</p>
        </div>
      </div>

      <template v-else>
        <!-- Chat Header -->
        <header class="bg-white border-b border-zinc-200 px-6 py-4 flex items-center gap-4">
          <button class="md:hidden p-2 -ml-2 hover:bg-zinc-100 rounded-lg" @click="isSidebarVisible = true">
            <ArrowLeft class="w-5 h-5 text-zinc-600" />
          </button>
          <div class="flex items-center gap-4 flex-1">
            <div class="w-10 h-10 rounded-full bg-zinc-100 flex items-center justify-center border border-zinc-200">
              <User class="w-5 h-5 text-zinc-400" />
            </div>
            <div>
              <div class="flex items-center gap-3">
                <h3 class="font-bold text-zinc-900">Customer {{ selectedUser.customer_id.slice(-8) }}</h3>
                <span 
                  :class="[
                    'text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest',
                    selectedUser.current_state === 'TALK_TO_HUMAN' 
                      ? 'bg-red-600 text-white' 
                      : 'bg-emerald-100 text-emerald-700'
                  ]"
                >
                  {{ selectedUser.current_state === 'TALK_TO_HUMAN' ? 'Staff Triage' : 'AI Processing' }}
                </span>
              </div>
              <p class="text-[11px] text-zinc-400 font-mono mt-0.5">Source: {{ selectedUser.source }} · ID: {{ selectedUser.customer_id }}</p>
            </div>
          </div>
        </header>
        
        <!-- Message List -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin" ref="messageBox">
          <template v-for="log in messages" :key="log.id">
            <!-- Customer Message -->
            <div v-if="log.customer_message" class="flex justify-start items-end gap-3 group">
              <div class="w-8 h-8 rounded-full bg-white border border-zinc-200 flex items-center justify-center flex-shrink-0 shadow-sm">
                <User class="w-4 h-4 text-zinc-400" />
              </div>
              <div class="max-w-[70%] space-y-1">
                <div class="bg-white border border-zinc-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm">
                  <p class="text-[14px] text-zinc-800 whitespace-pre-wrap leading-relaxed">{{ log.customer_message }}</p>
                </div>
                <span class="text-[10px] text-zinc-400 font-mono px-1 opacity-0 group-hover:opacity-100 transition-opacity">{{ formatTime(log.created_at) }}</span>
              </div>
            </div>

            <!-- Response (System/AI) -->
            <div v-if="log.response" class="flex justify-end items-end gap-3 group">
              <div class="max-w-[70%] space-y-1 text-right">
                <div class="bg-primary-600 text-white rounded-2xl rounded-br-none px-4 py-3 shadow-md shadow-primary-500/10">
                  <p class="text-[14px] whitespace-pre-wrap leading-relaxed">{{ log.response }}</p>
                </div>
                <div class="flex items-center justify-end gap-1.5 px-1">
                   <Bot class="w-3 h-3 text-primary-500" />
                   <span class="text-[10px] text-zinc-400 font-mono">{{ formatTime(log.created_at) }}</span>
                </div>
              </div>
              <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 border border-primary-200 shadow-sm">
                <Bot class="w-4 h-4 text-primary-600" />
              </div>
            </div>
          </template>
        </div>

        <!-- Chat Input -->
        <div class="bg-white border-t border-zinc-200 p-6">
          <div class="flex gap-4 items-center max-w-5xl mx-auto">
            <div class="relative flex-1">
              <input 
                v-model="newMessage" 
                @keyup.enter="handleSendMessage" 
                placeholder="Send a direct message or instructions..." 
                class="w-full pl-4 pr-12 py-3 bg-zinc-50 border border-zinc-200 rounded-xl outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all text-sm"
              />
              <button 
                @click="handleSendMessage" 
                :disabled="!newMessage.trim()" 
                class="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-primary-600 hover:bg-primary-50 rounded-lg disabled:text-zinc-300 disabled:hover:bg-transparent transition-all"
              >
                <Send class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>