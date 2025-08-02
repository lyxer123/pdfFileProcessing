import os
import json
import pickle
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib

class StandardModelTrainer:
    """标准文档识别模型训练器"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_info = {}
    
    def load_features(self, features_path: str) -> List[Dict[str, Any]]:
        """加载特征数据"""
        if not os.path.exists(features_path):
            raise FileNotFoundError(f"特征文件不存在: {features_path}")
        
        with open(features_path, 'r', encoding='utf-8') as f:
            features = json.load(f)
        
        print(f"加载了 {len(features)} 个文件的特征")
        return features
    
    def extract_training_features(self, features: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """提取训练特征向量"""
        X = []
        y = []
        
        for feature in features:
            # 跳过有错误的文件
            if "error" in feature.get("content_features", {}):
                continue
            
            # 构建特征向量
            feature_vector = self._build_feature_vector(feature)
            X.append(feature_vector)
            
            # 标签：1表示标准文档，0表示非标准文档
            label = 1 if feature["is_standard"] else 0
            y.append(label)
        
        return np.array(X), np.array(y)
    
    def _build_feature_vector(self, feature: Dict[str, Any]) -> List[float]:
        """构建特征向量"""
        vector = []
        
        # 文件名特征
        filename_features = feature["filename_features"]
        
        # 标准类型编码（one-hot编码）
        std_types = ["GB", "DB", "NB", "T", "QGDW"]
        for std_type in std_types:
            vector.append(1.0 if filename_features["standard_type"] == std_type else 0.0)
        
        # 是否有标准编号
        vector.append(1.0 if filename_features["standard_code"] else 0.0)
        
        # 是否有年份
        vector.append(1.0 if filename_features["year"] else 0.0)
        
        # 是否电动汽车相关
        vector.append(1.0 if filename_features["ev_related"] else 0.0)
        
        # 是否标准相关
        vector.append(1.0 if filename_features["standard_related"] else 0.0)
        
        # 内容特征
        content_features = feature.get("content_features", {})
        
        # 文本长度（归一化）
        text_length = content_features.get("text_length", 0)
        vector.append(min(1.0, text_length / 10000))  # 归一化到0-1
        
        # 关键词计数
        std_keywords = content_features.get("standard_keywords_count", 0)
        ev_keywords = content_features.get("ev_keywords_count", 0)
        exclude_keywords = content_features.get("exclude_keywords_count", 0)
        
        vector.append(min(1.0, std_keywords / 50))  # 归一化
        vector.append(min(1.0, ev_keywords / 30))   # 归一化
        vector.append(min(1.0, exclude_keywords / 20))  # 归一化
        
        # 标准相关段落数量
        std_sections = len(content_features.get("standard_sections", []))
        vector.append(min(1.0, std_sections / 10))
        
        # 电动汽车相关段落数量
        ev_sections = len(content_features.get("ev_sections", []))
        vector.append(min(1.0, ev_sections / 10))
        
        return vector
    
    def get_feature_names(self) -> List[str]:
        """获取特征名称列表"""
        feature_names = []
        
        # 标准类型
        std_types = ["GB", "DB", "NB", "T", "QGDW"]
        for std_type in std_types:
            feature_names.append(f"std_type_{std_type}")
        
        # 其他特征
        other_features = [
            "has_standard_code", "has_year", "ev_related", "standard_related",
            "text_length_norm", "std_keywords_norm", "ev_keywords_norm", 
            "exclude_keywords_norm", "std_sections_norm", "ev_sections_norm"
        ]
        feature_names.extend(other_features)
        
        return feature_names
    
    def train_model(self, features: List[Dict[str, Any]], test_size: float = 0.2) -> Dict[str, Any]:
        """训练模型"""
        print("开始训练标准文档识别模型...")
        
        # 提取特征向量
        X, y = self.extract_training_features(features)
        
        if len(X) == 0:
            raise ValueError("没有有效的训练数据")
        
        print(f"训练数据形状: X={X.shape}, y={y.shape}")
        print(f"标准文档数量: {np.sum(y == 1)}")
        print(f"非标准文档数量: {np.sum(y == 0)}")
        
        # 保存特征名称
        self.feature_names = self.get_feature_names()
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # 训练随机森林模型
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 生成分类报告
        report = classification_report(y_test, y_pred, target_names=['非标准', '标准'])
        
        # 特征重要性
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        # 保存模型信息
        self.model_info = {
            "accuracy": accuracy,
            "classification_report": report,
            "feature_importance": feature_importance,
            "n_samples": len(X),
            "n_features": X.shape[1],
            "test_size": test_size
        }
        
        print(f"模型训练完成，准确率: {accuracy:.4f}")
        print("\n分类报告:")
        print(report)
        
        print("\n特征重要性:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:10]:
            print(f"  {feature}: {importance:.4f}")
        
        return self.model_info
    
    def save_model(self, model_dir: str):
        """保存模型"""
        os.makedirs(model_dir, exist_ok=True)
        
        # 保存模型
        model_path = os.path.join(model_dir, "standard_classifier.pkl")
        joblib.dump(self.model, model_path)
        
        # 保存标准化器
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        # 保存特征名称
        feature_names_path = os.path.join(model_dir, "feature_names.json")
        with open(feature_names_path, 'w', encoding='utf-8') as f:
            json.dump(self.feature_names, f, ensure_ascii=False, indent=2)
        
        # 保存模型信息
        model_info_path = os.path.join(model_dir, "model_info.json")
        with open(model_info_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_info, f, ensure_ascii=False, indent=2)
        
        print(f"模型已保存到: {model_dir}")
        print(f"  - 模型文件: {model_path}")
        print(f"  - 标准化器: {scaler_path}")
        print(f"  - 特征名称: {feature_names_path}")
        print(f"  - 模型信息: {model_info_path}")
    
    def load_model(self, model_dir: str):
        """加载模型"""
        # 加载模型
        model_path = os.path.join(model_dir, "standard_classifier.pkl")
        self.model = joblib.load(model_path)
        
        # 加载标准化器
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        self.scaler = joblib.load(scaler_path)
        
        # 加载特征名称
        feature_names_path = os.path.join(model_dir, "feature_names.json")
        with open(feature_names_path, 'r', encoding='utf-8') as f:
            self.feature_names = json.load(f)
        
        # 加载模型信息
        model_info_path = os.path.join(model_dir, "model_info.json")
        with open(model_info_path, 'r', encoding='utf-8') as f:
            self.model_info = json.load(f)
        
        print(f"模型已从 {model_dir} 加载")
    
    def predict(self, feature: Dict[str, Any]) -> Tuple[int, float]:
        """预测单个文件"""
        if self.model is None:
            raise ValueError("模型未加载，请先调用 load_model()")
        
        # 构建特征向量
        feature_vector = self._build_feature_vector(feature)
        X = np.array([feature_vector])
        
        # 标准化
        X_scaled = self.scaler.transform(X)
        
        # 预测
        prediction = self.model.predict(X_scaled)[0]
        probability = self.model.predict_proba(X_scaled)[0]
        
        return prediction, probability[1]  # 返回标准文档的概率
