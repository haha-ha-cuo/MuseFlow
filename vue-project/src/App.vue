<script setup>
import { RouterView } from 'vue-router'
import PlayerBar from './components/PlayerBar.vue'
</script>

<template>
  <div class="app-layout">
    <div class="sidebar">
      <div class="logo">
        <img src="/logo.svg" alt="Music Logo" class="brand-icon" />
        MuseFlow
      </div>
      <nav>
        <router-link to="/" class="nav-item active">Listen Now</router-link>
        <a href="#" class="nav-item">Browse</a>
        <a href="#" class="nav-item">Radio</a>
      </nav>
      
      <div class="section-title">Library</div>
      <nav>
        <a href="#" class="nav-item">Recently Added</a>
        <a href="#" class="nav-item">Artists</a>
        <a href="#" class="nav-item">Albums</a>
        <a href="#" class="nav-item">Songs</a>
      </nav>
    </div>

    <main class="main-content">
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
}

.brand-icon {
  width: 40px;
  height: 40px;
  display: block;
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
}

.nav-item:hover {
  background: rgba(0,0,0,0.05);
}

.nav-item.active {
  background: rgba(0,0,0,0.05);
  color: var(--color-accent);
  font-weight: 500;
}

.main-content {
  margin-left: 260px; /* Offset sidebar */
  flex: 1;
  background: var(--color-background);
}
</style>
