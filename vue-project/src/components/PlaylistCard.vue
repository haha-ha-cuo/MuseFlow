<script setup>
import { defineProps, ref } from 'vue'
import { Play, Music } from 'lucide-vue-next'

const props = defineProps({
  id: Number,
  title: String,
  artist: String,
  cover: String
})

const hasError = ref(false)

// 生成一个基于标题的随机渐变色 SVG
const getPlaceholder = (text) => {
  // 简单的哈希函数，确保同一个标题生成的颜色是一样的
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash);
  }
  const c1 = `hsl(${hash % 360}, 70%, 80%)`;
  const c2 = `hsl(${(hash + 40) % 360}, 70%, 60%)`;
  
  return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:${c1};stop-opacity:1" /><stop offset="100%" style="stop-color:${c2};stop-opacity:1" /></linearGradient></defs><rect width="100%" height="100%" fill="url(%23g)" /></svg>`
}
</script>

<template>
  <div class="playlist-card">
    <div class="cover-wrapper">
      <img 
        v-if="!hasError" 
        :src="cover" 
        :alt="title" 
        loading="lazy" 
        @error="hasError = true"
      />
      <div v-else class="placeholder-cover">
        <img :src="getPlaceholder(title)" alt="" class="bg-pattern" />
        <Music size="48" color="white" class="note-icon" />
      </div>

      <div class="play-overlay">
        <Play fill="currentColor" size="24" />
      </div>
    </div>
    <div class="info">
      <h3>{{ title }}</h3>
      <p>{{ artist }}</p>
    </div>
  </div>
</template>

<style scoped>
.playlist-card {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.playlist-card:hover {
  transform: scale(1.02);
}

.cover-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  aspect-ratio: 1;
  margin-bottom: 12px;
  background-color: var(--color-background-secondary); /* 图片未加载时的底色 */
}

.placeholder-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.bg-pattern {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.note-icon {
  position: relative;
  z-index: 1;
  opacity: 0.8;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s;
}

.play-overlay {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-accent);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.playlist-card:hover .play-overlay {
  opacity: 1;
  transform: translateY(0);
}

.info h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info p {
  font-size: 14px;
  color: var(--color-text-secondary);
}
</style>
