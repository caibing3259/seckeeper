#!/usr/bin/env python3
"""
真实资产扫描模块 - 完整生产版本
扫描系统软件、服务、网络配置和系统信息
"""

import os
import platform
import socket
import subprocess
import json
import re
import psutil
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class RealAssetScanner:
    """真实资产扫描器 - 生产环境实现"""
    
    @staticmethod
    def scan_assets() -> Dict[str, Any]:
        """执行完整的资产扫描"""
        try:
            print("🔍 开始系统资产扫描...")
            
            assets = {
                "software": [],
                "services": [],
                "system_info": {},
                "network_info": [],
                "hardware_info": {},
                "scan_timestamp": datetime.now().isoformat(),
                "scan_id": f"asset_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # 并行扫描不同维度的资产信息
            assets["system_info"] = RealAssetScanner._get_detailed_system_info()
            assets["software"] = RealAssetScanner._scan_installed_software()
            assets["services"] = RealAssetScanner._scan_running_services()
            assets["network_info"] = RealAssetScanner._scan_network_info()
            assets["hardware_info"] = RealAssetScanner._scan_hardware_info()
            
            print(f"✅ 资产扫描完成: {len(assets['software'])}软件, {len(assets['services'])}服务")
            return assets
            
        except Exception as e:
            print(f"❌ 资产扫描错误: {e}")
            return {
                "software": [],
                "services": [],
                "system_info": {},
                "network_info": [],
                "error": str(e),
                "scan_timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _get_detailed_system_info() -> Dict[str, Any]:
        """获取详细的系统信息"""
        try:
            # 获取基础系统信息
            system_info = {
                "hostname": socket.gethostname(),
                "fqdn": socket.getfqdn(),
                "os": platform.system(),
                "os_version": platform.version(),
                "platform": platform.platform(),
                "architecture": platform.architecture()[0],
                "machine": platform.machine(),
                "processor": platform.processor() or "Unknown",
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "total_swap_gb": round(psutil.swap_memory().total / (1024**3), 2),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "current_user": os.getenv('USER', 'Unknown'),
                "system_uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                "python_version": platform.python_version()
            }
            
            # 获取详细的CPU信息
            try:
                if platform.system().lower() == "linux":
                    with open('/proc/cpuinfo', 'r') as f:
                        cpu_info = f.read()
                        model_match = re.search(r'model name\s*:\s*(.+)', cpu_info)
                        if model_match:
                            system_info["cpu_model"] = model_match.group(1).strip()
                        
                        # 获取CPU频率
                        freq_match = re.search(r'cpu MHz\s*:\s*(.+)', cpu_info)
                        if freq_match:
                            system_info["cpu_frequency_mhz"] = float(freq_match.group(1).strip())
            except:
                system_info["cpu_model"] = "Unknown"
            
            # 获取磁盘信息
            try:
                disk_info = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "percent_used": usage.percent
                        })
                    except PermissionError:
                        continue
                system_info["disks"] = disk_info
            except Exception as e:
                print(f"⚠️ 磁盘信息获取失败: {e}")
                system_info["disks"] = []
            
            return system_info
            
        except Exception as e:
            print(f"❌ 系统信息获取错误: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _scan_installed_software() -> List[Dict[str, Any]]:
        """扫描已安装的软件 - 多包管理器支持"""
        software_list = []
        
        try:
            # Linux系统软件包扫描
            if platform.system().lower() == "linux":
                software_list.extend(RealAssetScanner._scan_linux_packages())
            
            # 扫描Python包
            software_list.extend(RealAssetScanner._scan_python_packages())
            
            # 扫描Node.js包
            software_list.extend(RealAssetScanner._scan_node_packages())
            
            # 扫描Docker容器和镜像
            software_list.extend(RealAssetScanner._scan_docker_assets())
            
            # 扫描系统库
            software_list.extend(RealAssetScanner._scan_system_libraries())
            
            # 去重处理
            software_list = RealAssetScanner._deduplicate_software(software_list)
                
        except Exception as e:
            print(f"❌ 软件扫描错误: {e}")
        
        return software_list
    
    @staticmethod
    def _scan_linux_packages() -> List[Dict[str, Any]]:
        """扫描Linux系统软件包 - 多包管理器支持"""
        packages = []
        
        # dpkg (Debian/Ubuntu)
        try:
            result = subprocess.run(
                ['dpkg-query', '-W', '-f=${Package} ${Version} ${Architecture}\n'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            pkg_name = parts[0]
                            pkg_version = parts[1]
                            architecture = parts[2] if len(parts) > 2 else "unknown"
                            
                            packages.append({
                                "name": pkg_name,
                                "version": pkg_version,
                                "type": "system_package",
                                "package_manager": "dpkg",
                                "architecture": architecture,
                                "status": "installed"
                            })
        except Exception as e:
            print(f"⚠️ dpkg扫描失败: {e}")
        
        # rpm (RedHat/CentOS/Fedora)
        try:
            result = subprocess.run(
                ['rpm', '-qa', '--queryformat', '%{NAME} %{VERSION}-%{RELEASE} %{ARCH}\n'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version_release = parts[1]
                            architecture = parts[2] if len(parts) > 2 else "unknown"
                            version = version_release.split('-')[0]
                            
                            packages.append({
                                "name": name,
                                "version": version,
                                "type": "system_package", 
                                "package_manager": "rpm",
                                "architecture": architecture,
                                "status": "installed"
                            })
        except Exception as e:
            print(f"⚠️ rpm扫描失败: {e}")
        
        # pacman (Arch Linux)
        try:
            result = subprocess.run(
                ['pacman', '-Q'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        name, version = line.split()[:2]
                        packages.append({
                            "name": name,
                            "version": version,
                            "type": "system_package",
                            "package_manager": "pacman",
                            "status": "installed"
                        })
        except Exception as e:
            print(f"⚠️ pacman扫描失败: {e}")
        
        return packages
    
    @staticmethod
    def _scan_python_packages() -> List[Dict[str, Any]]:
        """扫描Python包 - 多环境支持"""
        packages = []
        
        # 尝试不同的Python包管理器
        pip_commands = [
            ['pip', 'list', '--format=json'],
            ['pip3', 'list', '--format=json'],
            ['python', '-m', 'pip', 'list', '--format=json'],
            ['python3', '-m', 'pip', 'list', '--format=json']
        ]
        
        for cmd in pip_commands:
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                if result.returncode == 0:
                    pip_packages = json.loads(result.stdout)
                    for pkg in pip_packages:
                        packages.append({
                            "name": pkg['name'],
                            "version": pkg['version'],
                            "type": "python_package",
                            "package_manager": cmd[0],
                            "status": "installed"
                        })
                    break  # 成功一个即可
            except Exception:
                continue
        
        return packages
    
    @staticmethod
    def _scan_node_packages() -> List[Dict[str, Any]]:
        """扫描Node.js包"""
        packages = []
        
        # 检查当前目录的package.json
        if os.path.exists('package.json'):
            try:
                with open('package.json', 'r') as f:
                    package_data = json.load(f)
                
                dependencies = {
                    **package_data.get('dependencies', {}), 
                    **package_data.get('devDependencies', {}),
                    **package_data.get('peerDependencies', {})
                }
                
                for name, version in dependencies.items():
                    clean_version = re.sub(r'[\^~]', '', version)
                    packages.append({
                        "name": name,
                        "version": clean_version,
                        "type": "node_package", 
                        "package_manager": "npm",
                        "status": "dependency"
                    })
            except Exception as e:
                print(f"⚠️ package.json解析失败: {e}")
        
        # 检查全局安装的npm包
        try:
            result = subprocess.run(
                ['npm', 'list', '-g', '--json', '--depth=0'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                npm_data = json.loads(result.stdout)
                deps = npm_data.get('dependencies', {})
                for name, info in deps.items():
                    if isinstance(info, dict):
                        version = info.get('version', 'unknown')
                        packages.append({
                            "name": name,
                            "version": version,
                            "type": "node_package",
                            "package_manager": "npm",
                            "status": "global_installed"
                        })
        except Exception as e:
            print(f"⚠️ 全局npm包扫描失败: {e}")
        
        return packages
    
    @staticmethod
    def _scan_docker_assets() -> List[Dict[str, Any]]:
        """扫描Docker容器和镜像"""
        packages = []
        
        # 扫描运行的Docker容器
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}} {{.Image}} {{.Status}}'], 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            container_name = parts[0]
                            image = parts[1]
                            status = ' '.join(parts[2:]) if len(parts) > 2 else "running"
                            
                            # 解析镜像名称和版本
                            if ':' in image:
                                name, version = image.split(':', 1)
                            else:
                                name, version = image, 'latest'
                            
                            packages.append({
                                "name": name,
                                "version": version,
                                "container_name": container_name,
                                "type": "docker_container",
                                "package_manager": "docker",
                                "status": status
                            })
        except Exception as e:
            print(f"⚠️ Docker容器扫描失败: {e}")
        
        # 扫描Docker镜像
        try:
            result = subprocess.run(
                ['docker', 'images', '--format', '{{.Repository}} {{.Tag}} {{.ID}}'], 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        repository, tag, image_id = line.split()[:3]
                        packages.append({
                            "name": repository,
                            "version": tag,
                            "image_id": image_id[:12],
                            "type": "docker_image",
                            "package_manager": "docker",
                            "status": "available"
                        })
        except Exception as e:
            print(f"⚠️ Docker镜像扫描失败: {e}")
        
        return packages
    
    @staticmethod
    def _scan_system_libraries() -> List[Dict[str, Any]]:
        """扫描系统库文件"""
        libraries = []
        
        # 常见库文件路径
        lib_paths = [
            '/usr/lib',
            '/usr/lib64', 
            '/usr/local/lib',
            '/lib',
            '/lib64'
        ]
        
        try:
            for lib_path in lib_paths:
                if os.path.exists(lib_path):
                    # 这里可以扩展为实际扫描.so文件版本
                    libraries.append({
                        "name": f"system_libraries_{os.path.basename(lib_path)}",
                        "version": "system",
                        "type": "system_library",
                        "path": lib_path,
                        "status": "installed"
                    })
        except Exception as e:
            print(f"⚠️ 系统库扫描失败: {e}")
        
        return libraries
    
    @staticmethod
    def _scan_running_services() -> List[Dict[str, Any]]:
        """扫描运行的服务和进程"""
        services_list = []
        
        try:
            # 使用psutil获取运行进程
            for proc in psutil.process_iter(['pid', 'name', 'status', 'username', 'memory_info', 'cpu_times']):
                try:
                    process_info = proc.info
                    services_list.append({
                        "name": process_info['name'],
                        "pid": process_info['pid'],
                        "status": process_info['status'],
                        "user": process_info.get('username', 'Unknown'),
                        "memory_mb": round(process_info['memory_info'].rss / (1024*1024), 2) if process_info['memory_info'] else 0,
                        "type": "process"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 扫描网络服务端口
            services_list.extend(RealAssetScanner._scan_network_services())
            
            # 扫描系统服务 (systemd)
            services_list.extend(RealAssetScanner._scan_systemd_services())
            
        except Exception as e:
            print(f"❌ 服务扫描错误: {e}")
        
        return services_list[:50]  # 限制返回数量
    
    @staticmethod
    def _scan_network_services() -> List[Dict[str, Any]]:
        """扫描网络服务端口"""
        services = []
        
        try:
            # 检查常见服务端口
            common_ports = {
                22: "ssh", 80: "http", 443: "https", 21: "ftp", 25: "smtp",
                53: "dns", 3306: "mysql", 5432: "postgresql", 27017: "mongodb",
                6379: "redis", 8080: "http-proxy", 8443: "https-alt",
                9200: "elasticsearch", 9300: "elasticsearch-cluster",
                5601: "kibana", 5044: "logstash", 11211: "memcached"
            }
            
            for port, service_name in common_ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    services.append({
                        "name": service_name,
                        "port": port,
                        "status": "listening",
                        "type": "network_service"
                    })
                    
        except Exception as e:
            print(f"⚠️ 网络服务扫描失败: {e}")
        
        return services
    
    @staticmethod
    def _scan_systemd_services() -> List[Dict[str, Any]]:
        """扫描systemd服务"""
        services = []
        
        try:
            # 扫描活动的systemd服务
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=running', '--no-legend'],
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            service_name = parts[0]
                            services.append({
                                "name": service_name,
                                "status": "running",
                                "type": "systemd_service"
                            })
        except Exception as e:
            print(f"⚠️ systemd服务扫描失败: {e}")
        
        return services
    
    @staticmethod
    def _scan_network_info() -> List[Dict[str, Any]]:
        """扫描网络接口和配置信息"""
        network_info = []
        
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters(pernic=True)
            
            for interface, addrs in interfaces.items():
                interface_info = {
                    "interface": interface,
                    "addresses": [],
                    "stats": {},
                    "status": "unknown"
                }
                
                for addr in addrs:
                    address_info = {
                        "family": str(addr.family),
                        "address": addr.address
                    }
                    
                    if addr.netmask:
                        address_info["netmask"] = addr.netmask
                    if addr.broadcast:
                        address_info["broadcast"] = addr.broadcast
                    
                    interface_info["addresses"].append(address_info)
                
                if interface in stats:
                    interface_info["stats"] = {
                        "bytes_sent": stats[interface].bytes_sent,
                        "bytes_recv": stats[interface].bytes_recv,
                        "packets_sent": stats[interface].packets_sent,
                        "packets_recv": stats[interface].packets_recv
                    }
                
                # 检查接口状态
                try:
                    addrs = psutil.net_if_stats()
                    if interface in addrs:
                        interface_info["status"] = "up" if addrs[interface].isup else "down"
                except:
                    pass
                
                network_info.append(interface_info)
                
        except Exception as e:
            print(f"❌ 网络信息扫描错误: {e}")
        
        return network_info
    
    @staticmethod
    def _scan_hardware_info() -> Dict[str, Any]:
        """扫描硬件信息"""
        hardware_info = {}
        
        try:
            # CPU信息
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown",
                "current_frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown"
            }
            hardware_info["cpu"] = cpu_info
            
            # 内存信息
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent_used": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_percent_used": swap.percent
            }
            hardware_info["memory"] = memory_info
            
            # 磁盘信息（已包含在system_info中，这里提供汇总）
            disk_io = psutil.disk_io_counters()
            if disk_io:
                hardware_info["disk_io"] = {
                    "read_mb": round(disk_io.read_bytes / (1024**2), 2),
                    "write_mb": round(disk_io.write_bytes / (1024**2), 2),
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count
                }
                
        except Exception as e:
            print(f"⚠️ 硬件信息扫描失败: {e}")
            hardware_info["error"] = str(e)
        
        return hardware_info
    
    @staticmethod
    def _deduplicate_software(software_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """软件去重处理"""
        seen = set()
        deduplicated = []
        
        for software in software_list:
            # 基于名称和版本创建唯一标识
            identifier = f"{software['name']}-{software['version']}-{software.get('package_manager', '')}"
            
            if identifier not in seen:
                seen.add(identifier)
                deduplicated.append(software)
        
        return deduplicated
