from fastapi import APIRouter, HTTPException, status, Query

from api.models.response_models import APIResponse
from api.models.review_models import ReviewResult
from api.models.student_models import StudentBasicInfo
from api.crud.student_crud import StudentCRUD
from api.crud.review_crud import ReviewCRUD

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/{student_id}", response_model=APIResponse[ReviewResult])
def review_student_graduation(
    student_id: str,
    major: str | None = Query(
        None, description="主修科系代號（若不指定則使用學生本身科系）"
    ),
    double_major: str | None = Query(None, description="雙主修科系代號"),
    minor: list[str] | None = Query(
        None, description="輔系科系代號列表（不分系學生必須至少提供一個）"
    ),
):
    """
    對指定學生進行畢業審查計算

    - **student_id**: 學生的學號（路徑參數）
    - **major**: (查詢參數) 主修科系代號，若不指定則使用學生本身科系
    - **double_major**: (查詢參數) 雙主修科系代號，可選
    - **minor**: (查詢參數) 輔系科系代號列表，可選，可指定多個。**不分系(AN)學生必須至少提供一個輔系**

    範例：
    - 一般學生: POST /review/D10944101
    - 不分系學生（至少一個輔系）: POST /review/A10999999?minor=B5
    - 不分系學生含主修和輔系: POST /review/A10999999?major=CS&minor=B5
    - 含雙主修和輔系: POST /review/D10944101?double_major=EE&minor=CS&minor=MATH
    """
    try:
        # 1. 取得學生資料
        student = StudentCRUD.get_student_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到學生 {student_id}",
            )

        # 2. 執行審查
        try:
            review_results = ReviewCRUD.review_student(
                student=student,
                major_department=major,
                double_major_department=double_major,
                minor_departments=minor,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

        # 3. 組裝回應資料
        # 主修審查結果
        main_result = review_results.get("main")
        if not main_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="主修審查失敗",
            )

        # 建立學生基本資訊
        student_basic_info = StudentBasicInfo(
            id=student.id, name=student.name, major=student.major
        )

        # 建立回應 - 只返回主修審查結果
        review_result = ReviewResult(
            student_info=student_basic_info,
            is_eligible_for_graduation=main_result.is_valid,
            evaluation_results=main_result,
        )

        return APIResponse(
            success=True,
            message=f"學生 {student_id} 畢業審查計算完成",
            data=review_result,
        )

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到學生 {student_id} 的資料",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"審查計算時發生錯誤: {str(e)}",
        )
