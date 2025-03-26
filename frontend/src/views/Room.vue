<template>
  <div class="room-container">
    <div class="room-header">
      <el-button @click="$router.push('/')">返回首页</el-button>
      <div class="room-info">
        <h2>房间号: {{ roomId }}</h2>
        <div class="player-count">
          玩家数: {{ playerCount }}/4
        </div>
      </div>
    </div>

    <div class="room-content">
      <div v-if="!isHost" class="waiting-message">
        <el-alert
          title="等待房主开始游戏"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <div v-else-if="playerCount < 4" class="waiting-message">
        <el-alert
          :title="`等待其他玩家加入 (${playerCount}/4)`"
          type="warning"
          :closable="false"
          show-icon
        />
      </div>

      <div v-else class="start-game">
        <el-button type="primary" size="large" @click="startGame">
          开始游戏
        </el-button>
      </div>

      <div class="player-list">
        <el-card v-for="(player, index) in players" 
                 :key="index" 
                 class="player-card"
                 :class="{ 'host': index === 0 }">
          <template #header>
            <div class="player-header">
              <span>玩家 {{ index + 1 }}</span>
              <el-tag v-if="index === 0" type="success" size="small">房主</el-tag>
            </div>
          </template>
          <div class="player-status">
            {{ player.ready ? '已准备' : '未准备' }}
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Room',
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      players: [
        { ready: true },
        { ready: false },
        { ready: false },
        { ready: false }
      ]
    }
  },
  computed: {
    ...mapState(['playerIndex']),
    playerCount() {
      return this.players.filter(p => p.ready).length
    },
    isHost() {
      return this.playerIndex === 0
    }
  },
  methods: {
    ...mapActions(['joinRoom']),
    startGame() {
      this.$router.push('/game/online')
    }
  },
  created() {
    this.$store.dispatch('connectSocket')
    this.$store.dispatch('joinRoom', this.roomId)
  }
}
</script>

<style scoped>
.room-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.room-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.room-info h2 {
  margin: 0;
  color: #409EFF;
}

.room-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.waiting-message {
  margin: 20px 0;
}

.start-game {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.player-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.player-card {
  text-align: center;
}

.player-card.host {
  border-color: #409EFF;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.player-status {
  color: #909399;
}
</style> 