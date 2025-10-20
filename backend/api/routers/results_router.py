from fastapi import APIRouter, HTTPException, status

from api.crud.result_crud import ResultCRUD
from api.models.result_models import ResultBasicInfo
from api.models.response_models import APIResponse

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/", response_model=APIResponse[list[ResultBasicInfo]])
def get_all_results():
    """
    取得所有審查結果的基本資訊

    返回所有已保存的審查結果列表，按建立時間倒序排列（最新的在前）
    """
    try:
        results = ResultCRUD.get_all_results()
        return APIResponse(
            success=True,
            message=f"成功取得 {len(results)} 筆審查結果",
            data=results,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取審查結果列表失敗: {str(e)}",
        )


@router.get("/file/{filename}", response_model=APIResponse[dict])
def get_result_by_filename(filename: str):
    """
    根據檔名取得審查結果的詳細資訊

    Parameters:
    - filename: 結果檔案名稱，例如：AN4116089_20_Oct_2025_14_30.json
    """
    try:
        result = ResultCRUD.get_result_by_filename(filename)
        return APIResponse(
            success=True,
            message=f"成功取得審查結果 {filename}",
            data=result,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到審查結果檔案: {filename}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取審查結果失敗: {str(e)}",
        )


@router.delete("/file/{filename}", response_model=APIResponse[None])
def delete_result_by_filename(filename: str):
    """
    根據檔名刪除審查結果

    Parameters:
    - filename: 結果檔案名稱
    """
    try:
        ResultCRUD.delete_result_by_filename(filename)
        return APIResponse(
            success=True,
            message=f"成功刪除審查結果 {filename}",
            data=None,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到審查結果檔案: {filename}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除審查結果失敗: {str(e)}",
        )


@router.delete("/", response_model=APIResponse[None])
def delete_all_results():
    """
    刪除所有審查結果

    ⚠️ 警告：此操作將刪除所有已保存的審查記錄，無法復原！
    """
    try:
        deleted_count = ResultCRUD.delete_all_results()
        return APIResponse(
            success=True,
            message=f"成功刪除 {deleted_count} 筆審查記錄",
            data=None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除所有審查結果失敗: {str(e)}",
        )
