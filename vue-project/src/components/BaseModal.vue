<script setup>
defineProps({
  isOpen: Boolean,
  title: String
})

defineEmits(['close'])
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-body">
        <slot></slot>
      </div>
      
      <div class="modal-footer" v-if="$slots.footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: var(--color-background);
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: var(--shadow-md);
  animation: popIn 0.2s ease-out;
  border: 1px solid var(--color-border);
}

.modal-header {
  padding: 24px 24px 8px; /* 增加顶部padding，减少底部padding */
  /* border-bottom: 1px solid var(--color-border); */ /* 移除底部分割线 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  font-size: 24px;
  color: var(--color-text-secondary);
  line-height: 1;
}

.modal-body {
  padding: 16px 24px; /* 调整左右padding与header/footer一致 */
}

.modal-footer {
  padding: 8px 24px 24px; /* 增加底部padding */
  /* border-top: 1px solid var(--color-border); */ /* 移除顶部分割线 */
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>