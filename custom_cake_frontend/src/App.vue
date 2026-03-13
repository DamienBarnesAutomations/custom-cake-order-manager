<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { 
  CalendarDays, 
  ClipboardList, 
  History as HistoryIcon, 
  MessageCircle,
  Menu,
  X,
  Cake,
  Activity,
  User,
  Sun,
  Moon,
  ChevronRight
} from 'lucide-vue-next'
import api from './services/api'

const route = useRoute()
const isSidebarOpen = ref(true)
const upcomingCount = ref(0)
const isDark = ref(typeof window !== 'undefined' && localStorage.getItem('cake-theme') === 'dark')

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (typeof window !== 'undefined') {
    localStorage.setItem('cake-theme', isDark.value ? 'dark' : 'light')
  }
}

watch(isDark, (val) => {
  if (typeof document !== 'undefined') {
    if (val) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
}, { immediate: true })

const fetchStats = async () => {
  try {
    const response = await api.get('/upcoming')
    upcomingCount.value = Array.isArray(response.data) ? response.data.length : 0
  } catch (err) {
    console.error('Pulse stats error:', err)
  }
}

onMounted(() => {
  fetchStats()
  const interval = setInterval(fetchStats, 30000)
  onUnmounted(() => clearInterval(interval))
})

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const navItems = [
  { path: '/upcoming', name: 'Schedule', icon: CalendarDays, description: 'Active Production' },
  { path: '/review', name: 'Triage', icon: ClipboardList, description: 'New Requests' },
  { path: '/history', name: 'Archive', icon: HistoryIcon, description: 'Order History' },
  { path: '/chat-logs', name: 'Support', icon: MessageCircle, description: 'Customer Chat' },
]

const getPageTitle = () => {
  const found = navItems.find(item => item.path === route.path)
  return found?.name || 'Dashboard'
}
</script>

<template>
  <div class="min-h-screen bg-bg flex flex-col lg:flex-row overflow-hidden transition-colors duration-500">
    <!-- Sidebar -->
    <aside 
      :class="[
        'hidden lg:flex flex-col bg-zinc-900 text-white transition-all duration-300 ease-in-out border-r border-white/5 shadow-2xl z-50',
        isSidebarOpen ? 'w-64' : 'w-20'
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center gap-3 px-5 border-b border-white/5 bg-zinc-950/50">
        <div class="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/20">
          <Cake class="w-5 h-5 text-white" />
        </div>
        <Transition name="slide-fade">
          <div v-if="isSidebarOpen" class="min-w-0">
            <h1 class="font-bold text-sm tracking-tight uppercase leading-none mb-0.5">Precious Place</h1>
            <p class="text-[10px] text-zinc-500 font-medium uppercase tracking-widest leading-none">Bakery OS</p>
          </div>
        </Transition>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-6 space-y-1 overflow-y-auto scrollbar-thin">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item group"
          :class="{ 'nav-item-active': route.path === item.path }"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110" />
          <Transition name="slide-fade">
            <div v-if="isSidebarOpen" class="flex-1 min-w-0">
              <p class="text-sm font-semibold truncate leading-none mb-1">{{ item.name }}</p>
              <p class="text-[10px] opacity-50 truncate leading-none">{{ item.description }}</p>
            </div>
          </Transition>
          
          <!-- Tooltip for collapsed sidebar -->
          <div v-if="!isSidebarOpen" class="absolute left-16 bg-zinc-800 text-white text-[11px] px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-all translate-x-2 group-hover:translate-x-0 whitespace-nowrap z-50 shadow-xl border border-white/10">
            <p class="font-bold mb-0.5">{{ item.name }}</p>
            <p class="opacity-60 text-[9px] uppercase tracking-wider">{{ item.description }}</p>
          </div>
        </RouterLink>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-4 border-t border-white/5 bg-zinc-950/20">
        <div v-if="isSidebarOpen" class="flex flex-col gap-1.5">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
            <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">System Online</p>
          </div>
          <p class="text-[9px] text-zinc-600 font-mono">Terminal v1.5.0-alpha</p>
        </div>
        <div v-else class="flex justify-center">
           <div class="w-2 h-2 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50"></div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 h-screen relative">
      <!-- Header -->
      <header class="h-16 bg-surface border-b border-border px-4 lg:px-8 flex items-center justify-between sticky top-0 z-40">
        <div class="flex items-center gap-4">
          <button @click="toggleSidebar" class="hidden lg:flex p-2 -ml-2 rounded-lg hover:bg-bg transition-all text-text-secondary">
            <Menu v-if="!isSidebarOpen" class="w-5 h-5" />
            <X v-else class="w-5 h-5" />
          </button>
          
          <div class="flex lg:hidden items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/20">
              <Cake class="w-4 h-4 text-white" />
            </div>
          </div>

          <div class="h-8 w-px bg-border hidden md:block"></div>

          <div class="flex flex-col">
            <div class="flex items-center gap-2">
              <h2 class="text-sm font-bold text-text-primary uppercase tracking-wider">{{ getPageTitle() }}</h2>
              <ChevronRight class="w-3.5 h-3.5 text-text-muted" />
              <span class="text-[10px] font-mono text-text-muted">{{ route.path }}</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3 lg:gap-6">
          <!-- Stats Pulse -->
          <div class="hidden sm:flex items-center gap-3 px-4 py-1.5 bg-bg border border-border rounded-full shadow-sm">
             <div class="flex flex-col items-end">
                <p class="text-[9px] font-bold text-text-muted uppercase tracking-widest leading-none">In Production</p>
                <p class="text-xs font-mono font-bold text-primary-600 leading-tight">{{ upcomingCount }} Orders</p>
             </div>
             <div class="w-8 h-8 rounded-full bg-primary-50 flex items-center justify-center border border-primary-100">
                <Activity class="w-4 h-4 text-primary-500 animate-pulse" />
             </div>
          </div>

          <!-- Theme Toggle -->
          <button 
            @click="toggleTheme" 
            class="p-2.5 rounded-xl hover:bg-bg text-text-secondary transition-all border border-transparent hover:border-border group"
            :title="isDark ? 'Switch to Light' : 'Switch to Dark'"
          >
            <Sun v-if="isDark" class="w-5 h-5 transition-transform group-hover:rotate-45" />
            <Moon v-else class="w-5 h-5 transition-transform group-hover:-rotate-12" />
          </button>

          <!-- User Profile -->
          <div class="flex items-center gap-3 pl-2 border-l border-border">
            <div class="w-9 h-9 rounded-xl bg-zinc-100 dark:bg-zinc-800 border border-border flex items-center justify-center overflow-hidden">
               <User class="w-4 h-4 text-text-muted" />
            </div>
            <div class="hidden md:block">
              <p class="text-xs font-bold text-text-primary leading-none mb-0.5">Administrator</p>
              <p class="text-[10px] text-text-muted font-medium uppercase tracking-tighter">Kitchen Access</p>
            </div>
          </div>
        </div>
      </header>

      <!-- Viewport -->
      <main class="flex-1 overflow-y-auto p-4 lg:p-8 scrollbar-thin">
        <div class="max-w-[1600px] mx-auto">
          <RouterView v-slot="{ Component }">
            <Transition name="fade" mode="out-in">
              <component :is="Component" />
            </Transition>
          </RouterView>
        </div>
      </main>

      <!-- Mobile Nav -->
      <nav class="lg:hidden fixed bottom-0 left-0 right-0 h-16 bg-surface border-t border-border flex items-center justify-around px-2 z-50 shadow-2xl pb-safe">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center justify-center gap-1 w-full h-full transition-all duration-300"
          :class="route.path === item.path ? 'text-primary-600' : 'text-text-muted'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="text-[9px] font-bold uppercase tracking-tighter">{{ item.name }}</span>
          <div v-if="route.path === item.path" class="absolute bottom-0 w-8 h-1 bg-primary-600 rounded-t-full"></div>
        </RouterLink>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  border-radius: 0.75rem;
  color: #a1a1aa;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 0.25rem;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #fafafa;
}

.nav-item-active {
  background-color: var(--app-primary);
  color: #ffffff !important;
  box-shadow: 0 8px 20px -4px rgba(124, 58, 237, 0.4);
}

.nav-item-active p {
  color: #ffffff;
}

.slide-fade-enter-active, 
.slide-fade-leave-active { 
  transition: all 0.2s ease; 
}

.slide-fade-enter-from, 
.slide-fade-leave-to { 
  opacity: 0; 
  transform: translateX(-10px); 
}

.fade-enter-active, 
.fade-leave-active { 
  transition: opacity 0.2s ease; 
}

.fade-enter-from, 
.fade-leave-to { 
  opacity: 0; 
}
</style>
