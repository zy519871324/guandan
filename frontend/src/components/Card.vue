<template>
  <div 
    class="card" 
    :class="{
      'card--selected': selected,
      'card--face-down': faceDown,
      'card--played': played,
      'card--hoverable': hoverable,
      'card--stacked': stacked
    }"
    :style="cardStyle"
    @click="handleClick"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <div class="card__inner">
      <div class="card__front">
        <div class="card__suit card__suit--top">{{ suit }}</div>
        <div class="card__rank card__rank--top">{{ rank }}</div>
        <div class="card__suit card__suit--bottom">{{ suit }}</div>
        <div class="card__rank card__rank--bottom">{{ rank }}</div>
      </div>
      <div class="card__back"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Card',
  props: {
    suit: {
      type: String,
      required: true
    },
    rank: {
      type: String,
      required: true
    },
    selected: {
      type: Boolean,
      default: false
    },
    faceDown: {
      type: Boolean,
      default: false
    },
    played: {
      type: Boolean,
      default: false
    },
    hoverable: {
      type: Boolean,
      default: true
    },
    stacked: {
      type: Boolean,
      default: false
    },
    position: {
      type: Object,
      default: () => ({ x: 0, y: 0 })
    },
    index: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      touchStartX: 0,
      touchStartY: 0,
      isDragging: false
    }
  },
  computed: {
    cardStyle() {
      return {
        transform: `translate(${this.position.x}px, ${this.position.y}px)`,
        zIndex: this.selected ? 100 : 1
      }
    }
  },
  methods: {
    handleClick() {
      if (!this.hoverable) return
      this.$emit('click')
    },
    handleTouchStart(event) {
      if (!this.hoverable) return;
      this.touchStartX = event.touches[0].clientX;
      this.touchStartY = event.touches[0].clientY;
      this.isDragging = false;
    },
    handleTouchMove(event) {
      if (!this.hoverable) return;
      const touchX = event.touches[0].clientX;
      const touchY = event.touches[0].clientY;
      const deltaX = touchX - this.touchStartX;
      const deltaY = touchY - this.touchStartY;
      
      if (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10) {
        this.isDragging = true;
      }
    },
    handleTouchEnd(event) {
      if (!this.hoverable) return;
      if (!this.isDragging) {
        this.handleClick();
      }
      this.isDragging = false;
    }
  }
}
</script>

<style scoped>
.card {
  width: 70px;
  height: 100px;
  perspective: 1000px;
  cursor: pointer;
  position: relative;
  transition: transform 0.3s ease;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  touch-action: none; /* 防止触摸事件的默认行为 */
  -webkit-touch-callout: none; /* 防止长按菜单 */
  -webkit-user-select: none; /* 防止文本选择 */
}

.card--hoverable:hover {
  transform: translateY(-10px) !important;
}

.card--selected {
  transform: translateY(-20px) !important;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.card--played {
  animation: playCard 0.5s ease-out;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.card__inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.card--face-down .card__inner {
  transform: rotateY(180deg);
}

.card__front,
.card__back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 1.5em;
  font-weight: bold;
}

.card__front {
  background: white;
  color: #333;
  border: 2px solid #ddd;
  position: relative;
}

.card__back {
  background: linear-gradient(45deg, #b22222 25%, transparent 25%),
              linear-gradient(-45deg, #b22222 25%, transparent 25%),
              linear-gradient(45deg, transparent 75%, #b22222 75%),
              linear-gradient(-45deg, transparent 75%, #b22222 75%);
  background-size: 20px 20px;
  background-color: #d40000;
  transform: rotateY(180deg);
}

.card__suit {
  position: absolute;
  font-size: 0.6em;
  line-height: 1;
}

.card__suit--top {
  top: 5px;
  right: 5px;
}

.card__suit--bottom {
  bottom: 5px;
  left: 5px;
  transform: rotate(180deg);
}

.card__rank {
  position: absolute;
  font-size: 0.55em;
  line-height: 1;
}

.card__rank--top {
  top: 5px;
  left: 5px;
}

.card__rank--bottom {
  bottom: 5px;
  right: 5px;
  transform: rotate(180deg);
}

.card__suit[data-suit="♥"],
.card__suit[data-suit="♦"] {
  color: #ff0000 !important;  /* 使用 !important 确保红色生效 */
}

.card__suit[data-suit="♠"],
.card__suit[data-suit="♣"] {
  color: #000000 !important;
}

@keyframes playCard {
  0% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
  50% {
    transform: scale(1.2) translateY(-20px);
    opacity: 0.8;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card {
    width: 50px;
    height: 70px;
  }

  .card__suit {
    font-size: 0.5em;
  }

  .card__rank {
    font-size: 0.45em;
  }

  .card__suit--top,
  .card__rank--top {
    top: 3px;
  }

  .card__suit--bottom,
  .card__rank--bottom {
    bottom: 3px;
  }

  .card__suit--top,
  .card__suit--bottom {
    right: 3px;
    left: 3px;
  }

  .card__rank--top {
    top: 3px;
    left: 3px;
  }

  .card__rank--bottom {
    bottom: 3px;
    right: 3px;
  }

  .card--hoverable:hover {
    transform: translateY(-5px) !important;
  }

  .card--selected {
    transform: translateY(-10px) !important;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .card {
    width: 45px;
    height: 65px;
  }

  .card__suit {
    font-size: 0.45em;
  }

  .card__rank {
    font-size: 0.4em;
  }

  .card__suit--top,
  .card__rank--top {
    top: 2px;
  }

  .card__suit--bottom,
  .card__rank--bottom {
    bottom: 2px;
  }

  .card__suit--top,
  .card__suit--bottom {
    right: 2px;
    left: 2px;
  }

  .card__rank--top {
    top: 2px;
    left: 2px;
  }

  .card__rank--bottom {
    bottom: 2px;
    right: 2px;
  }

  .card--hoverable:hover {
    transform: translateY(-3px) !important;
  }

  .card--selected {
    transform: translateY(-6px) !important;
  }
}

.card--stacked {
  margin-left: -15px;
  transition: all 0.3s ease;
  position: relative;
}

.card--stacked:first-child {
  margin-left: 0;
}

.card--stacked .card__front {
  border-radius: 10px;
  transform-origin: left center;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.8));
}

.card--stacked .card__back {
  border-radius: 10px;
  transform-origin: left center;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.card--stacked:hover {
  z-index: 10;
  transform: translateX(15px) !important;
}

.card--stacked.card--selected {
  z-index: 20;
  transform: translateY(-20px) !important;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card--stacked {
    margin-left: -12px;
  }
  
  .card--stacked:hover {
    transform: translateX(12px) !important;
  }
  
  .card--stacked.card--selected {
    transform: translateY(-10px) !important;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .card--stacked {
    margin-left: -10px;
  }
  
  .card--stacked:hover {
    transform: translateX(10px) !important;
  }
  
  .card--stacked.card--selected {
    transform: translateY(-6px) !important;
  }
}

/* 花色颜色 */
.card__suit[data-suit="♥"],
.card__suit[data-suit="♦"] {
  color: #ff0000 !important;
}

.card__suit[data-suit="♠"],
.card__suit[data-suit="♣"] {
  color: #000000 !important;
}

/* 卡牌数字和花色位置 */
.card__suit--top {
  top: 5px;
  right: 5px;
}

.card__suit--bottom {
  bottom: 5px;
  left: 5px;
  transform: rotate(180deg);
}

.card__rank--top {
  top: 5px;
  left: 5px;
}

.card__rank--bottom {
  bottom: 5px;
  right: 5px;
  transform: rotate(180deg);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card__suit--top,
  .card__rank--top {
    top: 3px;
  }

  .card__suit--bottom,
  .card__rank--bottom {
    bottom: 3px;
  }

  .card__suit--top,
  .card__suit--bottom {
    right: 3px;
    left: 3px;
  }

  .card__rank--top {
    left: 3px;
  }

  .card__rank--bottom {
    right: 3px;
  }
}

/* 横屏适配 */
@media (max-height: 600px) and (orientation: landscape) {
  .card__suit--top,
  .card__rank--top {
    top: 2px;
  }

  .card__suit--bottom,
  .card__rank--bottom {
    bottom: 2px;
  }

  .card__suit--top,
  .card__suit--bottom {
    right: 2px;
    left: 2px;
  }

  .card__rank--top {
    left: 2px;
  }

  .card__rank--bottom {
    right: 2px;
  }
}
</style> 