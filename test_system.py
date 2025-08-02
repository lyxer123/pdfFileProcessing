#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
用于验证PDF标准文档识别系统的各个组件是否正常工作
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import STANDARD_PDFS_DIR, MODEL_DIR, OUTPUT_DIR
from extractor import StandardFeatureExtractor
from trainer import StandardModelTrainer
from predictor import StandardPredictor

def test_dependencies():
    """测试依赖包"""
    print("测试依赖包...")
    
    required_packages = [
        'pdfplumber', 'sklearn', 'numpy', 'joblib', 'tqdm'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 未安装")
            return False
    
    return True

def test_config():
    """测试配置文件"""
    print("\n测试配置文件...")
    
    # 检查必要的目录是否存在
    if not os.path.exists(STANDARD_PDFS_DIR):
        print(f"✗ 标准目录不存在: {STANDARD_PDFS_DIR}")
        return False
    
    print(f"✓ 标准目录: {STANDARD_PDFS_DIR}")
    
    # 检查标准文件数量
    pdf_files = [f for f in os.listdir(STANDARD_PDFS_DIR) if f.lower().endswith('.pdf')]
    print(f"✓ 找到 {len(pdf_files)} 个标准PDF文件")
    
    if len(pdf_files) == 0:
        print("✗ 没有找到标准PDF文件")
        return False
    
    return True

def test_extractor():
    """测试特征提取器"""
    print("\n测试特征提取器...")
    
    try:
        extractor = StandardFeatureExtractor()
        print("✓ 特征提取器创建成功")
        
        # 测试单个文件特征提取
        pdf_files = [f for f in os.listdir(STANDARD_PDFS_DIR) if f.lower().endswith('.pdf')]
        if pdf_files:
            test_file = os.path.join(STANDARD_PDFS_DIR, pdf_files[0])
            features = extractor.extract_pdf_features(test_file)
            
            if features and "is_standard" in features:
                print(f"✓ 特征提取成功: {pdf_files[0]}")
                print(f"  标准文档: {features['is_standard']}")
                print(f"  置信度: {features['confidence']:.3f}")
            else:
                print("✗ 特征提取失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 特征提取器测试失败: {e}")
        return False

def test_trainer():
    """测试模型训练器"""
    print("\n测试模型训练器...")
    
    try:
        trainer = StandardModelTrainer()
        print("✓ 模型训练器创建成功")
        
        # 检查特征文件是否存在
        features_path = os.path.join(MODEL_DIR, "standard_features.json")
        if not os.path.exists(features_path):
            print("✗ 特征文件不存在，请先运行特征提取")
            return False
        
        # 加载特征
        features = trainer.load_features(features_path)
        print(f"✓ 加载了 {len(features)} 个特征")
        
        # 测试特征向量构建
        if features:
            feature_vector = trainer._build_feature_vector(features[0])
            print(f"✓ 特征向量构建成功，维度: {len(feature_vector)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型训练器测试失败: {e}")
        return False

def test_predictor():
    """测试预测器"""
    print("\n测试预测器...")
    
    try:
        predictor = StandardPredictor(MODEL_DIR)
        print("✓ 预测器创建成功")
        
        # 检查模型文件是否存在
        model_files = [
            os.path.join(MODEL_DIR, "standard_classifier.pkl"),
            os.path.join(MODEL_DIR, "scaler.pkl"),
            os.path.join(MODEL_DIR, "feature_names.json")
        ]
        
        for model_file in model_files:
            if not os.path.exists(model_file):
                print(f"✗ 模型文件不存在: {model_file}")
                return False
        
        print("✓ 所有模型文件存在")
        
        # 测试模型加载
        predictor.load_model()
        print("✓ 模型加载成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 预测器测试失败: {e}")
        return False

def test_full_pipeline():
    """测试完整流程"""
    print("\n测试完整流程...")
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")
        
        # 复制几个标准文件到临时目录
        pdf_files = [f for f in os.listdir(STANDARD_PDFS_DIR) if f.lower().endswith('.pdf')]
        test_files = pdf_files[:3]  # 只测试前3个文件
        
        for file in test_files:
            src = os.path.join(STANDARD_PDFS_DIR, file)
            dst = os.path.join(temp_dir, file)
            shutil.copy2(src, dst)
        
        print(f"复制了 {len(test_files)} 个测试文件")
        
        # 测试预测
        try:
            predictor = StandardPredictor(MODEL_DIR)
            predictor.load_model()
            
            # 扫描测试文件
            test_pdf_files = [os.path.join(temp_dir, f) for f in test_files]
            
            # 预测单个文件
            if test_pdf_files:
                is_standard, confidence, features = predictor.predict_single_file(test_pdf_files[0])
                print(f"✓ 单文件预测成功: {test_files[0]}")
                print(f"  标准文档: {is_standard}")
                print(f"  置信度: {confidence:.3f}")
            
            return True
            
        except Exception as e:
            print(f"✗ 完整流程测试失败: {e}")
            return False

def main():
    """主测试函数"""
    print("PDF标准文档识别系统 - 测试脚本")
    print("=" * 50)
    
    tests = [
        ("依赖包", test_dependencies),
        ("配置文件", test_config),
        ("特征提取器", test_extractor),
        ("模型训练器", test_trainer),
        ("预测器", test_predictor),
        ("完整流程", test_full_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用。")
        return True
    else:
        print("❌ 部分测试失败，请检查系统配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 