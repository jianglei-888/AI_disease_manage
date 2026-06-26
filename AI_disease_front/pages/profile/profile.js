import auth from '../../utils/auth';
import authService from '../../services/auth.service';
import common from '../../utils/common';

Page({
  data: {
    userInfo: null,
    userInitial: 'U'
  },

  onLoad() {
    if (!auth.isLoggedIn()) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }
    this.getUserInfo();
  },

  async getUserInfo() {
    try {
      const response = await authService.getMe();
      if (response) {
        const name = response.username || response.email || 'U';
        this.setData({
          userInfo: response,
          userInitial: String(name).charAt(0).toUpperCase()
        });
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  },

  handlePersonalInfo() {
    wx.navigateTo({
      url: '/pages/personal-info/personal-info'
    });
  },

  handleHistory() {
    common.showToast('历史记录功能暂未实现');
  },

  handleNotification() {
    common.showToast('通知设置功能暂未实现');
  },

  handleDisclaimer() {
    common.showToast('免责声明功能暂未实现');
  },

  handlePrivacy() {
    common.showToast('隐私政策功能暂未实现');
  },

  handleAbout() {
    common.showToast('关于我们功能暂未实现');
  },

  handleLogout() {
    console.log('handleLogout called');
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        console.log('Modal result:', res);
        if (res.confirm) {
          // 清除token
          console.log('Clearing token');
          auth.clearToken();
          // 跳转到登录页
          console.log('Redirecting to login page');
          wx.redirectTo({
            url: '/pages/login/login'
          });
        }
      }
    });
  }
});