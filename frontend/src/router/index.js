import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Game from '../views/Game.vue'
import Lobby from '../views/Lobby.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/game/:roomId',
    name: 'Game',
    component: Game,
    props: true
  },
  {
    path: '/lobby/:roomId?',
    name: 'Lobby',
    component: Lobby,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 