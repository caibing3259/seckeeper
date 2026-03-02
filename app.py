#!/usr/bin/env python3
"""
SecKeeper 网络安全扫描与报告生成系统
主应用程序文件 - 完整生产版本
"""

import os
import json
import uuid
import tempfile
import threading
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seckeeper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SecKeeper")

# 导入真实核心模块
try:
    from core.real_asset_scanner import RealAssetScanner
    from core.real_compliance_checker import RealComplianceChecker
    from core.real_vulnerability_scanner import RealVulnerabilityScanner
    print("✅ 真实核心模块导入成功")
    
    # 初始化扫描器
    asset_scanner = RealAssetScanner()
    compliance_checker = RealComplianceChecker()
    vulnerability_scanner = RealVulnerabilityScanner()
    
except ImportError as e:
    print(f"❌ 核心模块导入失败: {e}")
    raise e

# 导入PDF生成器
try:
    from core.report_generator_fixed_safe import ReportGeneratorFixedSafe as ReportGeneratorFixed
    print("✅ 使用安全版PDF生成器")
except ImportError as e:
    print(f"❌ PDF生成器导入失败: {e}")
    raise e

app = Flask(__name__)
CORS(app)

# 线程安全的扫描状态管理
class ThreadSafeScanManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.status = {
            "is_scanning": False,
            "progress": 0,
            "current_step": "",
            "last_scan_time": None,
            "current_scan_id": None
        }
    
    def start_scan(self, scan_id):
        """开始扫描 - 线程安全"""
        with self.lock:
            if self.status['is_scanning']:
                return False, "扫描正在进行中，请稍后重试", self.status['current_scan_id']
            
            self.status.update({
                "is_scanning": True,
                "progress": 0,
                "current_step": "初始化扫描",
                "current_scan_id": scan_id,
                "last_scan_time": datetime.now().isoformat()
            })
            return True, "扫描已开始", scan_id
    
    def update_progress(self, step, progress):
        """更新进度 - 线程安全"""
        with self.lock:
            self.status.update({
                "current_step": step,
                "progress": progress
            })
    
    def complete_scan(self):
        """完成扫描 - 线程安全"""
        with self.lock:
            self.status.update({
                "is_scanning": False,
                "progress": 100,
                "current_step": "扫描完成"
            })
    
    def get_status(self):
        """获取状态 - 线程安全"""
        with self.lock:
            return self.status.copy()
    
    def force_reset(self):
        """强制重置扫描状态 - 用于恢复"""
        with self.lock:
            self.status.update({
                "is_scanning": False,
                "progress": 0,
                "current_step": "",
                "current_scan_id": None
            })
            return True

# 初始化扫描管理器
scan_manager = ThreadSafeScanManager()
scan_results = {}

def background_scan(scan_id, callback):
    """后台扫描任务"""
    try:
        print(f"🚀 后台扫描开始: {scan_id}")
        
        # 扫描步骤定义
        steps = [
            ("资产清点", asset_scanner.scan_assets, 25),
            ("合规检查", compliance_checker.run_compliance_checks, 50), 
            ("漏洞扫描", vulnerability_scanner.run_souffle_scan, 75),
            ("生成报告", None, 100)
        ]
        
        results = {}
        for step_name, step_func, progress in steps:
            scan_manager.update_progress(step_name, progress)
            print(f"🔧 执行步骤: {step_name}")
            
            if step_func:
                try:
                    step_result = step_func()
                    results[step_name] = step_result
                    print(f"✅ 步骤完成: {step_name}")
                    
                    # 模拟处理时间
                    time.sleep(2)
                except Exception as e:
                    print(f"❌ 步骤失败: {step_name}, 错误: {e}")
                    results[step_name] = {"error": str(e)}
        
        # 准备最终结果
        scan_result = {
            "scan_id": scan_id,
            "timestamp": datetime.now().isoformat(),
            "assets": results.get("资产清点", {}),
            "compliance": results.get("合规检查", {}),
            "vulnerabilities": results.get("漏洞扫描", {}),
            "status": "completed"
        }
        
        # 完成扫描
        scan_manager.complete_scan()
        
        print(f"🎉 后台扫描完成: {scan_id}")
        callback(scan_result)
        
    except Exception as e:
        print(f"❌ 后台扫描异常: {e}")
        traceback.print_exc()
        scan_manager.complete_scan()
        callback({"error": str(e)})

# API路由
@app.route('/api/assets', methods=['GET'])
def get_assets():
    """获取资产清点数据"""
    try:
        assets_data = asset_scanner.scan_assets()
        return jsonify({
            "success": True,
            "data": assets_data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"资产清点错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/compliance', methods=['GET'])
def get_compliance():
    """获取合规检查结果"""
    try:
        compliance_data = compliance_checker.run_compliance_checks()
        return jsonify({
            "success": True,
            "data": compliance_data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"合规检查错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/vulnerabilities', methods=['GET'])
def get_vulnerabilities():
    """获取漏洞扫描结果"""
    try:
        vuln_data = vulnerability_scanner.run_souffle_scan()
        return jsonify({
            "success": True,
            "data": vuln_data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"漏洞扫描错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """获取仪表盘概览数据"""
    try:
        # 获取各模块数据
        assets_data = asset_scanner.scan_assets()
        compliance_data = compliance_checker.run_compliance_checks()
        vuln_data = vulnerability_scanner.run_souffle_scan()
        
        # 计算概览统计
        overview = {
            "assets": {
                "software_count": len(assets_data.get('software', [])),
                "service_count": len(assets_data.get('services', []))
            },
            "compliance": {
                "total_checks": compliance_data['summary']['total'],
                "passed_checks": compliance_data['summary']['passed'],
                "compliance_rate": compliance_data['summary']['compliance_rate']
            },
            "vulnerabilities": vuln_data.get('scan_summary', {
                "total_vulnerabilities": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }),
            "system_health": "healthy" if vuln_data.get('scan_summary', {}).get('critical', 0) == 0 else "warning"
        }
        
        return jsonify({
            "success": True,
            "data": {
                "overview": overview,
                "scan_status": scan_manager.get_status(),
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Dashboard错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/scan', methods=['POST'])
def perform_scan():
    """执行一键扫描"""
    scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 尝试开始扫描
    success, message, current_scan_id = scan_manager.start_scan(scan_id)
    
    if not success:
        return jsonify({
            "success": False,
            "error": message,
            "current_scan_id": current_scan_id
        }), 409
    
    def scan_complete_callback(result):
        """扫描完成回调"""
        scan_results[scan_id] = result
        print(f"📝 扫描结果已保存: {scan_id}")
    
    try:
        # 在后端线程中执行扫描
        scan_thread = threading.Thread(
            target=background_scan,
            args=(scan_id, scan_complete_callback),
            daemon=True
        )
        scan_thread.start()
        
        return jsonify({
            "success": True,
            "data": {
                "scan_id": scan_id,
                "message": "扫描已开始，请稍后查看结果",
                "status_url": f"/api/scan/{scan_id}/status"
            }
        })
        
    except Exception as e:
        scan_manager.force_reset()
        logger.error(f"启动扫描失败: {e}")
        return jsonify({
            "success": False,
            "error": f"启动扫描失败: {str(e)}"
        }), 500

@app.route('/api/scan/status', methods=['GET'])
def get_scan_status():
    """获取当前扫描状态"""
    return jsonify({
        "success": True,
        "data": scan_manager.get_status()
    })

@app.route('/api/scan/<scan_id>/status', methods=['GET'])
def get_specific_scan_status(scan_id):
    """获取特定扫描的状态和结果"""
    status = scan_manager.get_status()
    
    if status['current_scan_id'] == scan_id:
        if status['is_scanning']:
            return jsonify({
                "success": True,
                "data": {
                    "scan_id": scan_id,
                    "status": "running",
                    "progress": status['progress'],
                    "current_step": status['current_step']
                }
            })
        else:
            result = scan_results.get(scan_id)
            if result:
                return jsonify({
                    "success": True,
                    "data": {
                        "scan_id": scan_id,
                        "status": "completed",
                        "result": result
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "扫描结果未找到"
                }), 404
    else:
        return jsonify({
            "success": False,
            "error": "扫描ID不匹配或扫描已结束"
        }), 404

@app.route('/api/report', methods=['POST'])
def generate_report():
    """生成PDF报告"""
    report_path = None
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "未提供扫描数据"
            }), 400
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            report_path = tmp_file.name
        
        # 生成PDF
        success = ReportGeneratorFixed.generate_pdf_report(data, report_path)
        
        if success and os.path.exists(report_path):
            file_size = os.path.getsize(report_path)
            if file_size > 100:  # 确保文件不是空的
                return send_file(
                    report_path,
                    as_attachment=True,
                    download_name=f"seckeeper_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    "success": False,
                    "error": "生成的PDF文件为空"
                }), 500
        else:
            return jsonify({
                "success": False,
                "error": "PDF报告生成失败"
            }), 500
            
    except Exception as e:
        logger.error(f"生成报告错误: {e}")
        return jsonify({
            "success": False,
            "error": f"生成报告时出错: {str(e)}"
        }), 500
    finally:
        if report_path and os.path.exists(report_path):
            os.unlink(report_path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SecKeeper Backend",
        "version": "2.0.0",
        "scan_status": scan_manager.get_status()
    })

@app.route('/api/debug/scan-state', methods=['GET'])
def debug_scan_state():
    """调试扫描状态"""
    return jsonify({
        "success": True,
        "data": {
            "scan_manager_status": scan_manager.get_status(),
            "scan_results_keys": list(scan_results.keys()),
            "thread_count": threading.active_count()
        }
    })

@app.route('/')
def index():
    """根路径"""
    return jsonify({
        "message": "SecKeeper API Server",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "assets": "/api/assets",
            "compliance": "/api/compliance", 
            "vulnerabilities": "/api/vulnerabilities",
            "dashboard": "/api/dashboard",
            "scan": "/api/scan",
            "health": "/api/health"
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SecKeeper 真实环境后端服务启动")
    print("=" * 60)
    print("📍 接口地址: http://127.0.0.1:5000")
    print("\n📋 核心功能:")
    print("  ✅ 真实资产扫描 (软件、服务、系统信息)")
    print("  ✅ 真实合规检查 (密码策略、SSH配置、防火墙)")
    print("  ✅ 真实漏洞扫描 (NVD CVE数据库集成)") 
    print("  ✅ 密码熵强度检测")
    print("  ✅ 实时扫描状态监控")
    print("\n⏰ 启动时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # 启动应用
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )
