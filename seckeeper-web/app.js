/// SecKeeper 前端逻辑 - 完整全面版本
class SecKeeperAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.timeout = 30000;
    }
    
    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            console.log(`[API] 请求: ${this.baseURL}${endpoint}`, options);
            
            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                signal: controller.signal,
                ...options
            };
            
            if (options.method === 'POST' && options.body) {
                config.body = JSON.stringify(options.body);
            }
            
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            console.log(`[API] 响应类型: ${contentType}`);
            
            if (contentType && contentType.includes('application/pdf')) {
                const blob = await response.blob();
                console.log(`[API] PDF blob 大小: ${blob.size} 字节`);
                return blob;
            }
            
            const data = await response.json();
            console.log(`[API] 响应:`, data);
            return data;
            
        } catch (error) {
            clearTimeout(timeoutId);
            console.error(`[API] 请求失败: ${endpoint}`, error);
            
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请检查后端服务是否启动');
            }
            throw error;
        }
    }
    
    async getSystemInfo() {
        return await this.request('/api/dashboard');
    }
    
    async getAssets() {
        return await this.request('/api/assets');
    }
    
    async getComplianceResults() {
        return await this.request('/api/compliance');
    }
    
    async getVulnerabilities() {
        return await this.request('/api/vulnerabilities');
    }
    
    async startFullScan() {
        return await this.request('/api/scan', { method: 'POST' });
    }
    
    async getScanStatus() {
        return await this.request('/api/scan/status');
    }
    
    async getSystemStatus() {
        return await this.request('/api/health');
    }
    
    async generateReport(scanData) {
        console.log('📤 发送PDF生成请求，数据:', scanData);
        return await this.request('/api/report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: scanData
        });
    }
}

class SecKeeperApp {
    constructor() {
        this.currentTab = 'dashboard';
        this.charts = {};
        this.api = new SecKeeperAPI();
        this.currentData = {
            systemInfo: null,
            software: [],
            services: [],
            compliance: [],
            vulnerabilities: []
        };
        this.scanState = {
            isScanning: false,
            lastScanTime: null,
            scanTimeout: null
        };
        this.init();
    }
    
    init() {
        console.log('SecKeeper 安全卫士初始化完成！');
        this.setupEventListeners();
        this.initCharts();
        this.showTab('dashboard');
        this.loadAllData();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        document.querySelectorAll('.nav-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('data-tab');
                this.showTab(tabName);
            });
        });
        
        const scanButton = document.querySelector('.scan-button');
        if (scanButton) {
            scanButton.addEventListener('click', () => {
                this.startFullScan();
            });
        }
        
        const reportButton = document.querySelector('.report-button');
        if (reportButton) {
            reportButton.addEventListener('click', () => {
                this.generatePDFReport();
            });
        }
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch(e.key) {
                    case '1': this.showTab('dashboard'); break;
                    case '2': this.showTab('assets'); break;
                    case '3': this.showTab('compliance'); break;
                    case '4': this.showTab('vulnerabilities'); break;
                    case 'r': this.refreshCurrentTab(); break;
                    case 'p': this.generatePDFReport(); break;
                }
            }
        });
    }
    
    showTab(tabName) {
        this.currentTab = tabName;
        
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active-tab');
        });
        document.querySelectorAll('.nav-button').forEach(btn => {
            btn.classList.remove('active-nav');
        });
        
        const activeTab = document.getElementById(tabName);
        const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
        
        if (activeTab) {
            activeTab.classList.add('active-tab');
        }
        if (activeBtn) {
            activeBtn.classList.add('active-nav');
        }
        
        this.loadTabData(tabName);
    }
    
    loadTabData(tabName) {
        console.log('切换到标签页:', tabName);
        switch(tabName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'assets':
                this.loadAssetData();
                break;
            case 'compliance':
                this.loadComplianceData();
                break;
            case 'vulnerabilities':
                this.loadVulnerabilityData();
                break;
        }
    }
    
    async loadAllData() {
        try {
            await this.loadSystemInfo();
            await this.loadAssetData();
            await this.loadComplianceData();
            await this.loadVulnerabilityData();
            this.loadDashboardData();
            this.showNotification('<i class="fas fa-plug"></i> 成功连接到后端服务', 'success');
        } catch (error) {
            console.warn('后端服务连接失败，使用模拟数据:', error);
            this.showNotification('<i class="fas fa-wifi-slash"></i> 后端服务未连接，使用演示数据', 'warning');
            this.loadMockData();
        }
    }
    
    async loadSystemInfo() {
        try {
            const response = await this.api.getSystemInfo();
            this.currentData.systemInfo = response.data || response;
        } catch (error) {
            console.warn('获取系统信息失败，使用模拟数据');
            this.currentData.systemInfo = this.getMockSystemInfo();
            throw error;
        }
    }
    
    async loadDashboardData() {
        this.updateDashboardStats();
        this.displayRealTimeStatus();
        setTimeout(() => {
            this.refreshCharts();
        }, 500);
    }
    
    async loadAssetData() {
        try {
            this.showLoading('assets', '<i class="fas fa-sync-alt loading-spinner"></i> 正在获取资产信息...');
            
            const assetsData = await this.api.getAssets();
            
            if (assetsData.success) {
                this.currentData.software = assetsData.data?.software || [];
                this.currentData.services = assetsData.data?.services || [];
            } else {
                throw new Error(assetsData.error || '获取资产数据失败');
            }
            
            this.displayAssetData();
            
        } catch (error) {
            this.showError('assets', `<i class="fas fa-exclamation-circle"></i> 获取资产数据失败: ${error.message}`);
            this.loadMockAssetData();
        }
    }
    
    async loadComplianceData() {
        try {
            this.showLoading('compliance', '<i class="fas fa-shield-alt"></i> 正在执行合规检查...');
            
            const complianceData = await this.api.getComplianceResults();
            console.log('合规检查原始数据:', complianceData);
            
            if (complianceData.success) {
                this.currentData.compliance = complianceData.data || complianceData;
            } else {
                throw new Error(complianceData.error || '获取合规数据失败');
            }
            
            this.displayComplianceData(this.currentData.compliance);
            
        } catch (error) {
            console.error('合规检查加载失败:', error);
            this.showError('compliance', `<i class="fas fa-exclamation-circle"></i> 获取合规数据失败: ${error.message}`);
            this.loadMockComplianceData();
        }
    }
    
    async loadVulnerabilityData() {
        try {
            this.showLoading('vulnerabilities', '<i class="fas fa-search"></i> 正在扫描漏洞...');
            
            const vulnData = await this.api.getVulnerabilities();
            console.log('漏洞扫描原始数据:', vulnData);
            
            if (vulnData.success) {
                this.currentData.vulnerabilities = vulnData.data || vulnData;
            } else {
                throw new Error(vulnData.error || '获取漏洞数据失败');
            }
            
            this.displayVulnerabilityData(this.currentData.vulnerabilities);
            
        } catch (error) {
            console.error('漏洞扫描加载失败:', error);
            this.showError('vulnerabilities', `<i class="fas fa-exclamation-circle"></i> 获取漏洞数据失败: ${error.message}`);
            this.loadMockVulnerabilityData();
        }
    }
    
    updateDashboardStats() {
        const dashboardData = this.currentData.systemInfo?.overview || {};
        const stats = {
            totalAssets: dashboardData.assets ? (dashboardData.assets.software_count + dashboardData.assets.service_count) : 0,
            complianceRate: dashboardData.compliance?.compliance_rate || this.calculateComplianceRate(),
            highRiskCount: dashboardData.vulnerabilities?.high || 0
        };
        
        document.getElementById('total-assets').textContent = stats.totalAssets;
        document.getElementById('compliance-rate').textContent = stats.complianceRate + '%';
        document.getElementById('high-risk-count').textContent = stats.highRiskCount;
    }
    
    calculateComplianceRate() {
        if (!this.currentData.compliance || !this.currentData.compliance.summary) return 0;
        return this.currentData.compliance.summary.compliance_rate || 0;
    }
    
    displayRealTimeStatus() {
        const systemInfo = this.currentData.systemInfo || {};
        const overview = systemInfo.overview || {};
        
        const statusData = [
            { 
                icon: 'microchip',
                label: '系统状态', 
                value: overview.system_health === 'healthy' ? '健康' : '异常', 
                status: overview.system_health === 'healthy' ? 'normal' : 'warning'
            },
            { 
                icon: 'box',
                label: '软件数量', 
                value: overview.assets?.software_count || 0, 
                status: 'normal' 
            },
            { 
                icon: 'cogs',
                label: '服务数量', 
                value: overview.assets?.service_count || 0, 
                status: 'normal' 
            },
            { 
                icon: 'shield-alt',
                label: '合规率', 
                value: (overview.compliance?.compliance_rate || 0) + '%', 
                status: 'normal' 
            }
        ];
        
        const statusGrid = document.getElementById('real-time-status');
        if (!statusGrid) return;
        
        statusGrid.innerHTML = statusData.map(item => `
            <div class="status-item ${item.status}">
                <div class="status-icon">
                    <i class="fas fa-${item.icon}"></i>
                </div>
                <div class="status-info">
                    <div class="status-label">${item.label}</div>
                    <div class="status-value">${item.value}</div>
                </div>
            </div>
        `).join('');
    }
    
    displayAssetData() {
        const assetsTab = document.getElementById('assets');
        
        const systemInfoHTML = this.displaySystemInfo();
        
        let softwareHTML = `
            <div style="margin-bottom: 25px;">
                <h4 style="color: #2c3e50; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-box"></i> 已安装软件 (${this.currentData.software.length}个)
                </h4>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th><i class="fas fa-cube"></i> 软件名称</th>
                            <th><i class="fas fa-code-branch"></i> 版本</th>
                            <th><i class="fas fa-info-circle"></i> 状态</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        this.currentData.software.forEach(pkg => {
            softwareHTML += `
                <tr>
                    <td><i class="fas fa-cube" style="color: #3498db; margin-right: 8px;"></i>${pkg.name || pkg.package_name || '未知软件'}</td>
                    <td>${pkg.version || pkg.package_version || '未知版本'}</td>
                    <td><span class="status-indicator status-safe"><i class="fas fa-check"></i> 已安装</span></td>
                </tr>
            `;
        });
        
        softwareHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        let servicesHTML = `
            <div>
                <h4 style="color: #2c3e50; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-cogs"></i> 系统服务 (${this.currentData.services.length}个)
                </h4>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th><i class="fas fa-server"></i> 服务名称</th>
                            <th><i class="fas fa-power-off"></i> 状态</th>
                            <th><i class="fas fa-info-circle"></i> 描述</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        this.currentData.services.forEach(service => {
            const status = service.status || service.state || 'running';
            const statusClass = status === 'running' ? 'status-safe' : 'status-warning';
            const statusText = status === 'running' ? '<i class="fas fa-play"></i> 运行中' : '<i class="fas fa-stop"></i> 已停止';
            
            servicesHTML += `
                <tr>
                    <td><i class="fas fa-server" style="color: #e67e22; margin-right: 8px;"></i>${service.name || service.service_name || '未知服务'}</td>
                    <td><span class="status-indicator ${statusClass}">${statusText}</span></td>
                    <td>${service.description || '系统服务'}</td>
                </tr>
            `;
        });
        
        servicesHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        assetsTab.innerHTML = `
            ${systemInfoHTML}
            <div class="card">
                <h3><i class="fas fa-desktop"></i> 软件资产总览</h3>
                <p style="margin-bottom: 20px;"><i class="fas fa-info-circle"></i> 共发现 <strong>${this.currentData.software.length}</strong> 个软件包，<strong>${this.currentData.services.length}</strong> 个系统服务</p>
                ${softwareHTML}
                ${servicesHTML}
            </div>
        `;
    }
    
    displaySystemInfo() {
        const info = this.currentData.systemInfo || {};
        
        return `
            <div class="card">
                <h3><i class="fas fa-info-circle"></i> 系统信息</h3>
                <div class="system-info-grid">
                    <div class="system-info-item"><i class="fas fa-laptop"></i> <strong>操作系统:</strong> ${info.os_name || info.os || '银河麒麟 V10'}</div>
                    <div class="system-info-item"><i class="fas fa-code"></i> <strong>内核版本:</strong> ${info.kernel_version || info.kernel || '5.10.0'}</div>
                    <div class="system-info-item"><i class="fas fa-microchip"></i> <strong>系统架构:</strong> ${info.architecture || 'x86_64'}</div>
                    <div class="system-info-item"><i class="fas fa-desktop"></i> <strong>主机名:</strong> ${info.hostname || 'kylin-server'}</div>
                    <div class="system-info-item"><i class="fas fa-clock"></i> <strong>运行时间:</strong> ${info.uptime || '1天'}</div>
                    <div class="system-info-item"><i class="fas fa-users"></i> <strong>在线用户:</strong> ${info.users || '1'}</div>
                </div>
            </div>
        `;
    }
    
    displayComplianceData(complianceData) {
        const complianceTab = document.getElementById('compliance');
        
        // 兼容多种数据结构
        const summary = complianceData.summary || {};
        const checks = complianceData.checks || complianceData.details || [];
        const passedCount = summary.passed || 0;
        const totalCount = summary.total || 0;
        const passRate = summary.compliance_rate || 0;
        
        console.log('显示合规数据:', { summary, checks, passedCount, totalCount, passRate });
        
        let complianceHTML = `
            <div class="card">
                <h3><i class="fas fa-shield-alt"></i> 安全合规检查</h3>
                <p style="margin-bottom: 20px;"><i class="fas fa-chart-bar"></i> 共检查 <strong>${totalCount}</strong> 个项目，通过率: <strong>${passRate}%</strong></p>
        `;
        
        if (checks.length === 0) {
            complianceHTML += `
                <div style="text-align: center; padding: 40px; color: #7f8c8d;">
                    <i class="fas fa-info-circle" style="font-size: 48px; margin-bottom: 20px;"></i>
                    <h3>暂无合规检查数据</h3>
                    <p>请执行一键扫描或检查后端服务</p>
                </div>
            `;
        } else {
            checks.forEach((item, index) => {
                const isPassed = item.passed || item.status === 'passed';
                const statusColor = isPassed ? '#27ae60' : '#e74c3c';
                const statusText = isPassed ? '通过' : '失败';
                const statusIcon = isPassed ? 'fa-check-circle' : 'fa-times-circle';
                const severity = item.risk_level || item.severity || 'medium';
                const severityText = severity === '高' || severity === 'high' ? '高危' : 
                                   severity === '中' || severity === 'medium' ? '中危' : '低危';
                const severityColor = severity === '高' || severity === 'high' ? '#e74c3c' : 
                                    severity === '中' || severity === 'medium' ? '#f39c12' : '#f1c40f';
                const severityIcon = severity === '高' || severity === 'high' ? 'fa-exclamation-triangle' : 
                                   severity === '中' || severity === 'medium' ? 'fa-exclamation' : 'fa-info-circle';
                
                complianceHTML += `
                    <div style="padding: 16px; margin: 12px 0; background: white; border-radius: 8px; border-left: 4px solid ${statusColor}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <strong style="flex: 1; min-width: 200px; font-size: 14px;">
                                <i class="fas ${severityIcon}" style="color: ${severityColor}; margin-right: 8px;"></i>
                                ${item.name || item.check || '安全检查项'}
                            </strong>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <span style="padding: 4px 8px; background: ${severityColor}; color: white; border-radius: 3px; font-size: 11px; font-weight: bold;">
                                    <i class="fas ${severityIcon}"></i> ${severityText}
                                </span>
                                <span style="color: ${statusColor}; font-weight: bold; display: flex; align-items: center; gap: 4px;">
                                    <i class="fas ${statusIcon}"></i>
                                    ${statusText}
                                </span>
                            </div>
                        </div>
                        <div style="color: #666; margin-top: 8px; font-size: 13px;">${item.description || item.details || '安全检查描述'}</div>
                        
                        ${item.checks ? `
                        <div style="margin-top: 12px; border-top: 1px solid #eee; padding-top: 12px;">
                            ${item.checks.map(check => `
                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid #f5f5f5;">
                                    <span style="font-size: 12px;">${check.name || '检查项'}</span>
                                    <span style="color: ${check.passed ? '#27ae60' : '#e74c3c'}; font-size: 12px;">
                                        ${check.passed ? '✓ 通过' : '✗ 失败'}
                                    </span>
                                </div>
                            `).join('')}
                        </div>` : ''}
                        
                        ${item.fix_suggestion || item.solution ? `
                        <div style="color: #e67e22; margin-top: 6px; font-size: 12px;">
                            <i class="fas fa-wrench"></i> <strong>修复建议:</strong> ${item.fix_suggestion || item.solution}
                        </div>` : ''}
                    </div>
                `;
            });
        }
        
        complianceHTML += '</div>';
        complianceTab.innerHTML = complianceHTML;
    }
    
    displayVulnerabilityData(vulnData) {
        const vulnTab = document.getElementById('vulnerabilities');
        
        // 兼容多种数据结构
        const vulnerabilities = vulnData.vulnerabilities || vulnData || [];
        const summary = vulnData.summary || {};
        
        console.log('显示漏洞数据:', { vulnerabilities, summary });
        
        let vulnHTML = `
            <div class="card">
                <h3><i class="fas fa-bug"></i> 系统漏洞扫描结果</h3>
                <p style="margin-bottom: 20px;"><i class="fas fa-search"></i> 共发现 <strong>${summary.total || vulnerabilities.length}</strong> 个安全漏洞</p>
        `;
        
        if (vulnerabilities.length === 0) {
            vulnHTML += `
                <div style="text-align: center; padding: 40px; color: #27ae60;">
                    <i class="fas fa-check-circle" style="font-size: 48px; margin-bottom: 20px;"></i>
                    <h3>未发现安全漏洞</h3>
                    <p>系统当前处于安全状态</p>
                </div>
            `;
        } else {
            vulnerabilities.forEach(vuln => {
                const level = vuln.severity || vuln.level || 'medium';
                const levelColor = level === 'critical' ? '#8b0000' : 
                                 level === 'high' ? '#e74c3c' : 
                                 level === 'medium' ? '#f39c12' : '#f1c40f';
                const levelText = level === 'critical' ? '严重' : 
                                level === 'high' ? '高危' : 
                                level === 'medium' ? '中危' : '低危';
                const levelIcon = level === 'critical' ? 'fa-skull-crossbones' : 
                                level === 'high' ? 'fa-exclamation-triangle' : 
                                level === 'medium' ? 'fa-exclamation' : 'fa-info-circle';
                
                vulnHTML += `
                    <div style="background: white; padding: 18px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid ${levelColor};">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong style="color: ${levelColor}; font-size: 1.1em;">
                                    <i class="fas fa-bug"></i> ${vuln.cve_id || vuln.id || '未知漏洞'}
                                </strong>
                                <span style="margin-left: 10px; padding: 4px 8px; background: ${levelColor}; color: white; border-radius: 3px; font-size: 11px; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;">
                                    <i class="fas ${levelIcon}"></i>
                                    ${levelText}
                                </span>
                            </div>
                            <div style="color: #7f8c8d; font-size: 12px;">
                                <i class="fas fa-calendar"></i> 发现时间: ${vuln.discovered || new Date().toISOString().split('T')[0]}
                            </div>
                        </div>
                        <div style="margin-top: 12px;">
                            <div style="margin-bottom: 6px; font-size: 13px;">
                                <i class="fas fa-file-alt"></i> <strong>标题:</strong> ${vuln.title || '漏洞标题'}
                            </div>
                            <div style="margin-bottom: 6px; font-size: 13px;">
                                <i class="fas fa-file-alt"></i> <strong>描述:</strong> ${vuln.description || vuln.details || '漏洞描述'}
                            </div>
                            <div style="margin-bottom: 6px; font-size: 13px;">
                                <i class="fas fa-cube"></i> <strong>影响组件:</strong> ${vuln.affected_software || vuln.affected || vuln.component || '系统组件'}
                            </div>
                            <div style="margin-bottom: 6px; font-size: 13px;">
                                <i class="fas fa-wrench"></i> <strong>修复方案:</strong> 
                                <code style="background: #f8f9fa; padding: 4px 8px; border-radius: 4px; font-family: 'Courier New', monospace; margin-left: 6px; font-size: 12px; border: 1px solid #e9ecef;">
                                    ${vuln.remediation || vuln.solution || vuln.fix || '请参考官方安全公告'}
                                </code>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        vulnHTML += '</div>';
        vulnTab.innerHTML = vulnHTML;
    }
    
    // === PDF报告生成功能 ===
    
    async generatePDFReport() {
        try {
            this.showNotification('<i class="fas fa-file-pdf"></i> 正在生成PDF报告...', 'info');
            
            const reportData = {
                scan_id: `report_${Date.now()}`,
                timestamp: new Date().toISOString(),
                assets: {
                    software: this.currentData.software,
                    services: this.currentData.services
                },
                compliance: this.currentData.compliance,
                vulnerabilities: this.currentData.vulnerabilities
            };
            
            console.log('📤 发送PDF报告数据:', reportData);
            
            const pdfBlob = await this.api.generateReport(reportData);
            
            if (!pdfBlob || pdfBlob.size === 0) {
                throw new Error('PDF文件为空');
            }
            
            console.log('✅ 收到PDF blob:', pdfBlob.size, '字节');
            
            const url = window.URL.createObjectURL(pdfBlob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `seckeeper_report_${new Date().toISOString().split('T')[0]}.pdf`;
            
            document.body.appendChild(a);
            a.click();
            
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showNotification('<i class="fas fa-check-circle"></i> PDF报告生成成功！', 'success');
            
        } catch (error) {
            console.error('❌ 生成PDF报告失败:', error);
            this.showNotification('<i class="fas fa-times-circle"></i> 生成PDF报告失败: ' + error.message, 'error');
            
            if (error.message.includes('后端服务未启动')) {
                this.showNotification('<i class="fas fa-info-circle"></i> 请确保后端服务正在运行', 'warning');
            } else if (error.message.includes('PDF文件为空')) {
                this.showNotification('<i class="fas fa-info-circle"></i> 后端PDF生成器返回了空文件', 'warning');
            }
        }
    }
    
    // === 图表功能 ===
    
    initCharts() {
        console.log('开始初始化图表');
        setTimeout(() => {
            this.initVulnerabilityChart();
            this.initComplianceChart();
        }, 100);
    }
    
    initVulnerabilityChart() {
        const chartElement = document.getElementById('vulnPieChart');
        if (!chartElement) {
            console.log('未找到漏洞图表容器');
            return;
        }

        try {
            const dashboardData = this.currentData.systemInfo?.overview || {};
            const vulnOverview = dashboardData.vulnerabilities || {};
            
            let levelCount = {
                critical: vulnOverview.critical || 0,
                high: vulnOverview.high || 0,
                medium: vulnOverview.medium || 0,
                low: vulnOverview.low || 0
            };
            
            if (levelCount.critical === 0 && levelCount.high === 0 && 
                levelCount.medium === 0 && levelCount.low === 0) {
                const vulnData = this.currentData.vulnerabilities || {};
                const vulnerabilities = vulnData.vulnerabilities || vulnData || [];
                
                levelCount = {
                    critical: vulnerabilities.filter(v => (v.severity || v.level) === 'critical').length,
                    high: vulnerabilities.filter(v => (v.severity || v.level) === 'high').length,
                    medium: vulnerabilities.filter(v => (v.severity || v.level) === 'medium').length,
                    low: vulnerabilities.filter(v => (v.severity || v.level) === 'low').length
                };
            }
            
            console.log('漏洞等级分布数据:', levelCount);
            
            this.charts.vulnerability = echarts.init(chartElement);
            const option = {
                title: {
                    text: '漏洞等级分布',
                    left: 'center',
                    textStyle: {
                        color: '#2c3e50',
                        fontSize: 14
                    }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                legend: {
                    orient: 'horizontal',
                    bottom: '0%',
                    data: ['严重', '高危', '中危', '低危']
                },
                series: [{
                    name: '漏洞等级',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: true,
                        formatter: '{b}: {c}'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: '16',
                            fontWeight: 'bold'
                        }
                    },
                    labelLine: {
                        show: true
                    },
                    data: [
                        { 
                            value: levelCount.critical, 
                            name: '严重', 
                            itemStyle: { color: '#8b0000' } 
                        },
                        { 
                            value: levelCount.high, 
                            name: '高危', 
                            itemStyle: { color: '#e74c3c' } 
                        },
                        { 
                            value: levelCount.medium, 
                            name: '中危', 
                            itemStyle: { color: '#f39c12' } 
                        },
                        { 
                            value: levelCount.low, 
                            name: '低危', 
                            itemStyle: { color: '#f1c40f' } 
                        }
                    ]
                }]
            };
            
            this.charts.vulnerability.setOption(option);
            console.log('漏洞图表初始化完成');
            
        } catch (error) {
            console.error('初始化漏洞图表失败:', error);
        }
    }
    
    initComplianceChart() {
        const chartElement = document.getElementById('complianceChart');
        if (!chartElement) {
            console.log('未找到合规图表容器');
            return;
        }

        try {
            const dashboardData = this.currentData.systemInfo?.overview || {};
            const complianceOverview = dashboardData.compliance || {};
            
            let passedCount = complianceOverview.passed_checks || 0;
            let totalCount = complianceOverview.total_checks || 0;
            let failedCount = totalCount - passedCount;
            
            if (totalCount === 0) {
                const complianceData = this.currentData.compliance || {};
                const summary = complianceData.summary || {};
                passedCount = summary.passed || 0;
                totalCount = summary.total || 0;
                failedCount = summary.failed || (totalCount - passedCount);
            }
            
            console.log('合规检查数据:', { passedCount, failedCount, totalCount });
            
            this.charts.compliance = echarts.init(chartElement);
            const option = {
                title: {
                    text: '合规检查统计',
                    left: 'center',
                    textStyle: {
                        color: '#2c3e50',
                        fontSize: 14
                    }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                legend: {
                    orient: 'horizontal',
                    bottom: '0%',
                    data: ['通过', '未通过']
                },
                series: [{
                    name: '合规检查',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: true,
                        formatter: '{b}: {c} ({d}%)'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: '16',
                            fontWeight: 'bold'
                        }
                    },
                    labelLine: {
                        show: true
                    },
                    data: [
                        { 
                            value: passedCount, 
                            name: '通过', 
                            itemStyle: { color: '#27ae60' } 
                        },
                        { 
                            value: failedCount, 
                            name: '未通过', 
                            itemStyle: { color: '#e74c3c' } 
                        }
                    ]
                }]
            };
            
            this.charts.compliance.setOption(option);
            console.log('合规图表初始化完成');
            
        } catch (error) {
            console.error('初始化合规图表失败:', error);
        }
    }
    
    refreshCharts() {
        if (this.charts.vulnerability) {
            this.charts.vulnerability.dispose();
        }
        if (this.charts.compliance) {
            this.charts.compliance.dispose();
        }
        
        this.initVulnerabilityChart();
        this.initComplianceChart();
    }
    
    // === 交互功能 ===
    
    async startFullScan() {
        if (this.scanState.isScanning) {
            this.showNotification('<i class="fas fa-sync-alt"></i> 扫描正在进行中，请稍候...', 'warning');
            return;
        }

        const button = document.querySelector('.scan-button');
        const originalText = button.innerHTML;
        
        this.scanState.isScanning = true;
        
        button.innerHTML = '<i class="fas fa-sync-alt loading-spinner"></i> 正在扫描，请稍候...';
        button.disabled = true;

        this.showNotification('<i class="fas fa-search"></i> 开始安全扫描...', 'info');
        
        try {
            console.log('开始执行全盘扫描...');
            
            const result = await this.api.startFullScan();
            
            if (result.success) {
                button.innerHTML = '<i class="fas fa-check-circle"></i> 扫描完成！';
                this.showNotification('<i class="fas fa-check-circle"></i> 安全扫描完成，数据已更新', 'success');
                
                this.showNotification('<i class="fas fa-sync-alt"></i> 正在更新数据...', 'info');
                
                await new Promise(resolve => setTimeout(resolve, 3000));
                await this.loadAllData();
                
                setTimeout(() => {
                    this.refreshCharts();
                    this.showNotification('<i class="fas fa-chart-pie"></i> 图表已更新', 'success');
                }, 1000);
                
            } else {
                throw new Error(result.error || '扫描失败');
            }
            
        } catch (error) {
            console.error('扫描失败:', error);
            button.innerHTML = '<i class="fas fa-times-circle"></i> 扫描失败';
            
            if (error.message.includes('后端服务未启动')) {
                this.showNotification('<i class="fas fa-server"></i> ' + error.message, 'error');
                this.showNotification('<i class="fas fa-info-circle"></i> 请运行: python app.py', 'warning');
            } else {
                this.showNotification('<i class="fas fa-times-circle"></i> 扫描失败: ' + error.message, 'error');
            }
            
            this.showNotification('<i class="fas fa-eye"></i> 使用演示数据更新图表', 'warning');
            this.loadMockData();
            
        } finally {
            this.scanState.isScanning = false;
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        }
    }
    
    // === 工具方法 ===
    
    showLoading(tabId, message = '<i class="fas fa-sync-alt loading-spinner"></i> 加载中...') {
        const tab = document.getElementById(tabId);
        tab.innerHTML = `
            <div class="card">
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 20px; color: #3498db;">
                        <i class="fas fa-sync-alt loading-spinner"></i>
                    </div>
                    <h3>${message}</h3>
                    <p>正在从安全引擎获取数据</p>
                </div>
            </div>
        `;
    }
    
    showError(tabId, message) {
        const tab = document.getElementById(tabId);
        const errorHTML = `
            <div class="card">
                <div style="text-align: center; padding: 40px; color: #e74c3c;">
                    <div style="font-size: 48px; margin-bottom: 20px;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3>数据加载失败</h3>
                    <p>${message}</p>
                    <div style="margin-top: 20px;">
                        <button onclick="window.secKeeperApp.retryLoad('${tabId}')" 
                                style="padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                            <i class="fas fa-redo"></i> 重试
                        </button>
                        <button onclick="window.secKeeperApp.useMockData('${tabId}')" 
                                style="padding: 10px 20px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                            <i class="fas fa-eye"></i> 使用演示数据
                        </button>
                    </div>
                </div>
            </div>
        `;
        tab.innerHTML = errorHTML;
    }
    
    async retryLoad(tabId) {
        await this[`load${tabId.charAt(0).toUpperCase() + tabId.slice(1)}Data`]();
    }
    
    useMockData(tabId) {
        switch(tabId) {
            case 'assets': this.loadMockAssetData(); break;
            case 'compliance': this.loadMockComplianceData(); break;
            case 'vulnerabilities': this.loadMockVulnerabilityData(); break;
        }
    }
    
    showNotification(message, type = 'info') {
        const colors = {
            info: '#3498db',
            success: '#27ae60',
            warning: '#f39c12',
            error: '#e74c3c'
        };
        
        const icons = {
            info: 'fa-info-circle',
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle'
        };
        
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type]};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            font-size: 14px;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="fas ${icons[type]}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    startAutoRefresh() {
        setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.loadDashboardData();
            }
        }, 60000);
    }
    
    refreshCurrentTab() {
        this.loadTabData(this.currentTab);
        this.showNotification('<i class="fas fa-sync-alt"></i> 数据已刷新', 'success');
    }
    
    // === 模拟数据方法 ===
    
    loadMockData() {
        this.currentData.systemInfo = this.getMockSystemInfo();
        this.currentData.software = this.getMockSoftware();
        this.currentData.services = this.getMockServices();
        this.currentData.compliance = this.getMockCompliance();
        this.currentData.vulnerabilities = this.getMockVulnerabilities();
        
        setTimeout(() => {
            this.refreshCharts();
        }, 500);
    }
    
    getMockSystemInfo() {
        return {
            overview: {
                assets: {
                    software_count: 156,
                    service_count: 23
                },
                compliance: {
                    total_checks: 10,
                    passed_checks: 8,
                    compliance_rate: 80
                },
                vulnerabilities: {
                    total: 2,
                    high: 1,
                    critical: 0,
                    medium: 1,
                    low: 0
                },
                system_health: "healthy"
            },
            os_name: '银河麒麟 V10 SP1',
            kernel_version: '5.10.0-18-generic',
            architecture: 'x86_64',
            hostname: 'kylin-secure-pc',
            uptime: '3天12小时',
            users: 1
        };
    }
    
    getMockSoftware() {
        return [
            { name: 'firefox', version: '100.0.kylin' },
            { name: 'python3', version: '3.8.0' },
            { name: 'openssh-server', version: '8.0p1' },
            { name: 'docker-ce', version: '20.10.0' },
            { name: 'nginx', version: '1.18.0' },
            { name: 'mysql-server', version: '8.0.0' }
        ];
    }
    
    getMockServices() {
        return [
            { name: 'sshd', status: 'running', description: 'SSH远程访问服务' },
            { name: 'docker', status: 'running', description: '容器引擎服务' },
            { name: 'nginx', status: 'running', description: 'Web服务器' },
            { name: 'mysql', status: 'running', description: '数据库服务' },
            { name: 'firewalld', status: 'running', description: '防火墙服务' }
        ];
    }
    
    loadMockAssetData() {
        this.currentData.software = this.getMockSoftware();
        this.currentData.services = this.getMockServices();
        this.displayAssetData();
    }
    
    loadMockComplianceData() {
        this.currentData.compliance = this.getMockCompliance();
        this.displayComplianceData(this.currentData.compliance);
    }
    
    getMockCompliance() {
        return {
            summary: {
                total: 10,
                passed: 8,
                failed: 2,
                compliance_rate: 80.0
            },
            checks: [
                { 
                    name: 'SSH服务安全配置',
                    category: 'SSH服务安全',
                    passed: false,
                    risk_level: '高',
                    checks: [
                        { name: 'SSH服务运行状态', passed: true },
                        { name: 'SSH禁止Root登录', passed: false }
                    ],
                    fix_suggestion: '编辑 /etc/ssh/sshd_config，设置 PermitRootLogin no'
                },
                { 
                    name: '密码复杂度策略',
                    category: '账户与密码策略',
                    passed: true,
                    risk_level: '中',
                    checks: [
                        { name: '密码最小长度', passed: true },
                        { name: '密码复杂度要求', passed: true }
                    ],
                    fix_suggestion: '密码策略符合要求'
                },
                { 
                    name: '防火墙状态检查',
                    category: '服务与端口管理',
                    passed: true,
                    risk_level: '高',
                    checks: [
                        { name: '防火墙运行状态', passed: true },
                        { name: '防火墙开机自启', passed: true }
                    ],
                    fix_suggestion: '防火墙配置正常'
                }
            ]
        };
    }
    
    loadMockVulnerabilityData() {
        this.currentData.vulnerabilities = this.getMockVulnerabilities();
        this.displayVulnerabilityData(this.currentData.vulnerabilities);
    }
    
    getMockVulnerabilities() {
        return {
            vulnerabilities: [
                { 
                    cve_id: 'CVE-2021-4034', 
                    severity: 'high', 
                    title: 'Polkit权限提升漏洞',
                    description: 'Polkit权限提升漏洞，攻击者可获得root权限', 
                    remediation: '运行命令: yum update polkit -y',
                    affected_software: 'polkit包',
                    discovered: '2024-01-15'
                },
                { 
                    cve_id: 'CVE-2022-0001', 
                    severity: 'medium', 
                    title: 'SSH配置弱点',
                    description: 'SSH配置弱点，可能被暴力破解', 
                    remediation: '修改SSH配置，禁用密码认证',
                    affected_software: 'openssh-server',
                    discovered: '2024-01-15'
                }
            ],
            summary: {
                total: 2,
                level_count: {
                    critical: 0,
                    high: 1,
                    medium: 1,
                    low: 0
                }
            }
        };
    }
}

// 全局函数
function showTab(tabName) {
    window.secKeeperApp.showTab(tabName);
}

function startFullScan() {
    window.secKeeperApp.startFullScan();
}

function generatePDFReport() {
    window.secKeeperApp.generatePDFReport();
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        animation: spin 1s linear infinite;
    }
    
    .shortcut-hint {
        position: fixed;
        bottom: 10px;
        right: 10px;
        background: rgba(52, 73, 94, 0.9);
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 1000;
    }
`;
document.head.appendChild(style);

// 添加快捷键提示
const shortcutHint = document.createElement('div');
shortcutHint.className = 'shortcut-hint';
shortcutHint.innerHTML = '<i class="fas fa-keyboard"></i> 快捷键: Ctrl+1/2/3/4 切换标签, Ctrl+R 刷新, Ctrl+P 生成报告';
document.body.appendChild(shortcutHint);

// 启动应用
window.secKeeperApp = new SecKeeperApp();
