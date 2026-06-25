import api from '../utils/api';

const personalInfoService = {
  /**
   * 获取个人信息
   */
  async getPersonalInfo() {
    try {
      const response = await api.request({
        url: '/api/personal-info/',
        method: 'GET'
      });
      return response;
    } catch (error) {
      console.error('获取个人信息失败:', error);
      throw error;
    }
  },

  /**
   * 保存个人信息
   * @param {Object} personalInfo - 个人信息对象
   */
  async savePersonalInfo(personalInfo) {
    try {
      const response = await api.request({
        url: '/api/personal-info/',
        method: 'POST',
        data: personalInfo
      });
      return response;
    } catch (error) {
      console.error('保存个人信息失败:', error);
      throw error;
    }
  }
};

export default personalInfoService;
