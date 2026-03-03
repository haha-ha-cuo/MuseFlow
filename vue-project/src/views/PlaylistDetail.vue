<script setup>
import { useRoute } from 'vue-router'
import { usePlayerStore } from '../stores/player'
import { Play, Upload, Plus, Music, Trash2, X, AlertCircle, CheckCircle } from 'lucide-vue-next'
import { ref, onMounted } from 'vue'

// Toast Notification System
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success') // 'success' or 'error'

const triggerToast = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Custom Confirm Dialog
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmCallback = ref(null)

const triggerConfirm = (message, callback) => {
  confirmMessage.value = message
  confirmCallback.value = callback
  showConfirm.value = true
}

const handleConfirm = async () => {
  if (confirmCallback.value) {
    // 等待回调函数执行完毕 (如果它是 async 的)
    await confirmCallback.value()
  }
  showConfirm.value = false // 这里不要直接关，让回调函数内部决定什么时候关，或者在 finally 里关
}

// 生成默认占位图 (与 PlaylistCard 保持一致)
const getPlaceholder = (text) => {
  if (!text) text = 'Music'
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash);
  }
  const c1 = `hsl(${hash % 360}, 70%, 80%)`;
  const c2 = `hsl(${(hash + 40) % 360}, 70%, 60%)`;
  
  return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:${c1};stop-opacity:1" /><stop offset="100%" style="stop-color:${c2};stop-opacity:1" /></linearGradient></defs><rect width="100%" height="100%" fill="url(%23g)" /></svg>`
}

const route = useRoute()
const playerStore = usePlayerStore()
const hasError = ref(false)
const isLoading = ref(true)
const showUploadModal = ref(false)
const uploadForm = ref({
  name: '',
  audioFile: null,
  coverFile: null,
  audioPreview: '',
  coverPreview: ''
})

const playlistInfo = ref({
  id: route.params.id,
  title: 'Loading...',
  description: 'Playlist description',
  cover: '',
  songs: []
})

// 模拟获取歌单详情
const fetchPlaylistDetail = async () => {
  isLoading.value = true
  try {
    // 1. 发起请求 (注意 URL 要和后端匹配)
    // 假设后端运行在 5000 端口
    const response = await fetch(`http://127.0.0.1:5000/api/playlists/id=${route.params.id}`)
    const result = await response.json()

    if (result.code === 200) {
      // 2. 成功获取数据，更新 playlistInfo
      // 注意：后端只返回了 songList，我们可能需要保留一些歌单的基础信息（标题、封面）
      // 如果后端能把歌单详情也一起返回最好，目前我们可以混合一下
      playlistInfo.value.songs = result.data
      
      // 这里的标题和封面暂时写死或从其他接口获取，或者后端一并返回
      playlistInfo.value.title = "Local Music" 
      playlistInfo.value.description = "Songs from your server"
    } else {
      console.error('获取失败:', result.msg)
    }
  } catch (error) {
    console.error('网络错误:', error)
  } finally {
    // 3. 无论成功失败，关闭 loading
    isLoading.value = false
  }
}


const handlePlay = (song) => {
  playerStore.playSong(song)
}

const openUploadModal = () => {
  showUploadModal.value = true
  // 重置表单
  uploadForm.value = {
    name: '',
    audioFile: null,
    coverFile: null,
    audioPreview: '',
    coverPreview: ''
  }
}

const handleFileSelect = (event, type) => {
  const file = event.target.files[0]
  if (!file) return

  if (type === 'audio') {
    uploadForm.value.audioFile = file
    uploadForm.value.name = file.name.replace(/\.[^/.]+$/, "") // 默认使用文件名作为歌名
    uploadForm.value.audioPreview = file.name
  } else if (type === 'cover') {
    uploadForm.value.coverFile = file
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadForm.value.coverPreview = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const isUploading = ref(false)
const uploadProgress = ref(0)

const submitUpload = async () => {
  if (!uploadForm.value.audioFile) {
    triggerToast('Please select an audio file.', 'error')
    return
  }
  
  if (isUploading.value) return
  isUploading.value = true
  uploadProgress.value = 0

  const formData = new FormData()
  formData.append('file', uploadForm.value.audioFile)
  formData.append('name', uploadForm.value.name)

  try {
    const xhr = new XMLHttpRequest()
    
    const promise = new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100
          uploadProgress.value = Math.round(percentComplete)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText))
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => {
        reject(new Error('Network error'))
      })

      xhr.open('POST', `http://127.0.0.1:5000/api/upload/playlistId=${route.params.id}`)
      xhr.send(formData)
    })

    const result = await promise
    
    if (result.code === 200) {
      const newSong = {
        ...result.data, 
        cover: uploadForm.value.coverPreview || result.data.cover || playlistInfo.value.cover
      }
      playlistInfo.value.songs.push(newSong)
      showUploadModal.value = false
      triggerToast('Upload successful!')
    } else {
      triggerToast('Upload failed: ' + result.msg, 'error')
    }
  } catch (error) {
    console.error('上传出错:', error)
    triggerToast('Upload error: ' + error.message, 'error')
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

const handleUploadCover = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/upload/playlistId=${route.params.id}`, {
      method: 'POST',
      body: formData
    })
    const result = await response.json()
    
    if (result.code === 200) {
      // 更新封面
      playlistInfo.value.cover = result.data.url
      hasError.value = false // 重置错误状态
      triggerToast('Cover updated successfully')
    } else {
      triggerToast('Cover upload failed: ' + result.msg, 'error')
    }
  } catch (error) {
    console.error('上传出错:', error)
    triggerToast('Upload error', 'error')
  }
}


const isDeleting = ref(false)

const handleDelete = async (song) => {
  if (isDeleting.value) return
  isDeleting.value = true

  // If the song to be deleted is playing, stop it first to release file lock
  if (playerStore.currentSong?.id === song.id) {
    playerStore.stop()
  }
  
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/songs/${song.id}`, {
      method: 'DELETE'
    })
    const result = await response.json()
    
    if (result.code === 200) {
      // 从列表中移除
      playlistInfo.value.songs = playlistInfo.value.songs.filter(s => s.id !== song.id)
      
      triggerToast('Song deleted successfully')
      showConfirm.value = false // 成功后关闭弹窗
    } else {
      triggerToast('Delete failed: ' + result.msg, 'error')
      // 失败了是否要关闭弹窗？通常保留让用户重试，或者也可以关闭。这里选择保留。
    }
  } catch (error) {
    console.error('删除出错:', error)
    triggerToast('Delete error, please check backend', 'error')
  } finally {
    isDeleting.value = false
  }
}

const confirmDelete = (song) => {
  triggerConfirm(`Are you sure you want to delete "${song.title}"?`, () => handleDelete(song))
}

onMounted(() => {
  fetchPlaylistDetail()
})
</script>

<template>
  <div class="playlist-page">
    <Transition name="fade" mode="out-in">
      <div v-if="isLoading" class="loading-container">
        <div class="spinner"></div>
        <span class="loading-text">Loading...</span>
      </div>
      
      <div v-else class="content-wrapper">
        <div class="header">
          <div class="cover-container">
            <!-- 判断逻辑: 有封面且加载未出错时显示图片，否则显示默认占位符 -->
        <img 
          v-if="playlistInfo.cover && !hasError" 
          :src="playlistInfo.cover" 
          class="cover-big" 
          alt="Playlist Cover" 
          @error="hasError = true"
        />
        <div v-else class="placeholder-cover">
          <img :src="getPlaceholder(playlistInfo.title)" alt="" class="bg-pattern" />
          <Music size="64" color="white" class="note-icon" />
        </div>

        <div class="cover-overlay">
          <Upload color="white" size="32" />
          <span>Change Cover</span>
        </div>
        <input type="file" @change="handleUploadCover" accept="image/*" class="cover-input" title="Change Cover" />
      </div>
      
      <div class="info">
        <h2>{{ playlistInfo.title }}</h2>
        <p>{{ playlistInfo.description }}</p>
        <div class="actions">
          <button class="play-btn-lg" @click="handlePlay(playlistInfo.songs[0])" v-if="playlistInfo.songs.length > 0">
            <Play fill="currentColor" size="20" style="margin-right: 4px;" /> Play
          </button>
          
          <div class="upload-song-wrapper">
            <button class="secondary-btn" @click="openUploadModal">
              <Plus size="18" /> Add Songs
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <Transition name="toast">
      <div v-if="showToast" class="toast-notification" :class="toastType">
        <CheckCircle v-if="toastType === 'success'" size="20" />
        <AlertCircle v-else size="20" />
        <span>{{ toastMessage }}</span>
      </div>
    </Transition>

    <!-- Custom Confirm Dialog -->
    <Transition name="fade">
      <div v-if="showConfirm" class="modal-overlay" style="z-index: 2000;">
        <div class="modal-content confirm-dialog">
          <h3>Confirm Action</h3>
          <p>{{ confirmMessage }}</p>
          <div class="modal-actions">
            <button class="cancel-btn" @click="showConfirm = false" :disabled="isDeleting">Cancel</button>
            <button class="submit-btn delete-confirm-btn" @click="handleConfirm" :disabled="isDeleting">
              {{ isDeleting ? 'Deleting...' : 'Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Upload Modal -->
    <Transition name="fade">
      <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
        <div class="modal-content">
          <h3>Upload New Song</h3>
          
          <div class="form-group">
            <label>Song Name</label>
            <input type="text" v-model="uploadForm.name" placeholder="Enter song name" />
          </div>

          <div class="form-group">
            <label>Audio File</label>
            <div class="file-input-wrapper">
              <button class="file-select-btn">
                {{ uploadForm.audioPreview || 'Choose Audio File' }}
              </button>
              <input type="file" @change="(e) => handleFileSelect(e, 'audio')" accept="audio/*" />
            </div>
          </div>

          <div class="form-group">
            <label>Cover Image (Optional)</label>
            <div class="file-input-wrapper">
               <button class="file-select-btn">
                {{ uploadForm.coverFile ? 'Image Selected' : 'Choose Cover Image' }}
              </button>
              <input type="file" @change="(e) => handleFileSelect(e, 'cover')" accept="image/*" />
            </div>
            <div v-if="uploadForm.coverPreview" class="preview-cover">
              <img :src="uploadForm.coverPreview" />
            </div>
          </div>

          <div class="modal-actions">
            <button class="cancel-btn" @click="showUploadModal = false" :disabled="isUploading">Cancel</button>
            <button class="submit-btn" @click="submitUpload" :disabled="isUploading">
              {{ isUploading ? `Uploading ${uploadProgress}%` : 'Upload' }}
            </button>
          </div>
          
          <div v-if="isUploading" class="upload-progress-bar">
            <div class="upload-progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
        </div>
      </div>
    </Transition>

    <div class="song-list">
      <div 
        v-for="(song, index) in playlistInfo.songs" 
        :key="song.id" 
        class="song-item"
        :class="{ active: playerStore.currentSong?.id === song.id }"
        @click="handlePlay(song)"
      >
        <span class="index">{{ index + 1 }}</span>
        <div class="song-details">
          <div class="song-title">{{ song.title }}</div>
          <div class="song-artist">{{ song.artist }}</div>
        </div>
        <span class="duration">{{ song.duration }}</span>
        <button class="delete-btn" @click.stop="confirmDelete(song)" title="Delete Song">
          <Trash2 size="16" />
        </button>
      </div>
      
      <div v-if="playlistInfo.songs.length === 0" class="empty-state">
            No songs yet. Click "Add Songs" to upload.
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.playlist-page {
  padding-bottom: 100px;
  min-height: 100%;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 60vh;
  gap: 16px;
}

.loading-text {
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--color-accent);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transition Styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.header {
  display: flex;
  padding: 40px;
  gap: 32px;
  align-items: flex-end;
  background: linear-gradient(to bottom, #f5f5f7, #ffffff);
}

.cover-container {
  position: relative;
  width: 260px;
  height: 260px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  background-color: var(--color-background-secondary);
}

.placeholder-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: filter 0.3s, transform 0.3s;
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
  opacity: 0.9;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

.cover-big {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s, transform 0.3s;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

.cover-overlay span {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
}

.cover-container:hover .cover-overlay {
  opacity: 1;
}

.cover-container:hover .cover-big,
.cover-container:hover .placeholder-cover {
  filter: blur(8px);
  transform: scale(1.1);
}

.cover-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-song-wrapper {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
}

.upload-song-wrapper input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.secondary-btn {
  background: rgba(0, 0, 0, 0.05);
  color: var(--color-accent);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.1s;
}

.secondary-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: var(--color-text-secondary);
}

.info {
  flex: 1;
}

.info h2 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
}

.info p {
  color: var(--color-text-secondary);
  font-size: 16px;
  margin-bottom: 24px;
}

.play-btn-lg {
  background: var(--color-accent);
  color: white;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  transition: transform 0.1s;
}

.play-btn-lg:active {
  transform: scale(0.98);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  padding: 32px;
  border-radius: 16px;
  width: 400px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-content h3 {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-group input[type="text"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input[type="text"]:focus {
  border-color: var(--color-accent);
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
}

.file-select-btn {
  width: 100%;
  padding: 10px 12px;
  background: #f5f5f7;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  text-align: left;
  color: #333;
  cursor: pointer;
}

.file-input-wrapper input[type="file"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.preview-cover {
  margin-top: 10px;
  width: 60px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
}

.preview-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.cancel-btn {
  padding: 8px 16px;
  background: transparent;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.submit-btn {
  padding: 8px 20px;
  background: var(--color-accent);
  color: white;
  border-radius: 8px;
  font-weight: 600;
}

.submit-btn:hover {
  opacity: 0.9;
}

.song-list {
  padding: 0 40px;
}

.song-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-background-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.song-item:hover {
  background: var(--color-background-secondary);
}

.song-item.active {
  color: var(--color-accent);
  background: rgba(250, 45, 72, 0.05);
}

.index {
  width: 30px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.song-details {
  flex: 1;
}

.song-title {
  font-weight: 500;
  font-size: 16px;
}

.song-artist {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.song-item.active .song-artist {
  color: var(--color-accent);
  opacity: 0.8;
}

.duration {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.delete-btn {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 12px;
}

.song-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #ff3b30; /* Red color for delete action */
}

/* Toast Styles */
.toast-notification {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 14px;
  z-index: 3000;
  color: #333;
}

.toast-notification.error {
  color: #ff3b30;
}

.toast-notification.success {
  color: #34c759;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}

/* Confirm Dialog Specifics */
.confirm-dialog {
  width: 320px;
  text-align: center;
}

.confirm-dialog h3 {
  margin-bottom: 12px;
}

.confirm-dialog p {
  color: var(--color-text-secondary);
  margin-bottom: 24px;
}

.delete-confirm-btn {
  background-color: #ff3b30;
}

.delete-confirm-btn:hover {
  background-color: #d63228;
}

.upload-progress-bar {
  width: 100%;
  height: 4px;
  background-color: var(--color-background-secondary);
  border-radius: 2px;
  margin-top: 16px;
  overflow: hidden;
}

.upload-progress-fill {
  height: 100%;
  background-color: var(--color-accent);
  transition: width 0.2s ease;
}
</style>