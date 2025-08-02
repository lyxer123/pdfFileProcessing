import os
import shutil
import json
from typing import Dict, List, Any, Tuple
from tqdm import tqdm
from extractor import StandardFeatureExtractor
from trainer import StandardModelTrainer
from config import MODEL_CONFIG, OUTPUT_DIR

class StandardPredictor:
    """标准文档预测器"""
    
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.extractor = StandardFeatureExtractor()
        self.trainer = StandardModelTrainer()
        self.loaded = False
    
    def load_model(self):
        """加载训练好的模型"""
        try:
            self.trainer.load_model(self.model_dir)
            self.loaded = True
            print("模型加载成功")
        except Exception as e:
            print(f"模型加载失败: {e}")
            raise
    
    def scan_pdf_files(self, root_dir: str) -> List[str]:
        """扫描指定目录下的所有PDF文件"""
        pdf_files = []
        
        print(f"正在扫描目录: {root_dir}")
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    pdf_files.append(pdf_path)
        
        print(f"找到 {len(pdf_files)} 个PDF文件")
        return pdf_files
    
    def predict_single_file(self, pdf_path: str) -> Tuple[bool, float, Dict[str, Any]]:
        """预测单个PDF文件"""
        if not self.loaded:
            raise ValueError("模型未加载，请先调用 load_model()")
        
        # 提取特征
        features = self.extractor.extract_pdf_features(pdf_path)
        
        # 使用模型预测
        prediction, probability = self.trainer.predict(features)
        
        # 判断是否为标准文档
        is_standard = prediction == 1 and probability >= MODEL_CONFIG["min_confidence"]
        
        return is_standard, probability, features
    
    def predict_batch_files(self, pdf_files: List[str], output_dir: str = None) -> List[Dict[str, Any]]:
        """批量预测PDF文件"""
        if not self.loaded:
            raise ValueError("模型未加载，请先调用 load_model()")
        
        results = []
        standard_files = []
        
        print(f"开始预测 {len(pdf_files)} 个PDF文件...")
        
        for pdf_path in tqdm(pdf_files, desc="预测进度"):
            try:
                is_standard, probability, features = self.predict_single_file(pdf_path)
                
                result = {
                    "file_path": pdf_path,
                    "filename": os.path.basename(pdf_path),
                    "is_standard": is_standard,
                    "confidence": probability,
                    "features": features
                }
                
                results.append(result)
                
                if is_standard:
                    standard_files.append(result)
                    print(f"✓ 标准文档: {os.path.basename(pdf_path)} (置信度: {probability:.3f})")
                else:
                    print(f"✗ 非标准: {os.path.basename(pdf_path)} (置信度: {probability:.3f})")
                    
            except Exception as e:
                print(f"预测失败 {pdf_path}: {e}")
                results.append({
                    "file_path": pdf_path,
                    "filename": os.path.basename(pdf_path),
                    "is_standard": False,
                    "confidence": 0.0,
                    "error": str(e)
                })
        
        print(f"\n预测完成:")
        print(f"  总文件数: {len(pdf_files)}")
        print(f"  标准文档: {len(standard_files)}")
        print(f"  非标准文档: {len(pdf_files) - len(standard_files)}")
        
        # 保存预测结果
        if output_dir:
            self.save_prediction_results(results, output_dir)
        
        return results
    
    def copy_standard_files(self, results: List[Dict[str, Any]], output_dir: str):
        """复制标准文档到输出目录"""
        standard_files = [r for r in results if r["is_standard"]]
        
        if not standard_files:
            print("没有找到标准文档")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"开始复制 {len(standard_files)} 个标准文档到 {output_dir}...")
        
        copied_count = 0
        for result in tqdm(standard_files, desc="复制进度"):
            try:
                source_path = result["file_path"]
                filename = result["filename"]
                
                # 处理文件名冲突
                target_path = os.path.join(output_dir, filename)
                counter = 1
                while os.path.exists(target_path):
                    name, ext = os.path.splitext(filename)
                    target_path = os.path.join(output_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                # 复制文件
                shutil.copy2(source_path, target_path)
                copied_count += 1
                
            except Exception as e:
                print(f"复制失败 {result['filename']}: {e}")
        
        print(f"复制完成，成功复制 {copied_count} 个文件")
    
    def save_prediction_results(self, results: List[Dict[str, Any]], output_dir: str):
        """保存预测结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细结果
        results_path = os.path.join(output_dir, "prediction_results.json")
        
        # 简化结果以便JSON序列化
        simplified_results = []
        for result in results:
            simplified_result = {
                "file_path": result["file_path"],
                "filename": result["filename"],
                "is_standard": result["is_standard"],
                "confidence": result["confidence"]
            }
            
            # 添加特征信息（简化）
            if "features" in result:
                features = result["features"]
                simplified_result["standard_type"] = features.get("filename_features", {}).get("standard_type")
                simplified_result["ev_related"] = features.get("filename_features", {}).get("ev_related")
                simplified_result["text_length"] = features.get("content_features", {}).get("text_length", 0)
            
            if "error" in result:
                simplified_result["error"] = result["error"]
            
            simplified_results.append(simplified_result)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(simplified_results, f, ensure_ascii=False, indent=2)
        
        # 保存标准文档列表
        standard_files = [r for r in simplified_results if r["is_standard"]]
        standard_list_path = os.path.join(output_dir, "standard_files.json")
        with open(standard_list_path, 'w', encoding='utf-8') as f:
            json.dump(standard_files, f, ensure_ascii=False, indent=2)
        
        # 生成统计报告
        stats = {
            "total_files": len(results),
            "standard_files": len(standard_files),
            "non_standard_files": len(results) - len(standard_files),
            "standard_ratio": len(standard_files) / len(results) if results else 0,
            "confidence_stats": {
                "min": min(r["confidence"] for r in results),
                "max": max(r["confidence"] for r in results),
                "avg": sum(r["confidence"] for r in results) / len(results) if results else 0
            }
        }
        
        stats_path = os.path.join(output_dir, "prediction_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"预测结果已保存到: {output_dir}")
        print(f"  - 详细结果: {results_path}")
        print(f"  - 标准文档列表: {standard_list_path}")
        print(f"  - 统计信息: {stats_path}")
        
        # 打印统计信息
        print(f"\n统计信息:")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  标准文档: {stats['standard_files']}")
        print(f"  非标准文档: {stats['non_standard_files']}")
        print(f"  标准文档比例: {stats['standard_ratio']:.2%}")
        print(f"  置信度范围: {stats['confidence_stats']['min']:.3f} - {stats['confidence_stats']['max']:.3f}")
        print(f"  平均置信度: {stats['confidence_stats']['avg']:.3f}")
    
    def predict_and_copy(self, root_dir: str, output_dir: str = None):
        """预测并复制标准文档的完整流程"""
        if output_dir is None:
            output_dir = OUTPUT_DIR
        
        # 扫描PDF文件
        pdf_files = self.scan_pdf_files(root_dir)
        
        if not pdf_files:
            print("未找到PDF文件")
            return
        
        # 批量预测
        results = self.predict_batch_files(pdf_files, output_dir)
        
        # 复制标准文档
        self.copy_standard_files(results, output_dir)
        
        return results
