// 模拟从后端获取的、AI已提取的事件
export const mockEvents = [
  {
    id: 1,
    title: "与申海彤讨论LLM集成",
    date: "2025-11-12",
    time: "14:00 - 15:00",
    location: "Zoom (链接待定)",
    attendees: ["zhou.xinquan@example.com", "shen.haitong@example.com"]
  },
  {
    id: 2,
    title: "与徐子怡同步UI组件库",
    date: "2025-11-13",
    time: "10:30 - 11:00",
    location: "COMP7607 Lab",
    attendees: ["zhou.xinquan@example.com", "xu.ziyi@example.com"]
  },
  {
    id: 3,
    title: "项目中期进度汇报",
    date: "2025-11-15",
    time: "16:00 - 17:00",
    location: "会议室 301",
    attendees: [
        "zhou.xinquan", 
        "xu.ziyi", 
        "zu.binshuo", 
        "shen.haitong", 
        "mao.wenyuan", 
        "he.junqian"
    ]
  }
];

// 模拟 AI 生成的邮件摘要
export const mockSummaries = [
  {
    id: 101,
    sender: "Shen Haitong",
    subject: "Re: LLM 集成问题",
    summary: "我已经完成了提示词工程（Prompt Engineering）的初稿 [cite: 69]。请在周三前查看，以便我们讨论 Gemini API 的集成细节。",
    receivedAt: "2025-11-10T18:30:00",
    hasEvent: true // 标记这个邮件包含一个待办事件
  },
  {
    id: 102,
    sender: "Course Admin (COMP7607A)",
    subject: "项目中期汇报安排",
    summary: "提醒所有小组：项目中期汇报定于下周五（11月15日）。请准备好你们的演示文稿和现场演示。",
    receivedAt: "2025-11-10T09:15:00",
    hasEvent: true
  },
  {
    id: 103,
    sender: "GitHub Notifications",
    subject: "[ai-email-scheduler] 2 issues created by zu.binshuo",
    summary: "祖宾硕 在你们的仓库中创建了 2 个新 issue：#1 '数据库连接失败' 和 #2 '用户认证API 404错误'。",
    receivedAt: "2025-11-09T21:45:00",
    hasEvent: false
  }
];