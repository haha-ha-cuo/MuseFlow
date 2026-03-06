import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { API_BASE_URL } from '@/config'

export const usePlayerStore = defineStore('player', () => {
  // 内部 Audio 对象
  const audio = new Audio()
  
  // 状态
  const isPlaying = ref(false)
  const currentSong = ref(null)
  const playlist = ref([])
  const currentIndex = ref(-1)
  const volume = ref(0.8)
  const currentTime = ref(0)
  const duration = ref(0)

  // 初始化监听器
  audio.addEventListener('ended', () => {
    nextSong()
  })
  
  audio.addEventListener('timeupdate', () => {
    currentTime.value = audio.currentTime
  })

  audio.addEventListener('loadedmetadata', () => {
    duration.value = audio.duration
  })
  
  // 监听错误
  audio.addEventListener('error', (e) => {
    console.error('Audio Playback Error:', e)
    isPlaying.value = false
  })

 
  // 动作
  async function playSong(song) {
    if (currentSong.value?.id === song.id) {
      togglePlay()
      return
    }

    currentSong.value = song
    
    // 如果歌曲不在当前列表中，加入列表
    if (!playlist.value.find(s => s.id === song.id)) {
      playlist.value.push(song)
    }
    currentIndex.value = playlist.value.findIndex(s => s.id === song.id)
    
    try {
      console.log('Playing URL:', song.url) // 打印正在播放的 URL
      audio.src = song.url
      audio.volume = volume.value
      await audio.play()
      isPlaying.value = true
    } catch (error) {
      console.log('Playing URL:', song.url) 
      console.error("播放失败:", error)
      isPlaying.value = false
    }
  }

  function togglePlay() {
    if (!currentSong.value) return
    
    if (isPlaying.value) {
      audio.pause()
      isPlaying.value = false
    } else {
      audio.play().catch(e => console.error(e))
      isPlaying.value = true
    }
  }

  function setVolume(val) {
    volume.value = val
    audio.volume = val
  }

  function seek(time) {
    audio.currentTime = time
    currentTime.value = time
  }
  
  // 停止播放并清空当前歌曲 (用于删除歌曲时)
  function stop() {
    audio.pause()
    audio.src = ''
    audio.load() // 强制释放资源
    isPlaying.value = false
    currentSong.value = null
    currentTime.value = 0
    duration.value = 0
  }

  function nextSong() {
    if (playlist.value.length === 0) return
    let nextIndex = currentIndex.value + 1
    if (nextIndex >= playlist.value.length) nextIndex = 0
    playSong(playlist.value[nextIndex])
  }

  function prevSong() {
    if (playlist.value.length === 0) return
    let prevIndex = currentIndex.value - 1
    if (prevIndex < 0) prevIndex = playlist.value.length - 1
    playSong(playlist.value[prevIndex])
  }

  return {
    isPlaying,
    currentSong,
    playlist,
    currentTime,
    duration,
    playSong,
    togglePlay,
    nextSong,
    prevSong,
    setVolume,
    seek,
    stop,
    volume,
    audio // 暴露 audio 对象以便需要时直接操作
  }
})
