<template>
  <div class="sound-manager">
    <audio ref="cardSound" src="/assets/sounds/card.mp3" preload="auto"></audio>
    <audio ref="winSound" src="/assets/sounds/win.mp3" preload="auto"></audio>
    <audio ref="loseSound" src="/assets/sounds/lose.mp3" preload="auto"></audio>
    <audio ref="levelUpSound" src="/assets/sounds/level-up.mp3" preload="auto"></audio>
    <audio ref="shuffleSound" src="/assets/sounds/shuffle.mp3" preload="auto"></audio>
    <audio ref="dealSound" src="/assets/sounds/deal.mp3" preload="auto"></audio>
    <audio ref="buttonSound" src="/assets/sounds/button.mp3" preload="auto"></audio>
    <audio ref="fireworkSound" src="/assets/sounds/firework.mp3" preload="auto"></audio>
  </div>
</template>

<script>
export default {
  name: 'SoundManager',
  data() {
    return {
      isMuted: false,
      volume: 0.5
    }
  },
  methods: {
    playCardSound() {
      this.playSound('cardSound');
    },
    playWinSound() {
      this.playSound('winSound');
    },
    playLoseSound() {
      this.playSound('loseSound');
    },
    playLevelUpSound() {
      this.playSound('levelUpSound');
    },
    playShuffleSound() {
      this.playSound('shuffleSound');
    },
    playDealSound() {
      this.playSound('dealSound');
    },
    playButtonSound() {
      this.playSound('buttonSound');
    },
    playFireworkSound() {
      this.playSound('fireworkSound');
    },
    playSound(soundName) {
      if (this.isMuted) return;
      const sound = this.$refs[soundName];
      if (sound) {
        sound.currentTime = 0;
        sound.volume = this.volume;
        sound.play().catch(error => {
          console.warn('Sound playback failed:', error);
        });
      }
    },
    setMute(muted) {
      this.isMuted = muted;
    },
    setVolume(volume) {
      this.volume = Math.max(0, Math.min(1, volume));
    }
  }
}
</script>

<style scoped>
.sound-manager {
  display: none;
}
</style> 