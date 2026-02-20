<script setup>
import { usePlayerStore } from '../stores/player'
import { storeToRefs } from 'pinia'
import { Play, Pause, SkipBack, SkipForward, Volume2 } from 'lucide-vue-next'

const playerStore = usePlayerStore()
const { currentSong, isPlaying } = storeToRefs(playerStore)
const { togglePlay, nextSong, prevSong } = playerStore


</script>

<template>
  <div class="player-bar" v-if="currentSong">
    <div class="song-info">
      <img :src="currentSong.cover" alt="Cover" class="cover" />
      <div class="text">
        <div class="title">{{ currentSong.title }}</div>
        <div class="artist">{{ currentSong.artist }}</div>
      </div>
    </div>

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

    <div class="volume">
      <Volume2 size="18" />
      <div class="slider-track">
        <div class="slider-fill"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

.controls {
  display: flex;
  align-items: center;
  gap: 24px;
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
  gap: 10px;
  color: var(--color-text-secondary);
}

.slider-track {
  width: 100px;
  height: 4px;
  background: rgba(0,0,0,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.slider-fill {
  width: 60%;
  height: 100%;
  background: var(--color-text-secondary);
}
</style>
