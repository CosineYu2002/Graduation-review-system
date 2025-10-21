from fastapi import APIRouter, HTTPException, status

from api.crud.rule_crud import RuleCRUD
from api.models.response_models import APIResponse
from api.models.rule_models import *

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("/", response_model=APIResponse[list[RuleBasicInfo]])
def get_all_rules():
    """
    取得所有規則的基本資訊

    返回所有系所的畢業規則列表，包含：
    - 系所代碼
    - 系所名稱（中文全名）
    - 適用入學年度
    - 所屬學院
    - 是否為輔系規則
    """
    try:
        rules_list = RuleCRUD.get_all_rules()
        return APIResponse(
            success=True,
            message=f"成功取得 {len(rules_list)} 條規則",
            data=rules_list,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得規則列表失敗: {str(e)}",
        )


@router.get(
    "/{department_code}/{admission_year}/{rule_type}",
    response_model=APIResponse[RuleDetail],
)
def get_rule_detail(department_code: str, admission_year: int, rule_type: RuleTypeEnum):
    """
    取得特定規則的詳細資訊

    Parameters:
    - department_code: 系所代碼（例如：E2、F7）
    - admission_year: 入學年度（例如：110、112）
    - rule_type: 規則類型（例如：major、minor）

    Returns:
    - 規則的完整內容，包含所有規則條目
    """
    try:
        rule_detail = RuleCRUD.get_rule_detail(
            department_code, admission_year, rule_type
        )

        if rule_detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到規則：{department_code} {admission_year} 學年度 {rule_type.value} 規則",
            )

        return APIResponse(
            success=True,
            message=f"成功取得 {rule_detail.basic_info.department_name} {admission_year} 學年度 {rule_type.value} 規則",
            data=rule_detail,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得規則詳細資訊失敗: {str(e)}",
        )


@router.post("/", response_model=APIResponse[RuleBasicInfo])
def create_rule(request: CreateRuleRequest):
    """
    新增畢業規則
    """
    try:
        rule_detail = RuleCRUD.create_rule(request)

        return APIResponse(
            success=True,
            message=f"成功新增 {rule_detail.department_name} {request.admission_year} 學年度規則",
            data=rule_detail,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"新增規則失敗: {str(e)}",
        )


@router.put(
    "/{department_code}/{admission_year}/{rule_type}",
    response_model=APIResponse[RuleBasicInfo],
)
def update_rule(
    department_code: str,
    admission_year: int,
    rule_type: RuleTypeEnum,
    request: CreateRuleRequest,
):
    """
    更新畢業規則

    Parameters:
    - department_code: 系所代碼
    - admission_year: 入學年度
    - rule_type: 規則類型
    - request: 更新的規則內容
    """
    try:
        # 確保路徑參數與請求體一致
        if (
            request.department_code != department_code
            or request.admission_year != admission_year
            or request.rule_type != rule_type
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="路徑參數與請求內容不一致",
            )

        rule_detail = RuleCRUD.update_rule(request)

        return APIResponse(
            success=True,
            message=f"成功更新 {rule_detail.department_name} {request.admission_year} 學年度規則",
            data=rule_detail,
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新規則失敗: {str(e)}",
        )


@router.delete(
    "/{department_code}/{admission_year}/{rule_type}", response_model=APIResponse[None]
)
def delete_rule(department_code: str, admission_year: int, rule_type: RuleTypeEnum):
    """
    刪除規則

    Parameters:
    - department_code: 系所代碼
    - admission_year: 入學年度
    - is_minor: 是否為輔系規則（選填）
    """
    try:
        success = RuleCRUD.delete_rule(department_code, admission_year, rule_type)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到規則：{department_code} {admission_year} 學年度 {rule_type.value} 規則",
            )

        return APIResponse(
            success=True,
            message=f"成功刪除 {department_code} {admission_year} 學年度 {rule_type.value} 規則",
            data=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除規則失敗: {str(e)}",
        )


@router.get("/departments/all", response_model=APIResponse[dict])
def get_all_departments():
    """
    取得所有系所資訊

    Returns:
    - 所有系所的代碼、名稱、學院資訊
    """
    try:
        departments = RuleCRUD.get_departments()
        return APIResponse(
            success=True,
            message=f"成功取得 {len(departments)} 個系所資訊",
            data=departments,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取得系所資訊失敗: {str(e)}",
        )
