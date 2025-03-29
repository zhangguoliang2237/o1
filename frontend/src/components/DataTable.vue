<template>
  <div class="data-table-container">
    <!-- 模板部分保持不变 -->
  </div>
</template>

<script>
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  data() {
    return {
      data: [],
      columns: [],
      searchColumn: '',
      searchValue: ''
    }
  },
  methods: {
    fetchData() {
      if (this.searchColumn && this.searchValue) {
        api.get(`/api/data/${this.searchColumn}/${this.searchValue}`)
          .then(response => {
            this.data = response.data;
            if (this.data.length > 0) {
              this.columns = Object.keys(this.data[0]);
            }
          })
          .catch(error => {
            console.error('API请求错误:', error);
            alert('查询失败，请检查后端服务是否运行');
          });
      } else {
        this.fetchAllData();
      }
    },
    fetchAllData() {
      api.get('/api/data')
        .then(response => {
          this.data = response.data;
          if (this.data.length > 0) {
            this.columns = Object.keys(this.data[0]);
          }
        })
        .catch(error => {
          console.error('API请求错误:', error);
          alert('获取数据失败，请检查后端服务是否运行');
        });
    }
  },
  mounted() {
    this.fetchAllData();
  }
}
</script>

<style scoped>
/* 样式部分保持不变 */
</style>