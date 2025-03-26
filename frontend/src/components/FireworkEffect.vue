<template>
  <div class="firework-container" ref="container">
    <div v-for="(firework, index) in fireworks" 
         :key="index" 
         class="firework"
         :style="firework.style">
      <div v-for="(particle, pIndex) in firework.particles" 
           :key="pIndex" 
           class="particle"
           :style="particle.style">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FireworkEffect',
  props: {
    count: {
      type: Number,
      default: 5
    }
  },
  data() {
    return {
      fireworks: [],
      colors: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
    }
  },
  methods: {
    createParticle(x, y, color) {
      const angle = Math.random() * Math.PI * 2;
      const velocity = Math.random() * 3 + 2;
      return {
        x,
        y,
        color,
        velocityX: Math.cos(angle) * velocity,
        velocityY: Math.sin(angle) * velocity,
        size: Math.random() * 3 + 2,
        opacity: 1,
        style: {}
      };
    },
    createFirework() {
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const color = this.colors[Math.floor(Math.random() * this.colors.length)];
      const particleCount = Math.floor(Math.random() * 20) + 20;
      
      return {
        x,
        y,
        color,
        particles: Array(particleCount).fill().map(() => this.createParticle(x, y, color)),
        style: {
          left: `${x}%`,
          top: `${y}%`
        }
      };
    },
    updateParticleStyle(particle) {
      particle.style = {
        left: `${particle.x}%`,
        top: `${particle.y}%`,
        width: `${particle.size}px`,
        height: `${particle.size}px`,
        backgroundColor: particle.color,
        opacity: particle.opacity
      };
    },
    animate() {
      this.fireworks.forEach(firework => {
        firework.particles.forEach(particle => {
          particle.x += particle.velocityX;
          particle.y += particle.velocityY;
          particle.velocityY += 0.1; // 重力效果
          particle.opacity -= 0.01;
          this.updateParticleStyle(particle);
        });
        
        firework.particles = firework.particles.filter(p => p.opacity > 0);
      });
      
      this.fireworks = this.fireworks.filter(f => f.particles.length > 0);
      
      if (this.fireworks.length > 0) {
        requestAnimationFrame(this.animate);
      }
    },
    start() {
      this.fireworks = Array(this.count).fill().map(() => this.createFirework());
      this.animate();
    }
  },
  mounted() {
    this.start();
  }
}
</script>

<style scoped>
.firework-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1000;
}

.firework {
  position: absolute;
  transform: translate(-50%, -50%);
}

.particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  transition: opacity 0.1s linear;
}
</style> 