#!/usr/bin/env python3
"""
Algorithm Game Theory Learning Tool
类似 Rustlings 的算法博弈论学习工具

基于 Tim Roughgarden 教授的《算法博弈论二十讲》
"""

import argparse
import json
import os
import sys
from pathlib import Path
from exercise_runner import ExerciseRunner, Color

EXERCISES_DIR = Path(__file__).parent / "exercises"
PROGRESS_FILE = Path(__file__).parent / "progress.json"


class AlgoGameTheoryTool:
    def __init__(self):
        self.exercises = self._load_exercises()
        self.progress = self._load_progress()
        self.runner = ExerciseRunner()

    def _load_exercises(self):
        """加载所有练习题"""
        exercises = []
        for category_dir in sorted(EXERCISES_DIR.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith('__'):
                for exercise_file in sorted(category_dir.glob("*.py")):
                    if not exercise_file.name.startswith('__'):
                        exercises.append({
                            'category': category_dir.name,
                            'name': exercise_file.stem,
                            'path': exercise_file,
                            'full_name': f"{category_dir.name}/{exercise_file.stem}"
                        })
        return exercises

    def _load_progress(self):
        """加载学习进度"""
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_progress(self):
        """保存学习进度"""
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def list_exercises(self):
        """列出所有练习题"""
        print(f"\n{Color.BOLD}{Color.CYAN}算法博弈论练习题列表{Color.END}\n")
        print(f"基于 Tim Roughgarden 教授的《算法博弈论二十讲》\n")

        current_category = None
        for i, ex in enumerate(self.exercises, 1):
            if ex['category'] != current_category:
                current_category = ex['category']
                category_name = self._get_category_name(current_category)
                print(f"\n{Color.BOLD}{Color.YELLOW}{category_name}{Color.END}")

            status = self.progress.get(ex['full_name'], {}).get('status', 'pending')
            status_symbol = "✓" if status == "completed" else "○"
            status_color = Color.GREEN if status == "completed" else Color.WHITE

            print(f"  {status_color}{status_symbol}{Color.END} {i:2d}. {ex['name']}")

        completed = sum(1 for ex in self.exercises
                       if self.progress.get(ex['full_name'], {}).get('status') == 'completed')
        total = len(self.exercises)
        progress_pct = (completed / total * 100) if total > 0 else 0

        print(f"\n{Color.BOLD}进度: {completed}/{total} ({progress_pct:.1f}%){Color.END}\n")

    def _get_category_name(self, category):
        """获取类别的中文名称"""
        category_names = {
            '01_intro': '第一章：基础概念',
            '02_nash_equilibrium': '第二章：纳什均衡',
            '03_mixed_strategies': '第三章：混合策略',
            '04_auctions': '第四章：拍卖理论',
            '05_mechanism_design': '第五章：机制设计',
            '06_efficiency': '第六章：效率与社会福利',
            '07_cooperative_games': '第七章：协同博弈',
            '08_matching': '第八章：匹配理论',
            '09_potential_games': '第九章：势博弈',
            '10_network_games': '第十章：网络博弈',
            '11_voting': '第十一章：投票理论'
        }
        return category_names.get(category, category)

    def run_exercise(self, exercise_name):
        """运行指定的练习题"""
        exercise = None

        # 支持通过序号或名称查找练习
        if exercise_name.isdigit():
            idx = int(exercise_name) - 1
            if 0 <= idx < len(self.exercises):
                exercise = self.exercises[idx]
        else:
            for ex in self.exercises:
                if ex['name'] == exercise_name or ex['full_name'] == exercise_name:
                    exercise = ex
                    break

        if not exercise:
            print(f"{Color.RED}错误: 找不到练习 '{exercise_name}'{Color.END}")
            return False

        print(f"\n{Color.CYAN}运行练习: {exercise['full_name']}{Color.END}\n")

        success = self.runner.run(exercise['path'])

        if success:
            self.progress[exercise['full_name']] = {'status': 'completed'}
            self._save_progress()
            print(f"\n{Color.GREEN}{Color.BOLD}✓ 恭喜！练习完成！{Color.END}\n")
        else:
            self.progress[exercise['full_name']] = {'status': 'attempted'}
            self._save_progress()
            print(f"\n{Color.YELLOW}继续加油！请修改代码后重试。{Color.END}\n")

        return success

    def watch_mode(self):
        """监视模式：自动运行下一个未完成的练习"""
        print(f"{Color.CYAN}进入监视模式...{Color.END}\n")

        for exercise in self.exercises:
            status = self.progress.get(exercise['full_name'], {}).get('status', 'pending')
            if status != 'completed':
                print(f"{Color.BOLD}下一个练习: {exercise['full_name']}{Color.END}\n")
                success = self.run_exercise(exercise['name'])
                if not success:
                    print(f"\n{Color.YELLOW}请修改代码并运行: python algo_game_theory.py run {exercise['name']}{Color.END}\n")
                    return

        print(f"\n{Color.GREEN}{Color.BOLD}🎉 恭喜！所有练习都已完成！{Color.END}\n")

    def hint(self, exercise_name):
        """显示练习提示"""
        exercise = None

        if exercise_name.isdigit():
            idx = int(exercise_name) - 1
            if 0 <= idx < len(self.exercises):
                exercise = self.exercises[idx]
        else:
            for ex in self.exercises:
                if ex['name'] == exercise_name or ex['full_name'] == exercise_name:
                    exercise = ex
                    break

        if not exercise:
            print(f"{Color.RED}错误: 找不到练习 '{exercise_name}'{Color.END}")
            return

        self.runner.show_hint(exercise['path'])

    def reset_progress(self):
        """重置学习进度"""
        self.progress = {}
        self._save_progress()
        print(f"{Color.GREEN}学习进度已重置{Color.END}")


def main():
    parser = argparse.ArgumentParser(
        description='算法博弈论学习工具 - 基于 Tim Roughgarden 教授的《算法博弈论二十讲》'
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # list 命令
    subparsers.add_parser('list', help='列出所有练习题')

    # run 命令
    run_parser = subparsers.add_parser('run', help='运行指定的练习题')
    run_parser.add_argument('exercise', help='练习题名称或序号')

    # watch 命令
    subparsers.add_parser('watch', help='监视模式：自动运行下一个未完成的练习')

    # hint 命令
    hint_parser = subparsers.add_parser('hint', help='显示练习提示')
    hint_parser.add_argument('exercise', help='练习题名称或序号')

    # reset 命令
    subparsers.add_parser('reset', help='重置学习进度')

    args = parser.parse_args()

    tool = AlgoGameTheoryTool()

    if args.command == 'list':
        tool.list_exercises()
    elif args.command == 'run':
        tool.run_exercise(args.exercise)
    elif args.command == 'watch':
        tool.watch_mode()
    elif args.command == 'hint':
        tool.hint(args.exercise)
    elif args.command == 'reset':
        tool.reset_progress()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
