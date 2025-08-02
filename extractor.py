import os
import re
import json
import pdfplumber
from typing import Dict, List, Tuple, Any
from config import STANDARD_TYPES, EV_KEYWORDS, STANDARD_KEYWORDS, EXCLUDE_KEYWORDS, MODEL_CONFIG

class StandardFeatureExtractor:
    """标准文档特征提取器"""
    
    def __init__(self):
        self.features = []
        self.standard_patterns = self._build_standard_patterns()
    
    def _build_standard_patterns(self) -> Dict[str, List[str]]:
        """构建标准模式匹配规则"""
        patterns = {}
        for std_type, config in STANDARD_TYPES.items():
            patterns[std_type] = config["patterns"]
        return patterns
    
    def extract_filename_features(self, filename: str) -> Dict[str, Any]:
        """从文件名提取特征"""
        features = {
            "filename": filename,
            "standard_type": None,
            "standard_code": None,
            "year": None,
            "ev_related": False,
            "standard_related": False
        }
        
        # 检测标准类型
        for std_type, patterns in self.standard_patterns.items():
            for pattern in patterns:
                if pattern in filename:
                    features["standard_type"] = std_type
                    break
            if features["standard_type"]:
                break
        
        # 提取标准编号
        std_code_patterns = [
            r'GB/T\s*(\d+[-\d]*)',
            r'GB\s*(\d+[-\d]*)',
            r'DB\d+[-\s]*(\d+[-\d]*)',
            r'NB/T\s*(\d+[-\d]*)',
            r'T/[A-Z]+\s*(\d+[-\d]*)',
            r'Q/GDW\s*(\d+[-\d]*)'
        ]
        
        for pattern in std_code_patterns:
            match = re.search(pattern, filename)
            if match:
                features["standard_code"] = match.group(1)
                break
        
        # 提取年份
        year_pattern = r'20\d{2}'
        year_match = re.search(year_pattern, filename)
        if year_match:
            features["year"] = year_match.group()
        
        # 检测电动汽车相关
        features["ev_related"] = any(keyword in filename for keyword in EV_KEYWORDS)
        
        # 检测标准相关
        features["standard_related"] = any(keyword in filename for keyword in STANDARD_KEYWORDS)
        
        return features
    
    def extract_content_features(self, text: str) -> Dict[str, Any]:
        """从文档内容提取特征"""
        features = {
            "text_length": len(text),
            "standard_keywords_count": 0,
            "ev_keywords_count": 0,
            "exclude_keywords_count": 0,
            "standard_sections": [],
            "ev_sections": []
        }
        
        # 统计关键词出现次数
        for keyword in STANDARD_KEYWORDS:
            count = text.count(keyword)
            features["standard_keywords_count"] += count
        
        for keyword in EV_KEYWORDS:
            count = text.count(keyword)
            features["ev_keywords_count"] += count
        
        for keyword in EXCLUDE_KEYWORDS:
            count = text.count(keyword)
            features["exclude_keywords_count"] += count
        
        # 提取标准相关段落
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in STANDARD_KEYWORDS):
                features["standard_sections"].append({
                    "line": i,
                    "content": line.strip()
                })
            
            if any(keyword in line for keyword in EV_KEYWORDS):
                features["ev_sections"].append({
                    "line": i,
                    "content": line.strip()
                })
        
        return features
    
    def extract_pdf_features(self, pdf_path: str) -> Dict[str, Any]:
        """从PDF文件提取完整特征"""
        features = {
            "file_path": pdf_path,
            "filename_features": {},
            "content_features": {},
            "is_standard": False,
            "confidence": 0.0
        }
        
        # 提取文件名特征
        filename = os.path.basename(pdf_path)
        features["filename_features"] = self.extract_filename_features(filename)
        
        # 提取内容特征
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                max_pages = min(MODEL_CONFIG["max_pages_to_extract"], len(pdf.pages))
                
                for i in range(max_pages):
                    page = pdf.pages[i]
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
                
                if len(text) >= MODEL_CONFIG["min_text_length"]:
                    features["content_features"] = self.extract_content_features(text)
                else:
                    features["content_features"] = {"text_length": len(text)}
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            features["content_features"] = {"error": str(e)}
        
        # 计算是否为标准文档的置信度
        features["is_standard"], features["confidence"] = self._calculate_standard_confidence(features)
        
        return features
    
    def _calculate_standard_confidence(self, features: Dict[str, Any]) -> Tuple[bool, float]:
        """计算标准文档置信度"""
        confidence = 0.0
        
        # 文件名特征权重
        filename_features = features["filename_features"]
        if filename_features["standard_type"]:
            confidence += 0.4
        if filename_features["standard_code"]:
            confidence += 0.2
        if filename_features["standard_related"]:
            confidence += 0.1
        if filename_features["ev_related"]:
            confidence += 0.1
        
        # 内容特征权重
        content_features = features["content_features"]
        if "standard_keywords_count" in content_features:
            std_count = content_features["standard_keywords_count"]
            ev_count = content_features["ev_keywords_count"]
            exclude_count = content_features["exclude_keywords_count"]
            
            # 标准关键词加分
            if std_count > 0:
                confidence += min(0.2, std_count * 0.01)
            
            # 电动汽车关键词加分
            if ev_count > 0:
                confidence += min(0.1, ev_count * 0.005)
            
            # 排除关键词减分
            if exclude_count > 0:
                confidence -= min(0.3, exclude_count * 0.02)
        
        # 确保置信度在0-1之间
        confidence = max(0.0, min(1.0, confidence))
        
        is_standard = confidence >= MODEL_CONFIG["min_confidence"]
        
        return is_standard, confidence
    
    def extract_all_standards(self, standard_dir: str) -> List[Dict[str, Any]]:
        """提取所有标准文件的特征"""
        all_features = []
        
        if not os.path.exists(standard_dir):
            print(f"标准目录不存在: {standard_dir}")
            return all_features
        
        pdf_files = [f for f in os.listdir(standard_dir) if f.lower().endswith('.pdf')]
        
        print(f"开始提取 {len(pdf_files)} 个标准文件的特征...")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(standard_dir, pdf_file)
            print(f"正在处理: {pdf_file}")
            
            features = self.extract_pdf_features(pdf_path)
            all_features.append(features)
        
        return all_features
    
    def save_features(self, features: List[Dict[str, Any]], output_path: str):
        """保存特征到JSON文件"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(features, f, ensure_ascii=False, indent=2)
        
        print(f"特征已保存到: {output_path}")
        print(f"总共提取了 {len(features)} 个文件的特征")
        
        # 统计标准文档数量
        standard_count = sum(1 for f in features if f["is_standard"])
        print(f"其中标准文档: {standard_count} 个")
        print(f"非标准文档: {len(features) - standard_count} 个")
