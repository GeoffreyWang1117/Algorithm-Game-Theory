"""
Citi Bike 数据下载和处理管道

功能：
1. 从Citi Bike S3自动下载数据
2. 数据清洗和预处理
3. 特征工程
4. 生成训练就绪的数据集
"""

import os
import sys
import argparse
import yaml
from datetime import datetime, timedelta
from pathlib import Path
import requests
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
import numpy as np
from tqdm import tqdm


class CitiBikeDataPipeline:
    """Citi Bike 数据管道"""

    def __init__(self, config_path='configs/data_config.yaml'):
        """初始化数据管道"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.raw_dir = Path(self.config['download']['raw_dir'])
        self.processed_dir = Path(self.config['download']['processed_dir'])

        # 创建目录
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def download_data(self, year, month):
        """
        下载指定月份的数据

        参数:
            year: 年份 (2020-2024)
            month: 月份 (1-12)

        返回:
            Path: 下载文件的路径
        """
        # 构建URL
        base_url = self.config['data_source']['base_url']
        file_pattern = self.config['data_source']['file_pattern']
        filename = file_pattern.format(year=year, month=month)

        url = base_url + filename
        output_path = self.raw_dir / filename

        # 如果文件已存在，跳过
        csv_path = output_path.with_suffix('').with_suffix('.csv')
        if csv_path.exists():
            print(f"✓ 文件已存在: {csv_path.name}")
            return csv_path

        print(f"下载: {filename}")

        try:
            # 下载文件
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            # 使用进度条下载
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                content = BytesIO()
                for chunk in response.iter_content(chunk_size=8192):
                    content.write(chunk)
                    pbar.update(len(chunk))

            # 解压ZIP文件
            if self.config['download']['auto_extract']:
                print(f"解压: {filename}")
                with ZipFile(content) as zf:
                    # 找到CSV文件
                    csv_filename = [name for name in zf.namelist() if name.endswith('.csv')][0]
                    zf.extract(csv_filename, self.raw_dir)

                    csv_path = self.raw_dir / csv_filename

                print(f"✓ 下载完成: {csv_path.name}")
                return csv_path

        except requests.HTTPError as e:
            print(f"✗ 下载失败 ({e.response.status_code}): {filename}")
            return None
        except Exception as e:
            print(f"✗ 错误: {e}")
            return None

    def download_recent_months(self, num_months=3):
        """
        下载最近几个月的数据

        参数:
            num_months: 下载月份数

        返回:
            list: 下载的文件路径列表
        """
        downloaded_files = []
        current_date = datetime.now()

        print(f"\n开始下载最近 {num_months} 个月的数据...\n")

        for i in range(num_months):
            # 计算目标月份（从上个月开始，因为当月数据可能不完整）
            target_date = current_date - timedelta(days=30 * (i + 1))
            year = target_date.year
            month = target_date.month

            file_path = self.download_data(year, month)
            if file_path:
                downloaded_files.append(file_path)

        print(f"\n✓ 成功下载 {len(downloaded_files)} 个文件")
        return downloaded_files

    def clean_data(self, df):
        """
        数据清洗

        参数:
            df: 原始数据DataFrame

        返回:
            DataFrame: 清洗后的数据
        """
        print("数据清洗中...")

        initial_rows = len(df)

        # 1. 删除缺失值
        df = df.dropna(subset=['start_station_id', 'end_station_id',
                               'started_at', 'ended_at'])

        # 2. 转换时间列
        df['started_at'] = pd.to_datetime(df['started_at'])
        df['ended_at'] = pd.to_datetime(df['ended_at'])

        # 3. 计算骑行时长（秒）
        df['duration'] = (df['ended_at'] - df['started_at']).dt.total_seconds()

        # 4. 过滤异常骑行
        min_duration = self.config['preprocessing']['min_trip_duration']
        max_duration = self.config['preprocessing']['max_trip_duration']

        df = df[(df['duration'] >= min_duration) & (df['duration'] <= max_duration)]

        # 5. 过滤异常坐标（纽约市范围）
        nyc_bounds = {
            'lat_min': 40.5, 'lat_max': 40.9,
            'lng_min': -74.1, 'lng_max': -73.7
        }

        df = df[
            (df['start_lat'] >= nyc_bounds['lat_min']) &
            (df['start_lat'] <= nyc_bounds['lat_max']) &
            (df['start_lng'] >= nyc_bounds['lng_min']) &
            (df['start_lng'] <= nyc_bounds['lng_max']) &
            (df['end_lat'] >= nyc_bounds['lat_min']) &
            (df['end_lat'] <= nyc_bounds['lat_max']) &
            (df['end_lng'] >= nyc_bounds['lng_min']) &
            (df['end_lng'] <= nyc_bounds['lng_max'])
        ]

        final_rows = len(df)
        removed_ratio = (initial_rows - final_rows) / initial_rows * 100

        print(f"  原始记录: {initial_rows:,}")
        print(f"  清洗后: {final_rows:,}")
        print(f"  移除: {removed_ratio:.1f}%")

        return df

    def aggregate_station_data(self, df, freq='1H'):
        """
        聚合站点级别数据

        参数:
            df: 清洗后的数据
            freq: 时间聚合频率（默认1小时）

        返回:
            DataFrame: 聚合后的站点时序数据
        """
        print(f"聚合站点数据（频率: {freq}）...")

        # 计算到达（arrivals）
        arrivals = df.groupby([
            pd.Grouper(key='ended_at', freq=freq),
            'end_station_id'
        ]).size().reset_index(name='arrivals')

        arrivals.rename(columns={
            'ended_at': 'timestamp',
            'end_station_id': 'station_id'
        }, inplace=True)

        # 计算出发（departures）
        departures = df.groupby([
            pd.Grouper(key='started_at', freq=freq),
            'start_station_id'
        ]).size().reset_index(name='departures')

        departures.rename(columns={
            'started_at': 'timestamp',
            'start_station_id': 'station_id'
        }, inplace=True)

        # 合并
        station_ts = pd.merge(
            arrivals, departures,
            on=['timestamp', 'station_id'],
            how='outer'
        ).fillna(0)

        # 计算净流量
        station_ts['net_flow'] = station_ts['arrivals'] - station_ts['departures']

        # 排序
        station_ts = station_ts.sort_values(['station_id', 'timestamp'])

        print(f"  生成时序记录: {len(station_ts):,}")
        print(f"  覆盖站点数: {station_ts['station_id'].nunique()}")
        print(f"  时间范围: {station_ts['timestamp'].min()} 至 {station_ts['timestamp'].max()}")

        return station_ts

    def compute_station_metadata(self, df):
        """
        计算站点元数据

        参数:
            df: 清洗后的数据

        返回:
            DataFrame: 站点元数据
        """
        print("计算站点元数据...")

        # 合并起点和终点站信息
        start_stations = df[['start_station_id', 'start_station_name',
                             'start_lat', 'start_lng']].copy()
        start_stations.columns = ['station_id', 'station_name', 'lat', 'lng']

        end_stations = df[['end_station_id', 'end_station_name',
                           'end_lat', 'end_lng']].copy()
        end_stations.columns = ['station_id', 'station_name', 'lat', 'lng']

        all_stations = pd.concat([start_stations, end_stations])

        # 去重，取最常见的名称和平均坐标
        metadata = all_stations.groupby('station_id').agg({
            'station_name': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
            'lat': 'mean',
            'lng': 'mean'
        }).reset_index()

        # 计算每个站点的总骑行次数
        start_counts = df['start_station_id'].value_counts()
        end_counts = df['end_station_id'].value_counts()
        total_counts = start_counts.add(end_counts, fill_value=0)

        metadata['total_trips'] = metadata['station_id'].map(total_counts).fillna(0)

        # 过滤低频站点
        min_trips = self.config['preprocessing']['min_station_trips']
        metadata = metadata[metadata['total_trips'] >= min_trips]

        # 默认容量
        metadata['capacity'] = self.config['station_metadata']['default_capacity']

        print(f"  有效站点数: {len(metadata)}")

        return metadata

    def process_file(self, file_path):
        """
        处理单个文件

        参数:
            file_path: CSV文件路径

        返回:
            tuple: (station_timeseries, station_metadata)
        """
        print(f"\n处理文件: {file_path.name}")

        # 读取数据
        print("读取数据...")
        df = pd.read_csv(file_path)
        print(f"  读取记录: {len(df):,}")

        # 清洗数据
        df = self.clean_data(df)

        # 聚合站点数据
        station_ts = self.aggregate_station_data(df)

        # 计算站点元数据
        metadata = self.compute_station_metadata(df)

        return station_ts, metadata

    def process_all_files(self, file_paths):
        """
        处理所有下载的文件

        参数:
            file_paths: 文件路径列表

        返回:
            tuple: (combined_timeseries, combined_metadata)
        """
        all_timeseries = []
        all_metadata = []

        for file_path in file_paths:
            ts, meta = self.process_file(file_path)
            all_timeseries.append(ts)
            all_metadata.append(meta)

        # 合并所有时序数据
        print("\n合并所有时序数据...")
        combined_ts = pd.concat(all_timeseries, ignore_index=True)
        combined_ts = combined_ts.sort_values(['station_id', 'timestamp'])

        # 合并站点元数据（取最新的）
        print("合并站点元数据...")
        combined_meta = pd.concat(all_metadata, ignore_index=True)
        combined_meta = combined_meta.groupby('station_id').last().reset_index()

        print(f"\n总计:")
        print(f"  时序记录: {len(combined_ts):,}")
        print(f"  站点数: {len(combined_meta)}")

        return combined_ts, combined_meta

    def save_processed_data(self, timeseries, metadata):
        """
        保存处理后的数据

        参数:
            timeseries: 时序数据
            metadata: 站点元数据
        """
        print("\n保存处理后的数据...")

        # 保存时序数据
        ts_path = self.processed_dir / 'station_timeseries.csv'
        timeseries.to_csv(ts_path, index=False)
        print(f"  ✓ 时序数据: {ts_path}")

        # 保存元数据
        meta_path = self.processed_dir / 'station_metadata.csv'
        metadata.to_csv(meta_path, index=False)
        print(f"  ✓ 站点元数据: {meta_path}")

        # 保存统计信息
        stats = {
            'total_records': len(timeseries),
            'num_stations': len(metadata),
            'date_range': {
                'start': str(timeseries['timestamp'].min()),
                'end': str(timeseries['timestamp'].max())
            },
            'stations': metadata['station_id'].tolist()
        }

        import json
        stats_path = self.processed_dir / 'data_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"  ✓ 统计信息: {stats_path}")

    def run(self, num_months=3):
        """
        运行完整的数据管道

        参数:
            num_months: 下载月份数
        """
        print("=" * 70)
        print("Citi Bike 数据管道")
        print("=" * 70)

        # 1. 下载数据
        file_paths = self.download_recent_months(num_months)

        if not file_paths:
            print("\n✗ 没有可处理的文件")
            return

        # 2. 处理数据
        timeseries, metadata = self.process_all_files(file_paths)

        # 3. 保存数据
        self.save_processed_data(timeseries, metadata)

        print("\n" + "=" * 70)
        print("✓ 数据管道完成！")
        print("=" * 70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Citi Bike 数据下载和处理')

    parser.add_argument(
        '--months',
        type=int,
        default=3,
        help='下载最近几个月的数据（默认3）'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='configs/data_config.yaml',
        help='配置文件路径'
    )

    args = parser.parse_args()

    # 运行管道
    pipeline = CitiBikeDataPipeline(config_path=args.config)
    pipeline.run(num_months=args.months)


if __name__ == '__main__':
    main()
