import auth from '../../utils/auth';
import healthService from '../../services/health.service';
import common from '../../utils/common';

Page({
  data: {
    loading: true,
    records: [],
    averageSystolic: '0',
    averageDiastolic: '0',
    averageBloodSugar: '0',
    bloodPressureTrend: '稳定',
    bloodSugarTrend: '稳定',
    bpTrend: { pillCls: 'pill-flat', pillLabel: '— 稳定' },
    bsTrend: { pillCls: 'pill-flat', pillLabel: '— 稳定' },
    abnormalCount: 0,
    abnormalTips: [],
    bpSpark: [],
    bsSpark: []
  },

  onLoad() {
    if (!auth.isLoggedIn()) {
      wx.redirectTo({ url: '/pages/login/login' });
      return;
    }
    this.getAnalysisData();
  },

  async getAnalysisData() {
    try {
      this.setData({ loading: true });
      const response = await healthService.getRecords({ limit: 10 });
      const records = (response && response.records) || [];
      records.forEach(r => { r.formattedTime = common.formatDate(r.measured_at); });
      const analysis = this.analyzeData(records);
      this.setData({ records, ...analysis, loading: false });
    } catch (error) {
      console.error('获取分析数据失败:', error);
      common.showToast('获取分析数据失败');
      this.setData({ loading: false });
    }
  },

  analyzeData(records) {
    if (!records || records.length === 0) {
      return {
        averageSystolic: '0', averageDiastolic: '0', averageBloodSugar: '0',
        bloodPressureTrend: '暂无数据', bloodSugarTrend: '暂无数据',
        bpTrend: { pillCls: 'pill-flat', pillLabel: '— 暂无' },
        bsTrend: { pillCls: 'pill-flat', pillLabel: '— 暂无' },
        abnormalCount: 0, abnormalTips: [],
        bpSpark: [], bsSpark: []
      };
    }

    let totalS = 0, totalD = 0, totalB = 0, abnormalCount = 0;
    records.forEach(r => {
      totalS += r.systolic; totalD += r.diastolic; totalB += r.blood_sugar;
      r.alert = (r.systolic > 140 || r.diastolic > 90 || r.blood_sugar > 7.0);
      if (r.systolic > 140 || r.diastolic > 90) abnormalCount++;
      if (r.blood_sugar > 7.0) abnormalCount++;
    });

    const averageSystolic = (totalS / records.length).toFixed(1);
    const averageDiastolic = (totalD / records.length).toFixed(1);
    const averageBloodSugar = (totalB / records.length).toFixed(1);

    let bloodPressureTrend = '稳定';
    let bloodSugarTrend = '稳定';
    let bpTrend = { pillCls: 'pill-flat', pillLabel: '— 稳定' };
    let bsTrend = { pillCls: 'pill-flat', pillLabel: '— 稳定' };

    if (records.length >= 2) {
      const first = records[0];
      const last = records[records.length - 1];
      const sDiff = first.systolic - last.systolic;
      const dDiff = first.diastolic - last.diastolic;
      if (sDiff > 5 || dDiff > 5) {
        bloodPressureTrend = '上升';
        bpTrend = { pillCls: 'pill-up', pillLabel: '↗ 上升' };
      } else if (sDiff < -5 || dDiff < -5) {
        bloodPressureTrend = '下降';
        bpTrend = { pillCls: 'pill-down', pillLabel: '↘ 下降' };
      } else {
        bpTrend = { pillCls: 'pill-flat', pillLabel: '— 稳定' };
      }

      const bDiff = first.blood_sugar - last.blood_sugar;
      if (bDiff > 0.5) {
        bloodSugarTrend = '上升';
        bsTrend = { pillCls: 'pill-up', pillLabel: '↗ 上升' };
      } else if (bDiff < -0.5) {
        bloodSugarTrend = '下降';
        bsTrend = { pillCls: 'pill-down', pillLabel: '↘ 下降' };
      }
    }

    const tips = [];
    if (parseFloat(averageSystolic) > 140 || parseFloat(averageDiastolic) > 90) {
      tips.push('您的平均血压偏高，建议减少盐分摄入，保持规律运动');
    } else if (parseFloat(averageSystolic) < 90 || parseFloat(averageDiastolic) < 60) {
      tips.push('您的平均血压偏低，建议适当增加盐分摄入，避免久站');
    }
    if (parseFloat(averageBloodSugar) > 7.0) {
      tips.push('您的平均血糖偏高，建议控制碳水化合物摄入并增加运动');
    } else if (parseFloat(averageBloodSugar) < 3.9) {
      tips.push('您的平均血糖偏低，建议随身携带糖果、定时进餐');
    }
    const abnormalTips = tips.map((text, i) => ({ text, idx: i + 1 }));

    // spark 数据：按记录顺序归一化
    const sysVals = records.map(r => r.systolic);
    const bsVals  = records.map(r => r.blood_sugar);
    const bpSpark = this.normalizeSpark(sysVals, 90, 160);
    const bsSpark = this.normalizeSpark(bsVals,  3.5, 10);

    return {
      averageSystolic, averageDiastolic, averageBloodSugar,
      bloodPressureTrend, bloodSugarTrend,
      bpTrend, bsTrend,
      abnormalCount, abnormalTips,
      bpSpark, bsSpark
    };
  },

  normalizeSpark(vals, lo, hi) {
    if (!vals || !vals.length) return [];
    return vals.map(v => {
      const ratio = (v - lo) / (hi - lo);
      return Math.max(6, Math.min(100, Math.round(ratio * 100)));
    });
  }
});
