# core/report_generator_fixed_safe.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import traceback

class ReportGeneratorFixedSafe:
    
    # 类变量存储字体配置
    CHINESE_FONT = 'Helvetica'
    ENGLISH_FONT = 'Helvetica'
    FONTS_CONFIGURED = False
    
    @staticmethod
    def _setup_fonts():
        """设置中英文字体 - 增强版本，确保字体完全覆盖"""
        if ReportGeneratorFixedSafe.FONTS_CONFIGURED:
            return
            
        try:
            print("🔠 初始化字体配置...")
            
            # 清空已注册的字体（避免重复）
            try:
                # 获取当前已注册的字体并清除（除了系统默认字体）
                registered_fonts = pdfmetrics.getRegisteredFontNames()
                for font in registered_fonts:
                    if font not in ['Helvetica', 'Times-Roman', 'Courier', 'Symbol', 'ZapfDingbats']:
                        try:
                            # 无法直接取消注册，但我们可以覆盖注册
                            pass
                        except:
                            pass
            except:
                pass
            
            # 注册英文字体 - 优先使用DejaVuSans（支持更全的字符集）
            english_font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            ]
            
            english_font_registered = False
            for font_path in english_font_paths:
                if os.path.exists(font_path):
                    try:
                        font_name = os.path.basename(font_path).split('.')[0]
                        # 使用唯一名称避免冲突
                        unique_name = f"English_{font_name}"
                        pdfmetrics.registerFont(TTFont(unique_name, font_path))
                        ReportGeneratorFixedSafe.ENGLISH_FONT = unique_name
                        print(f"✅ 英文字体注册成功: {unique_name} -> {font_path}")
                        english_font_registered = True
                        break
                    except Exception as e:
                        print(f"❌ 英文字体注册失败 {font_path}: {e}")
                        continue
            
            # 注册中文字体 - 优先使用支持字符集更全的字体
            chinese_font_paths = [
                # 优先尝试 Noto 字体（Google的开源字体，覆盖范围广）
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf",
                # 文泉驿字体
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                # 文鼎字体
                "/usr/share/fonts/truetype/arphic/uming.ttc",
                "/usr/share/fonts/truetype/arphic/ukai.ttc",
                # Droid 字体
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            ]
            
            chinese_font_registered = False
            for font_path in chinese_font_paths:
                if os.path.exists(font_path):
                    try:
                        font_name = os.path.basename(font_path).split('.')[0]
                        # 使用唯一名称避免冲突
                        unique_name = f"Chinese_{font_name}"
                        pdfmetrics.registerFont(TTFont(unique_name, font_path))
                        ReportGeneratorFixedSafe.CHINESE_FONT = unique_name
                        print(f"✅ 中文字体注册成功: {unique_name} -> {font_path}")
                        chinese_font_registered = True
                        break
                    except Exception as e:
                        print(f"❌ 中文字体注册失败 {font_path}: {e}")
                        continue
            
            # 如果中文字体注册失败，尝试使用英文字体作为备用
            if not chinese_font_registered and english_font_registered:
                ReportGeneratorFixedSafe.CHINESE_FONT = ReportGeneratorFixedSafe.ENGLISH_FONT
                print("⚠️ 使用英文字体作为中文字体备用")
            
            # 如果英文字体注册失败，使用系统默认
            if not english_font_registered:
                ReportGeneratorFixedSafe.ENGLISH_FONT = 'Helvetica'
                print("⚠️ 使用默认英文字体 Helvetica")
            
            ReportGeneratorFixedSafe.FONTS_CONFIGURED = True
            
            # 打印最终字体配置
            available_fonts = pdfmetrics.getRegisteredFontNames()
            print(f"🎯 最终字体配置:")
            print(f"  - 中文: {ReportGeneratorFixedSafe.CHINESE_FONT}")
            print(f"  - 英文: {ReportGeneratorFixedSafe.ENGLISH_FONT}")
            print(f"  - 可用字体: {available_fonts}")
            
        except Exception as e:
            print(f"❌ 字体配置失败: {e}")
            ReportGeneratorFixedSafe.CHINESE_FONT = 'Helvetica'
            ReportGeneratorFixedSafe.ENGLISH_FONT = 'Helvetica'
            ReportGeneratorFixedSafe.FONTS_CONFIGURED = True

    @staticmethod
    def _create_styles():
        """创建中英文分开的样式 - 增强版本"""
        styles = getSampleStyleSheet()
        
        # 确保字体已配置
        ReportGeneratorFixedSafe._setup_fonts()
        
        # 混合字体标题样式 - 使用中文字体但确保英文也能显示
        title_style = ParagraphStyle(
            'MixedTitle',
            parent=styles['Heading1'],
            fontName=ReportGeneratorFixedSafe.CHINESE_FONT,  # 使用支持中英文字体
            fontSize=16,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1,  # 居中
            leading=20
        )
        
        # 混合字体副标题样式
        heading2_style = ParagraphStyle(
            'MixedHeading2',
            parent=styles['Heading2'],
            fontName=ReportGeneratorFixedSafe.CHINESE_FONT,  # 使用支持中英文字体
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50'),
            leading=18
        )
        
        # 英文字体样式 - 专门用于纯英文内容
        english_style = ParagraphStyle(
            'EnglishStyle',
            parent=styles['Normal'],
            fontName=ReportGeneratorFixedSafe.ENGLISH_FONT,
            fontSize=10,
            spaceAfter=12,
            leading=14
        )
        
        # 混合字体样式 - 用于中英文混合内容
        mixed_style = ParagraphStyle(
            'MixedStyle',
            parent=styles['Normal'],
            fontName=ReportGeneratorFixedSafe.CHINESE_FONT,  # 使用支持中英文字体
            fontSize=10,
            spaceAfter=12,
            leading=14
        )
        
        return {
            'title': title_style,
            'heading2': heading2_style,
            'english': english_style,
            'mixed': mixed_style
        }

    @staticmethod
    def _safe_get_data(data, keys, default="未知"):
        """安全地获取嵌套字典数据"""
        try:
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current if current is not None else default
        except:
            return default

    @staticmethod
    def _debug_font_usage(text, font_name):
        """调试字体使用情况"""
        # 这个函数可以帮助诊断哪些字符可能无法在指定字体中显示
        try:
            # 检查文本中是否包含中文字符
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            # 检查文本中是否包含英文字符
            has_english = any('A' <= char <= 'z' for char in text)
            
            if has_chinese and has_english:
                print(f"🔤 混合文本: '{text[:50]}...' 使用字体: {font_name}")
            elif has_chinese:
                print(f"🀂 中文文本: '{text[:50]}...' 使用字体: {font_name}")
            elif has_english:
                print(f"🔠 英文文本: '{text[:50]}...' 使用字体: {font_name}")
                
        except Exception as e:
            # 忽略调试错误
            pass

    @staticmethod
    def _create_overview_table(scan_data):
        """创建概览表格"""
        try:
            # 安全地访问数据
            scan_time = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['timestamp'])
            scan_id = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['scan_id'])
            
            # 获取资产信息
            assets = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['assets'], {})
            software_list = ReportGeneratorFixedSafe._safe_get_data(assets, ['software'], [])
            services_list = ReportGeneratorFixedSafe._safe_get_data(assets, ['services'], [])
            
            software_count = len(software_list) if isinstance(software_list, list) else 0
            services_count = len(services_list) if isinstance(services_list, list) else 0
            
            # 获取合规信息
            compliance = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['compliance'], {})
            compliance_summary = ReportGeneratorFixedSafe._safe_get_data(compliance, ['summary'], {})
            compliance_total = ReportGeneratorFixedSafe._safe_get_data(compliance_summary, ['total'], 0)
            compliance_passed = ReportGeneratorFixedSafe._safe_get_data(compliance_summary, ['passed'], 0)
            compliance_rate = ReportGeneratorFixedSafe._safe_get_data(compliance_summary, ['compliance_rate'], 0)
            
            # 获取漏洞信息
            vulnerabilities = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['vulnerabilities'], {})
            vuln_list = ReportGeneratorFixedSafe._safe_get_data(vulnerabilities, ['vulnerabilities'], [])
            vuln_count = len(vuln_list) if isinstance(vuln_list, list) else 0
            
            # 如果有漏洞摘要信息，使用摘要
            vuln_summary = ReportGeneratorFixedSafe._safe_get_data(vulnerabilities, ['summary'], {})
            if vuln_summary and isinstance(vuln_summary, dict):
                total_from_summary = ReportGeneratorFixedSafe._safe_get_data(vuln_summary, ['total'])
                if total_from_summary != "未知":
                    vuln_count = total_from_summary
            
            print(f"📊 数据统计 - 软件: {software_count}, 服务: {services_count}, 合规率: {compliance_rate}%, 漏洞: {vuln_count}")
            
            # 创建概览数据 - 使用混合字体确保所有字符都能显示
            overview_data = [
                ['扫描时间:', scan_time],
                ['扫描ID:', scan_id],
                ['报告生成时间:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['', ''],  # 空行分隔
                ['软件资产数量:', str(software_count)],
                ['服务资产数量:', str(services_count)],
                ['合规检查总数:', str(compliance_total)],
                ['通过检查数:', str(compliance_passed)],
                ['合规率:', f"{compliance_rate}%"],
                ['发现漏洞数:', str(vuln_count)]
            ]
            
            # 创建概览表格 - 使用混合字体
            overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
            overview_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), ReportGeneratorFixedSafe.CHINESE_FONT),  # 全部使用混合字体
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('SPAN', (0, 3), (1, 3)),
                ('BACKGROUND', (0, 4), (0, -1), colors.HexColor('#e8f4fd')),
            ]))
            
            return overview_table
            
        except Exception as e:
            print(f"❌ 创建概览表格失败: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def _create_software_table(software_list):
        """创建软件资产表格 - 使用混合字体"""
        try:
            print(f"🔧 创建软件表格，输入数据长度: {len(software_list) if software_list else 0}")
            
            if not software_list or not isinstance(software_list, list):
                print("⚠️ 软件列表为空或不是列表")
                return None
            
            # 表格标题行
            software_data = [['软件名称', '版本', '类型']]
            
            # 安全地处理每个软件项
            valid_count = 0
            for software in software_list:
                if not isinstance(software, dict):
                    print(f"⚠️ 跳过非字典项: {software}")
                    continue
                
                try:
                    # 安全地获取软件信息
                    name = ReportGeneratorFixedSafe._safe_get_data(software, ['name'], '未知')
                    version = ReportGeneratorFixedSafe._safe_get_data(software, ['version'], '未知')
                    software_type = ReportGeneratorFixedSafe._safe_get_data(software, ['type'], '未知')
                    
                    software_data.append([name, version, software_type])
                    valid_count += 1
                    
                    # 限制数量避免表格过大
                    if valid_count >= 20:
                        print("⚠️ 软件数量超过20，截断")
                        break
                        
                except Exception as e:
                    print(f"⚠️ 处理软件项失败: {e}, 数据: {software}")
                    continue
            
            print(f"✅ 有效软件数量: {valid_count}")
            
            if valid_count == 0:
                return None
            
            # 创建表格 - 使用混合字体确保所有字符都能显示
            software_table = Table(software_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            software_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), ReportGeneratorFixedSafe.CHINESE_FONT),  # 使用混合字体
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            
            return software_table
            
        except Exception as e:
            print(f"❌ 创建软件表格失败: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def _create_services_table(services_list):
        """创建服务资产表格 - 使用混合字体"""
        try:
            if not services_list or not isinstance(services_list, list):
                return None
            
            services_data = [['服务名称', '端口', '状态']]
            valid_count = 0
            
            for service in services_list:
                if not isinstance(service, dict):
                    continue
                
                try:
                    name = ReportGeneratorFixedSafe._safe_get_data(service, ['name'], '未知')
                    port = ReportGeneratorFixedSafe._safe_get_data(service, ['port'], '未知')
                    status = ReportGeneratorFixedSafe._safe_get_data(service, ['status'], '未知')
                    
                    services_data.append([name, str(port), status])
                    valid_count += 1
                    
                    if valid_count >= 15:
                        break
                        
                except Exception as e:
                    print(f"⚠️ 处理服务项失败: {e}")
                    continue
            
            if valid_count == 0:
                return None
            
            services_table = Table(services_data, colWidths=[2*inch, 1*inch, 1*inch])
            services_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), ReportGeneratorFixedSafe.CHINESE_FONT),  # 使用混合字体
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            return services_table
            
        except Exception as e:
            print(f"⚠️ 创建服务表格失败: {e}")
            return None

    @staticmethod
    def _create_compliance_table(compliance_data):
        """创建合规检查表格 - 使用混合字体"""
        try:
            details = ReportGeneratorFixedSafe._safe_get_data(compliance_data, ['details'], [])
            if not details or not isinstance(details, list):
                return None
            
            compliance_data_table = [['检查项目', '状态', '描述']]
            valid_count = 0
            
            for check in details:
                if not isinstance(check, dict):
                    continue
                
                try:
                    check_name = ReportGeneratorFixedSafe._safe_get_data(check, ['check'], '未知')
                    status = ReportGeneratorFixedSafe._safe_get_data(check, ['status'], '未知')
                    description = ReportGeneratorFixedSafe._safe_get_data(check, ['description'], '未知')
                    
                    compliance_data_table.append([check_name, status, description])
                    valid_count += 1
                    
                    if valid_count >= 10:
                        break
                        
                except Exception as e:
                    print(f"⚠️ 处理合规检查项失败: {e}")
                    continue
            
            if valid_count == 0:
                return None
            
            compliance_table = Table(compliance_data_table, colWidths=[2*inch, 1*inch, 2*inch])
            compliance_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), ReportGeneratorFixedSafe.CHINESE_FONT),  # 使用混合字体
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (1, 1), (1, -1), colors.green),
            ]))
            
            # 动态设置状态颜色
            for i in range(1, len(compliance_data_table)):
                status = compliance_data_table[i][1].lower()
                if status == 'failed':
                    compliance_table.setStyle(TableStyle([
                        ('TEXTCOLOR', (1, i), (1, i), colors.red)
                    ]))
                elif status == 'passed':
                    compliance_table.setStyle(TableStyle([
                        ('TEXTCOLOR', (1, i), (1, i), colors.green)
                    ]))
            
            return compliance_table
            
        except Exception as e:
            print(f"⚠️ 创建合规表格失败: {e}")
            return None

    @staticmethod
    def _create_vulnerabilities_table(vulnerabilities_data):
        """创建漏洞信息表格 - 使用混合字体"""
        try:
            vuln_list = ReportGeneratorFixedSafe._safe_get_data(vulnerabilities_data, ['vulnerabilities'], [])
            if not vuln_list or not isinstance(vuln_list, list):
                return None
            
            vuln_data = [['漏洞ID', '严重程度', '标题', '修复建议']]
            valid_count = 0
            
            for vuln in vuln_list:
                if not isinstance(vuln, dict):
                    continue
                
                try:
                    cve_id = ReportGeneratorFixedSafe._safe_get_data(vuln, ['cve_id'], '未知')
                    severity = ReportGeneratorFixedSafe._safe_get_data(vuln, ['severity'], '未知')
                    title = ReportGeneratorFixedSafe._safe_get_data(vuln, ['title'], '未知')
                    remediation = ReportGeneratorFixedSafe._safe_get_data(vuln, ['remediation'], '未知')
                    
                    # 截断长文本
                    title = title[:50] + "..." if len(title) > 50 else title
                    remediation = remediation[:60] + "..." if len(remediation) > 60 else remediation
                    
                    vuln_data.append([cve_id, severity, title, remediation])
                    valid_count += 1
                    
                    if valid_count >= 10:
                        break
                        
                except Exception as e:
                    print(f"⚠️ 处理漏洞项失败: {e}")
                    continue
            
            if valid_count == 0:
                return None
            
            vuln_table = Table(vuln_data, colWidths=[1.2*inch, 0.8*inch, 2*inch, 1.5*inch])
            vuln_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), ReportGeneratorFixedSafe.CHINESE_FONT),  # 使用混合字体
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            return vuln_table
            
        except Exception as e:
            print(f"⚠️ 创建漏洞表格失败: {e}")
            return None

    @staticmethod
    def generate_pdf_report(scan_data, output_path):
        """安全版的PDF生成器 - 使用混合字体确保字符完全显示"""
        try:
            print(f"🔧 安全版PDF生成器开始: {output_path}")
            print(f"📊 输入数据键: {list(scan_data.keys())}")
            
            # 确保字体已配置
            ReportGeneratorFixedSafe._setup_fonts()
            
            # 创建文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # 获取样式
            styles = ReportGeneratorFixedSafe._create_styles()
            
            # 构建内容
            elements = []
            
            # 标题 - 使用混合字体
            elements.append(Paragraph("SecKeeper 安全扫描报告", styles['title']))
            elements.append(Spacer(1, 20))
            
            # 创建概览表格
            overview_table = ReportGeneratorFixedSafe._create_overview_table(scan_data)
            if overview_table:
                elements.append(overview_table)
            else:
                elements.append(Paragraph("无法生成概览信息", styles['mixed']))
            
            elements.append(Spacer(1, 20))
            
            # 软件资产部分
            try:
                assets = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['assets'], {})
                software_list = ReportGeneratorFixedSafe._safe_get_data(assets, ['software'], [])
                software_count = len(software_list) if isinstance(software_list, list) else 0
                
                if software_count > 0:
                    elements.append(Paragraph("软件资产", styles['heading2']))
                    elements.append(Spacer(1, 12))
                    
                    software_table = ReportGeneratorFixedSafe._create_software_table(software_list)
                    if software_table:
                        elements.append(software_table)
                    else:
                        elements.append(Paragraph("无有效软件信息", styles['mixed']))
                    
                    elements.append(Spacer(1, 20))
            except Exception as e:
                print(f"⚠️ 软件信息处理失败: {e}")
            
            # 服务资产部分
            try:
                services_list = ReportGeneratorFixedSafe._safe_get_data(assets, ['services'], [])
                services_count = len(services_list) if isinstance(services_list, list) else 0
                
                if services_count > 0:
                    elements.append(Paragraph("服务资产", styles['heading2']))
                    elements.append(Spacer(1, 12))
                    
                    services_table = ReportGeneratorFixedSafe._create_services_table(services_list)
                    if services_table:
                        elements.append(services_table)
                    else:
                        elements.append(Paragraph("无有效服务信息", styles['mixed']))
                    
                    elements.append(Spacer(1, 20))
            except Exception as e:
                print(f"⚠️ 服务信息处理失败: {e}")
            
            # 合规检查部分
            try:
                compliance = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['compliance'], {})
                compliance_details = ReportGeneratorFixedSafe._safe_get_data(compliance, ['details'], [])
                
                if compliance_details and isinstance(compliance_details, list) and len(compliance_details) > 0:
                    elements.append(Paragraph("合规检查详情", styles['heading2']))
                    elements.append(Spacer(1, 12))
                    
                    compliance_table = ReportGeneratorFixedSafe._create_compliance_table(compliance)
                    if compliance_table:
                        elements.append(compliance_table)
                    else:
                        elements.append(Paragraph("无合规检查详情", styles['mixed']))
                    
                    elements.append(Spacer(1, 20))
            except Exception as e:
                print(f"⚠️ 合规信息处理失败: {e}")
            
            # 漏洞信息部分
            try:
                vulnerabilities = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['vulnerabilities'], {})
                vuln_list = ReportGeneratorFixedSafe._safe_get_data(vulnerabilities, ['vulnerabilities'], [])
                vuln_count = len(vuln_list) if isinstance(vuln_list, list) else 0
                
                if vuln_count > 0:
                    elements.append(Paragraph("安全漏洞", styles['heading2']))
                    elements.append(Spacer(1, 12))
                    
                    vuln_table = ReportGeneratorFixedSafe._create_vulnerabilities_table(vulnerabilities)
                    if vuln_table:
                        elements.append(vuln_table)
                    else:
                        elements.append(Paragraph("无有效漏洞信息", styles['mixed']))
                    
                    elements.append(Spacer(1, 20))
            except Exception as e:
                print(f"⚠️ 漏洞信息处理失败: {e}")
            
            # 总结部分
            elements.append(Paragraph("报告总结", styles['heading2']))
            elements.append(Spacer(1, 12))
            
            # 重新获取统计数据用于总结
            assets = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['assets'], {})
            software_count = len(ReportGeneratorFixedSafe._safe_get_data(assets, ['software'], []))
            services_count = len(ReportGeneratorFixedSafe._safe_get_data(assets, ['services'], []))
            compliance_rate = ReportGeneratorFixedSafe._safe_get_data(scan_data, ['compliance', 'summary', 'compliance_rate'], 0)
            vuln_count = len(ReportGeneratorFixedSafe._safe_get_data(scan_data, ['vulnerabilities', 'vulnerabilities'], []))
            
            summary_text = f"""
            本次安全扫描共发现:
            • {software_count} 个软件资产
            • {services_count} 个服务资产  
            • 系统合规率为 {compliance_rate}%
            • 发现 {vuln_count} 个安全漏洞
            
            建议根据扫描结果及时处理发现的安全问题。
            """
            
            elements.append(Paragraph(summary_text, styles['mixed']))
            
            # 生成PDF
            print("📄 开始构建PDF文档...")
            doc.build(elements)
            
            # 验证生成的文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ 安全版PDF生成成功，文件大小: {file_size} 字节")
                
                # 验证PDF格式
                with open(output_path, 'rb') as f:
                    header = f.read(20)
                    is_pdf = header.startswith(b'%PDF')
                    print(f"🔍 PDF文件头验证: {is_pdf}")
                
                return True
            else:
                print("❌ PDF文件未生成")
                return False
            
        except Exception as e:
            print(f"❌ 安全版PDF生成失败: {str(e)}")
            traceback.print_exc()
            return False

# 初始化字体配置
ReportGeneratorFixedSafe._setup_fonts()
