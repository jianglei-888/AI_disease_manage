# AI 慢性病管理系统 - 微信小程序

> 与 [../AI_disease_backend](../AI_disease_backend) 配套的前端。

## 技术栈

- 微信原生小程序（WXML / WXSS / JS）
- 微信开发者工具调试

## 快速开始

1. 用**微信开发者工具**打开 `AI_disease_front/` 目录
2. 修改 [utils/api.js](utils/api.js) 第 4 行，把 `API_BASE_URL` 改成你后端机器的局域网 IP（不能是 `127.0.0.1`，小程序不会走本机回环）

   ```js
   const API_BASE_URL = 'http://192.168.1.100:8001';  // 改成你的
   ```

3. 微信开发者工具里勾选 **不校验合法域名**（开发期）
4. 点"编译"

## 页面

| 页面 | 路径 | 说明 |
|---|---|---|
| 登录 | `pages/login` | 邮箱 + 密码登录 |
| 注册 | `pages/register` | 邮箱 + 用户名 + 密码 |
| 首页 | `pages/home` | 今日血压血糖卡片 + 快捷入口 |
| 提交数据 | `pages/submit` | 录入一条血压血糖记录 |
| 聊天 | `pages/chat` | 与 AI 健康助手对话 |
| 个人中心 | `pages/profile` | 退出登录 / 关于 |
| 个人信息 | `pages/personal-info` | 填写年龄 / 用药史等 |
| 数据分析 | `pages/analysis` | 历史趋势图表 |

## 目录结构

```
AI_disease_front/
├── app.js / app.json / app.wxss    # 全局
├── project.config.json             # 微信开发者工具项目配置
├── pages/                          # 8 个页面（每页 .wxml .js .json .wxss）
├── components/                     # 可复用组件
├── services/                       # 每个后端域一个 service
│   ├── auth.service.js
│   ├── health.service.js
│   └── chat.service.js
├── utils/
│   ├── api.js                      # wx.request 封装
│   ├── auth.js                     # token 存取
│   ├── storage.js                  # wx.storage 封装
│   └── common.js                   # 时间格式化 / Toast / 邮箱校验
└── images/                         # tabBar 图标
```

## 全局状态

`app.js` 的 `globalData` 持有 `token / userInfo / isLoggedIn`。登录成功后 `app.login(token, user)` 会同步存 `wx.storage`。`onLaunch` 时从 storage 恢复。

## 注意事项

- **不要把 `API_BASE_URL` 提交为生产域名**：项目代码里保留开发默认值，你部署时改成你服务端点
- 小程序要求 HTTPS 域名备案，**开发期只能在开发者工具里勾选"不校验合法域名"**
- 头像 / 图片资源都在 `images/`，直接替换即可
