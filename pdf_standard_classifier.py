import os
import shutil
import pdfplumber
import re
from tqdm import tqdm

# 设置根目录
ROOT_DIR = "I:"  # 修改为你的PDF存放目录（支持整个硬盘）
OUTPUT_DIR = "./标准分类"

# 定义更细粒度的分类及关键词
CATEGORIES = {
    # 标准文档类
    "国标": {
        "keywords": ["GB/T", "GB ", "国家标准", "国家市场监督管理总局", "国家标准化管理委员会", "中华人民共和国国家标准"],
        "priority": 15,
        "min_confidence": 0.6
    },
    "行标": {
        "keywords": ["JT/T", "DL/T", "YY/T", "行业标准", "行业规范", "电力行业标准", "通信行业标准"],
        "priority": 14,
        "min_confidence": 0.6
    },
    "团标": {
        "keywords": ["团体标准", "T/CSAE", "T/CESA", "T/", "中电联", "中国电力企业联合会"],
        "priority": 13,
        "min_confidence": 0.6
    },
    "企业标准": {
        "keywords": ["企业标准", "公司标准", "Q/", "企标"],
        "priority": 12,
        "min_confidence": 0.6
    },
    
    # 技术文档类
    "设备通讯协议": {
        "keywords": ["通信协议", "通讯协议", "modbus", "通信规约", "通讯规约", "接口协议", "通信接口"],
        "patterns": [r"modbus", r"通信协议", r"通讯协议", r"接口协议"],
        "priority": 11,
        "min_confidence": 0.4
    },
    "电路图": {
        "keywords": ["schematic", "电路图", "原理图", "SCH", "电气原理", "接线图", "电路原理", "电气图"],
        "patterns": [r"sch", r"circuit", r"wiring", r"electrical", r"原理图", r"电路图"],
        "priority": 10,
        "min_confidence": 0.4
    },
    "规格书": {
        "keywords": ["datasheet", "规格书", "技术规格", "产品规格", "specification", "技术参数", "产品说明书", "技术手册"],
        "patterns": [r"datasheet", r"spec", r"规格书", r"技术规格", r"产品规格"],
        "priority": 9,
        "min_confidence": 0.4
    },
    "芯片数据手册": {
        "keywords": ["芯片", "chip", "datasheet", "数据手册", "技术手册", "产品手册"],
        "patterns": [r"datasheet", r"芯片", r"chip", r"数据手册"],
        "priority": 8,
        "min_confidence": 0.4
    },
    "元器件说明书": {
        "keywords": ["元器件", "电阻", "电容", "电感", "晶振", "component", "规格书"],
        "patterns": [r"元器件", r"电阻", r"电容", r"晶振", r"component"],
        "priority": 7,
        "min_confidence": 0.4
    },
    "说明书": {
        "keywords": ["说明书", "使用说明", "操作手册", "用户手册", "manual", "guide", "instruction", "使用指南", "操作指南"],
        "patterns": [r"manual", r"guide", r"instruction", r"说明书", r"使用说明", r"操作手册"],
        "priority": 6,
        "min_confidence": 0.4
    },
    "图纸": {
        "keywords": ["图纸", "drawing", "CAD", "设计图", "工程图", "机械图", "电气图纸", "施工图"],
        "patterns": [r"drawing", r"cad", r"图纸", r"设计图", r"工程图"],
        "priority": 5,
        "min_confidence": 0.4
    },
    "专利": {
        "keywords": ["专利", "patent", "发明", "实用新型", "专利申请", "专利技术", "发明专利"],
        "patterns": [r"patent", r"专利", r"发明", r"实用新型"],
        "priority": 4,
        "min_confidence": 0.4
    },
    "合同": {
        "keywords": ["合同", "contract", "协议", "agreement", "项目合同", "技术合同"],
        "patterns": [r"合同", r"contract", r"协议", r"agreement"],
        "priority": 3,
        "min_confidence": 0.4
    },
    "论文": {
        "keywords": ["论文", "paper", "research", "study", "analysis", "investigation"],
        "patterns": [r"论文", r"paper", r"research", r"study"],
        "priority": 2,
        "min_confidence": 0.4
    },
    "技术文档": {
        "keywords": ["技术文档", "技术规范", "技术要求", "技术方案", "技术报告", "技术标准", "技术规格", "技术参数"],
        "patterns": [r"技术", r"规范", r"要求", r"方案", r"标准", r"规格"],
        "priority": 1,
        "min_confidence": 0.3
    },
    "其他": {
        "keywords": [],
        "priority": 0,
        "min_confidence": 0.0
    }
}

# 排除关键词（如果文档包含这些词，降低其作为标准文档的可能性）
EXCLUDE_KEYWORDS = [
    "datasheet", "schematic", "manual", "guide", "instruction", "drawing", "cad",
    "规格书", "说明书", "图纸", "电路图", "原理图", "操作手册", "用户手册",
    "产品", "芯片", "模块", "设备", "系统", "控制器", "传感器"
]

# 特殊文件类型识别规则
SPECIAL_RULES = {
    "设备通讯协议": {
        "filename_patterns": [
            r"modbus", r"通信协议", r"通讯协议", r"接口协议", r"通信规约", r"通讯规约"
        ],
        "content_keywords": ["modbus", "通信协议", "通讯协议", "接口协议", "通信规约", "通讯规约"]
    },
    "芯片数据手册": {
        "filename_patterns": [
            r"datasheet", r"芯片", r"chip", r"数据手册", r"技术手册"
        ],
        "content_keywords": ["datasheet", "芯片", "chip", "数据手册", "技术手册", "产品手册"]
    },
    "元器件说明书": {
        "filename_patterns": [
            r"\d+[A-Z]+\d+",  # 类似 49 C423021_6.8KΩ±0.5%100MW_2020-03-06
            r"[A-Z]+\d+[A-Z]+",  # 类似 CK45-E3DD472ZYGNA
            r"电阻", r"电容", r"晶振", r"component"
        ],
        "content_keywords": ["电阻", "电容", "电感", "晶振", "元器件", "component", "规格书"]
    },
    "规格书": {
        "filename_patterns": [
            r"datasheet", r"spec", r"规格书", r"技术规格", r"产品规格",
            r"\d+[A-Z]+\d+",  # 类似 34 C191602_2.2MH@1KHZ3A_2018-05-02
            r"[A-Z]+\d+[A-Z]+",  # 类似 1N4148WS
            r"semiconductor",  # 半导体相关
        ],
        "content_keywords": ["参数", "规格", "特性", "电气特性", "机械特性", "封装", "引脚", "datasheet", "specification"]
    },
    "图纸": {
        "filename_patterns": [
            r"图纸", r"drawing", r"cad", r"设计图", r"工程图", r"电气原理图纸"
        ],
        "content_keywords": ["图纸", "设计图", "工程图", "施工图", "装配图", "零件图"]
    },
    "说明书": {
        "filename_patterns": [
            r"说明书", r"manual", r"guide", r"使用说明", r"操作手册", r"用户手册", r"使用说明书"
        ],
        "content_keywords": ["使用说明", "操作说明", "安装说明", "维护说明", "注意事项", "使用方法", "操作步骤"]
    },
    "合同": {
        "filename_patterns": [
            r"合同", r"contract", r"协议", r"agreement", r"项目合同"
        ],
        "content_keywords": ["合同", "contract", "协议", "agreement", "项目合同", "技术合同"]
    },
    "论文": {
        "filename_patterns": [
            r"论文", r"paper", r"research", r"study", r"analysis"
        ],
        "content_keywords": ["论文", "paper", "research", "study", "analysis", "investigation"]
    },
    "其他": {
        "filename_patterns": [
            r"回复", r"登记表", r"申请表", r"报价", r"报告", r"计划", r"项目计划", r"录用通知", r"白皮书", r"宣传册"
        ],
        "content_keywords": ["回复", "登记", "申请", "报价", "报告", "计划", "通知", "项目", "录用", "白皮书", "宣传"]
    }
}

# 特定文件名的精确匹配规则
EXACT_MATCHES = {
    # 原有精确匹配
    "1N4148WS_Diotec_Semiconductor.pdf": "规格书",
    "单相电表模块ATT7053AU使用说明书1.1.pdf": "说明书",
    "永联科技回复.pdf": "其他",
    "红外读头.pdf": "说明书",
    "苏创自研控制器项目计划.pdf": "技术文档",
    
    # 新增精确匹配
    "1_固德威并网MTG2SMTSDTG2MSDNSXS系列逆变器Modbus通信协议-客户版.pdf": "设备通讯协议",
    "1_固德威并网MTG2SMTSDTG2MSDNSXS系列逆变器Modbus通信协议（正泰是smt）.pdf": "设备通讯协议",
    "1-2 Blue Pill STM32 con LDmicro.pdf": "说明书",
    "4 C2922458_等级_X1,Y24.7NF±10%250VAC_2022-07-26.PDF": "元器件说明书",
    "4-台区智能融合终端功能模块型式规范-征求意见稿.pdf": "企业标准",
    "6.2《大规模电动汽车安全充放电与车-网智能互动关键技术》科学技术项目合同.pdf": "合同",
    "6.78 MHz Wireless Power Transfer with Self Resonant Coils at 95 percent DC-DC Efficiency.pdf": "论文",
    "7-功率分析仪.pdf": "技术文档",
    "08-29-19 PCCC Documentation.pdf": "技术文档",
    "8.1 科学技术项目合同（2023版）-20231117V2.pdf": "合同",
    "8BG000-A7680C-TE_V3.01_DL(230831).pdf": "图纸",
    "11-2.高比例可再生能源接入下考虑运行灵活性的电力系统规划研究-论文1-国网滨州供电公司.pdf": "论文",
    "49 C423021_6.8KΩ±0.5%100MW_2020-03-06.PDF": "元器件说明书",
    "55 C2989257_20KΩ±0.5%100MW_2022-07-08.PDF": "元器件说明书",
    "63 C23186_5.1KΩ±1%100MW_2020-03-06.PDF": "元器件说明书",
    "64 C23162_4.7KΩ±1%100MW_2020-03-06.PDF": "元器件说明书",
    "67 C2988907_2.2KΩ±0.5%100MW_2022-07-08.PDF": "元器件说明书",
    "70 C2989011_12KΩ±0.5%100MW_2022-07-08.PDF": "元器件说明书",
    "102 C1669859_32.768KHZ±20PPM7PF_2021-11-26.PDF": "元器件说明书",
    "1125369445.pdf": "芯片数据手册",
    "223120313211441084.inform.en.pdf": "其他",
    "223120315313547084.inform.en.pdf": "其他",
    "A Blockchain-based Carbon Credit Ecosystem.pdf": "其他",
    "All-SiC 9.5 kWdm3 On-Board Power Electronics for 50 kW-85 kHz Automotive IPT System.pdf": "论文",
    "AN-LAN86xx-BIN-Ref-Design-60001718.pdf": "技术文档",
    "applsci-11-07569-v2.pdf": "论文",
    "atecc608a_summary.pdf": "芯片数据手册",
    "atmel-128.pdf": "芯片数据手册",
    "ChargingPile.pdf": "电路图",
    "CK45-E3DD472ZYGNA.pdf": "元器件说明书",
    "Comparison of 22 kHz and 85 kHz 50 kW Wireless Charging System Using Si and SiC Switches for Electric Vehicle.pdf": "论文",
    "Comprehensive Evaluation of Rectangular and Double-D Coil Geometry for 50 kW-85 kHz IPT System.pdf": "论文",
    "Control Method for Inductive Power Transfer with High Partial-Load Efficiency and Resonance Tracking.pdf": "论文",
    "D3V3XA4B10LP.pdf": "芯片数据手册",
    "datasheet.pdf": "芯片数据手册",
    "DGD05463.pdf": "芯片数据手册",
    "DiPho_AFE.pdf": "电路图",
    "DiPho_digital.pdf": "电路图",
    "Downloader_C340.pdf": "电路图",
    "Downloader_cp2104&ch9012f.pdf": "电路图",
    "EA_TechBrief-10SPE-DT_final.pdf": "其他",
    "ENIP.cpp Documentation.pdf": "技术文档",
    "ESP-R8_POE_3_SCHEMATIC.pdf": "电路图",
    "esp-r8-poe-3.pdf": "说明书",
    "ESP32_Datasheet.pdf": "芯片数据手册",
    "ESP32_Hardware_design_guidelines.pdf": "技术文档",
    "ESP32_picoc_C_Language_Interpreter.pdf": "说明书",
    "ESP32_Technical_reference_manual.pdf": "技术文档",
    "esp32_v0a.pdf": "电路图",
    "esp32_v0b.pdf": "电路图",
    "ESP32-C6-EVB_Rev_A.pdf": "电路图",
    "ESP32-EVB_Rev_A.pdf": "电路图",
    "ESP32-EVB_Rev_B.pdf": "电路图",
    "ESP32-EVB_Rev_D.pdf": "电路图",
    "ESP32-EVB_Rev_F.pdf": "电路图",
    "ESP32-EVB_Rev_H-BOM.pdf": "其他",
    "ESP32-EVB_Rev_H.pdf": "电路图",
    "ESP32-EVB_Rev_I-BOM.pdf": "其他",
    "ESP32-S3 Parallel TFT with Touch 4.0\" ST7701 v1.2.PDF": "电路图"
}

def ensure_output_dirs():
    """创建输出分类目录"""
    for category in CATEGORIES:
        os.makedirs(os.path.join(OUTPUT_DIR, category), exist_ok=True)

def extract_text_from_pdf(pdf_path, max_pages=3):
    """从PDF提取文本"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            # 只取前几页进行判断
            for page in pdf.pages[:max_pages]:
                page_text = page.extract_text() or ''
                text += page_text + ' '
            return text.strip()
    except Exception as e:
        print(f"❌ 无法读取 {pdf_path}: {e}")
        return ""

def check_exact_matches(filename):
    """检查精确匹配"""
    return EXACT_MATCHES.get(filename, None)

def check_special_rules(filename, text):
    """检查特殊规则"""
    filename_lower = filename.lower()
    text_lower = text.lower()
    
    for category, rules in SPECIAL_RULES.items():
        # 检查文件名模式
        for pattern in rules["filename_patterns"]:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                # 检查内容关键词
                content_score = 0
                for keyword in rules["content_keywords"]:
                    if keyword in text_lower:
                        content_score += 1
                
                # 如果文件名匹配且内容也匹配，返回高置信度
                if content_score > 0:
                    return category, 0.9
                # 如果只有文件名匹配，返回中等置信度
                return category, 0.7
    
    return None, 0

def calculate_confidence(text, category_config):
    """计算分类置信度"""
    text_upper = text.upper()
    score = 0
    total_keywords = len(category_config["keywords"])
    
    # 关键词匹配
    for keyword in category_config["keywords"]:
        if keyword.upper() in text_upper:
            score += 1
    
    # 正则表达式匹配
    if "patterns" in category_config:
        for pattern in category_config["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.5
    
    # 计算置信度
    confidence = score / max(total_keywords, 1)
    
    # 如果包含排除关键词，降低置信度
    exclude_count = 0
    for exclude_word in EXCLUDE_KEYWORDS:
        if exclude_word.upper() in text_upper:
            exclude_count += 1
    
    if exclude_count > 0:
        confidence *= (0.9 ** exclude_count)  # 降低惩罚力度
    
    return min(confidence, 1.0)

def classify_pdf(pdf_path):
    """智能分类PDF文档"""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None
    
    # 获取文件名
    filename = os.path.basename(pdf_path)
    
    # 首先检查精确匹配
    exact_match = check_exact_matches(filename)
    if exact_match:
        return exact_match, 1.0  # 最高置信度
    
    # 获取文件名（不含扩展名）
    filename_no_ext = os.path.splitext(filename)[0]
    
    # 检查特殊规则
    special_category, special_confidence = check_special_rules(filename_no_ext, text)
    if special_category and special_confidence > 0.7:
        return special_category, special_confidence
    
    # 文件名关键词匹配
    filename_lower = filename_no_ext.lower()
    filename_keywords = {
        "设备通讯协议": ["modbus", "通信协议", "通讯协议", "接口协议"],
        "电路图": ["sch", "schematic", "电路图", "原理图", "电气原理"],
        "规格书": ["datasheet", "规格书", "spec", "技术规格"],
        "芯片数据手册": ["datasheet", "芯片", "chip", "数据手册"],
        "元器件说明书": ["电阻", "电容", "晶振", "component"],
        "说明书": ["manual", "guide", "说明书", "使用说明", "操作手册"],
        "图纸": ["drawing", "cad", "图纸", "设计图", "工程图"],
        "专利": ["patent", "专利", "发明", "实用新型"],
        "合同": ["合同", "contract", "协议", "agreement"],
        "论文": ["论文", "paper", "research", "study"],
        "技术文档": ["技术", "规范", "要求", "方案", "标准"]
    }
    
    # 检查文件名匹配
    for category, keywords in filename_keywords.items():
        for keyword in keywords:
            if keyword in filename_lower:
                if category in CATEGORIES:
                    return category, 0.9  # 高置信度
    
    best_category = None
    best_confidence = 0
    best_priority = -1
    
    # 遍历所有分类
    for category, config in CATEGORIES.items():
        confidence = calculate_confidence(text, config)
        
        # 检查是否达到最小置信度
        if confidence >= config["min_confidence"]:
            # 优先选择置信度高的，如果置信度相同则选择优先级高的
            if (confidence > best_confidence or 
                (confidence == best_confidence and config["priority"] > best_priority)):
                best_category = category
                best_confidence = confidence
                best_priority = config["priority"]
    
    # 如果没有找到合适的分类，尝试更宽松的匹配
    if not best_category or best_confidence < 0.2:
        # 对技术文档进行更宽松的匹配
        tech_keywords = ["技术", "规范", "要求", "方案", "标准", "规格", "参数", "配置", "设计", "开发"]
        tech_score = 0
        for keyword in tech_keywords:
            if keyword in text:
                tech_score += 1
        
        if tech_score >= 2:  # 至少包含2个技术相关词汇
            return "技术文档", 0.5
    
    return best_category, best_confidence

def classify_all_pdfs(root_dir):
    """主函数：遍历并分类PDF"""
    ensure_output_dirs()
    
    # 统计信息
    stats = {category: 0 for category in CATEGORIES}
    total_files = 0
    
    for dirpath, _, filenames in tqdm(os.walk(root_dir), desc="扫描PDF文件"):
        for fname in filenames:
            if fname.lower().endswith(".pdf"):
                total_files += 1
                full_path = os.path.join(dirpath, fname)
                
                result = classify_pdf(full_path)
                if result:
                    category, confidence = result
                    if category:
                        dest_path = os.path.join(OUTPUT_DIR, category, fname)
                        try:
                            shutil.copy2(full_path, dest_path)
                            stats[category] += 1
                            print(f"✅ {fname} → {category} (置信度: {confidence:.2f})")
                        except Exception as e:
                            print(f"❌ 复制失败 {fname}: {e}")
                    else:
                        print(f"⏩ 无匹配类别：{fname}")
                else:
                    print(f"❌ 无法处理：{fname}")
    
    # 打印统计信息
    print(f"\n📊 分类统计:")
    print(f"总文件数: {total_files}")
    for category, count in stats.items():
        if count > 0:
            print(f"{category}: {count} 个文件")

if __name__ == "__main__":
    classify_all_pdfs(ROOT_DIR)
