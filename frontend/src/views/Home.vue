<template>
  <div class="home">
    <h1>掼蛋游戏</h1>
    <div class="mode-selection">
      <div class="mode-card" @click="selectMode('single')">
        <h2>单人模式</h2>
        <p>与AI对战</p>
      </div>
      <div class="mode-card" @click="selectMode('multiplayer')">
        <h2>多人模式</h2>
        <p>邀请好友一起玩</p>
      </div>
    </div>
    <div v-if="selectedMode" class="player-info">
      <input v-model="playerName" placeholder="请输入您的名字" />
      <button @click="startGame" :disabled="!playerName">开始游戏</button>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'Home',
  data() {
    return {
      selectedMode: '',
      playerName: ''
    }
  },
  methods: {
    selectMode(mode) {
      this.selectedMode = mode;
    },
    async startGame() {
      try {
        // 创建游戏
        const response = await api.get(`/game/create?player_name=${encodeURIComponent(this.playerName)}&mode=${this.selectedMode}`);
        
        if (this.selectedMode === 'single') {
          // 单人模式直接进入游戏
          this.$router.push({
            name: 'Game',
            params: { roomId: response.data.roomId },
            query: { playerId: response.data.playerId }
          });
        } else {
          // 多人模式进入大厅
          this.$router.push({
            name: 'Lobby',
            params: { roomId: response.data.roomId },
            query: { playerId: response.data.playerId }
          });
        }
      } catch (error) {
        console.error('创建游戏失败', error);
        alert('创建游戏失败，请重试');
      }
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 40px;
}

.mode-selection {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 40px;
}

.mode-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  width: 200px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.mode-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.mode-card h2 {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #2c3e50;
}

.mode-card p {
  color: #6c757d;
}

.player-info {
  margin-top: 30px;
}

input {
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  width: 300px;
  margin-right: 10px;
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

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style> 