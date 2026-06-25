import storage from './storage';

export default {
  // 保存token
  saveToken(token) {
    storage.set('token', token);
  },
  
  // 获取token
  getToken() {
    return storage.get('token');
  },
  
  // 清除token
  clearToken() {
    storage.remove('token');
  },
  
  // 检查是否已登录
  isLoggedIn() {
    return !!this.getToken();
  }
};