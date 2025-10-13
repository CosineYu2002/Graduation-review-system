from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pathlib import Path

from rule_engine.models.student import Student
from rule_engine.factory import StudentFactory
from api.crud.student_crud import StudentCRUD
from api.models.student_models import APIResponse, StudentBasicInfo

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=APIResponse[list[StudentBasicInfo]])
def get_all_students():
    """
    取得所有學生的基本資訊（學號、姓名、主修科系）
    """
    try:
        student_list = StudentCRUD.get_all_students()
        return APIResponse(
            success=True,
            message=f"成功取得 {len(student_list)} 位學生的基本資訊",
            data=student_list,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取學生列表失敗: {str(e)}",
        )


@router.get("/{student_id}", response_model=APIResponse[Student])
def get_student_detail(student_id: str):
    """
    根據學號取得學生的詳細資訊（包含修課列表）
    """
    try:
        student_info = StudentCRUD.get_student_by_id(student_id)
        return APIResponse(
            success=True,
            message=f"成功取得學生 {student_id} 的詳細資訊",
            data=student_info,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取學生 {student_id} 詳細資訊失敗: {str(e)}",
        )


@router.post("/upload-excel", response_model=APIResponse[list[StudentBasicInfo]])
async def upload_excel_students(file: UploadFile = File(...), major: str = ""):
    """
    上傳 Excel 檔案並批量新增學生資料

    Parameters:
    - file: Excel 檔案 (.xlsx 格式)
    - major: 預設科系（選填，如果 Excel 中沒有科系資訊則使用此值）

    Excel 檔案需要包含以下欄位：
    - 學號, 姓名, 課程名稱, 課程碼, 學分數, 成績, 承抵課程別, 選必修(0,1必修，2選修), 學年, 學期
    """
    file_size = 0
    temp_file: Path | None = None
    try:
        # 驗證檔案格式
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="未提供檔案"
            )

        if not file.filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只支援 .xlsx 格式檔案"
            )

        # 檢查檔案大小（限制為 10MB）

        try:
            # 建立臨時檔案
            temp_file = Path(f"temp_{file.filename}")

            # 寫入檔案內容並計算大小
            with open(temp_file, "wb") as buffer:
                while chunk := await file.read(1024):  # 讀取 1KB 塊
                    file_size += len(chunk)
                    if file_size > 10 * 1024 * 1024:  # 10MB 限制
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="檔案大小超過 10MB 限制",
                        )
                    buffer.write(chunk)

            # 使用 StudentFactory 處理 Excel 檔案
            output_path = Path("data/students")
            students = StudentFactory.load_students_from_excel(
                excel_file_path=temp_file, output_path=output_path, major=major
            )

            return APIResponse(
                success=True,
                message=f"成功從 Excel 檔案匯入 {len(students)} 位學生資料",
                data=list(students.values()),
            )

        finally:
            # 清理臨時檔案
            if temp_file and temp_file.exists():
                temp_file.unlink()

    except HTTPException:
        raise
    except Exception as e:
        # 確保清理臨時檔案
        if temp_file is not None and temp_file.exists():
            temp_file.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Excel 檔案處理失敗: {str(e)}",
        )


@router.delete("/", response_model=APIResponse[None])
def delete_all_students():
    """
    刪除所有學生資料
    """
    try:
        deleted_count = StudentCRUD.delete_all_students()
        return APIResponse(
            success=True,
            message=f"成功刪除 {deleted_count} 位學生的資料",
            data=None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除學生資料失敗: {str(e)}",
        )


@router.delete("/{student_id}", response_model=APIResponse[None])
def delete_student(student_id: str):
    """
    刪除特定學生資料
    """
    try:
        StudentCRUD.delete_student_by_id(student_id)
        return APIResponse(
            success=True,
            message=f"成功刪除學生 {student_id} 的資料",
            data=None,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"學生 {student_id} 不存在",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除學生 {student_id} 資料失敗: {str(e)}",
        )
