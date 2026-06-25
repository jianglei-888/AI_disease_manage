export default {
  // 存储数据
  set(key, value) {
    wx.setStorageSync(key, value);
  },
  
  // 获取数据
  get(key) {
    return wx.getStorageSync(key);
  },
  
  // 删除数据
  remove(key) {
    wx.removeStorageSync(key);
  },
  
  // 清空所有数据
  clear() {
    wx.clearStorageSync();
  }
};