# 掼蛋扑克游戏

一个基于 HTML5 的掼蛋扑克游戏，支持单机模式和联机模式。

## 功能特点

- 单机模式：与 AI 对战
- 联机模式：支持多人实时对战
- 完整的掼蛋游戏规则实现
- 实时游戏状态同步
- 美观的用户界面

## 技术栈

- 前端：Vue.js + HTML5 + CSS3
- 后端：Python FastAPI
- 数据库：MongoDB

## 项目结构

```
guandan/
├── frontend/          # 前端代码
│   ├── src/
│   │   ├── components/  # Vue 组件
│   │   ├── views/      # 页面视图
│   │   ├── assets/     # 静态资源
│   │   └── utils/      # 工具函数
│   └── package.json
├── backend/           # 后端代码
│   ├── app/          # 应用代码
│   └── tests/        # 测试代码
└── README.md
```

## 安装和运行

### 前端

```bash
cd frontend
npm install
npm run serve
```

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 游戏规则

1. 4人对战，分两队（队友坐对角）
2. 使用两副扑克牌（108张）
3. 支持多种牌型：单张、对子、三张、顺子等
4. 包含特殊规则：炸弹、同花顺、逢人配等
5. 采用升级制，从2级开始，最高到A级

## 开发计划

- [x] 项目初始化
- [ ] 基础游戏逻辑实现
- [ ] 单机模式开发
- [ ] 联机模式开发
- [ ] UI 设计和实现
- [ ] 测试和优化
