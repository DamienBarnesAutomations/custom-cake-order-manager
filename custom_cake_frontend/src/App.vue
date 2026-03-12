<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { 
  CalendarDays, 
  ClipboardList, 
  History, 
  MessageCircle,
  Menu,
  X,
  Cake
} from 'lucide-vue-next'

const route = useRoute()
const isSidebarOpen = ref(false)
const isMobile = ref(false)

// Check if mobile on mount
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    isSidebarOpen.value = true
  }
}

if (typeof window !== 'undefined') {
  checkMobile()
  window.addEventListener('resize', checkMobile)
}

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  if (isMobile.value) {
    isSidebarOpen.value = false
  }
}

const navItems = [
  { path: '/upcoming', name: 'Upcoming Orders', icon: CalendarDays },
  { path: '/review', name: 'Review Orders', icon: ClipboardList },
  { path: '/history', name: 'Historic Orders', icon: History },
  { path: '/chat-logs', name: 'Chat Logs', icon: MessageCircle },
]

const getPageTitle = () => {
  const found = navItems.find(item => item.path === route.path)
  return found?.name || 'Dashboard'
}
</script>

<template>
  <div class="min-h-screen bg-zinc-50 flex">
    <!-- Mobile Overlay -->
    <Transition name="fade">
      <div 
        v-if="isMobile && isSidebarOpen" 
        class="fixed inset-0 bg-black/50 z-40 lg:hidden"
        @click="closeSidebar"
      ></div>
    </Transition>

    <!-- Sidebar -->
    <aside 
      :class="[
        'fixed lg:static inset-y-0 left-0 z-50 flex flex-col bg-zinc-900 text-white transition-all duration-300 ease-in-out',
        isSidebarOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full lg:w-20 lg:translate-x-0'
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-5 py-5 border-b border-zinc-800">
        <div class="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center flex-shrink-0">
          <Cake class="w-5 h-5 text-white" />
        </div>
        <Transition name="slide-fade">
          <span v-if="isSidebarOpen" class="font-semibold text-lg whitespace-nowrap">Cake Manager</span>
        </Transition>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-item group"
          :class="{ 'nav-item-active': route.path === item.path }"
          @click="closeSidebar"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <Transition name="slide-fade">
            <span v-if="isSidebarOpen" class="whitespace-nowrap">{{ item.name }}</span>
          </Transition>
        </RouterLink>
      </nav>

      <!-- Footer -->
      <div class="px-3 py-4 border-t border-zinc-800">
        <div v-if="isSidebarOpen" class="text-xs text-zinc-500 px-4">
          <p>Cake Order Manager v1.0</p>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top Header -->
      <header class="bg-white border-b border-zinc-200 px-4 py-3 flex items-center gap-4 sticky top-0 z-30">
        <!-- Mobile Menu Toggle -->
        <button 
          @click="toggleSidebar"
          class="p-2 rounded-lg hover:bg-zinc-100 transition-colors lg:hidden"
        >
          <Menu v-if="!isSidebarOpen" class="w-5 h-5 text-zinc-600" />
          <X v-else class="w-5 h-5 text-zinc-600" />
        </button>

        <!-- Page Title -->
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-semibold text-zinc-900">{{ getPageTitle() }}</h1>
        </div>

        <!-- Spacer -->
        <div class="flex-1"></div>

        <!-- Actions (placeholder for future) -->
        <div class="flex items-center gap-2">
          <span class="text-sm text-zinc-500 hidden sm:inline">Admin</span>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 p-4 lg:p-6 overflow-y-auto">
        <Transition name="fade" mode="out-in">
          <RouterView />
        </Transition>
      </main>
    </div>
  </div>
</template>

<style scoped>
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: #a1a1aa;
  transition: all 0.2s;
}

.nav-item:hover {
  background-color: #3f3f46;
  color: #fafafa;
}

.nav-item-active {
  background-color: rgba(139, 92, 246, 0.1);
  color: #a78bfa;
}

.nav-item-active:hover {
  background-color: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
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

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
