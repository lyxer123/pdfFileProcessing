#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF标准文档识别系统
基于pdfs/标准文件夹下的标准文件，提取特征并建立模型，
然后验证I盘下所有PDF文件，将满足标准特征的PDF文件拷贝到"I盘标准"文件夹
"""

import os
import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import STANDARD_PDFS_DIR, MODEL_DIR, OUTPUT_DIR
from extractor import StandardFeatureExtractor
from trainer import StandardModelTrainer
from predictor import StandardPredictor

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'pdfplumber', 'sklearn', 'numpy', 'joblib', 'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def step1_extract_features():
    """步骤1: 提取标准文件特征"""
    print("=" * 60)
    print("步骤1: 提取标准文件特征")
    print("=" * 60)
    
    if not os.path.exists(STANDARD_PDFS_DIR):
        print(f"错误: 标准文件目录不存在: {STANDARD_PDFS_DIR}")
        return False
    
    # 创建特征提取器
    extractor = StandardFeatureExtractor()
    
    # 提取所有标准文件的特征
    features = extractor.extract_all_standards(STANDARD_PDFS_DIR)
    
    if not features:
        print("错误: 没有提取到任何特征")
        return False
    
    # 保存特征到model目录
    features_path = os.path.join(MODEL_DIR, "standard_features.json")
    extractor.save_features(features, features_path)
    
    return True

def step2_train_model():
    """步骤2: 训练模型"""
    print("=" * 60)
    print("步骤2: 训练标准文档识别模型")
    print("=" * 60)
    
    features_path = os.path.join(MODEL_DIR, "standard_features.json")
    if not os.path.exists(features_path):
        print(f"错误: 特征文件不存在: {features_path}")
        print("请先运行步骤1提取特征")
        return False
    
    # 创建模型训练器
    trainer = StandardModelTrainer()
    
    # 加载特征
    features = trainer.load_features(features_path)
    
    # 训练模型
    model_info = trainer.train_model(features)
    
    # 保存模型
    trainer.save_model(MODEL_DIR)
    
    return True

def step3_predict_and_copy(target_dir: str = "I:"):
    """步骤3: 预测并复制标准文档"""
    print("=" * 60)
    print("步骤3: 预测并复制标准文档")
    print("=" * 60)
    
    # 检查模型是否存在
    model_files = [
        os.path.join(MODEL_DIR, "standard_classifier.pkl"),
        os.path.join(MODEL_DIR, "scaler.pkl"),
        os.path.join(MODEL_DIR, "feature_names.json")
    ]
    
    for model_file in model_files:
        if not os.path.exists(model_file):
            print(f"错误: 模型文件不存在: {model_file}")
            print("请先运行步骤1和步骤2训练模型")
            return False
    
    # 检查目标目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误: 目标目录不存在: {target_dir}")
        return False
    
    # 创建预测器
    predictor = StandardPredictor(MODEL_DIR)
    
    # 加载模型
    predictor.load_model()
    
    # 预测并复制标准文档
    results = predictor.predict_and_copy(target_dir, OUTPUT_DIR)
    
    return True

def run_full_pipeline(target_dir: str = "I:"):
    """运行完整的处理流程"""
    print("PDF标准文档识别系统")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 创建必要的目录
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 步骤1: 提取特征
    if not step1_extract_features():
        return False
    
    # 步骤2: 训练模型
    if not step2_train_model():
        return False
    
    # 步骤3: 预测并复制
    if not step3_predict_and_copy(target_dir):
        return False
    
    print("=" * 60)
    print("处理完成!")
    print(f"标准文档已复制到: {OUTPUT_DIR}")
    print("=" * 60)
    
    return True

def main():
    """主函数"""
    global OUTPUT_DIR
    
    parser = argparse.ArgumentParser(description="PDF标准文档识别系统")
    parser.add_argument("--target", "-t", default="I:", 
                       help="目标目录路径 (默认: I:)")
    parser.add_argument("--step", "-s", type=int, choices=[1, 2, 3],
                       help="运行指定步骤 (1: 提取特征, 2: 训练模型, 3: 预测复制)")
    parser.add_argument("--output", "-o", default=OUTPUT_DIR,
                       help=f"输出目录 (默认: {OUTPUT_DIR})")
    
    args = parser.parse_args()
    
    # 更新输出目录
    OUTPUT_DIR = args.output
    
    if args.step:
        # 运行指定步骤
        if args.step == 1:
            success = step1_extract_features()
        elif args.step == 2:
            success = step2_train_model()
        elif args.step == 3:
            success = step3_predict_and_copy(args.target)
    else:
        # 运行完整流程
        success = run_full_pipeline(args.target)
    
    if success:
        print("处理成功完成!")
        sys.exit(0)
    else:
        print("处理失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 