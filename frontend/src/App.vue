<template>
  <div id="app">
    <router-view></router-view>
    <audio ref="cardSound" src="/sounds/card.mp3"></audio>
    <audio ref="winSound" src="/sounds/win.mp3"></audio>
    <audio ref="loseSound" src="/sounds/lose.mp3"></audio>
    <audio ref="levelUpSound" src="/sounds/level-up.mp3"></audio>
  </div>
</template>

<script>
export default {
  name: 'App',
  methods: {
    playCardSound() {
      this.$refs.cardSound.currentTime = 0;
      this.$refs.cardSound.play();
    },
    playWinSound() {
      this.$refs.winSound.currentTime = 0;
      this.$refs.winSound.play();
    },
    playLoseSound() {
      this.$refs.loseSound.currentTime = 0;
      this.$refs.loseSound.play();
    },
    playLevelUpSound() {
      this.$refs.levelUpSound.currentTime = 0;
      this.$refs.levelUpSound.play();
    }
  }
}
</script>

<style>
#app {
  font-family: 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style> 