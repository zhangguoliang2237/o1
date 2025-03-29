<template>
  <div class="side-menu">
    <h3>数据查询系统</h3>
    <ul>
      <li><a href="#" @click.prevent="changeView('stock')">股票数据</a></li>
      <li><a href="#" @click.prevent="changeView('analysis')">数据分析</a></li>
      <li><a href="#" @click.prevent="changeView('settings')">系统设置</a></li>
    </ul>
  </div>
</template>

<script>
export default {
  methods: {
    changeView(view) {
      this.$emit('change-view', view);
    }
  }
}
</script>

<style scoped>
.side-menu {
  width: 200px;
  background-color: #f5f5f5;
  padding: 20px;
  height: 100vh;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}
.side-menu h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}
.side-menu ul {
  list-style: none;
  padding: 0;
}
.side-menu li {
  margin-bottom: 10px;
}
.side-menu a {
  color: #2c3e50;
  text-decoration: none;
  display: block;
  padding: 8px;
  border-radius: 4px;
}
.side-menu a:hover {
  background-color: #e0e0e0;
}
</style>