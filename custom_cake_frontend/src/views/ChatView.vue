<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { 
  MessageCircle, 
  Send, 
  ArrowLeft,
  User,
  Bot,
  AlertCircle,
  Clock,
  Search,
  Hash,
  ExternalLink,
  Terminal,
  Activity,
  ChevronRight
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

const filteredUsers = computed(() => {
  if (!searchUser.value) return userList.value;
  const term = searchUser.value.toLowerCase();
  return userList.value.filter(u => 
    u.customer_id.toLowerCase().includes(term) || 
    u.source.toLowerCase().includes(term)
  );
});

const formatTime = (dateStr: string) => new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

onMounted(() => {
  fetchUsers();
  const interval = setInterval(fetchUsers, 10000); 
  onUnmounted(() => {
    clearInterval(interval);
    stopPolling();
  });
});
</script>

<template>
  <div class="flex h-[calc(100vh-10rem)] lg:h-[calc(100vh-8rem)] bg-surface border border-border rounded-2xl overflow-hidden shadow-2xl animate-in relative">
    <!-- Sidebar - Session Triage -->
    <aside 
      :class="[
        'w-full md:w-80 border-r border-border flex flex-col flex-shrink-0 transition-all duration-300 z-30 bg-surface',
        isSidebarVisible ? 'translate-x-0' : '-translate-x-full md:translate-x-0 absolute md:relative h-full',
        !isSidebarVisible && 'hidden md:flex'
      ]"
    >
      <div class="p-5 border-b border-border bg-bg/50">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-black text-xs uppercase tracking-[0.2em] text-text-primary flex items-center gap-2">
            <Activity class="w-4 h-4 text-primary-500" />
            Active Nodes
          </h3>
          <span class="text-[10px] font-mono font-bold text-text-muted bg-bg px-2 py-0.5 rounded border border-border">{{ filteredUsers.length }}</span>
        </div>
        <div class="relative group">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted group-focus-within:text-primary-500 transition-colors" />
          <input 
            v-model="searchUser"
            placeholder="FILTER BY ID OR SOURCE..." 
            class="w-full pl-9 pr-3 py-2.5 bg-bg border border-border rounded-xl text-[10px] font-bold uppercase tracking-widest outline-none focus:ring-2 focus:ring-primary-500/20 transition-all"
          />
        </div>
      </div>

      <div class="flex-1 overflow-y-auto scrollbar-thin bg-bg/10">
        <div v-if="loadingUsers" class="p-8 space-y-4">
          <div v-for="i in 5" :key="i" class="skeleton h-16 w-full opacity-50"></div>
        </div>
        
        <template v-else>
          <div 
            v-for="user in filteredUsers" 
            :key="user.customer_id" 
            :class="[
              'p-4 border-b border-border/50 cursor-pointer transition-all relative group',
              selectedUser?.customer_id === user.customer_id 
                ? 'bg-primary-50/50 dark:bg-primary-900/10' 
                : 'hover:bg-bg'
            ]"
            @click="handleSelectUser(user)"
          >
            <!-- Active Indicator -->
            <div v-if="selectedUser?.customer_id === user.customer_id" class="absolute left-0 top-0 w-1 h-full bg-primary-600 shadow-[0_0_10px_rgba(124,58,237,0.5)]"></div>

            <div class="flex items-center gap-4">
              <div :class="[
                'w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 border-2 transition-transform group-hover:scale-105', 
                user.current_state === 'TALK_TO_HUMAN' 
                  ? 'bg-red-50 border-red-500/20 dark:bg-red-950/20' 
                  : 'bg-surface border-border shadow-sm'
              ]">
                <User v-if="user.current_state !== 'TALK_TO_HUMAN'" :class="['w-5 h-5', selectedUser?.customer_id === user.customer_id ? 'text-primary-600' : 'text-text-muted']" />
                <AlertCircle v-else class="w-5 h-5 text-red-500 animate-pulse" />
              </div>
              
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                  <span class="font-black text-xs text-text-primary tracking-tight font-mono uppercase truncate">
                    ID: {{ user.customer_id.slice(-6) }}
                  </span>
                  <span class="text-[9px] text-text-muted font-mono font-bold flex items-center gap-1 bg-bg px-1.5 py-0.5 rounded">
                    {{ formatTime(user.last_interaction) }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-[9px] px-1.5 py-0.5 rounded font-black uppercase tracking-widest bg-zinc-100 dark:bg-zinc-800 text-text-secondary border border-border/50">
                    {{ user.source }}
                  </span>
                  <span 
                    v-if="user.current_state === 'TALK_TO_HUMAN'" 
                    class="text-[9px] px-1.5 py-0.5 rounded font-black uppercase tracking-widest bg-red-600 text-white shadow-lg shadow-red-500/20"
                  >
                    PRIORITY
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </aside>

    <!-- Chat Interface -->
    <main class="flex-1 flex flex-col bg-bg/30 relative overflow-hidden">
      <!-- Empty State -->
      <div v-if="!selectedUser" class="flex-1 flex items-center justify-center p-12 text-center relative">
        <div class="absolute inset-0 opacity-[0.03] pointer-events-none overflow-hidden flex items-center justify-center">
          <Terminal class="w-[500px] h-[500px]" />
        </div>
        <div class="max-w-sm relative z-10">
          <div class="w-24 h-24 rounded-3xl bg-surface border border-border flex items-center justify-center mx-auto mb-8 shadow-2xl group cursor-default">
            <MessageCircle class="w-10 h-10 text-primary-500 transition-transform group-hover:scale-110 duration-500" />
          </div>
          <h4 class="text-text-primary font-black uppercase tracking-[0.2em] mb-3">Initialize Uplink</h4>
          <p class="text-text-muted text-xs leading-relaxed font-medium">
            Select a neural node from the left to monitor live transmissions and override AI protocols.
          </p>
        </div>
      </div>

      <template v-else>
        <!-- Chat Header -->
        <header class="bg-surface border-b border-border px-6 py-4 flex items-center gap-4 z-20 shadow-sm">
          <button class="md:hidden p-2.5 -ml-2 hover:bg-bg rounded-xl text-text-muted" @click="isSidebarVisible = true">
            <ArrowLeft class="w-5 h-5" />
          </button>
          <div class="flex items-center gap-4 flex-1 overflow-hidden">
            <div class="w-12 h-12 rounded-xl bg-bg border border-border flex items-center justify-center flex-shrink-0 shadow-inner">
              <User class="w-6 h-6 text-primary-500" />
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-3 flex-wrap">
                <h3 class="font-black text-sm text-text-primary tracking-tight truncate uppercase">Terminal #{{ selectedUser.customer_id }}</h3>
                <div 
                  :class="[
                    'text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest flex items-center gap-1.5',
                    selectedUser.current_state === 'TALK_TO_HUMAN' 
                      ? 'bg-red-600 text-white shadow-lg shadow-red-500/20' 
                      : 'bg-primary-600 text-white shadow-lg shadow-primary-500/20'
                  ]"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></div>
                  {{ selectedUser.current_state === 'TALK_TO_HUMAN' ? 'Staff Intervention' : 'AI Logic Flow' }}
                </div>
              </div>
              <p class="text-[10px] text-text-muted font-mono mt-1 flex items-center gap-2">
                <Hash class="w-3 h-3" /> Origin: <span class="text-text-secondary font-bold uppercase tracking-wider">{{ selectedUser.source }}</span>
              </p>
            </div>
          </div>
          <div class="hidden sm:flex gap-2">
             <button class="btn btn-secondary px-3 h-10 text-[10px] font-black uppercase tracking-widest">
               <ExternalLink class="w-3.5 h-3.5" /> Log
             </button>
          </div>
        </header>
        
        <!-- Message Scroller -->
        <div class="flex-1 overflow-y-auto p-6 lg:p-8 space-y-8 scrollbar-thin scroll-smooth bg-[radial-gradient(var(--app-border)_1px,transparent_1px)] [background-size:24px_24px]" ref="messageBox">
          <template v-for="(log, idx) in messages" :key="log.id">
            <!-- Customer Message -->
            <div v-if="log.customer_message" class="flex justify-start items-end gap-4 group">
              <div class="w-9 h-9 rounded-xl bg-surface border border-border flex items-center justify-center flex-shrink-0 shadow-sm group-hover:border-primary-300 transition-colors">
                <User class="w-4 h-4 text-text-muted" />
              </div>
              <div class="max-w-[80%] lg:max-w-[60%] space-y-1.5 animate-in">
                <div class="bg-surface border border-border rounded-2xl rounded-bl-none px-5 py-3.5 shadow-sm text-text-primary">
                  <p class="text-[13px] whitespace-pre-wrap leading-relaxed font-medium">{{ log.customer_message }}</p>
                </div>
                <div class="flex items-center gap-2 px-1">
                  <span class="text-[9px] text-text-muted font-bold font-mono tracking-widest">{{ formatTime(log.created_at) }}</span>
                </div>
              </div>
            </div>

            <!-- Bot/Staff Response -->
            <div v-if="log.response && log.response.trim()" class="flex justify-end items-end gap-4 group">
              <div class="max-w-[80%] lg:max-w-[60%] space-y-1.5 text-right animate-in">
                <div class="bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-2xl rounded-br-none px-5 py-3.5 shadow-xl">
                  <p class="text-[13px] whitespace-pre-wrap leading-relaxed font-bold">{{ log.response }}</p>
                </div>
                <div class="flex items-center justify-end gap-2 px-1">
                   <span class="text-[9px] text-text-muted font-bold font-mono tracking-widest">{{ formatTime(log.created_at) }}</span>
                   <div class="flex items-center gap-1 bg-zinc-100 dark:bg-zinc-800 px-1.5 py-0.5 rounded border border-border">
                      <Bot class="w-2.5 h-2.5 text-primary-500" />
                      <span class="text-[8px] font-black uppercase text-text-muted tracking-tighter">System</span>
                   </div>
                </div>
              </div>
              <div class="w-9 h-9 rounded-xl bg-zinc-900 dark:bg-white flex items-center justify-center flex-shrink-0 shadow-lg transition-transform group-hover:-translate-y-1">
                <Bot class="w-5 h-5 text-white dark:text-zinc-900" />
              </div>
            </div>
          </template>
        </div>

        <!-- Interface Input -->
        <div class="bg-surface border-t border-border p-6 lg:p-8 z-20 shadow-[0_-4px_20px_rgba(0,0,0,0.03)]">
          <div class="flex gap-4 items-center max-w-6xl mx-auto relative group">
            <div class="absolute -left-12 opacity-0 group-focus-within:opacity-100 transition-opacity hidden lg:block">
               <ChevronRight class="w-6 h-6 text-primary-500 animate-pulse" />
            </div>
            <div class="relative flex-1">
              <input 
                v-model="newMessage" 
                @keyup.enter="handleSendMessage" 
                placeholder="EXECUTE MANUAL OVERRIDE COMMAND..." 
                class="w-full pl-6 pr-16 py-4 bg-bg border border-border rounded-2xl outline-none focus:ring-4 focus:ring-primary-500/10 focus:border-primary-500 transition-all text-xs font-black uppercase tracking-widest placeholder:text-text-muted/40"
              />
              <button 
                @click="handleSendMessage" 
                :disabled="!newMessage.trim()" 
                class="absolute right-2.5 top-1/2 -translate-y-1/2 p-3 bg-primary-600 text-white hover:bg-primary-700 rounded-xl disabled:bg-zinc-200 dark:disabled:bg-zinc-800 disabled:text-zinc-400 dark:disabled:text-zinc-600 transition-all shadow-lg shadow-primary-500/20 active:scale-95"
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

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: var(--color-zinc-200);
  border-radius: 9999px;
}
.dark .scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: var(--color-zinc-800);
}
</style>
