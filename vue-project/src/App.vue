<script setup>
import { RouterView } from 'vue-router'
import PlayerBar from './components/PlayerBar.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import { ref, onMounted } from 'vue'
import { Sun, Moon, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const isDarkMode = ref(false)
const isSidebarCollapsed = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  const theme = isDarkMode.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  // Check local storage or system preference
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
    document.documentElement.setAttribute('data-theme', savedTheme)
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    isDarkMode.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<template>
  <div class="app-layout">
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <button class="collapse-btn" @click="toggleSidebar" :title="isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'">
        <ChevronRight v-if="isSidebarCollapsed" size="20" />
        <ChevronLeft v-else size="20" />
      </button>

      <div class="logo">
        <img src="/logo.svg" alt="Music Logo" class="brand-icon" />
        <span class="brand-text" v-show="!isSidebarCollapsed">MuseFlow</span>
      </div>
      <nav>
        <router-link to="/" class="nav-item active" :title="isSidebarCollapsed ? $t('sidebar.listenNow') : ''">
          <span class="nav-text">{{ $t('sidebar.listenNow') }}</span>
        </router-link>
        <a href="#" class="nav-item" :title="isSidebarCollapsed ? $t('sidebar.browse') : ''">
          <span class="nav-text">{{ $t('sidebar.browse') }}</span>
        </a>
        <a href="#" class="nav-item" :title="isSidebarCollapsed ? $t('sidebar.radio') : ''">
          <span class="nav-text">{{ $t('sidebar.radio') }}</span>
        </a>
      </nav>
      
      <div class="section-title" v-show="!isSidebarCollapsed">{{ $t('sidebar.library') }}</div>
      <nav>
        <a href="#" class="nav-item" :title="isSidebarCollapsed ? $t('sidebar.recentlyAdded') : ''">
           <span class="nav-text">{{ $t('sidebar.recentlyAdded') }}</span>
        </a>
        <a href="#" class="nav-item" :title="isSidebarCollapsed ? $t('sidebar.artists') : ''">
           <span class="nav-text">{{ $t('sidebar.artists') }}</span>
        </a>
        <a href="#" class="nav-item" :title="isSidebarCollapsed ? $t('sidebar.albums') : ''">
           <span class="nav-text">{{ $t('sidebar.albums') }}</span>
        </a>
        <a href="#" class="nav-item" :title="isSidebarCollapsed ? $t('sidebar.songs') : ''">
           <span class="nav-text">{{ $t('sidebar.songs') }}</span>
        </a>
      </nav>

      <div class="theme-toggle-container">
        <button class="theme-toggle-btn" @click="toggleTheme" :title="isDarkMode ? $t('sidebar.switchToLight') : $t('sidebar.switchToDark')">
          <Sun v-if="isDarkMode" size="20" />
          <Moon v-else size="20" />
          <span v-show="!isSidebarCollapsed">{{ isDarkMode ? $t('sidebar.lightMode') : $t('sidebar.darkMode') }}</span>
        </button>
        <div style="margin-top: 8px;">
           <LanguageSwitcher :collapsed="isSidebarCollapsed" />
        </div>
      </div>
    </div>

    <main class="main-content" :class="{ expanded: isSidebarCollapsed }">
      <RouterView />
    </main>

    <PlayerBar />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  background: var(--color-background-secondary);
  padding: 32px;
  position: fixed;
  height: 100vh;
  border-right: 1px solid var(--color-border);
  transition: transform 0.3s ease;
  z-index: 100;
  left: 0;
  top: 0;
}

.sidebar.collapsed {
  transform: translateX(-100%);
}

.collapse-btn {
  position: absolute;
  top: 50%;
  left: 100%; /* Align exactly to the right edge */
  margin-left: -1px; /* Overlap the border slightly to look seamless */
  transform: translateY(-50%);
  width: 20px;
  height: 40px;
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  border-left: 1px solid var(--color-background-secondary); /* Use background color to hide the left border line */
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text-secondary);
  box-shadow: 4px 0 8px rgba(0,0,0,0.05);
  z-index: 101;
  transition: all 0.3s ease;
}

/* When collapsed, the sidebar is hidden, so we need the button to look like a tab on the left edge of screen */
.sidebar.collapsed .collapse-btn {
  border-left: 1px solid var(--color-border); /* Restore border when detached from visible sidebar */
  background: var(--color-background-secondary);
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}

.collapse-btn:hover {
  color: var(--color-accent);
  background: var(--color-background); /* Lighten slightly on hover */
}

.logo {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  letter-spacing: -0.5px;
  overflow: hidden;
  white-space: nowrap;
}

.sidebar.collapsed .logo {
  justify-content: center;
}

.brand-icon {
  width: 40px;
  height: 40px;
  display: block;
  flex-shrink: 0;
}


.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  margin-top: 32px;
  margin-bottom: 12px;
  padding-left: 12px;
}

.nav-item {
  display: block;
  padding: 8px 12px;
  border-radius: 6px;
  color: var(--color-text);
  font-size: 15px;
  margin-bottom: 2px;
  transition: background 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 36px; /* Fixed height for consistent alignment */
}

.sidebar.collapsed .nav-item {
  text-align: center;
  padding: 8px 0;
}

.sidebar.collapsed .nav-text {
  display: none; /* Hide text, maybe replace with icons later */
}

/* Fallback: since we don't have icons for nav items yet, show first letter or keep text hidden? 
   Ideally we should add icons to nav items. For now, let's keep it simple.
   Actually, without icons, collapsed state is unusable. 
   Let's assume user wants to hide text. 
   BUT we need icons. 
   Let's add some icons to nav items for better UX.
*/

.nav-item:hover {
  background: rgba(0,0,0,0.05);
}

.nav-item.active {
  background: rgba(0,0,0,0.05);
  color: var(--color-accent);
  font-weight: 500;
}

.theme-toggle-container {
  margin-top: auto; /* Push to bottom */
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  width: 100%;
  border-radius: 8px;
  color: var(--color-text);
  font-size: 15px;
  transition: background 0.2s;
  overflow: hidden;
  white-space: nowrap;
}

.sidebar.collapsed .theme-toggle-btn {
  justify-content: center;
  padding: 10px 0;
}

.theme-toggle-btn:hover {
  background: rgba(0,0,0,0.05);
}

.main-content {
  margin-left: 260px; /* Offset sidebar */
  flex: 1;
  background: var(--color-background);
  transition: margin-left 0.3s ease;
}

.main-content.expanded {
  margin-left: 0;
}
</style>
