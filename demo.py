#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档识别系统 - 演示脚本
演示如何使用系统处理I盘中的PDF文件
"""

import os
import sys
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import STANDARD_PDFS_DIR, MODEL_DIR, OUTPUT_DIR
from extractor import StandardFeatureExtractor
from trainer import StandardModelTrainer
from predictor import StandardPredictor

def demo_feature_extraction():
    """演示特征提取"""
    print("=" * 60)
    print("演示1: 特征提取")
    print("=" * 60)
    
    extractor = StandardFeatureExtractor()
    
    # 选择一个标准文件进行演示
    pdf_files = [f for f in os.listdir(STANDARD_PDFS_DIR) if f.lower().endswith('.pdf')]
    if pdf_files:
        demo_file = os.path.join(STANDARD_PDFS_DIR, pdf_files[0])
        print(f"演示文件: {pdf_files[0]}")
        
        # 提取特征
        features = extractor.extract_pdf_features(demo_file)
        
        # 显示特征信息
        print(f"文件名特征:")
        filename_features = features["filename_features"]
        print(f"  标准类型: {filename_features['standard_type']}")
        print(f"  标准编号: {filename_features['standard_code']}")
        print(f"  年份: {filename_features['year']}")
        print(f"  电动汽车相关: {filename_features['ev_related']}")
        print(f"  标准相关: {filename_features['standard_related']}")
        
        print(f"内容特征:")
        content_features = features["content_features"]
        print(f"  文本长度: {content_features.get('text_length', 0)}")
        print(f"  标准关键词数: {content_features.get('standard_keywords_count', 0)}")
        print(f"  电动汽车关键词数: {content_features.get('ev_keywords_count', 0)}")
        print(f"  排除关键词数: {content_features.get('exclude_keywords_count', 0)}")
        
        print(f"预测结果:")
        print(f"  是否为标准文档: {features['is_standard']}")
        print(f"  置信度: {features['confidence']:.3f}")
        
        return True
    
    return False

def demo_model_prediction():
    """演示模型预测"""
    print("\n" + "=" * 60)
    print("演示2: 模型预测")
    print("=" * 60)
    
    # 创建预测器
    predictor = StandardPredictor(MODEL_DIR)
    predictor.load_model()
    
    # 选择几个文件进行演示
    pdf_files = [f for f in os.listdir(STANDARD_PDFS_DIR) if f.lower().endswith('.pdf')]
    demo_files = pdf_files[:5]  # 演示前5个文件
    
    print(f"演示文件数量: {len(demo_files)}")
    
    for i, filename in enumerate(demo_files, 1):
        file_path = os.path.join(STANDARD_PDFS_DIR, filename)
        
        try:
            is_standard, confidence, features = predictor.predict_single_file(file_path)
            
            status = "✓ 标准" if is_standard else "✗ 非标准"
            print(f"{i}. {status} {filename}")
            print(f"   置信度: {confidence:.3f}")
            
            # 显示关键特征
            filename_features = features["filename_features"]
            if filename_features["standard_type"]:
                print(f"   标准类型: {filename_features['standard_type']}")
            
        except Exception as e:
            print(f"{i}. ✗ 预测失败: {filename}")
            print(f"   错误: {e}")
    
    return True

def demo_batch_processing():
    """演示批量处理"""
    print("\n" + "=" * 60)
    print("演示3: 批量处理")
    print("=" * 60)
    
    # 创建预测器
    predictor = StandardPredictor(MODEL_DIR)
    predictor.load_model()
    
    # 创建临时目录用于演示
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"创建临时演示目录: {temp_dir}")
        
        # 复制几个文件到临时目录
        pdf_files = [f for f in os.listdir(STANDARD_PDFS_DIR) if f.lower().endswith('.pdf')]
        demo_files = pdf_files[:10]  # 演示前10个文件
        
        for file in demo_files:
            src = os.path.join(STANDARD_PDFS_DIR, file)
            dst = os.path.join(temp_dir, file)
            shutil.copy2(src, dst)
        
        print(f"复制了 {len(demo_files)} 个文件到演示目录")
        
        # 扫描文件
        pdf_paths = predictor.scan_pdf_files(temp_dir)
        print(f"扫描到 {len(pdf_paths)} 个PDF文件")
        
        # 批量预测
        results = predictor.predict_batch_files(pdf_paths)
        
        # 统计结果
        standard_count = sum(1 for r in results if r["is_standard"])
        non_standard_count = len(results) - standard_count
        
        print(f"\n批量处理结果:")
        print(f"  总文件数: {len(results)}")
        print(f"  标准文档: {standard_count}")
        print(f"  非标准文档: {non_standard_count}")
        print(f"  标准文档比例: {standard_count/len(results)*100:.1f}%")
        
        # 显示标准文档列表
        if standard_count > 0:
            print(f"\n识别出的标准文档:")
            for result in results:
                if result["is_standard"]:
                    print(f"  ✓ {result['filename']} (置信度: {result['confidence']:.3f})")
    
    return True

def demo_full_pipeline():
    """演示完整流程"""
    print("\n" + "=" * 60)
    print("演示4: 完整流程")
    print("=" * 60)
    
    print("完整流程包括以下步骤:")
    print("1. 从 pdfs/标准/ 目录提取特征")
    print("2. 训练标准文档识别模型")
    print("3. 扫描I盘并识别标准文档")
    print("4. 将标准文档复制到 I盘标准/ 目录")
    
    print(f"\n当前配置:")
    print(f"  标准文件目录: {STANDARD_PDFS_DIR}")
    print(f"  模型目录: {MODEL_DIR}")
    print(f"  输出目录: {OUTPUT_DIR}")
    
    # 检查I盘是否存在
    if os.path.exists("I:"):
        print(f"\n✓ I盘存在，可以运行完整流程")
        print("运行命令: python main.py")
    else:
        print(f"\n✗ I盘不存在，请修改目标目录")
        print("运行命令: python main.py --target <目标目录>")
    
    return True

def main():
    """主演示函数"""
    print("PDF标准文档识别系统 - 演示")
    print("=" * 60)
    
    # 检查系统状态
    print("检查系统状态...")
    
    # 检查标准目录
    if not os.path.exists(STANDARD_PDFS_DIR):
        print(f"✗ 标准目录不存在: {STANDARD_PDFS_DIR}")
        return False
    
    # 检查模型文件
    model_files = [
        os.path.join(MODEL_DIR, "standard_classifier.pkl"),
        os.path.join(MODEL_DIR, "scaler.pkl"),
        os.path.join(MODEL_DIR, "feature_names.json")
    ]
    
    model_ready = all(os.path.exists(f) for f in model_files)
    
    if model_ready:
        print("✓ 模型已训练，可以进行预测")
    else:
        print("✗ 模型未训练，请先运行: python main.py --step 1 && python main.py --step 2")
        return False
    
    # 运行演示
    demos = [
        ("特征提取", demo_feature_extraction),
        ("模型预测", demo_model_prediction),
        ("批量处理", demo_batch_processing),
        ("完整流程", demo_full_pipeline)
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"演示失败: {demo_name} - {e}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 