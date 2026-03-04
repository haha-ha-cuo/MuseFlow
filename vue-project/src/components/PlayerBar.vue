<script setup>
import { usePlayerStore } from '../stores/player'
import { storeToRefs } from 'pinia'
import { Play, Pause, SkipBack, SkipForward, Volume2 } from 'lucide-vue-next'
import { computed, ref, onUnmounted } from 'vue'

const playerStore = usePlayerStore()
const { currentSong, isPlaying, currentTime, duration, volume } = storeToRefs(playerStore)
const { togglePlay, nextSong, prevSong, seek, setVolume } = playerStore

const isDragging = ref(false)
const isDraggingVolume = ref(false)
const dragPercentage = ref(0)
const dragVolumePercentage = ref(0) // 新增：音量拖拽时的临时百分比
const progressBarRef = ref(null)
const volumeBarRef = ref(null)


const formatTime = ( seconds ) => {
  if ( ! seconds ) return '0:00'
  const mins = Math . floor ( seconds / 60 )
  const secs = Math . floor ( seconds % 60 )
  return ` ${ mins } : ${ secs . toString ().
  padStart ( 2 , '0' ) } `
}
// ... formatTime ...

const progressPercentage = computed(() => {
  if (isDragging.value) return dragPercentage.value
  if (!duration.value) return 0
  return (currentTime.value / duration.value) * 100
})

// 新增：音量条的显示百分比
const volumePercentage = computed(() => {
  if (isDraggingVolume.value) return dragVolumePercentage.value
  return volume.value * 100
})

const handleMouseDown = (e) => {
  isDragging.value = true
  updateDragPosition(e)
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (e) => {
  if (isDragging.value) {
    updateDragPosition(e)
  }
}

const handleMouseUp = (e) => {
  if (isDragging.value) {
    updateDragPosition(e)
    const seekTime = (dragPercentage.value / 100) * duration.value
    seek(seekTime)
    isDragging.value = false
  }
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const handleVolumeMouseDown = (e) => {
  isDraggingVolume.value = true
  updateVolumePosition(e)
  document.addEventListener('mousemove', handleVolumeMouseMove)
  document.addEventListener('mouseup', handleVolumeMouseUp)
}

const handleVolumeMouseMove = (e) => {
  if (isDraggingVolume.value) {
    updateVolumePosition(e)
  }
}

const handleVolumeMouseUp = (e) => {
  if (isDraggingVolume.value) {
    updateVolumePosition(e)
    isDraggingVolume.value = false
  }
  document.removeEventListener('mousemove', handleVolumeMouseMove)
  document.removeEventListener('mouseup', handleVolumeMouseUp)
}

const updateVolumePosition = (e) => {
  if (!volumeBarRef.value) return
  const rect = volumeBarRef.value.getBoundingClientRect()
  const clickX = e.clientX - rect.left
  let newVolume = clickX / rect.width
  newVolume = Math.max(0, Math.min(1, newVolume)) // Clamp between 0 and 1
  
  // 1. 更新临时显示状态（无延迟）
  dragVolumePercentage.value = newVolume * 100
  
  // 2. 更新实际音量
  setVolume(newVolume)
  // console.log('Current Volume:', newVolume.toFixed(2)) 
}

const updateDragPosition = (e) => {
  if (!progressBarRef.value) return
  const rect = progressBarRef.value.getBoundingClientRect()
  const clickX = e.clientX - rect.left
  let percentage = (clickX / rect.width) * 100
  percentage = Math.max(0, Math.min(100, percentage)) // Clamp between 0 and 100
  dragPercentage.value = percentage
}

// 清理事件监听，防止内存泄漏
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('mousemove', handleVolumeMouseMove)
  document.removeEventListener('mouseup', handleVolumeMouseUp)
})
</script>

<template>
  <Transition name="slide-up">
    <div class="player-bar" v-if="currentSong">
      <div class="song-info">
        <img :src="currentSong.cover" alt="Cover" class="cover" />
        <div class="text">
          <div class="title">{{ currentSong.title }}</div>
          <div class="artist">{{ currentSong.artist }}</div>
        </div>
      </div>

      <div class="controls-wrapper">
        <div class="controls">
          <button @click="prevSong" class="control-btn sm">
            <SkipBack size="20" fill="currentColor" />
          </button>
          <button @click="togglePlay" class="control-btn play-pause">
            <Pause v-if="isPlaying" fill="currentColor" size="24" />
            <Play v-else fill="currentColor" size="24" class="play-icon" />
          </button>
          <button @click="nextSong" class="control-btn sm">
            <SkipForward size="20" fill="currentColor" />
          </button>
        </div>
        
        <div class="progress-container">
          <span class="time">{{ isDragging ? formatTime((dragPercentage / 100) * duration) : formatTime(currentTime) }}</span>
          <div class="progress-bar" :class="{ 'dragging': isDragging }" ref="progressBarRef" @mousedown="handleMouseDown">
            <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
          </div>
          <span class="time">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <div class="volume">
        <Volume2 size="18" />
        <div class="progress-bar volume-bar" :class="{ 'dragging': isDraggingVolume }" ref="volumeBarRef" @mousedown="handleVolumeMouseDown">
          <div class="progress-fill" :style="{ width: volumePercentage + '%' }"></div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: var(--glass-material);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  z-index: 100;
}

.song-info {
  display: flex;
  align-items: center;
  width: 30%;
}

.cover {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  margin-right: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.title {
  font-weight: 600;
  font-size: 14px;
}

.artist {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.controls-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 40%;
}

.controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.progress-container {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 8px;
}

.time {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  width: 35px;
  text-align: center;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background-color: rgba(0,0,0,0.1); /* 轨道颜色 */
  border-radius: 2px;
  cursor: pointer;
  position: relative;
  /* 增加点击区域高度，更容易交互，但用 margin 而不是 padding + clip */
  margin: 6px 0; 
}

.progress-fill {
  height: 100%;
  background-color: var(--color-text-secondary); /* 已走过进度的颜色 */
  border-radius: 2px;
  position: relative;
  transition: background-color 0.2s;
}

/* 进度条上的圆点 */
.progress-fill::after {
  content: '';
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  width: 12px;
  height: 12px;
  background-color: var(--color-text);
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: transform 0.1s ease;
  z-index: 10;
}

/* 悬浮时或拖拽中：进度条变深色，圆点出现 */
.progress-bar:hover .progress-fill,
.progress-bar.dragging .progress-fill {
  background-color: var(--color-accent);
}

.progress-bar:hover .progress-fill::after,
.progress-bar.dragging .progress-fill::after {
  transform: translateY(-50%) scale(1);
}

.control-btn {
  color: var(--color-text);
  opacity: 0.8;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  opacity: 1;
}

.play-pause {
  opacity: 1;
  background: var(--color-text); /* Invert color for contrast */
  color: var(--color-background);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.play-icon {
  margin-left: 2px; /* Visual centering */
}

.volume {
  width: 30%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  color: var(--color-text-secondary);
}

/* 提高优先级，确保宽度生效且不被 flex 拉伸 */
.progress-bar.volume-bar {
  width: 100px !important;
  flex: 0 0 auto; 
  margin: 0; /* 在这里不需要 margin，因为父容器是居中的 */
}
</style>
