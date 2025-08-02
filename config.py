import os

# 标准文件路径配置
STANDARD_PDFS_DIR = "./pdfs/标准"
MODEL_DIR = "./model"
OUTPUT_DIR = "./I盘标准"

# 标准类型分类
STANDARD_TYPES = {
    "GB": {
        "name": "国家标准",
        "patterns": ["GB/T", "GB ", "中华人民共和国国家标准"],
        "priority": 10
    },
    "DB": {
        "name": "地方标准", 
        "patterns": ["DB", "地方标准"],
        "priority": 9
    },
    "NB": {
        "name": "行业标准",
        "patterns": ["NB/T", "NB-", "行业标准"],
        "priority": 8
    },
    "T": {
        "name": "团体标准",
        "patterns": ["T/", "团体标准"],
        "priority": 7
    },
    "QGDW": {
        "name": "企业标准",
        "patterns": ["Q/GDW", "企业标准"],
        "priority": 6
    }
}

# 电动汽车相关关键词
EV_KEYWORDS = [
    "电动汽车", "充电", "充电桩", "充电站", "换电", "电池", "充电接口", 
    "充电系统", "充电设备", "充电协议", "充电电缆", "充电控制器",
    "充电基础设施", "充电管理", "充电安全", "充电计量", "充电通信"
]

# 标准文档特征关键词
STANDARD_KEYWORDS = [
    "标准", "规范", "要求", "技术规范", "技术要求", "技术标准",
    "管理规范", "设计规范", "建设标准", "安全要求", "试验规范",
    "术语", "定义", "分类", "标识", "符号", "代号"
]

# 排除关键词（非标准文档）
EXCLUDE_KEYWORDS = [
    "datasheet", "schematic", "manual", "guide", "instruction", "drawing", "cad",
    "规格书", "说明书", "图纸", "电路图", "原理图", "操作手册", "用户手册",
    "产品", "芯片", "模块", "设备", "系统", "控制器", "传感器", "合同", "协议"
]

# 模型训练参数
MODEL_CONFIG = {
    "min_confidence": 0.6,
    "max_pages_to_extract": 5,
    "min_text_length": 100,
    "feature_weight": {
        "filename": 0.3,
        "content": 0.7
    }
}

# 文件处理配置
FILE_CONFIG = {
    "supported_extensions": [".pdf"],
    "max_file_size_mb": 100,
    "encoding": "utf-8"
}
