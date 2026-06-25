import auth from '../../utils/auth';
import healthService from '../../services/health.service';
import common from '../../utils/common';

Page({
  data: {
    loading: true,
    records: [],
    averageSystolic: 0,
    averageDiastolic: 0,
    averageBloodSugar: 0,
    bloodPressureTrend: '',
    bloodSugarTrend: '',
    abnormalCount: 0,
    abnormalTips: []
  },

  onLoad() {
    // 检查是否已登录
    if (!auth.isLoggedIn()) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    // 获取分析数据
    this.getAnalysisData();
  },

  async getAnalysisData() {
    try {
      this.setData({ loading: true });

      // 获取最近10条记录
      const response = await healthService.getRecords({ limit: 10 });
      if (response && response.records) {
        const records = response.records;
        
        // 格式化时间
        records.forEach(record => {
          record.formattedTime = common.formatDate(record.measured_at);
        });

        // 分析数据
        const analysis = this.analyzeData(records);

        this.setData({
          records: records,
          averageSystolic: analysis.averageSystolic,
          averageDiastolic: analysis.averageDiastolic,
          averageBloodSugar: analysis.averageBloodSugar,
          bloodPressureTrend: analysis.bloodPressureTrend,
          bloodSugarTrend: analysis.bloodSugarTrend,
          abnormalCount: analysis.abnormalCount,
          abnormalTips: analysis.abnormalTips
        });
      }
    } catch (error) {
      console.error('获取分析数据失败:', error);
      common.showToast('获取分析数据失败');
    } finally {
      this.setData({ loading: false });
    }
  },

  // 分析数据
  analyzeData(records) {
    if (!records || records.length === 0) {
      return {
        averageSystolic: 0,
        averageDiastolic: 0,
        averageBloodSugar: 0,
        bloodPressureTrend: '暂无数据',
        bloodSugarTrend: '暂无数据',
        abnormalCount: 0,
        abnormalTips: []
      };
    }

    // 计算平均值
    let totalSystolic = 0;
    let totalDiastolic = 0;
    let totalBloodSugar = 0;
    let abnormalCount = 0;
    const abnormalTips = [];

    records.forEach(record => {
      totalSystolic += record.systolic;
      totalDiastolic += record.diastolic;
      totalBloodSugar += record.blood_sugar;

      // 检查异常值
      if (record.systolic > 140 || record.diastolic > 90) {
        abnormalCount++;
      }
      if (record.blood_sugar > 7.0) {
        abnormalCount++;
      }
    });

    const averageSystolic = (totalSystolic / records.length).toFixed(1);
    const averageDiastolic = (totalDiastolic / records.length).toFixed(1);
    const averageBloodSugar = (totalBloodSugar / records.length).toFixed(1);

    // 分析趋势
    let bloodPressureTrend = '稳定';
    let bloodSugarTrend = '稳定';

    if (records.length >= 2) {
      const first = records[0];
      const last = records[records.length - 1];

      // 血压趋势
      const systolicDiff = first.systolic - last.systolic;
      const diastolicDiff = first.diastolic - last.diastolic;
      
      if (systolicDiff > 5 || diastolicDiff > 5) {
        bloodPressureTrend = '上升';
      } else if (systolicDiff < -5 || diastolicDiff < -5) {
        bloodPressureTrend = '下降';
      }

      // 血糖趋势
      const bloodSugarDiff = first.blood_sugar - last.blood_sugar;
      if (bloodSugarDiff > 0.5) {
        bloodSugarTrend = '上升';
      } else if (bloodSugarDiff < -0.5) {
        bloodSugarTrend = '下降';
      }
    }

    // 生成异常提示
    if (parseFloat(averageSystolic) > 140 || parseFloat(averageDiastolic) > 90) {
      abnormalTips.push('您的平均血压偏高，建议减少盐分摄入，保持规律运动');
    } else if (parseFloat(averageSystolic) < 90 || parseFloat(averageDiastolic) < 60) {
      abnormalTips.push('您的平均血压偏低，建议适当增加盐分摄入，避免长时间站立');
    }

    if (parseFloat(averageBloodSugar) > 7.0) {
      abnormalTips.push('您的平均血糖偏高，建议控制碳水化合物摄入，增加运动');
    } else if (parseFloat(averageBloodSugar) < 3.9) {
      abnormalTips.push('您的平均血糖偏低，建议随身携带糖果，定时进餐');
    }

    return {
      averageSystolic,
      averageDiastolic,
      averageBloodSugar,
      bloodPressureTrend,
      bloodSugarTrend,
      abnormalCount,
      abnormalTips
    };
  }
});