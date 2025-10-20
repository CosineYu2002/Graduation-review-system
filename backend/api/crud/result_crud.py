from pathlib import Path
import json
from datetime import datetime
from api.models.result_models import ResultBasicInfo


class ResultCRUD:
    @staticmethod
    def get_all_results() -> list[ResultBasicInfo]:
        """
        取得所有審查結果的基本資訊

        Returns:
            list[ResultBasicInfo]: 包含所有審查結果的列表，每個結果包含基本資訊
        """
        results_dir = Path("data/evaluation_results")
        results_info: list[ResultBasicInfo] = []

        if not results_dir.exists():
            return []

        json_files = list(results_dir.glob("*.json"))
        for result_file in sorted(
            json_files, key=lambda x: x.stat().st_mtime, reverse=True
        ):
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 提取基本資訊
                result_info = ResultBasicInfo(
                    file_name=result_file.name,
                    student_id=data.get("id", ""),
                    student_name=data.get("name", ""),
                )
                results_info.append(result_info)
            except Exception as e:
                print(f"警告：跳過檔案 {result_file.name}: {e}")
                continue

        return results_info

    @staticmethod
    def get_result_by_filename(filename: str) -> dict:
        """
        根據檔名取得審查結果的詳細資訊

        Args:
            filename: 結果檔案名稱

        Returns:
            dict: 完整的審查結果資料

        Raises:
            FileNotFoundError: 找不到指定的結果檔案
        """
        results_dir = Path("data/evaluation_results")
        result_file = results_dir / filename

        if not result_file.exists():
            raise FileNotFoundError(f"找不到結果檔案: {filename}")

        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    @staticmethod
    def delete_result_by_filename(filename: str) -> bool:
        """
        根據檔名刪除審查結果

        Args:
            filename: 結果檔案名稱

        Returns:
            bool: 刪除成功返回 True

        Raises:
            FileNotFoundError: 找不到指定的結果檔案
        """
        results_dir = Path("data/evaluation_results")
        result_file = results_dir / filename

        if not result_file.exists():
            raise FileNotFoundError(f"找不到結果檔案: {filename}")

        result_file.unlink()
        return True

    @staticmethod
    def delete_all_results() -> int:
        """
        刪除所有審查結果

        Returns:
            int: 刪除的檔案數量
        """
        results_dir = Path("data/evaluation_results")

        if not results_dir.exists():
            return 0

        json_files = list(results_dir.glob("*.json"))
        deleted_count = 0

        for result_file in json_files:
            result_file.unlink()
            deleted_count += 1

        return deleted_count
