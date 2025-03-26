<template>
  <div class="game-container">
    <!-- 游戏信息 -->
    <div class="game-info">
      <div class="level">当前等级: {{ currentLevel }}</div>
      <div class="room-id" v-if="roomId">房间号: {{ roomId }}</div>
    </div>

    <!-- 其他玩家区域 -->
    <div class="other-players">
      <div v-for="(player, index) in otherPlayers" 
           :key="index" 
           class="player-area"
           :class="{ 'player-area--active': player.isActive }">
        <div class="player-avatar">
          <img :src="getAvatarUrl(player.avatar)" :alt="player.name">
          <div class="player-status" :class="{ 'player-status--active': player.isActive }"></div>
        </div>
        <div class="player-info">
          <div class="player-name">{{ player.name }}</div>
          <div class="card-count">剩余: {{ player.cardCount }}张</div>
        </div>
        <div class="played-cards" v-if="player.lastPlayedCards">
          <Card
            v-for="(card, cardIndex) in player.lastPlayedCards"
            :key="cardIndex"
            :suit="card[0]"
            :rank="card.slice(1)"
            :played="true"
            :hoverable="false"
            :position="{ x: cardIndex * 20, y: 0 }"
          />
        </div>
      </div>
    </div>

    <!-- 玩家手牌区域 -->
    <div class="player-hand">
      <div class="hand-controls">
        <button @click="sortCards" class="btn btn-sort">
          {{ sortMode === 'suit' ? '按大小排序' : '按花色排序' }}
        </button>
      </div>
      <div class="cards">
        <Card
          v-for="(card, index) in sortedPlayerHand"
          :key="index"
          :suit="card[0]"
          :rank="card.slice(1)"
          :selected="selectedCards.includes(card)"
          @click="handleCardClick(card)"
          :position="{ x: index * 15, y: 0 }"
          :index="index"
          :stacked="true"
        />
      </div>
      <div class="controls">
        <button @click="handlePlayCards" :disabled="!canPlay" class="btn btn-primary">
          出牌
        </button>
        <button @click="passTurn" :disabled="!canPass" class="btn btn-secondary">
          过牌
        </button>
      </div>
    </div>

    <!-- 粒子效果 -->
    <ParticleEffect
      v-if="showParticles"
      :color="particleColor"
      :count="30"
    />

    <!-- 游戏结束弹窗 -->
    <div v-if="gameEnd" class="game-end-modal">
      <div class="modal-content">
        <h2>游戏结束</h2>
        <p>{{ gameEndMessage }}</p>
        <button @click="startNewGame" class="btn btn-primary">开始新游戏</button>
      </div>
    </div>

    <!-- 洗牌动画 -->
    <div v-if="isShuffling" class="shuffle-animation">
      <div class="shuffle-cards">
        <Card
          v-for="n in 52"
          :key="n"
          :face-down="true"
          :hoverable="false"
          :position="getShufflePosition(n)"
        />
      </div>
    </div>

    <!-- 发牌动画 -->
    <div v-if="isDealing" class="dealing-animation">
      <div class="dealing-cards">
        <Card
          v-for="(card, index) in dealingCards"
          :key="index"
          :suit="card[0]"
          :rank="card.slice(1)"
          :face-down="true"
          :hoverable="false"
          :position="getDealingPosition(index)"
        />
      </div>
    </div>

    <!-- 烟花效果 -->
    <FireworkEffect
      v-if="showFireworks"
      :count="5"
    />

    <!-- 音效管理器 -->
    <SoundManager ref="soundManager" />
  </div>
</template>

<script>
import Card from '../components/Card.vue';
import ParticleEffect from '../components/ParticleEffect.vue';
import FireworkEffect from '../components/FireworkEffect.vue';
import SoundManager from '../components/SoundManager.vue';
import { io } from 'socket.io-client';

export default {
  name: 'Game',
  components: {
    Card,
    ParticleEffect,
    FireworkEffect,
    SoundManager
  },
  data() {
    return {
      socket: null,
      roomId: null,
      currentLevel: 2,
      playerHand: [],
      selectedCards: [],
      otherPlayers: [],
      gameEnd: false,
      gameEndMessage: '',
      canPlay: false,
      canPass: false,
      isShuffling: false,
      isDealing: false,
      dealingCards: [],
      showParticles: false,
      particleColor: '#ffd700',
      showFireworks: false,
      sortMode: 'suit',
      gameState: {
        currentPlayer: 0,
        lastPlay: null,
        lastPlayer: -1,
        gameStarted: false,
        gameOver: false,
        winner: null,
        players: [
          { id: 0, name: '玩家', hand: [], isHuman: true },
          { id: 1, name: '电脑1', hand: [], isHuman: false },
          { id: 2, name: '电脑2', hand: [], isHuman: false },
          { id: 3, name: '电脑3', hand: [], isHuman: false }
        ]
      }
    }
  },
  computed: {
    sortedPlayerHand() {
      if (!this.playerHand.length) return [];
      
      const cards = this.playerHand.slice();
      if (this.sortMode === 'suit') {
        // 按花色排序：♠、♥、♦、♣、小王、大王
        const suitOrder = { '♠': 1, '♥': 2, '♦': 3, '♣': 4, '小': 5, '大': 6 };
        return cards.sort((a, b) => {
          const suitA = suitOrder[a[0]] || 0;
          const suitB = suitOrder[b[0]] || 0;
          if (suitA !== suitB) return suitA - suitB;
          return this.getRankValue(a.slice(1)) - this.getRankValue(b.slice(1));
        });
      } else {
        // 按大小排序
        return cards.sort((a, b) => {
          const rankA = this.getRankValue(a.slice(1));
          const rankB = this.getRankValue(b.slice(1));
          if (rankA !== rankB) return rankA - rankB;
          const suitOrder = { '♠': 1, '♥': 2, '♦': 3, '♣': 4 };
          return (suitOrder[a[0]] || 0) - (suitOrder[b[0]] || 0);
        });
      }
    }
  },
  created() {
    this.roomId = this.$route.params.roomId;
    this.connectSocket();
  },
  mounted() {
    // 自动开始游戏
    this.startGame();
  },
  methods: {
    connectSocket() {
      this.socket = io('http://localhost:8000');
      
      this.socket.on('connect', () => {
        console.log('Connected to server');
        if (this.roomId) {
          this.socket.emit('join_room', { room_id: this.roomId });
        } else {
          this.socket.emit('create_room');
        }
      });

      this.socket.on('room_created', (data) => {
        this.roomId = data.room_id;
        this.$router.push(`/game/${this.roomId}`);
      });

      this.socket.on('game_state_update', (data) => {
        this.updateGameState(data);
      });

      this.socket.on('card_played', (data) => {
        this.handleCardPlayed(data);
      });

      this.socket.on('turn_passed', (data) => {
        this.handleTurnPassed(data);
      });

      this.socket.on('game_end', (data) => {
        this.handleGameEnd(data);
      });
    },
    updateGameState(data) {
      this.currentLevel = data.current_level;
      this.playerHand = data.players_hands[0];
      this.updateOtherPlayers(data);
      this.updateControls(data);
    },
    updateOtherPlayers(data) {
      this.otherPlayers = data.players_hands.slice(1).map((hand, index) => ({
        name: `玩家${index + 2}`,
        cardCount: hand.length,
        lastPlayedCards: data.last_played_cards,
        isActive: data.current_player === index + 1,
        avatar: `/assets/images/avatar${(index % 4) + 1}.png`
      }));
    },
    updateControls(data) {
      this.canPlay = data.current_player === 0;
      this.canPass = data.last_played_cards && data.current_player === 0;
    },
    handleCardClick(card) {
      if (!this.canPlay) return;
      
      const index = this.playerHand.indexOf(card);
      if (index === -1) return;
      
      if (this.selectedCards.includes(card)) {
        // 取消选择
        this.selectedCards = this.selectedCards.filter(c => c !== card);
      } else {
        // 选择卡牌
        this.selectedCards.push(card);
      }
      
      // 播放音效
      this.$refs.soundManager.playCardSound();
    },
    
    handlePlayCards() {
      if (!this.canPlay || this.selectedCards.length === 0) return;
      
      // 检查出牌是否合法
      const isValid = this.checkPlayValid(this.selectedCards);
      if (!isValid) {
        this.$message.error('出牌不合法');
        return;
      }
      
      // 发送出牌消息
      this.socket.emit('play_cards', {
        room_id: this.roomId,
        cards: this.selectedCards
      });
      
      // 清空选中的卡牌
      this.selectedCards = [];
      
      // 播放音效
      this.$refs.soundManager.playPlaySound();
    },
    
    checkPlayValid(cards) {
      // 如果是第一手牌，可以任意出
      if (!this.gameState.lastPlay) return true;
      
      // 检查出牌数量是否相同
      if (cards.length !== this.gameState.lastPlay.length) return false;
      
      // 检查出牌类型是否相同
      const lastType = this.getCardsType(this.gameState.lastPlay);
      const currentType = this.getCardsType(cards);
      
      return lastType === currentType;
    },
    
    getCardsType(cards) {
      // 获取卡牌类型（单张、对子、顺子等）
      if (cards.length === 1) return 'single';
      if (cards.length === 2 && cards[0].slice(1) === cards[1].slice(1)) return 'pair';
      if (cards.length >= 3 && this.isStraight(cards)) return 'straight';
      return 'invalid';
    },
    
    isStraight(cards) {
      // 检查是否为顺子
      const values = cards.map(card => this.getRankValue(card.slice(1))).sort((a, b) => a - b);
      for (let i = 1; i < values.length; i++) {
        if (values[i] !== values[i-1] + 1) return false;
      }
      return true;
    },
    
    getRankValue(rank) {
      const rankValues = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, '王': 15
      };
      return rankValues[rank] || 0;
    },
    passTurn() {
      this.socket.emit('pass_turn', {
        room_id: this.roomId
      });
    },
    handleCardPlayed(data) {
      // 更新其他玩家的出牌信息
      const playerIndex = this.otherPlayers.findIndex(p => p.name === data.player);
      if (playerIndex !== -1) {
        this.otherPlayers[playerIndex].lastPlayedCards = data.cards;
      }
    },
    handleTurnPassed(data) {
      // 更新过牌信息
      const playerIndex = this.otherPlayers.findIndex(p => p.name === data.player);
      if (playerIndex !== -1) {
        this.otherPlayers[playerIndex].lastPlayedCards = null;
      }
    },
    handleGameEnd(data) {
      this.gameEnd = true;
      const isWinner = data.winner_team === 0;
      this.gameEndMessage = isWinner ? '恭喜你获胜！' : '很遗憾，你输了。';
      
      if (isWinner) {
        this.showFireworks = true;
        this.$refs.soundManager.playWinSound();
        this.$refs.soundManager.playFireworkSound();
      } else {
        this.$refs.soundManager.playLoseSound();
      }
      
      if (data.new_level > this.currentLevel) {
        this.$refs.soundManager.playLevelUpSound();
      }
    },
    startNewGame() {
      this.gameEnd = false;
      this.showFireworks = false;
      this.$refs.soundManager.playButtonSound();
      this.socket.emit('create_room');
    },
    getShufflePosition(index) {
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const radius = 200;
      const angle = (index / 52) * Math.PI * 2;
      return {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius
      };
    },
    startShuffleAnimation() {
      this.isShuffling = true;
      this.$refs.soundManager.playShuffleSound();
      setTimeout(() => {
        this.isShuffling = false;
        this.startDealingAnimation();
      }, 2000);
    },
    startDealingAnimation() {
      this.isDealing = true;
      this.dealingCards = [...this.playerHand];
      this.$refs.soundManager.playDealSound();
      setTimeout(() => {
        this.isDealing = false;
      }, 3000);
    },
    getDealingPosition(index) {
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const targetX = (index % 13) * 80 - 520;
      const targetY = Math.floor(index / 13) * 120 - 60;
      return {
        x: centerX + targetX,
        y: centerY + targetY
      };
    },
    getAvatarUrl(avatar) {
      return avatar || '';  // 暂时返回空字符串
    },
    initializeDeck() {
      const deck = [];
      const suits = ['♠', '♥', '♦', '♣'];
      const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
      
      // 添加两副牌
      for (let i = 0; i < 2; i++) {
        // 添加普通牌
        for (const suit of suits) {
          for (const rank of ranks) {
            deck.push(suit + rank);
          }
        }
        // 添加大小王
        deck.push('小王');
        deck.push('大王');
      }
      
      return deck;
    },
    shuffleDeck(deck) {
      for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
      }
    },
    dealCards(deck) {
      // 每个玩家27张牌
      for (let i = 0; i < 27; i++) {
        for (let player = 0; player < 4; player++) {
          this.gameState.players[player].hand.push(deck.pop());
        }
      }
      
      // 更新玩家手牌显示
      this.playerHand = this.gameState.players[0].hand;
      
      // 更新其他玩家信息
      this.otherPlayers = this.gameState.players.slice(1).map((player, index) => ({
        name: `电脑${index + 1}`,
        cardCount: player.hand.length,
        lastPlayedCards: null,
        isActive: false,
        avatar: ''
      }));
    },
    startGame() {
      // 重置游戏状态
      this.gameState = {
        currentPlayer: 0,
        lastPlay: null,
        lastPlayer: -1,
        gameStarted: true,
        gameOver: false,
        winner: null,
        players: [
          { id: 0, name: '玩家', hand: [], isHuman: true },
          { id: 1, name: '电脑1', hand: [], isHuman: false },
          { id: 2, name: '电脑2', hand: [], isHuman: false },
          { id: 3, name: '电脑3', hand: [], isHuman: false }
        ]
      };
      
      // 初始化牌组
      const deck = this.initializeDeck();
      
      // 洗牌
      this.shuffleDeck(deck);
      
      // 发牌
      this.dealCards(deck);
      
      // 播放发牌音效
      this.$refs.soundManager.playDealSound();
      
      // 开始洗牌动画
      this.startShuffleAnimation();
      
      // 开始发牌动画
      setTimeout(() => {
        this.startDealingAnimation();
      }, 2000);
    },
    sortCards() {
      this.sortMode = this.sortMode === 'suit' ? 'rank' : 'suit';
      this.$refs.soundManager.playButtonSound();
    }
  }
}
</script>

<style scoped>
.game-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  background-color: #1a472a;  /* 使用纯色背景代替图片 */
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.game-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.game-info {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 10px;
  margin-bottom: 20px;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 2;
}

.other-players {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  z-index: 2;
}

.player-area {
  background: rgba(0, 0, 0, 0.6);
  padding: 15px;
  border-radius: 10px;
  min-width: 150px;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.player-area--active {
  border-color: #4CAF50;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
}

.player-avatar {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto 10px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.player-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.player-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #666;
  border: 2px solid rgba(0, 0, 0, 0.5);
}

.player-status--active {
  background: #4CAF50;
  box-shadow: 0 0 10px #4CAF50;
}

.player-info {
  text-align: center;
  margin-bottom: 10px;
}

.player-name {
  font-size: 1.2em;
  margin-bottom: 5px;
  color: #fff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.card-count {
  font-size: 0.9em;
  opacity: 0.8;
  margin-bottom: 10px;
}

.played-cards {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-top: 10px;
  min-height: 100px;
}

.player-hand {
  margin-top: auto;
  background: rgba(0, 0, 0, 0.6);
  padding: 20px;
  border-radius: 10px;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 2;
}

.hand-controls {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.btn-sort {
  background: #2196F3;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-sort:hover {
  background: #1976D2;
  transform: translateY(-2px);
}

.cards {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  min-height: 120px;
  position: relative;
  padding: 0 20px;
}

.cards .card {
  position: absolute;
  transition: all 0.3s ease;
  transform-origin: left center;
}

.cards .card--stacked {
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
}

.cards .card--stacked:hover {
  transform: translateX(10px);
}

.cards .card--selected {
  transform: translateY(-20px);
  z-index: 100;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.btn {
  padding: 12px 24px;
  font-size: 1.1em;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: bold;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: #f44336;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #da190b;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.game-end-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 15px;
  text-align: center;
  color: #333;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: modalAppear 0.3s ease-out;
}

.modal-content h2 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 2em;
}

.modal-content p {
  margin-bottom: 20px;
  font-size: 1.2em;
  color: #666;
}

.shuffle-animation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.shuffle-cards {
  position: relative;
  width: 100%;
  height: 100%;
}

.dealing-animation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.dealing-cards {
  position: relative;
  width: 100%;
  height: 100%;
}

.dealing-cards .card {
  position: absolute;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation: dealCard 0.5s ease-out forwards;
}

@keyframes modalAppear {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes dealCard {
  from {
    transform: translate(0, 0) scale(0.5);
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .game-container {
    padding: 10px;
  }

  .game-info {
    flex-direction: column;
    gap: 5px;
    padding: 10px;
  }

  .other-players {
    flex-wrap: wrap;
    gap: 10px;
  }

  .player-avatar {
    width: 40px;
    height: 40px;
  }

  .player-status {
    width: 8px;
    height: 8px;
  }

  .player-area {
    min-width: 100px;
    padding: 10px;
  }

  .player-hand {
    padding: 10px;
  }

  .cards {
    padding: 0 10px;
  }

  .cards .card {
    transform: scale(0.8);
  }
  
  .cards .card--stacked:hover {
    transform: translateX(5px) scale(0.8);
  }
  
  .cards .card--selected {
    transform: translateY(-10px) scale(0.8);
  }

  .controls {
    flex-direction: column;
    gap: 10px;
  }

  .btn {
    width: 100%;
    padding: 10px;
  }

  .modal-content {
    width: 90%;
    max-width: 300px;
    padding: 20px;
  }

  .modal-content h2 {
    font-size: 1.5em;
  }

  .modal-content p {
    font-size: 1em;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .game-container {
    padding: 5px;
  }

  .game-info {
    margin-bottom: 10px;
  }

  .other-players {
    margin-bottom: 10px;
  }

  .player-avatar {
    width: 30px;
    height: 30px;
  }

  .player-status {
    width: 6px;
    height: 6px;
  }

  .player-area {
    min-width: 80px;
    padding: 5px;
  }

  .player-name {
    font-size: 1em;
  }

  .card-count {
    font-size: 0.8em;
  }

  .played-cards {
    min-height: 80px;
  }

  .player-hand {
    padding: 10px;
  }

  .cards {
    min-height: 100px;
  }
}

/* 烟花效果容器 */
.firework-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1001;
}
</style> 