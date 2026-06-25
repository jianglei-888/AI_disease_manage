import authService from '../../services/auth.service';
import auth from '../../utils/auth';
import common from '../../utils/common';

Page({
  data: {
    email: '',
    password: '',
    remember: false
  },

  onLoad() {
    // 检查是否已登录
    if (auth.isLoggedIn()) {
      wx.switchTab({
        url: '/pages/home/home'
      });
    }
  },

  bindEmailInput(e) {
    this.setData({
      email: e.detail.value
    });
  },

  bindPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  bindRememberChange(e) {
    this.setData({
      remember: e.detail.value
    });
  },

  async handleLogin() {
    const { email, password } = this.data;

    // 验证输入
    if (!email || !password) {
      common.showToast('请输入邮箱和密码');
      return;
    }

    if (!common.validateEmail(email)) {
      common.showToast('请输入正确的邮箱格式');
      return;
    }

    common.showLoading('登录中...');

    try {
      const response = await authService.login({ email, password });
      
      if (response.access_token) {
        // 保存token
        auth.saveToken(response.access_token);
        
        // 登录成功，跳转到首页
        wx.switchTab({
          url: '/pages/home/home'
        });
        
        common.showToast('登录成功');
      } else {
        common.showToast('登录失败，请检查邮箱和密码');
      }
    } catch (error) {
      console.error('登录失败:', error);
      common.showToast('登录失败，请稍后重试');
    } finally {
      common.hideLoading();
    }
  },

  handleForgotPassword() {
    common.showToast('忘记密码功能暂未实现');
  }
});