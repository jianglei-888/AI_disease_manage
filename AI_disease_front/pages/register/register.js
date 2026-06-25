import authService from '../../services/auth.service';
import auth from '../../utils/auth';
import common from '../../utils/common';

Page({
  data: {
    username: '',
    email: '',
    password: '',
    confirm_password: ''
  },

  bindUsernameInput(e) {
    this.setData({
      username: e.detail.value
    });
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

  bindConfirmPasswordInput(e) {
    this.setData({
      confirm_password: e.detail.value
    });
  },

  async handleRegister() {
    const { username, email, password, confirm_password } = this.data;

    // 验证输入
    if (!username || !email || !password || !confirm_password) {
      common.showToast('请填写所有必填项');
      return;
    }

    if (!common.validateEmail(email)) {
      common.showToast('请输入正确的邮箱格式');
      return;
    }

    if (password.length < 6) {
      common.showToast('密码长度至少为6位');
      return;
    }

    if (password !== confirm_password) {
      common.showToast('两次输入的密码不一致');
      return;
    }

    common.showLoading('注册中...');

    try {
      const response = await authService.register({ username, email, password,confirm_password });
      
      if (response.access_token) {
        // 保存token
        auth.saveToken(response.access_token);
        
        // 注册成功，跳转到首页
        wx.switchTab({
          url: '/pages/home/home'
        });
        
        common.showToast('注册成功');
      } else {
        common.showToast('注册失败，请稍后重试');
      }
    } catch (error) {
      console.error('注册失败:', error);
      common.showToast('注册失败，请稍后重试');
    } finally {
      common.hideLoading();
    }
  }
});