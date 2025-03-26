<template>
  <div class="lobby">
    <h1>等待其他玩家加入</h1>
    
    <div class="room-info">
      <p>房间ID: <span>{{ roomId }}</span></p>
      <p>当前人数: <span>{{ playerCount }}/4</span></p>
    </div>
    
    <div class="invite-link">
      <h2>邀请好友</h2>
      <div class="link-container">
        <input v-model="inviteLink" readonly />
        <button @click="copyLink">复制链接</button>
      </div>
    </div>
    
    <div class="players-list">
      <h2>玩家列表</h2>
      <ul>
        <li v-for="(player, index) in players" :key="index">
          {{ player.name }}
          <span v-if="player.id === playerId">(你)</span>
        </li>
      </ul>
    </div>
    
    <div class="waiting-message" v-if="playerCount < 4">
      <p>正在等待其他玩家加入...</p>
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
    
    <button class="back-button" @click="goBack">返回主页</button>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'Lobby',
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      playerId: '',
      players: [],
      playerCount: 1,
      pollInterval: null
    }
  },
  computed: {
    inviteLink() {
      return `${window.location.origin}/lobby/${this.roomId}`;
    }
  },
  created() {
    // 从 URL 获取 playerId
    this.playerId = this.$route.query.playerId;
    
    // 开始定时获取房间状态
    this.pollRoomStatus();
    this.pollInterval = setInterval(this.pollRoomStatus, 3000);
  },
  beforeUnmount() {
    // 清除定时器
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  },
  methods: {
    async pollRoomStatus() {
      try {
        const response = await api.get(`/game/status/${this.roomId}`);
        this.players = response.data.players;
        this.playerCount = this.players.length;
        
        // 如果人数已满，跳转到游戏页面
        if (this.playerCount === 4) {
          this.$router.push({
            name: 'Game',
            params: { roomId: this.roomId },
            query: { playerId: this.playerId }
          });
        }
      } catch (error) {
        console.error('获取房间状态失败', error);
      }
    },
    copyLink() {
      navigator.clipboard.writeText(this.inviteLink)
        .then(() => {
          alert('邀请链接已复制到剪贴板');
        })
        .catch(err => {
          console.error('复制失败:', err);
        });
    },
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.lobby {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 30px;
}

h2 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-top: 30px;
  margin-bottom: 15px;
}

.room-info {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.room-info p {
  font-size: 1.2rem;
  margin: 10px 0;
}

.room-info span {
  font-weight: bold;
  color: #42b983;
}

.invite-link {
  margin-bottom: 30px;
}

.link-container {
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
}

button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #3aa876;
}

.players-list {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

ul {
  list-style: none;
  padding: 0;
}

li {
  font-size: 1.2rem;
  padding: 10px;
  border-bottom: 1px solid #e9ecef;
}

li:last-child {
  border-bottom: none;
}

.waiting-message {
  margin-top: 30px;
  font-size: 1.2rem;
  color: #6c757d;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 15px;
}

.loading-dots span {
  width: 12px;
  height: 12px;
  background-color: #42b983;
  border-radius: 50%;
  display: inline-block;
  animation: loading 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.back-button {
  margin-top: 40px;
  background-color: #6c757d;
}

.back-button:hover {
  background-color: #5a6268;
}
</style> 