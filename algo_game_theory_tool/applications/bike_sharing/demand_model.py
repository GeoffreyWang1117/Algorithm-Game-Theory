"""
共享单车需求预测模型

功能：
1. 时空特征工程
2. XGBoost/RandomForest/LSTM模型训练
3. 需求预测和评估
4. 模型持久化
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import pickle
import json

from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor

import matplotlib.pyplot as plt
import seaborn as sns


class FeatureEngineer:
    """时空特征工程"""

    def __init__(self, config):
        self.config = config

    def add_temporal_features(self, df):
        """
        添加时间特征

        参数:
            df: DataFrame with 'timestamp' column

        返回:
            DataFrame with temporal features
        """
        df = df.copy()

        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['day_of_month'] = df['timestamp'].dt.day
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

        # 高峰时段
        df['is_morning_rush'] = df['hour'].between(7, 9).astype(int)
        df['is_evening_rush'] = df['hour'].between(17, 20).astype(int)
        df['is_rush_hour'] = (df['is_morning_rush'] | df['is_evening_rush']).astype(int)

        # 周期性编码（避免小时23和0的距离问题）
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

        return df

    def add_lag_features(self, df, target='net_flow', lags=None):
        """
        添加滞后特征

        参数:
            df: DataFrame (must be sorted by timestamp within each station)
            target: Target column name
            lags: List of lag periods (hours)

        返回:
            DataFrame with lag features
        """
        if lags is None:
            lags = self.config['features']['lags']

        df = df.copy()

        for lag in lags:
            df[f'{target}_lag_{lag}h'] = df.groupby('station_id')[target].shift(lag)

        return df

    def add_rolling_features(self, df, target='net_flow', windows=None):
        """
        添加滚动统计特征

        参数:
            df: DataFrame
            target: Target column
            windows: List of window sizes (hours)

        返回:
            DataFrame with rolling features
        """
        if windows is None:
            windows = self.config['features']['rolling']['windows']

        df = df.copy()

        for window in windows:
            # 滚动均值
            df[f'{target}_rolling_mean_{window}h'] = (
                df.groupby('station_id')[target]
                .rolling(window=window, min_periods=1)
                .mean()
                .reset_index(0, drop=True)
            )

            # 滚动标准差
            df[f'{target}_rolling_std_{window}h'] = (
                df.groupby('station_id')[target]
                .rolling(window=window, min_periods=1)
                .std()
                .reset_index(0, drop=True)
            )

        return df

    def add_station_features(self, df, metadata):
        """
        添加站点特征

        参数:
            df: Time series DataFrame
            metadata: Station metadata DataFrame

        返回:
            DataFrame with station features
        """
        df = df.copy()

        # 合并站点元数据
        station_features = metadata[['station_id', 'capacity', 'lat', 'lng']]
        df = df.merge(station_features, on='station_id', how='left')

        # 计算平均利用率（需要历史数据）
        if 'arrivals' in df.columns and 'departures' in df.columns:
            # 估计当前单车数（简化）
            df['estimated_bikes'] = df.groupby('station_id')['net_flow'].cumsum()
            df['estimated_bikes'] = df['estimated_bikes'].clip(lower=0, upper=df['capacity'])
            df['utilization'] = df['estimated_bikes'] / df['capacity']
        else:
            df['utilization'] = 0.5  # 默认值

        return df

    def create_features(self, df, metadata):
        """
        创建所有特征

        参数:
            df: Raw timeseries data
            metadata: Station metadata

        返回:
            DataFrame with all features
        """
        print("特征工程...")

        # 1. 时间特征
        df = self.add_temporal_features(df)
        print(f"  ✓ 时间特征")

        # 2. 滞后特征
        df = self.add_lag_features(df)
        print(f"  ✓ 滞后特征")

        # 3. 滚动特征
        df = self.add_rolling_features(df)
        print(f"  ✓ 滚动特征")

        # 4. 站点特征
        df = self.add_station_features(df, metadata)
        print(f"  ✓ 站点特征")

        # 5. 删除初始的NaN（由于lag和rolling）
        initial_rows = len(df)
        df = df.dropna()
        print(f"  ✓ 删除NaN: {initial_rows - len(df)} 行")

        return df


class DemandPredictor:
    """需求预测模型"""

    def __init__(self, config_path='configs/model_config.yaml'):
        """初始化预测器"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.target_column = self.config['model']['target']

    def prepare_data(self, df):
        """
        准备训练数据

        参数:
            df: DataFrame with features

        返回:
            tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        print("\n准备训练数据...")

        # 选择特征列（排除元数据列）
        exclude_cols = ['timestamp', 'station_id', 'arrivals', 'departures',
                       'net_flow', 'station_name']

        self.feature_columns = [col for col in df.columns if col not in exclude_cols]

        X = df[self.feature_columns]
        y = df[self.target_column]

        print(f"  特征数量: {len(self.feature_columns)}")
        print(f"  样本数量: {len(X)}")

        # 时间序列分割（避免数据泄露）
        train_ratio = self.config['model']['train_ratio']
        val_ratio = self.config['model']['val_ratio']

        n = len(X)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        X_train = X.iloc[:train_end]
        X_val = X.iloc[train_end:val_end]
        X_test = X.iloc[val_end:]

        y_train = y.iloc[:train_end]
        y_val = y.iloc[train_end:val_end]
        y_test = y.iloc[val_end:]

        print(f"  训练集: {len(X_train)} ({len(X_train)/n*100:.1f}%)")
        print(f"  验证集: {len(X_val)} ({len(X_val)/n*100:.1f}%)")
        print(f"  测试集: {len(X_test)} ({len(X_test)/n*100:.1f}%)")

        return X_train, X_val, X_test, y_train, y_val, y_test

    def train_xgboost(self, X_train, y_train, X_val, y_val):
        """
        训练XGBoost模型

        参数:
            X_train, y_train: 训练数据
            X_val, y_val: 验证数据

        返回:
            Trained model
        """
        print("\n训练XGBoost模型...")

        params = self.config['xgboost']

        model = xgb.XGBRegressor(
            objective=params['objective'],
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            learning_rate=params['learning_rate'],
            subsample=params['subsample'],
            colsample_bytree=params['colsample_bytree'],
            min_child_weight=params['min_child_weight'],
            gamma=params['gamma'],
            reg_alpha=params['reg_alpha'],
            reg_lambda=params['reg_lambda'],
            random_state=42,
            n_jobs=-1
        )

        model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_val, y_val)],
            eval_metric=params['eval_metric'],
            early_stopping_rounds=params['early_stopping_rounds'],
            verbose=50
        )

        print(f"  ✓ 最佳迭代: {model.best_iteration}")

        return model

    def train_random_forest(self, X_train, y_train):
        """训练随机森林模型"""
        print("\n训练Random Forest模型...")

        params = self.config['random_forest']

        model = RandomForestRegressor(
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            min_samples_split=params['min_samples_split'],
            min_samples_leaf=params['min_samples_leaf'],
            max_features=params['max_features'],
            n_jobs=params['n_jobs'],
            random_state=42
        )

        model.fit(X_train, y_train)

        return model

    def evaluate(self, model, X, y, dataset_name='Test'):
        """
        评估模型性能

        参数:
            model: Trained model
            X, y: Evaluation data
            dataset_name: Dataset name for display

        返回:
            dict: Evaluation metrics
        """
        y_pred = model.predict(X)

        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        r2 = r2_score(y, y_pred)

        print(f"\n{dataset_name} 集性能:")
        print(f"  MAE:  {mae:.3f} bikes/hour")
        print(f"  RMSE: {rmse:.3f} bikes/hour")
        print(f"  R²:   {r2:.3f}")

        # 检查性能阈值
        thresholds = self.config['performance_thresholds']
        passed = True

        if mae > thresholds['max_mae']:
            print(f"  ⚠ MAE 超过阈值 {thresholds['max_mae']}")
            passed = False

        if rmse > thresholds['max_rmse']:
            print(f"  ⚠ RMSE 超过阈值 {thresholds['max_rmse']}")
            passed = False

        if r2 < thresholds['min_r2']:
            print(f"  ⚠ R² 低于阈值 {thresholds['min_r2']}")
            passed = False

        if passed:
            print(f"  ✓ 所有指标通过阈值")

        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'passed': passed
        }

    def plot_feature_importance(self, model, top_k=20):
        """绘制特征重要性"""
        if not hasattr(model, 'feature_importances_'):
            print("模型不支持特征重要性分析")
            return

        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance.head(top_k), x='importance', y='feature')
        plt.title(f'Top {top_k} Feature Importance')
        plt.xlabel('Importance')
        plt.tight_layout()

        output_dir = Path('outputs/figures')
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / 'feature_importance.png', dpi=150)
        print(f"\n  ✓ 特征重要性图保存至: outputs/figures/feature_importance.png")

    def save_model(self, model, metrics):
        """保存模型和元数据"""
        output_dir = Path(self.config['model_persistence']['save_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存模型
        model_path = output_dir / 'demand_predictor.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'target_column': self.target_column,
                'config': self.config
            }, f)

        print(f"\n  ✓ 模型保存至: {model_path}")

        # 保存评估指标
        metrics_path = output_dir / 'model_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"  ✓ 指标保存至: {metrics_path}")

    @classmethod
    def load_model(cls, model_path='models/demand_predictor.pkl'):
        """加载保存的模型"""
        with open(model_path, 'rb') as f:
            data = pickle.load(f)

        predictor = cls.__new__(cls)
        predictor.model = data['model']
        predictor.scaler = data['scaler']
        predictor.feature_columns = data['feature_columns']
        predictor.target_column = data['target_column']
        predictor.config = data['config']

        return predictor

    def predict(self, X):
        """预测"""
        if self.model is None:
            raise ValueError("模型未训练或加载")

        return self.model.predict(X)


def main():
    """主函数：训练需求预测模型"""
    print("=" * 70)
    print("Citi Bike 需求预测模型训练")
    print("=" * 70)

    # 1. 加载数据
    print("\n加载数据...")
    data_dir = Path('data/processed')

    timeseries = pd.read_csv(data_dir / 'station_timeseries.csv')
    timeseries['timestamp'] = pd.to_datetime(timeseries['timestamp'])

    metadata = pd.read_csv(data_dir / 'station_metadata.csv')

    print(f"  ✓ 时序数据: {len(timeseries):,} 条记录")
    print(f"  ✓ 站点元数据: {len(metadata)} 个站点")

    # 2. 特征工程
    with open('configs/data_config.yaml', 'r') as f:
        data_config = yaml.safe_load(f)

    fe = FeatureEngineer(data_config)
    features_df = fe.create_features(timeseries, metadata)

    print(f"\n  ✓ 特征矩阵: {features_df.shape}")

    # 3. 训练模型
    predictor = DemandPredictor()

    X_train, X_val, X_test, y_train, y_val, y_test = predictor.prepare_data(features_df)

    # 选择模型类型
    model_type = predictor.config['model']['type']

    if model_type == 'xgboost':
        model = predictor.train_xgboost(X_train, y_train, X_val, y_val)
    elif model_type == 'random_forest':
        model = predictor.train_random_forest(X_train, y_train)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

    predictor.model = model

    # 4. 评估模型
    train_metrics = predictor.evaluate(model, X_train, y_train, 'Train')
    val_metrics = predictor.evaluate(model, X_val, y_val, 'Validation')
    test_metrics = predictor.evaluate(model, X_test, y_test, 'Test')

    # 5. 特征重要性
    predictor.plot_feature_importance(model)

    # 6. 保存模型
    all_metrics = {
        'train': train_metrics,
        'validation': val_metrics,
        'test': test_metrics,
        'timestamp': datetime.now().isoformat()
    }

    predictor.save_model(model, all_metrics)

    print("\n" + "=" * 70)
    print("✓ 模型训练完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
