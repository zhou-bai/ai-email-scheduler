# ai-email-scheduler
/docs存放api规范

后端用venv
克隆环境后`pip install -r requirements.txt`看看能不能安装依赖
后续你们有自己的依赖可以`pip freeze > requirements.txt`
测试依赖：`uvicorn main:app --reload`
打开`http://127.0.0.1:8000`
`http://127.0.0.1:8000/docs` 看 FastAPI 自动生成的 API 文档

# 前端启动
`npm run dev`

# 本地数据库初始化
`mysql -u root -p` 登陆数据库
`CREATE DATABASE ai_email_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
`mysql -u root -p ai_email_assistant < back-end/database/schema.sql`
这里的schema.sql只是示例，负责数据库设计的同学记得改里面的sql语句
复制.env.example里面的内容到自己的.env文件里面，记得改成自己的PASSWORD

# v1.0后端任务流程
1. 确认.env文件内有Google OAuth相关配置，可以使用自己的OAuth ID和密钥。如果使用我提供的配置需要发下你的gmail邮箱，添加进测试用户后即可正常使用
2. 启动后端程序，通过下面的地址获取授权链接：`http://127.0.0.1:8000/api/v1/auth/google/url?user_id=email` （填写自己的邮箱）
3. 访问输出的URL，选择账户并同意权限（包括 Gmail 和 Calendar）
4. 授权成功后会回到 `http://127.0.0.1:8000/api/v1/auth/google/callback?` ，此时后端完成令牌交换，检查数据库是否成功写入对应的用户和令牌
5. （可选）提前发送几封测试邮件给自己邮箱
6. 运行/tasks/example_scheduler_snippet.py，记得把里面user_key = "..."更改为自己的邮箱
