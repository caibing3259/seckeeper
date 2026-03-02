前端部分：backend/seckeeper-web
后端四个模块：
资产扫描backend/core/real_asset_scanner.py
合规检查backend/core/real_compliance_checker.py
漏洞扫描backend/core/real_vulnerability_scanner.py
报告生成backend/core/report_generator_fixed_safe.py
主程序backend/app.py

在网页和后端如果需要密码，sudo管理员密码为：yinheqilin1

操作流程：
双击桌面ces文件夹，找到backend文件夹，双击打开，在空白处鼠标右键
打开终端，输入运行，
sudo pip install -r requirements.txt（这一步安装依赖，运行正常可以跳过）
python3 app.py
回车；

保证前一个终端运行，在backend文件夹找到seckeeper-web双击打开，这是前端文件夹，
双击index.html文件即可打开浏览器进入相关页面


一、密码复杂度测试
项目通过系统配置检查来测试密码复杂度：
1.检查系统密码策略文件
读取 /etc/login.defs 中的 PASS_MIN_LEN 设置验证最小密码长度
检查 /etc/pam.d/common-password 中的 pam_pwquality.so 配置
验证是否启用了密码复杂度要求（如要求混合字符类型）
2.密码熵计算
使用数学公式计算密码强度：密码长度 × log₂(使用的字符集大小)
字符集包括小写字母、大写字母、数字、特殊字符
根据熵值评估密码强度等级
3.实际检查项目
密码最小长度是否达到安全标准（通常8位以上）
是否强制要求使用多种字符类型
密码过期策略设置
密码历史记录防止重复使用
二、CVE漏洞数据导入
项目采用本地JSON数据库管理CVE：
1.数据存储方式
使用 data/cve_database.json 文件存储所有CVE信息
每个CVE记录包含完整的元数据：ID、严重程度、描述、影响范围、修复方案等
2.导入新CVE的方法
首次运行自动初始化：创建包含基础CVE记录的数据库
手动JSON导入：通过格式化的JSON文件批量导入新CVE
单个CVE添加：直接编辑JSON文件添加个别漏洞
3.数据更新机制
代码预留了从NVD官方API获取数据的接口
支持从Ubuntu/Debian安全公告获取漏洞信息
提供数据合并和去重功能
