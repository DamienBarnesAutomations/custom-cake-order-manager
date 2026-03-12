<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { 
  CalendarDays, 
  ClipboardList, 
  History, 
  MessageCircle,
  Menu,
  X,
  Cake,
  Activity,
  User
} from 'lucide-vue-next'
import api from './services/api'

const route = useRoute()
const isSidebarOpen = ref(true)
const isMobile = ref(false)
const upcomingCount = ref(0)

const checkMobile = () => {
  const mobile = window.innerWidth < 1024
  isMobile.value = mobile
  if (mobile) {
    isSidebarOpen.value = false
  } else {
    isSidebarOpen.value = true
  }
}

const fetchStats = async () => {
  try {
    const response = await api.get('/upcoming')
    upcomingCount.value = response.data.length
  } catch (err) {
    console.error('Error fetching pulse stats:', err)
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchStats()
  const interval = setInterval(fetchStats, 30000)
  onUnmounted(() => {
    window.removeEventListener('resize', checkMobile)
    clearInterval(interval)
  })
})

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  if (isMobile.value) {
    isSidebarOpen.value = false
  }
}

const navItems = [
  { path: '/upcoming', name: 'Upcoming', icon: CalendarDays },
  { path: '/review', name: 'Review', icon: ClipboardList },
  { path: '/history', name: 'History', icon: History },
  { path: '/chat-logs', name: 'Live Chat', icon: MessageCircle },
]

const getPageTitle = () => {
  const found = navItems.find(item => item.path === route.path)
  return found?.name || 'Dashboard'
}
</script>

<template>
  <div class="min-h-screen bg-zinc-50 flex overflow-hidden">
    <!-- Mobile Overlay -->
    <Transition name="fade">
      <div 
        v-if="isMobile && isSidebarOpen" 
        class="fixed inset-0 bg-zinc-900/60 backdrop-blur-sm z-[60] lg:hidden"
        @click="closeSidebar"
      ></div>
    </Transition>

    <!-- Sidebar -->
    <aside 
      :class="[
        'fixed lg:static inset-y-0 left-0 z-[70] flex flex-col bg-zinc-900 text-white transition-all duration-300 ease-in-out border-r border-white/5 shadow-2xl lg:shadow-none',
        isSidebarOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full lg:w-20 lg:translate-x-0'
      ]"
    >
      <!-- Logo Area -->
      <div class="h-16 flex items-center justify-between px-5 border-b border-white/5 bg-zinc-950/50">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/20">
            <Cake class="w-4 h-4 text-white" />
          </div>
          <Transition name="slide-fade">
            <span v-if="isSidebarOpen" class="font-bold text-sm tracking-tight whitespace-nowrap uppercase">Precious Cake</span>
          </Transition>
        </div>
        
        <!-- Mobile Close Button -->
        <button 
          v-if="isMobile && isSidebarOpen" 
          @click="closeSidebar"
          class="p-2 -mr-2 text-zinc-400 hover:text-white lg:hidden"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto scrollbar-thin text-zinc-400">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item group relative"
          :class="{ 'nav-item-active': route.path === item.path }"
          @click="closeSidebar"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110" />
          <Transition name="slide-fade">
            <span v-if="isSidebarOpen" class="text-sm font-medium whitespace-nowrap">{{ item.name }}</span>
          </Transition>
          
          <!-- Tooltip for collapsed state -->
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
    <div class="flex-1 flex flex-col min-w-0 h-screen relative">
      <!-- Top Header -->
      <header class="h-16 bg-white border-b border-zinc-200 px-4 lg:px-6 flex items-center justify-between sticky top-0 z-40 shadow-sm shadow-zinc-950/5">
        <div class="flex items-center gap-3 lg:gap-4">
          <button 
            @click="toggleSidebar"
            class="p-2.5 -ml-1 rounded-lg bg-zinc-50 lg:bg-transparent hover:bg-zinc-100 transition-all text-zinc-600 border border-zinc-200 lg:border-transparent"
            aria-label="Toggle Menu"
          >
            <Menu v-if="!isSidebarOpen" class="w-5 h-5" />
            <X v-else class="w-5 h-5" />
          </button>
          <h1 class="text-sm lg:text-base font-bold text-zinc-900 uppercase tracking-wide truncate max-w-[120px] sm:max-w-none">
            {{ getPageTitle() }}
          </h1>
        </div>

        <!-- Production Pulse & User -->
        <div class="flex items-center gap-3 lg:gap-6">
          <div class="hidden sm:flex items-center gap-4 border-r border-zinc-100 pr-6">
             <div class="text-right">
                <p class="text-[10px] font-bold text-zinc-400 uppercase tracking-widest leading-none">In Production</p>
                <p class="text-sm font-mono font-bold text-primary-600">{{ upcomingCount }} Orders</p>
             </div>
             <div class="w-10 h-10 rounded-full bg-primary-50 flex items-center justify-center border border-primary-100">
                <Activity class="w-5 h-5 text-primary-500 animate-pulse" />
             </div>
          </div>
          
          <div class="flex items-center gap-2 lg:gap-3">
            <div class="w-8 h-8 rounded-full bg-zinc-100 border border-zinc-200 flex items-center justify-center overflow-hidden">
               <User class="w-4 h-4 text-zinc-400" />
            </div>
            <span class="text-[10px] lg:text-xs font-bold text-zinc-700 hidden md:block">Administrator</span>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-4 lg:p-6 scrollbar-thin">
        <div class="max-w-[1600px] mx-auto">
          <Transition name="fade" mode="out-in">
            <RouterView />
          </Transition>
        </div>
      </main>
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

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #fafafa;
}

.nav-item-active {
  background-color: #7c3aed;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
}

/* Transitions */
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
