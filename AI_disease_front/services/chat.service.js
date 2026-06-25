import api from '../utils/api';

export default {
  // 发送消息
  sendMessage(data) {
    return api.request({
      url: '/api/chat/messages',
      method: 'POST',
      data
    });
  },
  
  // 获取聊天历史
  getMessages(params) {
    return api.request({
      url: '/api/chat/messages',
      method: 'GET',
      data: params
    });
  }
};