import { createRouter, createWebHistory } from 'vue-router'
import MusicHome from '../views/MusicHome.vue'
import PlaylistDetail from '../views/PlaylistDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: MusicHome
    },
    {
      path: '/playlist/:id',
      name: 'playlist',
      component: PlaylistDetail
    }
  ]
})

export default router
