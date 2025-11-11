# ai-email-scheduler
/docs存放api规范

后端用venv  
克隆环境后`pip install -r requirements.txt`看看能不能安装依赖  
后续你们有自己的依赖可以`pip freeze > requirements.txt  `  
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