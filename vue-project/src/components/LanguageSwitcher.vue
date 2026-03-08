<template>
  <div class="language-switcher" v-click-outside="closeDropdown">
    <button class="lang-btn" @click="toggleDropdown" :class="{ collapsed: collapsed }">
      <Globe size="20" />
      <span v-if="!collapsed">{{ currentLangLabel }}</span>
    </button>
    
    <Transition name="fade">
      <div v-if="isOpen" class="lang-dropdown">
        <div 
          v-for="locale in availableLocales" 
          :key="locale.code"
          class="lang-option"
          :class="{ active: currentLocale === locale.code }"
          @click="changeLocale(locale.code)"
        >
          {{ locale.label }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Globe } from 'lucide-vue-next'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const { locale } = useI18n()
const isOpen = ref(false)

const availableLocales = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '中文' }
]

const currentLocale = computed(() => locale.value)
const currentLangLabel = computed(() => {
  return availableLocales.find(l => l.code === locale.value)?.label || 'English'
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = () => {
  isOpen.value = false
}

const changeLocale = (code) => {
  locale.value = code
  localStorage.setItem('user-locale', code)
  closeDropdown()
}

// Click outside directive (simple version)
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--color-text);
  font-size: 15px;
  transition: all 0.2s;
  width: 100%;
}

.lang-btn.collapsed {
  justify-content: center;
  padding: 10px 0;
}

.lang-btn:hover {
  background: rgba(0,0,0,0.05);
}

.lang-dropdown {
  position: absolute;
  bottom: 100%; /* Show upwards */
  top: auto;
  left: 0;
  width: 100%;
  margin-bottom: 8px;
  margin-top: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 8px;
  z-index: 100;
}

.lang-option {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text);
  font-size: 14px;
  transition: all 0.2s;
}

.lang-option:hover {
  background: var(--color-background-secondary);
}

.lang-option.active {
  background: var(--color-accent);
  color: white;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>