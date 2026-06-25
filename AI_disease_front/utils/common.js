export default {
  // 格式化时间
  formatDate(date) {
    if (!date) return '';
    
    let d;
    try {
      d = new Date(date);
      if (isNaN(d.getTime())) {
        return '';
      }
    } catch (error) {
      return '';
    }
    
    // 转换为本地时区
    const year = d.getFullYear();
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    const hours = d.getHours().toString().padStart(2, '0');
    const minutes = d.getMinutes().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  },
  
  // 显示提示信息
  showToast(title, duration = 2000, icon = 'none') {
    wx.showToast({
      title,
      duration,
      icon
    });
  },
  
  // 显示加载提示
  showLoading(title = '加载中...') {
    wx.showLoading({
      title
    });
  },
  
  // 隐藏加载提示
  hideLoading() {
    wx.hideLoading();
  },
  
  // 验证邮箱格式
  validateEmail(email) {
    const reg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    return reg.test(email);
  }
};