import auth from '../../utils/auth';
import common from '../../utils/common';
import personalInfoService from '../../services/personal-info.service';

Page({
  data: {
    personalInfo: {
      name: '',
      gender: '',
      age: '',
      medicationHistory: '',
      medicationContraindications: ''
    },
    statusTip: ''
  },

  onLoad() {
    // 检查是否已登录
    if (!auth.isLoggedIn()) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    // 加载个人信息
    this.loadPersonalInfo();
  },

  async loadPersonalInfo() {
    common.showLoading('加载中...');
    try {
      // 从后端API获取个人信息
      const response = await personalInfoService.getPersonalInfo();
      this.setData({
        personalInfo: {
          name: response.name || '',
          gender: response.gender || '',
          age: response.age || '',
          medicationHistory: response.medication_history || '',
          medicationContraindications: response.medication_contraindications || ''
        }
      });
    } catch (error) {
      console.error('加载个人信息失败:', error);
      // 如果API调用失败，从本地存储加载
      const personalInfo = wx.getStorageSync('personalInfo') || {
        name: '',
        gender: '',
        age: '',
        medicationHistory: '',
        medicationContraindications: ''
      };
      this.setData({
        personalInfo
      });
    } finally {
      common.hideLoading();
    }
  },

  bindNameInput(e) {
    this.setData({
      'personalInfo.name': e.detail.value
    });
  },

  bindAgeInput(e) {
    this.setData({
      'personalInfo.age': e.detail.value
    });
  },

  bindMedicationHistoryInput(e) {
    this.setData({
      'personalInfo.medicationHistory': e.detail.value
    });
  },

  bindMedicationContraindicationsInput(e) {
    this.setData({
      'personalInfo.medicationContraindications': e.detail.value
    });
  },

  handleGenderSelect(e) {
    const gender = e.currentTarget.dataset.gender;
    this.setData({
      'personalInfo.gender': gender
    });
  },

  async handleSave() {
    const { personalInfo } = this.data;

    // 验证输入
    if (!personalInfo.name) {
      common.showToast('请输入姓名');
      return;
    }

    if (!personalInfo.gender) {
      common.showToast('请选择性别');
      return;
    }

    if (!personalInfo.age) {
      common.showToast('请输入年龄');
      return;
    }

    common.showLoading('保存中...');
    try {
      // 保存个人信息到后端API
      const personalInfoData = {
        name: personalInfo.name,
        gender: personalInfo.gender,
        age: parseInt(personalInfo.age),
        medication_history: personalInfo.medicationHistory,
        medication_contraindications: personalInfo.medicationContraindications
      };

      await personalInfoService.savePersonalInfo(personalInfoData);

      // 同时保存到本地存储作为备份
      wx.setStorageSync('personalInfo', personalInfo);

      // 显示保存成功提示
      common.showToast('保存成功');
      
      // 立即返回上一页
      this.handleBack();
    } catch (error) {
      console.error('保存个人信息失败:', error);
      common.showToast('保存失败，请稍后重试');
    } finally {
      common.hideLoading();
    }
  },

  handleBack() {
    wx.navigateBack();
  }
});
