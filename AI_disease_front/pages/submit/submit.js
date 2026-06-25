import auth from '../../utils/auth';
import healthService from '../../services/health.service';
import common from '../../utils/common';

Page({
  data: {
    systolic: '',
    diastolic: '',
    bloodSugar: '',
    measuredAt: '',
    statusTip: ''
  },
  
  // 格式化日期时间
  formatDateTime(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  },

  onLoad() {
    // 检查是否已登录
    if (!auth.isLoggedIn()) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    // 设置默认时间为当前时间
    const now = new Date();
    const formattedTime = this.formatDateTime(now);
    this.setData({
      measuredAt: formattedTime
    });
  },

  bindSystolicInput(e) {
    this.setData({
      systolic: e.detail.value
    });
  },

  bindDiastolicInput(e) {
    this.setData({
      diastolic: e.detail.value
    });
  },

  bindBloodSugarInput(e) {
    this.setData({
      bloodSugar: e.detail.value
    });
  },

  openTimePicker() {
    // 生成时间选项
    const now = new Date();
    const options = [];
    
    // 当前时间
    const currentTime = this.formatDateTime(now);
    options.push(`当前时间: ${currentTime}`);
    
    // 1小时前
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    options.push(`1小时前: ${this.formatDateTime(oneHourAgo)}`);
    
    // 2小时前
    const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);
    options.push(`2小时前: ${this.formatDateTime(twoHoursAgo)}`);
    
    // 今天早上
    const thisMorning = new Date(now);
    thisMorning.setHours(8, 0, 0, 0);
    options.push(`今天早上: ${this.formatDateTime(thisMorning)}`);
    
    // 昨天晚上
    const lastNight = new Date(now);
    lastNight.setDate(lastNight.getDate() - 1);
    lastNight.setHours(20, 0, 0, 0);
    options.push(`昨天晚上: ${this.formatDateTime(lastNight)}`);
    
    // 显示操作菜单
    wx.showActionSheet({
      itemList: options,
      success: (res) => {
        // 根据选择的索引设置时间
        let selectedTime;
        switch (res.tapIndex) {
          case 0:
            selectedTime = currentTime;
            break;
          case 1:
            selectedTime = this.formatDateTime(oneHourAgo);
            break;
          case 2:
            selectedTime = this.formatDateTime(twoHoursAgo);
            break;
          case 3:
            selectedTime = this.formatDateTime(thisMorning);
            break;
          case 4:
            selectedTime = this.formatDateTime(lastNight);
            break;
          default:
            selectedTime = currentTime;
        }
        
        this.setData({
          measuredAt: selectedTime
        });
      }
    });
  },

  async handleSubmit() {
    console.log('handleSubmit called');
    const { systolic, diastolic, bloodSugar, measuredAt } = this.data;
    console.log('Form data:', { systolic, diastolic, bloodSugar, measuredAt });

    // 验证输入
    if (!systolic || !diastolic || !bloodSugar || !measuredAt) {
      console.log('Missing required fields');
      common.showToast('请填写所有必填项');
      return;
    }

    // 验证数据范围
    const systolicNum = parseInt(systolic);
    const diastolicNum = parseInt(diastolic);
    const bloodSugarNum = parseFloat(bloodSugar);

    if (systolicNum < 60 || systolicNum > 200) {
      common.showToast('收缩压值不在正常范围内');
      return;
    }

    if (diastolicNum < 40 || diastolicNum > 130) {
      common.showToast('舒张压值不在正常范围内');
      return;
    }

    if (bloodSugarNum < 2 || bloodSugarNum > 33) {
      common.showToast('血糖值不在正常范围内');
      return;
    }

    common.showLoading('提交中...');

    try {
      const response = await healthService.submitRecord({
        systolic: systolicNum,
        diastolic: diastolicNum,
        blood_sugar: bloodSugarNum,
        measured_at: measuredAt
      });

      if (response.id) {
        common.showToast('提交成功');
        
        // 置空输入框
        this.setData({
          systolic: '',
          diastolic: '',
          bloodSugar: '',
          // 保留测量时间
          statusTip: this.getStatusTip(systolicNum, diastolicNum, bloodSugarNum)
        });

        // 5秒后自动消失状态提示
        setTimeout(() => {
          this.setData({
            statusTip: ''
          });
        }, 5000);
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

  formatDateTime(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  },

  getStatusTip(systolic, diastolic, bloodSugar) {
    let tip = '';

    // 血压状态
    if (systolic < 90 || diastolic < 60) {
      tip += '血压偏低，请注意休息和补充营养。\n';
    } else if (systolic < 120 && diastolic < 80) {
      tip += '血压正常，请继续保持健康的生活方式。\n';
    } else if (systolic < 140 && diastolic < 90) {
      tip += '血压略高，请注意饮食和运动。\n';
    } else {
      tip += '血压较高，建议咨询医生。\n';
    }

    // 血糖状态
    if (bloodSugar < 3.9) {
      tip += '血糖偏低，请注意及时补充糖分。\n';
    } else if (bloodSugar < 6.1) {
      tip += '血糖正常，请继续保持健康的生活方式。\n';
    } else if (bloodSugar < 7.0) {
      tip += '血糖略高，请注意饮食控制。\n';
    } else {
      tip += '血糖较高，建议咨询医生。\n';
    }

    return tip;
  }
});