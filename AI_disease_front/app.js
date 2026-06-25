// app.js
import auth from './utils/auth';
import authService from './services/auth.service';

App({
  globalData: {
    userInfo: null,
    token: null,
    isLoggedIn: false
  },
  
  onLaunch() {
    // 检查登录状态
    const token = auth.getToken();
    if (token) {
      this.globalData.token = token;
      this.globalData.isLoggedIn = true;
      // 获取用户信息
      this.getUserInfo();
    }
  },
  
  async getUserInfo() {
    try {
      const response = await authService.getMe();
      if (response) {
        this.globalData.userInfo = response;
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 清除无效token
      auth.clearToken();
      this.globalData.token = null;
      this.globalData.isLoggedIn = false;
    }
  },
  
  login(token, userInfo) {
    this.globalData.token = token;
    this.globalData.userInfo = userInfo;
    this.globalData.isLoggedIn = true;
    auth.saveToken(token);
  },
  
  logout() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    this.globalData.isLoggedIn = false;
    auth.clearToken();
  }
});
