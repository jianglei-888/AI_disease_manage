import api from '../utils/api';

export default {
  // 注册
  register(data) {
    return api.request({
      url: '/api/auth/register',
      method: 'POST',
      data
    });
  },
  
  // 登录
  login(data) {
    return api.request({
      url: '/api/auth/login',
      method: 'POST',
      data
    });
  },
  
  // 获取用户信息
  getMe() {
    return api.request({
      url: '/api/auth/me',
      method: 'GET'
    });
  }
};