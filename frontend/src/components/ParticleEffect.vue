<template>
  <div class="particle-container" ref="container">
    <div v-for="(particle, index) in particles" 
         :key="index" 
         class="particle"
         :style="particle.style">
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParticleEffect',
  props: {
    color: {
      type: String,
      default: '#ffd700'
    },
    count: {
      type: Number,
      default: 20
    }
  },
  data() {
    return {
      particles: []
    }
  },
  methods: {
    createParticle() {
      const particle = {
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 3 + 2,
        speedX: (Math.random() - 0.5) * 8,
        speedY: (Math.random() - 0.5) * 8,
        opacity: 1,
        style: {}
      }
      this.updateParticleStyle(particle);
      return particle;
    },
    updateParticleStyle(particle) {
      particle.style = {
        left: `${particle.x}%`,
        top: `${particle.y}%`,
        width: `${particle.size}px`,
        height: `${particle.size}px`,
        opacity: particle.opacity,
        backgroundColor: this.color
      }
    },
    animate() {
      this.particles.forEach(particle => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        particle.opacity -= 0.02;
        this.updateParticleStyle(particle);
      });
      
      this.particles = this.particles.filter(p => p.opacity > 0);
      
      if (this.particles.length > 0) {
        requestAnimationFrame(this.animate);
      }
    },
    start() {
      this.particles = Array(this.count).fill().map(() => this.createParticle());
      this.animate();
    }
  },
  mounted() {
    this.start();
  }
}
</script>

<style scoped>
.particle-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1000;
}

.particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  transition: opacity 0.1s linear;
}
</style> 