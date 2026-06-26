import auth from '../../utils/auth';
import healthService from '../../services/health.service';
import common from '../../utils/common';

Page({
  data: {
    systolic: '',
    diastolic: '',
    bloodSugar: '',
    measuredAt: '',
    statusTip: '',
    bp: { cls: 'badge--ink', label: '—' },
    bs: { cls: 'badge--ink', label: '—' }
  },

  formatDateTime(date) {
    const y = date.getFullYear();
    const m = (date.getMonth() + 1).toString().padStart(2, '0');
    const d = date.getDate().toString().padStart(2, '0');
    const hh = date.getHours().toString().padStart(2, '0');
    const mm = date.getMinutes().toString().padStart(2, '0');
    return `${y}-${m}-${d} ${hh}:${mm}`;
  },

  onLoad() {
    if (!auth.isLoggedIn()) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }
    const now = new Date();
    this.setData({ measuredAt: this.formatDateTime(now) });
  },

  classifyBP(s, d) {
    if (s == null || d == null || s === '' || d === '') return { cls: 'badge--ink', label: '—' };
    if (s < 90 || d < 60) return { cls: 'badge--ink', label: '偏低' };
    if (s < 120 && d < 80) return { cls: 'badge--ok', label: '理想' };
    if (s < 140 && d < 90) return { cls: 'badge--warn', label: '正常高值' };
    return { cls: 'badge--alert', label: '偏高' };
  },

  classifyBS(bs) {
    if (bs == null || bs === '') return { cls: 'badge--ink', label: '—' };
    const v = parseFloat(bs);
    if (v < 3.9) return { cls: 'badge--ink', label: '偏低' };
    if (v < 6.1) return { cls: 'badge--ok', label: '正常' };
    if (v < 7.0) return { cls: 'badge--warn', label: '临界' };
    return { cls: 'badge--alert', label: '偏高' };
  },

  bindSystolicInput(e) {
    this.setData({ systolic: e.detail.value }, () => this.recomputeBadges());
  },

  bindDiastolicInput(e) {
    this.setData({ diastolic: e.detail.value }, () => this.recomputeBadges());
  },

  bindBloodSugarInput(e) {
    this.setData({ bloodSugar: e.detail.value }, () => this.recomputeBadges());
  },

  recomputeBadges() {
    const { systolic, diastolic, bloodSugar } = this.data;
    this.setData({
      bp: this.classifyBP(parseInt(systolic, 10), parseInt(diastolic, 10)),
      bs: this.classifyBS(bloodSugar)
    });
  },

  openTimePicker() {
    const now = new Date();
    const options = [];
    const currentTime = this.formatDateTime(now);
    options.push(`当前时间 · ${currentTime}`);

    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    options.push(`1 小时前 · ${this.formatDateTime(oneHourAgo)}`);

    const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);
    options.push(`2 小时前 · ${this.formatDateTime(twoHoursAgo)}`);

    const thisMorning = new Date(now);
    thisMorning.setHours(8, 0, 0, 0);
    options.push(`今早 08:00 · ${this.formatDateTime(thisMorning)}`);

    const lastNight = new Date(now);
    lastNight.setDate(lastNight.getDate() - 1);
    lastNight.setHours(20, 0, 0, 0);
    options.push(`昨晚 20:00 · ${this.formatDateTime(lastNight)}`);

    wx.showActionSheet({
      itemList: options,
      success: (res) => {
        const idx = res.tapIndex;
        const map = [currentTime, this.formatDateTime(oneHourAgo), this.formatDateTime(twoHoursAgo), this.formatDateTime(thisMorning), this.formatDateTime(lastNight)];
        this.setData({ measuredAt: map[idx] || currentTime });
      }
    });
  },

  async handleSubmit() {
    const { systolic, diastolic, bloodSugar, measuredAt } = this.data;
    if (!systolic || !diastolic || !bloodSugar || !measuredAt) {
      common.showToast('请填写所有必填项');
      return;
    }
    const sN = parseInt(systolic, 10);
    const dN = parseInt(diastolic, 10);
    const bsN = parseFloat(bloodSugar);
    if (sN < 60 || sN > 200) { common.showToast('收缩压值不在正常范围'); return; }
    if (dN < 40 || dN > 130) { common.showToast('舒张压值不在正常范围'); return; }
    if (bsN < 2 || bsN > 33) { common.showToast('血糖值不在正常范围'); return; }

    common.showLoading('提交中...');
    try {
      const response = await healthService.submitRecord({
        systolic: sN, diastolic: dN, blood_sugar: bsN, measured_at: measuredAt
      });
      if (response.id) {
        common.showToast('提交成功');
        this.setData({
          systolic: '', diastolic: '', bloodSugar: '',
          statusTip: this.getStatusTip(sN, dN, bsN),
          bp: { cls: 'badge--ink', label: '—' },
          bs: { cls: 'badge--ink', label: '—' }
        });
        setTimeout(() => this.setData({ statusTip: '' }), 5000);
      } else {
        common.showToast('提交失败，请稍后重试');
      }
    } catch (error) {
      console.error('提交数据失败:', error);
      common.showToast('提交失败，请稍后重试');
    } finally {
      common.hideLoading();
    }
  },

  getStatusTip(s, d, bs) {
    let tip = '';
    if (s < 90 || d < 60)      tip += '血压偏低 — 注意休息和补充营养。\n';
    else if (s < 120 && d < 80) tip += '血压理想 — 继续保持。\n';
    else if (s < 140 && d < 90) tip += '血压略高 — 注意饮食和运动。\n';
    else                       tip += '血压较高 — 建议咨询医生。\n';

    if (bs < 3.9)      tip += '血糖偏低 — 及时补充糖分。\n';
    else if (bs < 6.1) tip += '血糖正常 — 继续保持。\n';
    else if (bs < 7.0) tip += '血糖略高 — 注意饮食控制。\n';
    else               tip += '血糖较高 — 建议咨询医生。\n';
    return tip;
  }
});
