import auth from '../../utils/auth';
import healthService from '../../services/health.service';
import common from '../../utils/common';

Page({
  data: {
    latestRecord: null,
    dietAdvice: '',
    exerciseAdvice: ''
  },

  onLoad() {
    // 检查是否已登录
    if (!auth.isLoggedIn()) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    // 获取最新健康数据
    this.getLatestRecord();
    // 获取健康建议
    this.getHealthAdvice();
  },

  onShow() {
    // 页面显示时重新获取数据
    if (auth.isLoggedIn()) {
      this.getLatestRecord();
    }
  },

  async getLatestRecord() {
    try {
      const response = await healthService.getRecords({ limit: 1 });
      if (response.records && response.records.length > 0) {
        const record = response.records[0];
        console.log('Latest record:', record);
        console.log('Measured at:', record.measured_at);
        
        // 直接在数据获取时处理时间格式化
        try {
          record.formattedTime = common.formatDate(record.measured_at);
          console.log('Formatted time:', record.formattedTime);
        } catch (error) {
          console.error('Error formatting time in getLatestRecord:', error);
          record.formattedTime = record.measured_at || '';
        }
        
        this.setData({
          latestRecord: record
        });
      }else{
        this.setData({
          latestRecord:  {
            formattedTime: '暂无',
            dietAdvice: '',
            exerciseAdvice: ''
          }
        });

      }
    } catch (error) {
      console.error('获取健康数据失败:', error);
    }
  },

  async getHealthAdvice() {
    try {
      const response = await healthService.getAnalysis({ period: 'week' });
      if (response.advice) {
        this.setData({
          dietAdvice: response.advice.diet || '',
          exerciseAdvice: response.advice.exercise || ''
        });
      }
    } catch (error) {
      console.error('获取健康建议失败:', error);
    }
  },

  formatTime: function(time) {
    console.log('formatTime called with:', time);
    if (!time) return '';
    try {
      return common.formatDate(time);
    } catch (error) {
      console.error('Error formatting time:', error);
      return '';
    }
  }
});