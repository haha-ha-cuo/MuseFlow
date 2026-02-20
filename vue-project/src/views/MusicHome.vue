<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import PlaylistCard from '../components/PlaylistCard.vue'

const router = useRouter()

// 1. 将 playlists 定义为响应式空数组
const playlists = ref([])

// 2. 定义获取数据的函数
const fetchPlaylists = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/playlists')
    const result = await response.json()
    if (result.code === 200) {
      playlists.value = result.data
    } else {
      console.warn("后端返回错误:", result)
    }
  } catch (error) {
    console.error("连接后端失败。请检查：\n1. python main.py 是否正在运行？\n2. 端口是否为 5000？", error)
  }
}

// 3. 页面加载时自动请求数据
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
    </div>
    
    <div class="grid">
      <PlaylistCard 
        v-for="list in playlists" 
        :key="list.id"
        v-bind="list"
        @click="goToPlaylist(list.id)"
      />
    </div>
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
</style>
  