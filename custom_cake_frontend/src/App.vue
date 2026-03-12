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
  Moon
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
    console.error('Error fetching pulse stats:', err)
  }
}

onMounted(() => {
  fetchStats()
  const interval = setInterval(fetchStats, 30000)
  onUnmounted(() => {
    clearInterval(interval)
  })
})

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const navItems = [
  { path: '/upcoming', name: 'Upcoming', icon: CalendarDays },
  { path: '/review', name: 'Review', icon: ClipboardList },
  { path: '/history', name: 'History', icon: HistoryIcon },
  { path: '/chat-logs', name: 'Live Chat', icon: MessageCircle },
]

const getPageTitle = () => {
  const found = navItems.find(item => item.path === route.path)
  return found?.name || 'Dashboard'
}
</script>

<template>
  <div class="min-h-screen bg-bg flex flex-col lg:flex-row overflow-hidden transition-colors duration-500">
    <!-- Desktop Sidebar -->
    <aside 
      :class="[
        'hidden lg:flex flex-col bg-zinc-900 text-white transition-all duration-300 ease-in-out border-r border-white/5 shadow-2xl',
        isSidebarOpen ? 'w-64' : 'w-20'
      ]"
    >
      <!-- Logo Area -->
      <div class="h-16 flex items-center gap-3 px-5 border-b border-white/5 bg-zinc-950/50">
        <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/20">
          <Cake class="w-4 h-4 text-white" />
        </div>
        <Transition name="slide-fade">
          <span v-if="isSidebarOpen" class="font-bold text-sm tracking-tight whitespace-nowrap uppercase">Precious Cake</span>
        </Transition>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto scrollbar-thin text-zinc-400">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item group relative"
          :class="{ 'nav-item-active': route.path === item.path }"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110" />
          <Transition name="slide-fade">
            <span v-if="isSidebarOpen" class="text-sm font-medium whitespace-nowrap">{{ item.name }}</span>
          </Transition>
          <div v-if="!isSidebarOpen" class="absolute left-14 bg-zinc-800 text-white text-[11px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
            {{ item.name }}
          </div>
        </RouterLink>
      </nav>

      <!-- Sidebar Footer -->
      <div class="p-4 border-t border-white/5 bg-zinc-950/20">
        <div v-if="isSidebarOpen" class="flex flex-col gap-1">
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Admin Terminal</p>
          <p class="text-[10px] text-zinc-600 font-mono">Build v1.4.2-prod</p>
        </div>
        <div v-else class="flex justify-center">
           <Activity class="w-4 h-4 text-zinc-700" />
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 h-screen relative pb-16 lg:pb-0">
      <header class="h-16 bg-surface border-b border-border px-4 lg:px-6 flex items-center justify-between sticky top-0 z-40 shadow-sm shadow-zinc-950/5">
        <div class="flex items-center gap-3 lg:gap-4">
          <button @click="toggleSidebar" class="hidden lg:flex p-2 -ml-1 rounded-lg hover:bg-bg transition-all text-text-secondary border border-transparent">
            <Menu v-if="!isSidebarOpen" class="w-5 h-5" />
            <X v-else class="w-5 h-5" />
          </button>
          <div class="flex lg:hidden items-center gap-2 mr-2">
            <div class="w-7 h-7 rounded bg-primary-600 flex items-center justify-center">
              <Cake class="w-3.5 h-3.5 text-white" />
            </div>
          </div>
          <h1 class="text-sm lg:text-base font-bold text-text-primary uppercase tracking-wide truncate max-w-[150px] sm:max-w-none">{{ getPageTitle() }}</h1>
        </div>

        <div class="flex items-center gap-3 lg:gap-6">
          <button 
            @click="toggleTheme" 
            class="p-2 rounded-lg hover:bg-bg text-text-secondary transition-all"
            :title="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          >
            <Sun v-if="isDark" class="w-5 h-5" />
            <Moon v-else class="w-5 h-5" />
          </button>

          <div class="flex items-center gap-2 lg:gap-4 lg:border-r border-border lg:pr-6">
             <div class="text-right hidden sm:block">
                <p class="text-[9px] lg:text-[10px] font-bold text-text-muted uppercase tracking-widest leading-none">In Production</p>
                <p class="text-xs lg:text-sm font-mono font-bold text-primary-600">{{ upcomingCount }} Orders</p>
             </div>
             <div class="w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-primary-50 flex items-center justify-center border border-primary-100">
                <Activity class="w-4 h-4 lg:w-5 lg:h-5 text-primary-500 animate-pulse" />
             </div>
          </div>
          <div class="flex items-center gap-2 lg:gap-3">
            <div class="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-bg border border-border flex items-center justify-center overflow-hidden">
               <User class="w-3.5 h-3.5 lg:w-4 lg:h-4 text-text-muted" />
            </div>
            <span class="text-[10px] lg:text-xs font-bold text-text-secondary hidden md:block">Admin</span>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 lg:p-6 scrollbar-thin text-text-primary">
        <div class="max-w-[1600px] mx-auto">
          <Transition name="fade" mode="out-in">
            <RouterView />
          </Transition>
        </div>
      </main>

      <!-- Mobile Bottom Navigation -->
      <nav class="lg:hidden fixed bottom-0 left-0 right-0 h-16 bg-surface border-t border-border flex items-center justify-around px-2 z-50 shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="flex flex-col items-center justify-center gap-1 w-full h-full text-text-muted transition-colors"
          active-class="!text-primary-600"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="text-[10px] font-bold uppercase tracking-tighter">{{ item.name }}</span>
        </RouterLink>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.875rem;
  border-radius: 0.5rem;
  color: #a1a1aa;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.nav-item:hover { background-color: rgba(255, 255, 255, 0.05); color: #fafafa; }
.nav-item-active { background-color: #7c3aed; color: #ffffff !important; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25); }
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.2s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateX(-10px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>