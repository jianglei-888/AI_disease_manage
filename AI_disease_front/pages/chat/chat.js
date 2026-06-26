import auth from '../../utils/auth';
import chatService from '../../services/chat.service';
import common from '../../utils/common';

Page({
  data: {
    messages: [],
    inputMessage: '',
    loading: false,
    scrollTop: 0,
    online: true,
    sessionId: '000001'
  },

  onLoad() {
    if (!auth.isLoggedIn()) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }
    this.setData({ sessionId: String(Date.now()).slice(-6) });
    this.loadChatHistory();
  },

  onShow() {
    if (auth.isLoggedIn()) this.loadChatHistory();
  },

  bindMessageInput(e) {
    this.setData({ inputMessage: e.detail.value });
  },

  useSuggestion(e) {
    const text = e.currentTarget.dataset.text;
    this.setData({ inputMessage: text });
  },

  async loadChatHistory() {
    try {
      const response = await chatService.getMessages({ limit: 50 });
      if (response && response.messages) {
        this.setData({ messages: response.messages });
        this.scrollToBottom();
      }
    } catch (error) {
      console.error('加载聊天历史失败:', error);
    }
  },

  async handleSendMessage() {
    const { inputMessage } = this.data;
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      message: inputMessage,
      role: 'user',
      created_at: this.nowHHMM()
    };
    this.setData({
      messages: [...this.data.messages, userMessage],
      inputMessage: '',
      loading: true
    });
    this.scrollToBottom();

    try {
      const response = await chatService.sendMessage({ message: inputMessage });
      if (response && response.ai_response) {
        const aiMessage = {
          id: response.ai_response.id,
          message: response.ai_response.message,
          role: 'ai',
          created_at: response.ai_response.created_at || this.nowHHMM()
        };
        this.setData({
          messages: [...this.data.messages, aiMessage],
          loading: false
        });
        this.scrollToBottom();
      } else {
        common.showToast('发送失败，请稍后重试');
        this.setData({ loading: false });
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      common.showToast('发送失败，请稍后重试');
      this.setData({ loading: false });
    }
  },

  nowHHMM() {
    const d = new Date();
    return `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
  },

  scrollToBottom() {
    setTimeout(() => this.setData({ scrollTop: 999999 }), 80);
  }
});
