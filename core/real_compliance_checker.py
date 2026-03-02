#!/usr/bin/env python3
"""
真实合规检查模块 - 完整生产版本
基于密码熵检查和系统安全配置分析
"""

import re
import subprocess
import math
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

class RealComplianceChecker:
    """真实合规检查器 - 生产环境实现"""
    
    @staticmethod
    def run_compliance_checks() -> Dict[str, Any]:
        """执行真实合规检查"""
        try:
            print("🛡️ 开始系统合规检查...")
            
            checks = {
                "summary": {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "compliance_rate": 0
                },
                "checks": [],
                "scan_timestamp": datetime.now().isoformat(),
                "scan_id": f"compliance_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # 执行各类安全检查
            password_checks = RealComplianceChecker._check_password_policy()
            checks["checks"].extend(password_checks)
            
            ssh_checks = RealComplianceChecker._check_ssh_config()
            checks["checks"].extend(ssh_checks)
            
            firewall_checks = RealComplianceChecker._check_firewall()
            checks["checks"].extend(firewall_checks)
            
            system_checks = RealComplianceChecker._check_system_security()
            checks["checks"].extend(system_checks)
            
            network_checks = RealComplianceChecker._check_network_security()
            checks["checks"].extend(network_checks)
            
            # 计算统计
            total_checks = len(checks["checks"])
            passed_checks = sum(1 for check in checks["checks"] if check.get("passed", False))
            compliance_rate = round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0
            
            checks["summary"] = {
                "total": total_checks,
                "passed": passed_checks,
                "failed": total_checks - passed_checks,
                "compliance_rate": compliance_rate
            }
            
            print(f"✅ 合规检查完成: 通过 {passed_checks}/{total_checks} 项检查")
            return checks
            
        except Exception as e:
            print(f"❌ 合规检查错误: {e}")
            return {
                "summary": {"total": 0, "passed": 0, "failed": 0, "compliance_rate": 0},
                "checks": [{
                    "name": "合规检查系统",
                    "category": "系统",
                    "passed": False,
                    "description": f"检查过程出错: {str(e)}",
                    "risk_level": "高"
                }],
                "scan_timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _check_password_policy() -> List[Dict[str, Any]]:
        """检查密码策略 - 基于熵检查"""
        checks = []
        
        try:
            # 1. 检查系统密码策略配置
            if RealComplianceChecker._is_linux():
                checks.extend(RealComplianceChecker._check_linux_password_policy())
            
            # 2. 执行密码强度熵检查
            checks.extend(RealComplianceChecker._perform_entropy_checks())
            
            # 3. 检查密码历史与重用策略
            checks.extend(RealComplianceChecker._check_password_history_policy())
            
            # 4. 检查账户锁定策略
            checks.extend(RealComplianceChecker._check_account_lockout_policy())
            
            return checks
            
        except Exception as e:
            print(f"❌ 密码策略检查错误: {e}")
            return [{
                "name": "密码策略检查",
                "category": "密码策略",
                "passed": False,
                "description": f"检查过程出错: {str(e)}",
                "risk_level": "中"
            }]
    
    @staticmethod
    def _is_linux() -> bool:
        """检查是否为Linux系统"""
        import platform
        return platform.system().lower() == "linux"
    
    @staticmethod
    def _check_linux_password_policy() -> List[Dict[str, Any]]:
        """检查Linux系统密码策略"""
        checks = []
        
        try:
            # 检查PAM密码策略配置
            pam_files = [
                "/etc/pam.d/common-password",
                "/etc/pam.d/system-auth",
                "/etc/security/pwquality.conf"
            ]
            
            for pam_file in pam_files:
                if Path(pam_file).exists():
                    with open(pam_file, 'r') as f:
                        content = f.read()
                    
                    # 检查密码复杂度模块
                    if any(keyword in content for keyword in ['pam_pwquality.so', 'pam_cracklib.so']):
                        config_details = RealComplianceChecker._parse_pam_config(content)
                        checks.append({
                            "name": f"密码复杂度配置 - {Path(pam_file).name}",
                            "category": "密码策略",
                            "passed": True,
                            "description": f"系统配置了密码复杂度要求",
                            "risk_level": "低",
                            "details": config_details
                        })
                    else:
                        checks.append({
                            "name": f"密码复杂度配置 - {Path(pam_file).name}",
                            "category": "密码策略",
                            "passed": False,
                            "description": f"未配置密码复杂度要求",
                            "risk_level": "高",
                            "remediation": "安装并配置libpam-pwquality或libpam-cracklib"
                        })
            
            # 检查/etc/login.defs中的密码策略
            if Path("/etc/login.defs").exists():
                with open("/etc/login.defs", 'r') as f:
                    login_defs = f.read()
                
                # 检查最小密码长度
                min_len = RealComplianceChecker._extract_config_value(login_defs, "PASS_MIN_LEN")
                if min_len and int(min_len) >= 8:
                    checks.append({
                        "name": "最小密码长度",
                        "category": "密码策略",
                        "passed": True,
                        "description": f"密码最小长度要求: {min_len}位",
                        "risk_level": "低"
                    })
                else:
                    checks.append({
                        "name": "最小密码长度",
                        "category": "密码策略",
                        "passed": False,
                        "description": f"密码最小长度不足8位 (当前: {min_len or '未设置'})",
                        "risk_level": "高",
                        "remediation": "在/etc/login.defs中设置PASS_MIN_LEN 8"
                    })
                
                # 检查密码最大有效期
                max_days = RealComplianceChecker._extract_config_value(login_defs, "PASS_MAX_DAYS")
                if max_days and int(max_days) <= 90:
                    checks.append({
                        "name": "密码最大有效期",
                        "category": "密码策略", 
                        "passed": True,
                        "description": f"密码最大有效期: {max_days}天",
                        "risk_level": "低"
                    })
                else:
                    checks.append({
                        "name": "密码最大有效期",
                        "category": "密码策略",
                        "passed": False,
                        "description": f"密码有效期过长 (当前: {max_days or '未设置'}天)",
                        "risk_level": "中",
                        "remediation": "在/etc/login.defs中设置PASS_MAX_DAYS 90"
                    })
                        
        except Exception as e:
            print(f"❌ Linux密码策略检查错误: {e}")
            
        return checks
    
    @staticmethod
    def _parse_pam_config(content: str) -> Dict[str, Any]:
        """解析PAM配置详情"""
        details = {}
        
        # 提取常见PAM参数
        parameters = {
            'minlen': '最小长度',
            'minclass': '最小字符类别',
            'dcredit': '数字要求', 
            'ucredit': '大写字母要求',
            'lcredit': '小写字母要求',
            'ocredit': '特殊字符要求',
            'difok': '最少不同字符数',
            'maxrepeat': '最大重复字符数',
            'maxsequence': '最大序列长度'
        }
        
        for param, desc in parameters.items():
            match = re.search(rf'{param}\s*=\s*([^\s]+)', content)
            if match:
                details[desc] = match.group(1)
        
        return details
    
    @staticmethod
    def _extract_config_value(content: str, key: str) -> Optional[str]:
        """从配置文件中提取键值"""
        match = re.search(rf'^\s*{key}\s+(\d+)', content, re.MULTILINE)
        return match.group(1) if match else None
    
    @staticmethod
    def _perform_entropy_checks() -> List[Dict[str, Any]]:
        """执行密码熵检查"""
        checks = []
        
        # 测试密码样本
        test_passwords = [
            "Password123!",           # 中等强度
            "weakpassword",           # 弱密码
            "StrongPass2024!@#",      # 强密码  
            "12345678",               # 极弱密码
            "Admin@2024",             # 中等密码
            "Mu-icac-of-jaz-doad",    # 密码短语
            "P@ssw0rd!Secure2024",    # 强密码
            "qwerty123",              # 弱密码
            "CorrectHorseBatteryStaple", # 密码短语
        ]
        
        entropy_results = []
        for password in test_passwords:
            entropy_score = RealComplianceChecker._calculate_entropy(password)
            strength_analysis = RealComplianceChecker._analyze_password_strength(password)
            
            entropy_results.append({
                "password_sample": password[:2] + "*****" + password[-2:] if len(password) > 4 else "***",
                "entropy_score": round(entropy_score, 2),
                "strength_level": strength_analysis['level'],
                "crack_time_estimate": strength_analysis['crack_time'],
                "issues": strength_analysis['issues']
            })
        
        # 分析结果
        strong_count = sum(1 for r in entropy_results if r['strength_level'] in ['strong', 'very_strong'])
        avg_entropy = sum(r['entropy_score'] for r in entropy_results) / len(entropy_results)
        
        checks.append({
            "name": "密码熵强度测试",
            "category": "密码策略",
            "passed": avg_entropy >= 60,  # 平均熵值阈值
            "description": f"测试了 {len(test_passwords)} 个密码样本，平均熵值: {avg_entropy:.2f} bits",
            "risk_level": "低" if avg_entropy >= 60 else "高",
            "details": {
                "strong_passwords": strong_count,
                "total_tested": len(test_passwords),
                "entropy_threshold": 60,
                "results": entropy_results
            }
        })
        
        return checks
    
    @staticmethod
    def _calculate_entropy(password: str) -> float:
        """计算密码熵值"""
        if not password:
            return 0.0
        
        # 字符集分析
        char_sets = 0
        if re.search(r'[a-z]', password):
            char_sets += 26  # 小写字母
        if re.search(r'[A-Z]', password):
            char_sets += 26  # 大写字母  
        if re.search(r'[0-9]', password):
            char_sets += 10  # 数字
        if re.search(r'[^a-zA-Z0-9]', password):
            char_sets += 32  # 特殊字符
        
        if char_sets == 0:
            return 0.0
        
        # 熵计算: log2(字符集大小 ^ 密码长度)
        entropy = len(password) * math.log2(char_sets)
        
        # 常见模式惩罚
        penalties = 0
        
        # 重复字符惩罚
        repeats = len(password) - len(set(password))
        penalties += repeats * 0.5
        
        # 序列惩罚 (如123, abc)
        sequences = RealComplianceChecker._count_sequences(password)
        penalties += sequences * 1.0
        
        # 常见模式惩罚
        common_patterns = RealComplianceChecker._check_common_patterns(password)
        penalties += common_patterns * 2.0
        
        return max(0, entropy - penalties)
    
    @staticmethod
    def _count_sequences(password: str) -> int:
        """计算序列数量"""
        sequences = 0
        for i in range(len(password) - 2):
            # 数字序列
            if (password[i:i+3].isdigit() and 
                abs(ord(password[i]) - ord(password[i+1])) == 1 and
                abs(ord(password[i+1]) - ord(password[i+2])) == 1):
                sequences += 1
            # 字母序列  
            elif (password[i:i+3].isalpha() and
                  abs(ord(password[i].lower()) - ord(password[i+1].lower())) == 1 and
                  abs(ord(password[i+1].lower()) - ord(password[i+2].lower())) == 1):
                sequences += 1
        return sequences
    
    @staticmethod
    def _check_common_patterns(password: str) -> int:
        """检查常见弱密码模式"""
        common_patterns = [
            r'123456',
            r'password', 
            r'qwerty',
            r'admin',
            r'welcome',
            r'[0-9]{6,}',  # 长数字序列
            r'([a-zA-Z])\1{2,}',  # 重复字符
            r'(.)\1{2,}',  # 任何字符重复3次以上
        ]
        
        patterns_found = 0
        lower_password = password.lower()
        
        for pattern in common_patterns:
            if re.search(pattern, lower_password):
                patterns_found += 1
        
        return patterns_found
    
    @staticmethod
    def _analyze_password_strength(password: str) -> Dict[str, Any]:
        """分析密码强度"""
        entropy = RealComplianceChecker._calculate_entropy(password)
        
        # 基于熵值的强度分级
        if entropy >= 80:
            level = "very_strong"
            crack_time = "数百年"
        elif entropy >= 60:
            level = "strong" 
            crack_time = "数年"
        elif entropy >= 40:
            level = "medium"
            crack_time = "数天到数周"
        elif entropy >= 20:
            level = "weak"
            crack_time = "数分钟到数小时"
        else:
            level = "very_weak"
            crack_time = "瞬间"
        
        # 识别具体问题
        issues = []
        if len(password) < 8:
            issues.append("密码过短")
        if not re.search(r'[A-Z]', password):
            issues.append("缺少大写字母")
        if not re.search(r'[a-z]', password):
            issues.append("缺少小写字母") 
        if not re.search(r'[0-9]', password):
            issues.append("缺少数字")
        if not re.search(r'[^a-zA-Z0-9]', password):
            issues.append("缺少特殊字符")
        if RealComplianceChecker._check_common_patterns(password) > 0:
            issues.append("包含常见模式")
        
        return {
            "level": level,
            "crack_time": crack_time,
            "issues": issues
        }
    
    @staticmethod
    def _check_password_history_policy() -> List[Dict[str, Any]]:
        """检查密码历史与重用策略"""
        checks = []
        
        try:
            if RealComplianceChecker._is_linux():
                # 检查PAM的密码历史配置
                for pam_file in ["/etc/pam.d/common-password", "/etc/pam.d/system-auth"]:
                    if Path(pam_file).exists():
                        with open(pam_file, 'r') as f:
                            content = f.read()
                        
                        remember_match = re.search(r'remember=(\d+)', content)
                        if remember_match:
                            remember_count = remember_match.group(1)
                            checks.append({
                                "name": "密码历史策略",
                                "category": "密码策略",
                                "passed": int(remember_count) >= 5,
                                "description": f"系统配置了记住 {remember_count} 个历史密码",
                                "risk_level": "低" if int(remember_count) >= 5 else "中",
                                "remediation": "建议设置remember=12或更高"
                            })
                            break
                else:
                    checks.append({
                        "name": "密码历史策略", 
                        "category": "密码策略",
                        "passed": False,
                        "description": "未配置密码历史策略",
                        "risk_level": "高",
                        "remediation": "在PAM配置中添加password required pam_unix.so remember=12"
                    })
                        
        except Exception as e:
            print(f"❌ 密码历史检查错误: {e}")
            
        return checks
    
    @staticmethod
    def _check_account_lockout_policy() -> List[Dict[str, Any]]:
        """检查账户锁定策略"""
        checks = []
        
        try:
            if RealComplianceChecker._is_linux():
                # 检查PAM的账户锁定配置
                for pam_file in ["/etc/pam.d/common-auth", "/etc/pam.d/system-auth"]:
                    if Path(pam_file).exists():
                        with open(pam_file, 'r') as f:
                            content = f.read()
                        
                        if 'pam_tally2.so' in content or 'pam_faillock.so' in content:
                            checks.append({
                                "name": "账户锁定策略",
                                "category": "密码策略",
                                "passed": True,
                                "description": f"系统配置了账户锁定策略",
                                "risk_level": "低"
                            })
                            break
                else:
                    checks.append({
                        "name": "账户锁定策略",
                        "category": "密码策略",
                        "passed": False,
                        "description": "未配置账户锁定策略",
                        "risk_level": "中",
                        "remediation": "在PAM配置中添加账户锁定模块(pam_tally2或pam_faillock)"
                    })
                        
        except Exception as e:
            print(f"❌ 账户锁定策略检查错误: {e}")
            
        return checks
    
    @staticmethod
    def _check_ssh_config() -> List[Dict[str, Any]]:
        """检查SSH安全配置"""
        checks = []
        
        try:
            ssh_config_file = "/etc/ssh/sshd_config"
            
            if Path(ssh_config_file).exists():
                with open(ssh_config_file, 'r') as f:
                    content = f.read()
                
                # 检查关键安全配置
                security_checks = [
                    {
                        "name": "SSH Root登录禁用",
                        "config": "PermitRootLogin",
                        "expected": ["no", "prohibit-password"],
                        "risk": "高"
                    },
                    {
                        "name": "SSH密码认证",
                        "config": "PasswordAuthentication", 
                        "expected": ["no"],
                        "risk": "中"
                    },
                    {
                        "name": "空密码禁止",
                        "config": "PermitEmptyPasswords",
                        "expected": ["no"],
                        "risk": "高"
                    },
                    {
                        "name": "最大认证尝试次数",
                        "config": "MaxAuthTries",
                        "expected": lambda x: int(x) <= 3,
                        "risk": "中"
                    },
                    {
                        "name": "SSH协议版本",
                        "config": "Protocol",
                        "expected": lambda x: int(x) >= 2,
                        "risk": "高"
                    }
                ]
                
                for check in security_checks:
                    config_match = re.search(rf'^\s*{check["config"]}\s+(\S+)', content, re.MULTILINE | re.IGNORECASE)
                    if config_match:
                        value = config_match.group(1).lower()
                        
                        if callable(check["expected"]):
                            passed = check["expected"](value)
                        else:
                            passed = value in check["expected"]
                        
                        checks.append({
                            "name": check["name"],
                            "category": "SSH配置",
                            "passed": passed,
                            "description": f"{check['config']} = {value}",
                            "risk_level": check["risk"],
                            "remediation": f"建议设置 {check['config']} {check['expected']}" if not passed else None
                        })
                    else:
                        checks.append({
                            "name": check["name"],
                            "category": "SSH配置",
                            "passed": False,
                            "description": f"未配置 {check['config']}",
                            "risk_level": check["risk"],
                            "remediation": f"在sshd_config中明确设置 {check['config']}"
                        })
                
                return checks
                
        except Exception as e:
            print(f"❌ SSH配置检查错误: {e}")
        
        return [{
            "name": "SSH配置检查",
            "category": "SSH配置", 
            "passed": False,
            "description": f"检查失败: {str(e)}",
            "risk_level": "中"
        }]
    
    @staticmethod
    def _check_firewall() -> List[Dict[str, Any]]:
        """检查防火墙状态"""
        checks = []
        
        try:
            if RealComplianceChecker._is_linux():
                # 检查UFW状态
                try:
                    result = subprocess.run(['ufw', 'status'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        if "Status: active" in result.stdout:
                            checks.append({
                                "name": "UFW防火墙状态",
                                "category": "防火墙",
                                "passed": True,
                                "description": "UFW防火墙正在运行",
                                "risk_level": "低"
                            })
                        else:
                            checks.append({
                                "name": "UFW防火墙状态",
                                "category": "防火墙", 
                                "passed": False,
                                "description": "UFW防火墙未运行",
                                "risk_level": "高",
                                "remediation": "运行 'ufw enable' 启用防火墙"
                            })
                except Exception:
                    pass
                
                # 检查iptables
                try:
                    result = subprocess.run(['iptables', '-L', '-n'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        if "Chain INPUT" in result.stdout and "Chain FORWARD" in result.stdout:
                            # 检查是否有实际规则
                            lines = result.stdout.split('\n')
                            rule_count = sum(1 for line in lines if line and not line.startswith('Chain') 
                                           and not line.startswith('target') and not line.startswith('num'))
                            if rule_count > 0:
                                checks.append({
                                    "name": "iptables配置",
                                    "category": "防火墙",
                                    "passed": True, 
                                    "description": f"iptables规则已配置 ({rule_count} 条规则)",
                                    "risk_level": "低"
                                })
                            else:
                                checks.append({
                                    "name": "iptables配置",
                                    "category": "防火墙",
                                    "passed": False,
                                    "description": "iptables未配置有效规则",
                                    "risk_level": "高"
                                })
                except Exception:
                    pass
                
                # 检查firewalld (CentOS/RHEL)
                try:
                    result = subprocess.run(['firewall-cmd', '--state'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and "running" in result.stdout:
                        checks.append({
                            "name": "firewalld状态",
                            "category": "防火墙",
                            "passed": True,
                            "description": "firewalld正在运行",
                            "risk_level": "低"
                        })
                except Exception:
                    pass
                
                # 如果没有发现防火墙
                if not any(check['name'] in ['UFW防火墙状态', 'iptables配置', 'firewalld状态'] for check in checks):
                    checks.append({
                        "name": "防火墙状态",
                        "category": "防火墙",
                        "passed": False,
                        "description": "未检测到运行的防火墙",
                        "risk_level": "高",
                        "remediation": "安装并配置UFW、iptables或firewalld防火墙"
                    })
                
                return checks
                
        except Exception as e:
            print(f"❌ 防火墙检查错误: {e}")
        
        return [{
            "name": "防火墙检查",
            "category": "防火墙",
            "passed": False,
            "description": f"检查失败: {str(e)}",
            "risk_level": "高"
        }]
    
    @staticmethod
    def _check_system_security() -> List[Dict[str, Any]]:
        """检查系统安全配置"""
        checks = []
        
        try:
            # 检查SELinux/AppArmor
            if RealComplianceChecker._is_linux():
                # SELinux检查
                try:
                    result = subprocess.run(['getenforce'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        selinux_status = result.stdout.strip()
                        checks.append({
                            "name": "SELinux状态",
                            "category": "系统安全",
                            "passed": selinux_status == "Enforcing",
                            "description": f"SELinux状态: {selinux_status}",
                            "risk_level": "低" if selinux_status == "Enforcing" else "高"
                        })
                except Exception:
                    pass
                
                # 检查AppArmor
                try:
                    result = subprocess.run(['aa-status', '--enforced'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        checks.append({
                            "name": "AppArmor状态",
                            "category": "系统安全",
                            "passed": True,
                            "description": "AppArmor已启用并执行策略",
                            "risk_level": "低"
                        })
                    else:
                        # 检查aa-status是否存在
                        result = subprocess.run(['which', 'aa-status'], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            checks.append({
                                "name": "AppArmor状态",
                                "category": "系统安全",
                                "passed": False,
                                "description": "AppArmor未完全启用",
                                "risk_level": "中"
                            })
                except Exception:
                    pass
                
                # 检查自动安全更新
                try:
                    if Path("/etc/apt/apt.conf.d/20auto-upgrades").exists():
                        with open("/etc/apt/apt.conf.d/20auto-upgrades", 'r') as f:
                            content = f.read()
                            if 'APT::Periodic::Update-Package-Lists "1";' in content and 'APT::Periodic::Unattended-Upgrade "1";' in content:
                                checks.append({
                                    "name": "自动安全更新",
                                    "category": "系统安全",
                                    "passed": True,
                                    "description": "已配置自动安全更新",
                                    "risk_level": "低"
                                })
                            else:
                                checks.append({
                                    "name": "自动安全更新",
                                    "category": "系统安全",
                                    "passed": False,
                                    "description": "自动安全更新配置不完整",
                                    "risk_level": "中"
                                })
                    else:
                        checks.append({
                            "name": "自动安全更新",
                            "category": "系统安全",
                            "passed": False,
                            "description": "未配置自动安全更新",
                            "risk_level": "中",
                            "remediation": "配置unattended-upgrades包"
                        })
                except Exception:
                    pass
                
                # 检查核心转储设置
                try:
                    result = subprocess.run(['sysctl', 'kernel.core_pattern'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        core_pattern = result.stdout.strip()
                        if 'core' in core_pattern:
                            checks.append({
                                "name": "核心转储配置",
                                "category": "系统安全",
                                "passed": False,
                                "description": f"核心转储已启用: {core_pattern}",
                                "risk_level": "中",
                                "remediation": "考虑禁用核心转储以防止敏感信息泄露"
                            })
                except Exception:
                    pass
            
            return checks
            
        except Exception as e:
            print(f"❌ 系统安全检查错误: {e}")
            return []
    
    @staticmethod
    def _check_network_security() -> List[Dict[str, Any]]:
        """检查网络安全配置"""
        checks = []
        
        try:
            if RealComplianceChecker._is_linux():
                # 检查ICMP重定向
                try:
                    result = subprocess.run(['sysctl', 'net.ipv4.conf.all.accept_redirects'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        value = result.stdout.split('=')[1].strip()
                        if value == '0':
                            checks.append({
                                "name": "ICMP重定向保护",
                                "category": "网络安全",
                                "passed": True,
                                "description": "已禁用ICMP重定向",
                                "risk_level": "低"
                            })
                        else:
                            checks.append({
                                "name": "ICMP重定向保护",
                                "category": "网络安全",
                                "passed": False,
                                "description": "ICMP重定向未禁用",
                                "risk_level": "中"
                            })
                except Exception:
                    pass
                
                # 检查源路由
                try:
                    result = subprocess.run(['sysctl', 'net.ipv4.conf.all.accept_source_route'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        value = result.stdout.split('=')[1].strip()
                        if value == '0':
                            checks.append({
                                "name": "源路由保护",
                                "category": "网络安全",
                                "passed": True,
                                "description": "已禁用源路由",
                                "risk_level": "低"
                            })
                        else:
                            checks.append({
                                "name": "源路由保护",
                                "category": "网络安全",
                                "passed": False,
                                "description": "源路由未禁用",
                                "risk_level": "中"
                            })
                except Exception:
                    pass
                
                # 检查SYN Cookie保护
                try:
                    result = subprocess.run(['sysctl', 'net.ipv4.tcp_syncookies'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        value = result.stdout.split('=')[1].strip()
                        if value == '1':
                            checks.append({
                                "name": "SYN Flood保护",
                                "category": "网络安全",
                                "passed": True,
                                "description": "已启用SYN Cookie保护",
                                "risk_level": "低"
                            })
                        else:
                            checks.append({
                                "name": "SYN Flood保护",
                                "category": "网络安全",
                                "passed": False,
                                "description": "SYN Cookie保护未启用",
                                "risk_level": "中"
                            })
                except Exception:
                    pass
            
            return checks
            
        except Exception as e:
            print(f"❌ 网络安全检查错误: {e}")
            return []
