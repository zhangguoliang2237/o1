<template>
  <div id="app">
    <div class="app-container">
      <SideMenu @change-view="handleViewChange" />
      <div class="main-content">
        <DataTable v-if="currentView === 'stock'" />
        <div v-else-if="currentView === 'analysis'" class="placeholder">
          <h2>数据分析功能</h2>
          <p>正在开发中...</p>
        </div>
        <div v-else class="placeholder">
          <h2>系统设置</h2>
          <p>正在开发中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideMenu from './components/SideMenu.vue'
import DataTable from './components/DataTable.vue'

export default {
  name: 'App',
  components: {
    SideMenu,
    DataTable
  },
  data() {
    return {
      currentView: 'stock'
    }
  },
  methods: {
    handleViewChange(view) {
      this.currentView = view;
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.app-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #fff;
}

.placeholder {
  text-align: center;
  margin-top: 50px;
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  .side-menu {
    width: 100%;
    height: auto;
  }
}
</style>
