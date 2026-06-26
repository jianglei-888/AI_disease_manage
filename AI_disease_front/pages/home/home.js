import auth from '../../utils/auth';
import healthService from '../../services/health.service';
import common from '../../utils/common';

Page({
  data: {
    latestRecord: null,
    dietAdvice: '',
    exerciseAdvice: '',
    // 派生展示
    greetingTime: '晨间',
    greetingText: '早安',
    todayLabel: '',
    userName: '你',
    bpBadgeCls: 'badge--ink',
    bpBadgeLabel: '待记录',
    bsMarkerLeft: 50
  },

  onLoad() {
    if (!auth.isLoggedIn()) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }
    this.computeGreeting();
    this.getLatestRecord();
    this.getHealthAdvice();
  },

  onShow() {
    if (auth.isLoggedIn()) {
      this.getLatestRecord();
    }
  },

  computeGreeting() {
    const h = new Date().getHours();
    let greetingTime = '晨间', greetingText = '早安';
    if (h >= 5 && h < 11) { greetingTime = '晨间'; greetingText = '早安'; }
    else if (h >= 11 && h < 14) { greetingTime = '午间'; greetingText = '午安'; }
    else if (h >= 14 && h < 18) { greetingTime = '午后'; greetingText = '下午好'; }
    else if (h >= 18 && h < 23) { greetingTime = '夜间'; greetingText = '晚安'; }
    else { greetingTime = '深夜'; greetingText = '夜深了'; }

    const d = new Date();
    const week = ['日','一','二','三','四','五','六'][d.getDay()];
    const todayLabel = `${d.getMonth()+1}.${d.getDate()}  周${week}`;

    const app = getApp();
    const userName = (app && app.globalData && app.globalData.userInfo && app.globalData.userInfo.username) || '朋友';

    this.setData({ greetingTime, greetingText, todayLabel, userName });
  },

  classifyBP(s, d) {
    if (s == null || d == null) return { cls: 'badge--ink', label: '待记录' };
    if (s < 90 || d < 60) return { cls: 'badge--ink', label: '偏低' };
    if (s < 120 && d < 80) return { cls: 'badge--ok', label: '理想' };
    if (s < 140 && d < 90) return { cls: 'badge--warn', label: '正常高值' };
    return { cls: 'badge--alert', label: '偏高' };
  },

  calcBSMarker(bs) {
    // 3.9–6.1 正常  /  6.1–7.0 临界  /  <3.9 低 /  >7.0 高
    if (bs == null) return 50;
    if (bs <= 3.9) return 5;
    if (bs >= 11) return 95;
    if (bs <= 6.1) {
      // 3.9..6.1 映射到 5..50
      return 5 + (bs - 3.9) / (6.1 - 3.9) * 45;
    }
    if (bs <= 7.0) {
      return 50 + (bs - 6.1) / (7.0 - 6.1) * 20;
    }
    return Math.min(95, 70 + (bs - 7.0) * 4);
  },

  async getLatestRecord() {
    try {
      const response = await healthService.getRecords({ limit: 1 });
      if (response.records && response.records.length > 0) {
        const record = response.records[0];
        try { record.formattedTime = common.formatDate(record.measured_at); }
        catch (e) { record.formattedTime = record.measured_at || ''; }

        const bp = this.classifyBP(record.systolic, record.diastolic);
        this.setData({
          latestRecord: record,
          bpBadgeCls: bp.cls,
          bpBadgeLabel: bp.label,
          bsMarkerLeft: this.calcBSMarker(parseFloat(record.blood_sugar))
        });
      } else {
        this.setData({
          latestRecord: null,
          bpBadgeCls: 'badge--ink',
          bpBadgeLabel: '待记录',
          bsMarkerLeft: 50
        });
      }
    } catch (error) {
      console.error('获取健康数据失败:', error);
    }
  },

  async getHealthAdvice() {
    try {
      const response = await healthService.getAnalysis({ period: 'week' });
      if (response && response.advice) {
        this.setData({
          dietAdvice: response.advice.diet || '',
          exerciseAdvice: response.advice.exercise || ''
        });
      }
    } catch (error) {
      console.error('获取健康建议失败:', error);
    }
  }
});
