import api from '../utils/api';

export default {
  // 提交健康数据
  submitRecord(data) {
    return api.request({
      url: '/api/health/records',
      method: 'POST',
      data
    });
  },
  
  // 获取历史数据
  getRecords(params) {
    return api.request({
      url: '/api/health/records',
      method: 'GET',
      data: params
    });
  },
  
  // 获取数据分析
  getAnalysis(params) {
    return api.request({
      url: '/api/health/analysis',
      method: 'GET',
      data: params
    });
  }
};