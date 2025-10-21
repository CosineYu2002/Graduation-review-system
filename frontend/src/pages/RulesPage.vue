<template>
  <q-page padding>
    <div class="q-pa-md">
      <div class="row items-center q-mb-md">
        <div class="col">
          <div class="text-h4">規則資料管理</div>
          <div class="text-subtitle2 text-grey">管理各系所畢業審查規則</div>
        </div>
        <div class="col-auto">
          <q-btn color="primary" icon="add" label="新增規則" @click="openCreateDialog" />
        </div>
      </div>

      <!-- 規則列表 -->
      <q-card>
        <q-card-section>
          <div class="row items-center q-mb-md">
            <div class="col">
              <div class="text-h6">規則列表</div>
            </div>
            <div class="col-auto q-gutter-sm">
              <q-input
                v-model="searchQuery"
                dense
                outlined
                placeholder="搜尋系所或年度..."
                style="min-width: 250px"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
                <template v-slot:append>
                  <q-icon
                    v-if="searchQuery"
                    name="clear"
                    class="cursor-pointer"
                    @click="searchQuery = ''"
                  />
                </template>
              </q-input>
            </div>
          </div>

          <!-- 載入中 -->
          <div v-if="loading" class="text-center q-pa-lg">
            <q-spinner color="primary" size="3em" />
            <div class="q-mt-md text-grey">載入中...</div>
          </div>

          <!-- 規則表格 -->
          <q-table
            v-else
            :rows="filteredRules"
            :columns="columns"
            row-key="id"
            :pagination="{ rowsPerPage: 10 }"
            :rows-per-page-options="[10, 20, 50]"
            flat
            bordered
          >
            <template v-slot:body-cell-rule_type="props">
              <q-td :props="props">
                <q-badge :color="getRuleTypeBadgeColor(props.row.rule_type)">
                  {{ getRuleTypeLabel(props.row.rule_type) }}
                </q-badge>
              </q-td>
            </template>

            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn
                  flat
                  dense
                  round
                  color="primary"
                  icon="visibility"
                  @click="viewRuleDetail(props.row)"
                >
                  <q-tooltip>查看規則詳情</q-tooltip>
                </q-btn>
                <q-btn flat dense round color="orange" icon="edit" @click="editRule(props.row)">
                  <q-tooltip>編輯規則</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  dense
                  round
                  color="negative"
                  icon="delete"
                  @click="confirmDelete(props.row)"
                >
                  <q-tooltip>刪除規則</q-tooltip>
                </q-btn>
              </q-td>
            </template>

            <template v-slot:no-data>
              <div class="full-width text-center q-pa-lg">
                <q-icon name="rule" size="3em" color="grey" />
                <div class="text-h6 q-mt-md text-grey">目前沒有規則資料</div>
                <div class="text-body2 text-grey-6 q-mt-sm">
                  請點擊右上角「新增規則」按鈕來新增規則
                </div>
              </div>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- 新增規則對話框 -->
      <q-dialog v-model="createDialogOpen" persistent maximized>
        <q-card>
          <q-card-section class="row items-center">
            <div class="text-h6">新增規則</div>
            <q-space />
            <q-btn icon="close" flat round dense @click="closeCreateDialog" />
          </q-card-section>

          <q-separator />

          <q-card-section style="max-height: calc(100vh - 120px); overflow-y: auto">
            <RuleCreator
              ref="ruleCreatorRef"
              :department-options="departmentOptions"
              :submitting="submitting"
              @submit="submitCreateRule"
              @cancel="closeCreateDialog"
            />
          </q-card-section>
        </q-card>
      </q-dialog>

      <!-- 編輯規則對話框 -->
      <q-dialog v-model="editDialogOpen" persistent maximized>
        <q-card>
          <q-card-section class="row items-center">
            <div class="text-h6">編輯規則</div>
            <q-space />
            <q-btn icon="close" flat round dense @click="closeEditDialog" />
          </q-card-section>

          <q-separator />

          <q-card-section style="max-height: calc(100vh - 120px); overflow-y: auto">
            <RuleCreator
              v-if="editingRule"
              ref="editRuleCreatorRef"
              :department-options="departmentOptions"
              :submitting="submitting"
              :initial-data="editingRule"
              @submit="submitEditRule"
              @cancel="closeEditDialog"
            />
          </q-card-section>
        </q-card>
      </q-dialog>

      <!-- 規則詳情對話框 -->
      <q-dialog v-model="detailDialogOpen" maximized>
        <q-card>
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">規則詳情</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup />
          </q-card-section>

          <q-separator />

          <q-card-section v-if="selectedRule" style="max-height: 80vh; overflow-y: auto">
            <div>
              <!-- 基本資訊 -->
              <q-banner class="bg-grey-2 rounded-borders q-mb-md">
                <template v-slot:avatar>
                  <q-icon name="rule" color="primary" />
                </template>
                <div class="row q-gutter-md">
                  <div>
                    <strong>系所：</strong>{{ selectedRule.basic_info.department_name }} ({{
                      selectedRule.basic_info.department_code
                    }})
                  </div>
                  <div><strong>入學年度：</strong>{{ selectedRule.basic_info.admission_year }}</div>
                  <div><strong>學院：</strong>{{ selectedRule.basic_info.college }}</div>
                  <div>
                    <strong>類型：</strong>
                    <q-badge :color="getRuleTypeBadgeColor(selectedRule.basic_info.rule_type)">
                      {{ getRuleTypeLabel(selectedRule.basic_info.rule_type) }}
                    </q-badge>
                  </div>
                </div>
              </q-banner>

              <!-- 規則樹狀圖 -->
              <RuleTree :rule="selectedRule.rule_content" />
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'
import RuleTree from 'components/RuleTree.vue'
import RuleCreator from 'components/RuleCreator.vue'

const $q = useQuasar()

// 資料狀態
const loading = ref(false)
const submitting = ref(false)
const rules = ref([])
const departments = ref({})
const searchQuery = ref('')

// 對話框狀態
const createDialogOpen = ref(false)
const editDialogOpen = ref(false)
const detailDialogOpen = ref(false)
const selectedRule = ref(null)
const editingRule = ref(null)

// Ref for RuleCreator component
const ruleCreatorRef = ref(null)
const editRuleCreatorRef = ref(null)

// 表格欄位定義
const columns = [
  {
    name: 'department_code',
    label: '系所代碼',
    align: 'left',
    field: 'department_code',
    sortable: true,
  },
  {
    name: 'department_name',
    label: '系所名稱',
    align: 'left',
    field: 'department_name',
    sortable: true,
  },
  {
    name: 'admission_year',
    label: '入學年度',
    align: 'center',
    field: 'admission_year',
    sortable: true,
  },
  {
    name: 'college',
    label: '學院',
    align: 'left',
    field: 'college',
    sortable: true,
  },
  {
    name: 'rule_type',
    label: '類型',
    align: 'center',
    field: 'rule_type',
  },
  {
    name: 'actions',
    label: '操作',
    align: 'center',
  },
]

// 計算屬性
const filteredRules = computed(() => {
  if (!searchQuery.value) return rules.value

  const query = searchQuery.value.toLowerCase()
  return rules.value.filter(
    (rule) =>
      rule.department_code.toLowerCase().includes(query) ||
      rule.department_name.toLowerCase().includes(query) ||
      rule.admission_year.toString().includes(query) ||
      rule.college.toLowerCase().includes(query),
  )
})

const departmentOptions = computed(() => {
  return Object.entries(departments.value).map(([code, info]) => ({
    code,
    label: `${code} - ${info.name_zh_tw}`,
    college: info.college,
  }))
})

// 載入所有規則
async function loadRules() {
  loading.value = true
  try {
    const response = await api.get('/rules/')
    if (response.data.success) {
      rules.value = response.data.data
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '載入規則列表失敗',
      caption: error.response?.data?.detail || error.message,
    })
  } finally {
    loading.value = false
  }
}

// 載入系所資訊
async function loadDepartments() {
  try {
    const response = await api.get('/rules/departments/all')
    if (response.data.success) {
      departments.value = response.data.data
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '載入系所資訊失敗',
      caption: error.response?.data?.detail || error.message,
    })
  }
}

// 查看規則詳情
async function viewRuleDetail(rule) {
  try {
    const response = await api.get(
      `/rules/${rule.department_code}/${rule.admission_year}/${rule.rule_type}`,
    )
    if (response.data.success) {
      selectedRule.value = response.data.data
      detailDialogOpen.value = true
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '載入規則詳情失敗',
      caption: error.response?.data?.detail || error.message,
    })
  }
}

// 打開新增對話框
function openCreateDialog() {
  createDialogOpen.value = true
}

// 關閉新增對話框
function closeCreateDialog() {
  createDialogOpen.value = false
  if (ruleCreatorRef.value) {
    ruleCreatorRef.value.resetForm()
  }
}

// 編輯規則
async function editRule(rule) {
  try {
    // 載入完整規則資料
    const response = await api.get(
      `/rules/${rule.department_code}/${rule.admission_year}/${rule.rule_type}`,
    )
    if (response.data.success) {
      editingRule.value = {
        department_code: response.data.data.basic_info.department_code,
        admission_year: response.data.data.basic_info.admission_year,
        rule_type: response.data.data.basic_info.rule_type,
        rule_content: response.data.data.rule_content,
      }
      editDialogOpen.value = true
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '載入規則失敗',
      caption: error.response?.data?.detail || error.message,
    })
  }
}

// 關閉編輯對話框
function closeEditDialog() {
  editDialogOpen.value = false
  editingRule.value = null
}

// 提交編輯規則
async function submitEditRule(ruleData) {
  submitting.value = true
  try {
    const response = await api.put(
      `/rules/${ruleData.department_code}/${ruleData.admission_year}/${ruleData.rule_type}`,
      ruleData,
    )

    if (response.data.success) {
      $q.notify({
        type: 'positive',
        message: '更新規則成功',
      })
      closeEditDialog()
      loadRules()
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '更新規則失敗',
      caption: error.response?.data?.detail || error.message,
    })
  } finally {
    submitting.value = false
  }
}

// 提交新增規則
async function submitCreateRule(ruleData) {
  submitting.value = true
  try {
    const response = await api.post('/rules/', ruleData)

    if (response.data.success) {
      $q.notify({
        type: 'positive',
        message: '新增規則成功',
      })
      closeCreateDialog()
      loadRules()
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '新增規則失敗',
      caption: error.response?.data?.detail || error.message,
    })
  } finally {
    submitting.value = false
  }
}

// 確認刪除
function confirmDelete(rule) {
  $q.dialog({
    title: '確認刪除',
    message: `確定要刪除 ${rule.department_name} ${rule.admission_year} 學年度的${getRuleTypeLabel(rule.rule_type)}規則嗎？`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    deleteRule(rule)
  })
}

// 刪除規則
async function deleteRule(rule) {
  try {
    const response = await api.delete(
      `/rules/${rule.department_code}/${rule.admission_year}/${rule.rule_type}`,
    )

    if (response.data.success) {
      $q.notify({
        type: 'positive',
        message: '刪除規則成功',
      })
      loadRules()
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '刪除規則失敗',
      caption: error.response?.data?.detail || error.message,
    })
  }
}

// 輔助函數：取得規則類型標籤
function getRuleTypeLabel(ruleType) {
  const labels = {
    major: '主修',
    minor: '輔系',
    double_major: '雙主修',
  }
  return labels[ruleType] || ruleType
}

// 輔助函數：取得規則類型徽章顏色
function getRuleTypeBadgeColor(ruleType) {
  const colors = {
    major: 'primary',
    minor: 'orange',
    double_major: 'purple',
  }
  return colors[ruleType] || 'grey'
}

// 初始化
onMounted(() => {
  loadRules()
  loadDepartments()
})
</script>

<style scoped>
.rounded-borders {
  border-radius: 8px;
}
</style>
