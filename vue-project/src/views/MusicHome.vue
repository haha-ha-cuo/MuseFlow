<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import PlaylistCard from '../components/PlaylistCard.vue'
import BaseModal from '../components/BaseModal.vue'
import { API_BASE_URL } from '@/config'

const router = useRouter()

// 1. 将 playlists 定义为响应式空数组
const playlists = ref([])
const showCreateModal = ref(false)
const newPlaylistTitle = ref('')
const isCreating = ref(false)

// 2. 定义获取数据的函数
const fetchPlaylists = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/playlists`)
    const result = await response.json()
    if (result.code === 200) {
      playlists.value = result.data
    } else {
      console.warn("后端返回错误:", result)
    }
  } catch (error) {
    console.error("连接后端失败", error)
  }
}

// 3. 打开创建歌单模态框
const openCreateModal = () => {
  newPlaylistTitle.value = ''
  showCreateModal.value = true
}

// 4. 确认创建歌单
const confirmCreatePlaylist = async () => {
  if (!newPlaylistTitle.value.trim()) return
  
  isCreating.value = true
  try {
    const response = await fetch(`${API_BASE_URL}/playlists/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: newPlaylistTitle.value,
        artist: "User" // 默认创建者
      })
    })
    
    const result = await response.json()
    if (result.code === 200) {
      showCreateModal.value = false
      // 重新获取列表
      fetchPlaylists()
    } else {
      alert("创建失败: " + result.msg)
    }
  } catch (error) {
    console.error("创建歌单失败:", error)
    alert("网络错误，请检查后端服务")
  } finally {
    isCreating.value = false
  }
}

// 5. 页面加载时自动请求数据
onMounted(() => {
  fetchPlaylists()
})

const goToPlaylist = (id) => {
  router.push(`/playlist/${id}`)
}
</script>

<template>
  <div class="home-page">
    <div class="header-actions">
      <h1>Listen Now</h1>
      <button @click="openCreateModal" class="add-btn">
        <Plus :size="20" />
        New Playlist
      </button>
    </div>
    
    <div class="grid">
      <PlaylistCard 
        v-for="list in playlists" 
        :key="list.id"
        v-bind="list"
        @click="goToPlaylist(list.id)"
      />
    </div>

    <!-- 创建歌单模态框 -->
    <BaseModal 
      :isOpen="showCreateModal" 
      title="Create New Playlist" 
      @close="showCreateModal = false"
    >
      <input 
        v-model="newPlaylistTitle" 
        placeholder="Playlist Name" 
        class="modal-input"
        @keyup.enter="confirmCreatePlaylist"
        autofocus
      />
      <template #footer>
        <button class="btn-cancel" @click="showCreateModal = false">Cancel</button>
        <button class="btn-confirm" @click="confirmCreatePlaylist" :disabled="!newPlaylistTitle.trim() || isCreating">
          {{ isCreating ? 'Creating...' : 'Create' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.home-page {
  padding: 40px;
  padding-bottom: 100px; /* Space for PlayerBar */
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--color-accent);
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: opacity 0.2s;
}

.add-btn:hover {
  opacity: 0.9;
}

h1 {
  font-size: 34px;
  font-weight: 700;
  margin-bottom: 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 24px;
}

/* Modal Styles */
.modal-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  background-color: var(--color-background-secondary);
  color: var(--color-text);
}

.modal-input:focus {
  border-color: var(--color-accent);
}

.btn-cancel {
  padding: 8px 16px;
  color: var(--color-text-secondary);
  font-weight: 500;
  border-radius: 6px;
}

.btn-cancel:hover {
  background-color: var(--color-background-secondary);
}

.btn-confirm {
  padding: 8px 16px;
  background-color: var(--color-accent);
  color: white;
  font-weight: 600;
  border-radius: 6px;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-confirm:not(:disabled):hover {
  opacity: 0.9;
}
</style>
  