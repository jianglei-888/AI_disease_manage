// 后端 API 地址。
// 本地调试：改成 http://127.0.0.1:8001（端口需与后端 .env 的 APP_PORT 一致）
// 真机调试（小程序连后端）：改成你电脑的局域网 IP，如 http://192.168.1.100:8001
const API_BASE_URL = 'http://127.0.0.1:8001';

function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API_BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      timeout: 30000,
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + wx.getStorageSync('token')
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          reject(res.data);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}

export default { request };