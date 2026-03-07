<script setup>
import { useRoute, useRouter } from 'vue-router'
import { usePlayerStore } from '../stores/player'
import { Play, Upload, Plus, Music, Trash2, X, AlertCircle, CheckCircle, ArrowLeft, Edit } from 'lucide-vue-next'
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '@/config'

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
const router = useRouter()
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
    const response = await fetch(`${API_BASE_URL}/playlists/${route.params.id}`)
    const result = await response.json()

    if (result.code === 200) {
      playlistInfo.value = {
        title: result.title,
        description: result.description,
        songs: result.data || [],
        cover: result.cover 
      }
      console.log(playlistInfo.value.cover)
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
  playerStore.playlist = [...playlistInfo.value.songs] 
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

const showEditModal = ref(false)
const editForm = ref({
  title: '',
  description: '',
  coverFile: null,
  coverPreview: ''
})

const openEditModal = () => {
  editForm.value.title = playlistInfo.value.title
  editForm.value.description = playlistInfo.value.description
  editForm.value.coverFile = null
  editForm.value.coverPreview = playlistInfo.value.cover
  showEditModal.value = true
}

const isUpdating = ref(false)

const resetPlaylistCover = async () => {
  triggerConfirm('Are you sure you want to reset the playlist cover to default?', async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/playlists/reset/cover/${route.params.id}`, {
        method: 'POST'
      })
      const result = await response.json()
      
      if (result.code === 200) {
        playlistInfo.value.cover = ''
        editForm.value.coverPreview = ''
        editForm.value.coverFile = null
        showConfirm.value = false
        triggerToast('Cover reset successfully')
      } else {
        triggerToast('Reset failed: ' + result.msg, 'error')
      }
    } catch (error) {
      console.error('Reset error:', error)
      triggerToast('Reset error', 'error')
    }
  })
}

const submitEdit = async () => {
  if (!editForm.value.title) {
    triggerToast('Title cannot be empty', 'error')
    return
  }
  
  if (isUpdating.value) return
  isUpdating.value = true

  try {
    // 1. Update Text Info
    const response = await fetch(`${API_BASE_URL}/playlists/update/${route.params.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: editForm.value.title,
        description: editForm.value.description
      })
    })
    const result = await response.json()
    
    if (result.code === 200) {
      playlistInfo.value.title = editForm.value.title
      playlistInfo.value.description = editForm.value.description
      
      // 2. Upload Cover if selected
      if (editForm.value.coverFile) {
          const formData = new FormData()
          formData.append('file', editForm.value.coverFile)
          
          const uploadRes = await fetch(`${API_BASE_URL}/playlists/upload/cover/${route.params.id}`, {
              method: 'POST',
              body: formData
          })
          const uploadResult = await uploadRes.json()
          if (uploadResult.code === 200) {
               playlistInfo.value.cover = uploadResult.data.coverUrl
          } else {
              triggerToast('Info updated but cover failed: ' + uploadResult.msg, 'warning')
          }
      }

      showEditModal.value = false
      triggerToast('Playlist updated successfully')
    } else {
      triggerToast('Update failed: ' + result.msg, 'error')
    }
  } catch (error) {
    console.error('Update error:', error)
    triggerToast('Update error, please check backend', 'error')
  } finally {
    isUpdating.value = false
  }
}

const showCropModal = ref(false)
const cropImage = ref(null)
const cropCanvas = ref(null)
const CROP_CANVAS_SIZE = 400
const CROP_VIEWPORT_SIZE = 300 // Size of the fixed square selection box

const isDraggingCrop = ref(false)
const dragStart = ref({ x: 0, y: 0 })

const imageState = ref({
  x: 0,
  y: 0,
  scale: 1,
  minScale: 0.1
})

const openCropModal = (file, imageUrl = null) => {
  if (imageUrl) {
    const img = new Image()
    img.crossOrigin = "Anonymous"
    img.onload = () => {
      cropImage.value = img
      showCropModal.value = true
      initCropState(img)
    }
    img.src = imageUrl
  } else if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        cropImage.value = img
        showCropModal.value = true
        initCropState(img)
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const initCropState = (img) => {
  // Initialize scale to FILL the viewport (cover behavior)
  // We want the smallest dimension of the image to match the viewport size
  const scaleX = CROP_VIEWPORT_SIZE / img.width
  const scaleY = CROP_VIEWPORT_SIZE / img.height
  const initialScale = Math.max(scaleX, scaleY)
  
  imageState.value = {
    scale: initialScale,
    minScale: initialScale * 0.5, // Allow zooming out a bit more
    x: (CROP_CANVAS_SIZE - img.width * initialScale) / 2,
    y: (CROP_CANVAS_SIZE - img.height * initialScale) / 2
  }
  
  setTimeout(() => drawCropCanvas(), 100)
}

const drawCropCanvas = () => {
  if (!cropCanvas.value || !cropImage.value) return
  const ctx = cropCanvas.value.getContext('2d')
  const canvas = cropCanvas.value
  const img = cropImage.value
  const state = imageState.value

  // Set fixed canvas size
  canvas.width = CROP_CANVAS_SIZE
  canvas.height = CROP_CANVAS_SIZE

  // Clear
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Fill background
  ctx.fillStyle = '#1a1a1a'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Draw Image with transform
  ctx.drawImage(
    img, 
    state.x, 
    state.y, 
    img.width * state.scale, 
    img.height * state.scale
  )

  // Draw Overlay (Semi-transparent black)
  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
  
  // Calculate viewport rect
  const vpX = (CROP_CANVAS_SIZE - CROP_VIEWPORT_SIZE) / 2
  const vpY = (CROP_CANVAS_SIZE - CROP_VIEWPORT_SIZE) / 2
  
  // Draw 4 rectangles around the viewport
  // Top
  ctx.fillRect(0, 0, canvas.width, vpY)
  // Bottom
  ctx.fillRect(0, vpY + CROP_VIEWPORT_SIZE, canvas.width, canvas.height - (vpY + CROP_VIEWPORT_SIZE))
  // Left
  ctx.fillRect(0, vpY, vpX, CROP_VIEWPORT_SIZE)
  // Right
  ctx.fillRect(vpX + CROP_VIEWPORT_SIZE, vpY, canvas.width - (vpX + CROP_VIEWPORT_SIZE), CROP_VIEWPORT_SIZE)
  
  // Draw Viewport Border
  ctx.strokeStyle = '#fff'
  ctx.lineWidth = 2
  ctx.strokeRect(vpX, vpY, CROP_VIEWPORT_SIZE, CROP_VIEWPORT_SIZE)
}

const handleCropMouseDown = (e) => {
  isDraggingCrop.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
  window.addEventListener('mousemove', handleCropMouseMove)
  window.addEventListener('mouseup', handleCropMouseUp)
}

const handleCropMouseMove = (e) => {
  if (!isDraggingCrop.value) return
  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y
  dragStart.value = { x: e.clientX, y: e.clientY }
  
  // Move image instead of selection
  imageState.value.x += dx
  imageState.value.y += dy

  drawCropCanvas()
}

const handleCropWheel = (e) => {
  // Zoom logic
  const zoomSpeed = 0.001
  const delta = -e.deltaY * zoomSpeed
  const newScale = Math.max(imageState.value.minScale, imageState.value.scale + delta)
  
  // Zoom centered on canvas center (approximate)
  // To do precise mouse-centered zoom requires more math, center-zoom is usually fine for avatars
  const scaleRatio = newScale / imageState.value.scale
  const centerX = CROP_CANVAS_SIZE / 2
  const centerY = CROP_CANVAS_SIZE / 2
  
  imageState.value.x = centerX - (centerX - imageState.value.x) * scaleRatio
  imageState.value.y = centerY - (centerY - imageState.value.y) * scaleRatio
  imageState.value.scale = newScale
  
  drawCropCanvas()
}

const handleCropMouseUp = () => {
  isDraggingCrop.value = false
  window.removeEventListener('mousemove', handleCropMouseMove)
  window.removeEventListener('mouseup', handleCropMouseUp)
}

const confirmCrop = () => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  const img = cropImage.value
  const state = imageState.value
  
  // Output size
  canvas.width = 300
  canvas.height = 300
  
  // Viewport position on the crop canvas
  const vpX = (CROP_CANVAS_SIZE - CROP_VIEWPORT_SIZE) / 2
  const vpY = (CROP_CANVAS_SIZE - CROP_VIEWPORT_SIZE) / 2
  
  // Calculate the source rectangle on the original image
  // The viewport (vpX, vpY) corresponds to some point on the image (state.x, state.y)
  // Relationship: CanvasPoint = ImagePoint * scale + offset
  // So: ImagePoint = (CanvasPoint - offset) / scale
  
  const sourceX = (vpX - state.x) / state.scale
  const sourceY = (vpY - state.y) / state.scale
  const sourceW = CROP_VIEWPORT_SIZE / state.scale
  const sourceH = CROP_VIEWPORT_SIZE / state.scale
  
  ctx.drawImage(
    img,
    sourceX, sourceY, sourceW, sourceH, // Source rect
    0, 0, canvas.width, canvas.height   // Dest rect
  )

  canvas.toBlob((blob) => {
    const file = new File([blob], "cover.jpg", { type: "image/jpeg" })
    
    // 1. Upload Song Modal
    if (showUploadModal.value) {
      uploadForm.value.coverFile = file
      uploadForm.value.coverPreview = URL.createObjectURL(blob)
    } 
    // 2. Edit Playlist Modal
    else if (showEditModal.value) {
      editForm.value.coverFile = file
      editForm.value.coverPreview = URL.createObjectURL(blob)
    }
    // 3. Edit Song Modal
    else if (showEditSongModal.value) {
      editSongForm.value.coverFile = file
      editSongForm.value.coverPreview = URL.createObjectURL(blob)
    }
    // 4. Direct Playlist Cover Click (Main Page)
    else {
      uploadCover(file)
    }
    showCropModal.value = false
  }, 'image/jpeg', 0.9)
}

// 独立的上传封面逻辑
const uploadCover = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_BASE_URL}/playlists/upload/cover/${route.params.id}`, {
      method: 'POST',
      body: formData
    })
    const result = await response.json()
    
    if (result.code === 200) {
      playlistInfo.value.cover = result.data.coverUrl
      hasError.value = false
      triggerToast('Cover updated successfully')
    } else {
      triggerToast('Cover upload failed: ' + result.msg, 'error')
    }
  } catch (error) {
    console.error('上传出错:', error)
    triggerToast('Upload error', 'error')
  }
}

const currentRawCoverFile = ref(null)

const handleFileSelect = (event, type) => {
  const file = event.target.files[0]
  if (!file) return

  if (type === 'audio') {
    uploadForm.value.audioFile = file
    if(uploadForm.value.name === ''){
        uploadForm.value.name = file.name.replace(/\.[^/.]+$/, "")
    }
    uploadForm.value.audioPreview = file.name
  } else if (type === 'cover') {
    currentRawCoverFile.value = file
    openCropModal(file)
    event.target.value = '' // Reset input
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
  if (uploadForm.value.coverFile) {
    formData.append('cover', uploadForm.value.coverFile)
  }

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

      xhr.open('POST', `${API_BASE_URL}/upload/${route.params.id}/songs`)
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
      playerStore.playlist = playlistInfo.value.songs
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
    const response = await fetch(`${API_BASE_URL}/upload/playlistId=${route.params.id}`, {
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
    const response = await fetch(`${API_BASE_URL}/songs/${song.id}`, {
      method: 'DELETE'
    })
    const result = await response.json()
    
    if (result.code === 200) {
      // 从列表中移除
      playlistInfo.value.songs = playlistInfo.value.songs.filter(s => s.id !== song.id)
      playerStore.playlist = playlistInfo.value.songs
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

const showEditSongModal = ref(false)
const editSongForm = ref({
  id: null,
  title: '',
  artist: '',
  coverFile: null,
  coverPreview: ''
})

const openEditSongModal = (song) => {
  editSongForm.value.id = song.id
  editSongForm.value.title = song.title
  editSongForm.value.artist = song.artist
  editSongForm.value.coverFile = null
  editSongForm.value.coverPreview = song.cover
  showEditSongModal.value = true
}

const resetSongCover = async () => {
  triggerConfirm('Are you sure you want to reset the song cover to default?', async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/songs/reset/cover/${editSongForm.value.id}`, {
        method: 'POST'
      })
      const result = await response.json()
      
      if (result.code === 200) {
        const song = playlistInfo.value.songs.find(s => s.id === editSongForm.value.id)
        if (song) song.cover = ''
        
        editSongForm.value.coverPreview = ''
        editSongForm.value.coverFile = null
        showConfirm.value = false
        triggerToast('Cover reset successfully')
      } else {
        triggerToast('Reset failed: ' + result.msg, 'error')
      }
    } catch (error) {
      console.error('Reset error:', error)
      triggerToast('Reset error', 'error')
    }
  })
}

const isUpdatingSong = ref(false)

const submitEditSong = async () => {
  if (!editSongForm.value.title) {
    triggerToast('Song title cannot be empty', 'error')
    return
  }
  
  if (isUpdatingSong.value) return
  isUpdatingSong.value = true

  try {
    // 1. Update Text Info
    const response = await fetch(`${API_BASE_URL}/songs/update/${editSongForm.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: editSongForm.value.title,
        artist: editSongForm.value.artist
      })
    })
    const result = await response.json()
    
    if (result.code === 200) {
      // Update local state
      const song = playlistInfo.value.songs.find(s => s.id === editSongForm.value.id)
      if (song) {
        song.title = editSongForm.value.title
        song.artist = editSongForm.value.artist
      }

      // 2. Upload Cover if selected
      if (editSongForm.value.coverFile) {
          const formData = new FormData()
          formData.append('file', editSongForm.value.coverFile)
          
          const uploadRes = await fetch(`${API_BASE_URL}/songs/upload/cover/${editSongForm.value.id}`, {
              method: 'POST',
              body: formData
          })
          const uploadResult = await uploadRes.json()
          if (uploadResult.code === 200) {
               if (song) song.cover = uploadResult.data.coverUrl
          } else {
               triggerToast('Info updated but cover failed: ' + uploadResult.msg, 'warning')
          }
      }

      showEditSongModal.value = false
      triggerToast('Song updated successfully')
    } else {
      triggerToast('Update failed: ' + result.msg, 'error')
    }
  } catch (error) {
    console.error('更新出错:', error)
    triggerToast('Update error, please check backend', 'error')
  } finally {
    isUpdatingSong.value = false
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
          <button class="back-btn" @click="router.push('/')">
            <ArrowLeft size="24" />
          </button>
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
        <input type="file" @change="(e) => handleFileSelect(e, 'cover')" accept="image/*" class="cover-input" title="Change Cover" />
      </div>
      
      <div class="info">
        <h2>{{ playlistInfo.title }}</h2>
        <p>{{ playlistInfo.description }}</p>
        <div class="actions">
          <button class="play-btn-lg" @click="handlePlay(playlistInfo.songs[0])" v-if="playlistInfo.songs.length > 0">
            <Play fill="currentColor" size="20" style="margin-right: 4px;" /> Play
          </button>

          <button class="secondary-btn" @click="openEditModal">
            <Edit size="18" /> Edit Info
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

    <!-- Edit Playlist Info Modal -->
    <Transition name="fade">
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal-content">
          <h3>Edit Playlist Info</h3>
          
          <div class="form-group">
            <label>Playlist Title</label>
            <input type="text" v-model="editForm.title" placeholder="Enter playlist title" />
          </div>

          <div class="form-group">
            <label>Description</label>
            <input type="text" v-model="editForm.description" placeholder="Enter description" />
          </div>

          <div class="form-group">
            <label>Cover Image</label>
            <div class="file-input-wrapper">
               <button class="file-select-btn">
                {{ editForm.coverFile ? 'Image Selected' : 'Change Cover' }}
              </button>
              <input type="file" @change="(e) => handleFileSelect(e, 'cover')" accept="image/*" />
            </div>
            <div v-if="editForm.coverFile" class="preview-actions">
              <span class="file-name">Image Selected</span>
              <a href="#" @click.prevent="openCropModal(currentRawCoverFile)" class="preview-link">Preview / Edit Crop</a>
            </div>
            <div v-else-if="editForm.coverPreview && !editForm.coverPreview.includes('placehold.co')" class="preview-actions">
               <span class="file-name">Current Cover</span>
               <a href="#" @click.prevent="openCropModal(null, editForm.coverPreview)" class="preview-link">Preview / Edit Crop</a>
            </div>
             <button v-if="editForm.coverPreview && !editForm.coverPreview.includes('placehold.co')" class="reset-btn" @click="resetPlaylistCover" style="margin-top: 8px; font-size: 12px; padding: 4px 8px;">
                Reset Cover
            </button>
          </div>

          <div class="modal-actions">
            <button class="cancel-btn" @click="showEditModal = false" :disabled="isUpdating">Cancel</button>
            <button class="submit-btn" @click="submitEdit" :disabled="isUpdating">
              {{ isUpdating ? 'Saving...' : 'Save Changes' }}
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
            <div v-if="uploadForm.coverFile" class="preview-actions">
              <span class="file-name">Image Selected</span>
              <a href="#" @click.prevent="openCropModal(currentRawCoverFile)" class="preview-link">Preview / Edit Crop</a>
            </div>
            <div v-else-if="uploadForm.coverPreview && !uploadForm.coverPreview.includes('placehold.co')" class="preview-actions">
               <span class="file-name">Current Cover</span>
               <a href="#" @click.prevent="openCropModal(null, uploadForm.coverPreview)" class="preview-link">Preview / Edit Crop</a>
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
        <div class="song-actions">
          <button class="action-btn" @click.stop="openEditSongModal(song)" title="Edit Song">
            <Edit size="16" />
          </button>
          <button class="action-btn delete-btn" @click.stop="confirmDelete(song)" title="Delete Song">
            <Trash2 size="16" />
          </button>
        </div>
      </div>
      
      <div v-if="playlistInfo.songs.length === 0" class="empty-state">
            No songs yet. Click "Add Songs" to upload.
          </div>
        </div>
      </div>
    </Transition>
    <!-- Edit Song Info Modal -->
    <Transition name="fade">
      <div v-if="showEditSongModal" class="modal-overlay" @click.self="showEditSongModal = false">
        <div class="modal-content">
          <h3>Edit Song Info</h3>
          
          <div class="form-group">
            <label>Song Title</label>
            <input type="text" v-model="editSongForm.title" placeholder="Enter song title" />
          </div>

          <div class="form-group">
            <label>Artist</label>
            <input type="text" v-model="editSongForm.artist" placeholder="Enter artist name" />
          </div>

          <div class="form-group">
            <label>Cover Image</label>
            <div class="file-input-wrapper">
               <button class="file-select-btn">
                {{ editSongForm.coverFile ? 'Image Selected' : 'Change Cover' }}
              </button>
              <input type="file" @change="(e) => handleFileSelect(e, 'cover')" accept="image/*" />
            </div>
            <div v-if="editSongForm.coverFile" class="preview-actions">
              <span class="file-name">Image Selected</span>
              <a href="#" @click.prevent="openCropModal(currentRawCoverFile)" class="preview-link">Preview / Edit Crop</a>
            </div>
            <div v-else-if="editSongForm.coverPreview && !editSongForm.coverPreview.includes('placehold.co')" class="preview-actions">
               <span class="file-name">Current Cover</span>
               <a href="#" @click.prevent="openCropModal(null, editSongForm.coverPreview)" class="preview-link">Preview / Edit Crop</a>
            </div>
            <button v-if="editSongForm.coverPreview && !editSongForm.coverPreview.includes('placehold.co')" class="reset-btn" @click="resetSongCover" style="margin-top: 8px; font-size: 12px; padding: 4px 8px;">
                Reset Cover
            </button>
          </div>

          <div class="modal-actions">
            <button class="cancel-btn" @click="showEditSongModal = false" :disabled="isUpdatingSong">Cancel</button>
            <button class="submit-btn" @click="submitEditSong" :disabled="isUpdatingSong">
              {{ isUpdatingSong ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Crop Modal -->
    <Transition name="fade">
      <div v-if="showCropModal" class="modal-overlay" style="z-index: 3000;">
        <div class="modal-content crop-dialog">
          <h3>Crop Cover Image</h3>
          <div class="crop-container">
             <canvas 
               ref="cropCanvas" 
               @mousedown.prevent="handleCropMouseDown" 
               @wheel.prevent="handleCropWheel"
               style="cursor: grab;"
             ></canvas>
             <div class="crop-hint">Scroll to zoom, drag to move</div>
          </div>
          <div class="modal-actions">
            <button class="cancel-btn" @click="showCropModal = false">Cancel</button>
            <button class="submit-btn" @click="confirmCrop">Confirm Crop</button>
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
  padding: 20px 40px;
  gap: 32px;
  align-items: flex-end;
  /* background: linear-gradient(to bottom, #f5f5f7, #ffffff); */ /* 移除背景色，保持干净 */
  position: relative;
  margin-top: 20px;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 40px; /* 对齐 padding */
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  background: var(--color-background-secondary); /* 默认有淡背景 */
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}

.back-btn:hover {
  background: var(--color-border);
  color: var(--color-text);
  transform: scale(1.05);
}

.cover-container {
  margin-top: 40px; /* 给返回按钮留出空间 */
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
  background: var(--color-background-secondary);
  color: var(--color-accent);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.1s;
}

.secondary-btn:hover {
  background: var(--color-border);
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
  background: var(--color-background);
  padding: 32px;
  border-radius: 16px;
  width: 400px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.reset-btn {
  background: transparent;
  color: var(--color-accent);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: var(--color-background-secondary);
  color: #e00;
  border-color: #e00;
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
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  background: var(--color-background);
  color: var(--color-text);
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
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  text-align: left;
  color: var(--color-text);
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

.preview-actions {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.file-name {
  color: var(--color-text-secondary);
}

.preview-link {
  color: var(--color-accent);
  text-decoration: underline;
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

.crop-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.crop-hint {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-top: 12px;
}

.crop-hint {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 12px;
  margin-top: 8px;
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
  transition: background-color 0.2s;
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

.song-actions {
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 12px;
}

.song-item:hover .song-actions {
  opacity: 1;
}

.action-btn {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--color-text);
}

.delete-btn:hover {
  color: #ff3b30;
}

/* Toast Styles */
.toast-notification {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-background);
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 14px;
  z-index: 3000;
  color: var(--color-text);
  border: 1px solid var(--color-border);
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
.crop-dialog {
  width: auto;
  max-width: 90vw;
}

.crop-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  cursor: move;
}

canvas {
  max-width: 100%;
  border: 1px solid var(--color-border);
}
</style>