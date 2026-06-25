import auth from '../../utils/auth';
import chatService from '../../services/chat.service';
import common from '../../utils/common';

Page({
  data: {
    messages: [],
    inputMessage: '',
    loading: false,
    scrollTop: 0
  },

  onLoad() {
    // 检查是否已登录
    if (!auth.isLoggedIn()) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    // 加载聊天历史
    this.loadChatHistory();
  },

  onShow(){
    if (auth.isLoggedIn()) {
        // 加载聊天历史
        this.loadChatHistory();
    }

  },
  bindMessageInput(e) {
    this.setData({
      inputMessage: e.detail.value
    });
  },

  async loadChatHistory() {
    try {
      const response = await chatService.getMessages({ limit: 50 });
      if (response.messages) {
        this.setData({
          messages: response.messages
        });
        // 滚动到底部
        this.scrollToBottom();
      }
    } catch (error) {
      console.error('加载聊天历史失败:', error);
    }
  },

  async handleSendMessage() {
    const { inputMessage } = this.data;

    if (!inputMessage.trim()) {
      return;
    }

    // 添加用户消息到列表
    const userMessage = {
      id: Date.now(),
      message: inputMessage,
      role: 'user',
      created_at: new Date().toISOString()
    };

    this.setData({
      messages: [...this.data.messages, userMessage],
      inputMessage: '',
      loading: true
    });

    // 滚动到底部
    this.scrollToBottom();

    try {
      // 发送消息到后端
      const response = await chatService.sendMessage({ message: inputMessage });
      
      if (response.ai_response) {
        // 添加AI回复到列表
        const aiMessage = {
          id: response.ai_response.id,
          message: response.ai_response.message,
          role: 'ai',
          created_at: response.ai_response.created_at
        };

        this.setData({
          messages: [...this.data.messages, aiMessage],
          loading: false
        });

        // 滚动到底部
        this.scrollToBottom();
      } else {
        common.showToast('发送失败，请稍后重试');
        this.setData({
          loading: false
        });
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      common.showToast('发送失败，请稍后重试');
      this.setData({
        loading: false
      });
    }
  },

  scrollToBottom() {
    setTimeout(() => {
      this.setData({
        scrollTop: 999999
      });
    }, 100);
  },

  formatTime(time) {
    // 后端已经返回了格式化好的时间字符串，直接返回
    return time;
  }
});