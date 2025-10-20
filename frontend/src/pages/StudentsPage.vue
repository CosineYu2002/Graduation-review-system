<template>
  <q-page padding>
    <div class="q-pa-md">
      <div class="row items-center q-mb-md">
        <div class="col">
          <div class="text-h4">學生資料管理</div>
          <div class="text-subtitle2 text-grey">管理學生資訊與課程記錄</div>
        </div>
        <div class="col-auto">
          <q-btn
            color="primary"
            icon="upload_file"
            label="上傳 Excel"
            @click="uploadDialogOpen = true"
          />
        </div>
      </div>

      <!-- 學生列表 -->
      <q-card>
        <q-card-section>
          <div class="row items-center q-mb-md">
            <div class="col">
              <div class="text-h6">學生列表</div>
            </div>
            <div class="col-auto">
              <q-input v-model="searchQuery" dense outlined placeholder="搜尋學號或姓名...">
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

          <!-- 學生表格 -->
          <q-table
            v-else
            :rows="filteredStudents"
            :columns="columns"
            row-key="id"
            :pagination="{ rowsPerPage: 10 }"
            :rows-per-page-options="[10, 20, 50]"
            flat
            bordered
          >
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn
                  flat
                  dense
                  round
                  color="primary"
                  icon="visibility"
                  @click="viewStudentDetail(props.row.id)"
                >
                  <q-tooltip>查看詳細資料</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  dense
                  round
                  color="positive"
                  icon="fact_check"
                  @click="openReviewDialog(props.row)"
                >
                  <q-tooltip>畢業審查</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  dense
                  round
                  color="negative"
                  icon="delete"
                  @click="confirmDelete(props.row)"
                >
                  <q-tooltip>刪除學生</q-tooltip>
                </q-btn>
              </q-td>
            </template>

            <template v-slot:no-data>
              <div class="full-width text-center q-pa-lg">
                <q-icon name="person_off" size="3em" color="grey" />
                <div class="text-h6 q-mt-md text-grey">目前沒有學生資料</div>
                <div class="text-body2 text-grey-6 q-mt-sm">
                  請點擊右上角「上傳 Excel」按鈕來新增學生資料
                </div>
              </div>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- 上傳 Excel 對話框 -->
      <q-dialog v-model="uploadDialogOpen">
        <q-card style="min-width: 400px">
          <q-card-section>
            <div class="text-h6">上傳學生 Excel 檔案</div>
          </q-card-section>

          <q-card-section>
            <q-file
              v-model="excelFile"
              label="選擇 Excel 檔案"
              accept=".xlsx,.xls"
              outlined
              @update:model-value="onFileSelected"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>

            <q-input
              v-model="majorInput"
              label="主修科系代號"
              placeholder="例如：E2、AN"
              outlined
              class="q-mt-md"
              hint="請輸入學生的主修科系代號"
            />

            <div v-if="uploadError" class="q-mt-md">
              <q-banner dense class="bg-negative text-white">
                <template v-slot:avatar>
                  <q-icon name="error" />
                </template>
                {{ uploadError }}
              </q-banner>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="取消" color="grey" v-close-popup />
            <q-btn
              flat
              label="上傳"
              color="primary"
              :loading="uploading"
              :disable="!excelFile || !majorInput"
              @click="uploadExcel"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- 學生詳細資料對話框 -->
      <q-dialog v-model="detailDialogOpen" maximized>
        <q-card>
          <q-card-section class="row items-center bg-primary text-white">
            <div class="text-h6">學生詳細資料</div>
            <q-space />
            <q-btn flat dense round icon="close" v-close-popup />
          </q-card-section>

          <q-card-section v-if="selectedStudent" class="q-pa-lg">
            <!-- 基本資訊 -->
            <div class="text-h6 q-mb-md">基本資訊</div>
            <q-list bordered separator>
              <q-item>
                <q-item-section>
                  <q-item-label overline>學號</q-item-label>
                  <q-item-label>{{ selectedStudent.id }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label overline>姓名</q-item-label>
                  <q-item-label>{{ selectedStudent.name }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label overline>主修科系</q-item-label>
                  <q-item-label>{{ selectedStudent.major }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="selectedStudent.admission_year">
                <q-item-section>
                  <q-item-label overline>入學年度</q-item-label>
                  <q-item-label>{{ selectedStudent.admission_year }} 學年度</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>

            <!-- 修課記錄 -->
            <div class="text-h6 q-mt-lg q-mb-md">修課記錄</div>
            <q-table
              v-if="selectedStudent.courses && selectedStudent.courses.length > 0"
              :rows="selectedStudent.courses"
              :columns="courseColumns"
              row-key="course_name"
              :pagination="{ rowsPerPage: 20 }"
              flat
              bordered
            >
              <template v-slot:body-cell-grade="props">
                <q-td :props="props">
                  <q-badge
                    :color="getGradeColor(props.row.grade)"
                    :label="getGradeStatus(props.row.grade)"
                  />
                </q-td>
              </template>
            </q-table>
            <div v-else class="text-center text-grey q-pa-lg">此學生尚無修課記錄</div>
          </q-card-section>
        </q-card>
      </q-dialog>

      <!-- 審查對話框 -->
      <q-dialog v-model="reviewDialogOpen">
        <q-card style="min-width: 500px">
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">畢業審查</div>
          </q-card-section>

          <q-card-section v-if="reviewStudent">
            <div class="q-mb-md">
              <div class="text-subtitle1 q-mb-xs">學生資訊</div>
              <div class="text-body2 text-grey-7">學號：{{ reviewStudent.id }}</div>
              <div class="text-body2 text-grey-7">姓名：{{ reviewStudent.name }}</div>
              <div class="text-body2 text-grey-7">主修科系：{{ reviewStudent.major }}</div>
            </div>

            <q-separator class="q-my-md" />

            <!-- 不分系學生提示 -->
            <div v-if="reviewStudent.major === 'AN'" class="q-mb-md">
              <q-banner class="bg-orange-2 text-orange-9">
                <template v-slot:avatar>
                  <q-icon name="info" color="orange" />
                </template>
                <div class="text-body2">不分系學生必須至少選擇一個輔系進行審查</div>
              </q-banner>
            </div>

            <!-- 主修科系 -->
            <div class="q-mb-md">
              <q-input
                v-model="reviewMajor"
                outlined
                dense
                :label="reviewStudent?.major === 'AN' ? '主修科系代號（可選）' : '主修科系代號'"
                :hint="reviewStudent?.major === 'AN' ? '例如：B5, H5（可不填）' : '例如：B5, H5'"
                :disable="reviewStudent?.major !== 'AN'"
              />
            </div>

            <!-- 可選的雙主修 -->
            <div class="q-mb-md">
              <q-input
                v-model="reviewDoubleMajor"
                outlined
                dense
                label="雙主修科系代號（可選）"
                hint="例如：E2"
              />
            </div>

            <!-- 輔系 -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-sm">
                輔系科系代號{{ reviewStudent?.major === 'AN' ? ' *' : '（可選）' }}
              </div>
              <div v-for="(minor, index) in reviewMinors" :key="index" class="row q-mb-xs">
                <div class="col">
                  <q-input v-model="reviewMinors[index]" outlined dense placeholder="例如：H5" />
                </div>
                <div class="col-auto q-ml-sm">
                  <q-btn
                    flat
                    dense
                    round
                    color="negative"
                    icon="remove"
                    @click="removeMinor(index)"
                  />
                </div>
              </div>
              <q-btn flat dense color="primary" icon="add" label="新增輔系" @click="addMinor" />
            </div>

            <div v-if="reviewError" class="text-negative q-mb-md">
              <q-icon name="error" /> {{ reviewError }}
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="取消" color="grey" v-close-popup />
            <q-btn
              unelevated
              label="開始審查"
              color="primary"
              :loading="reviewing"
              @click="performReview"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- 審查結果對話框 -->
      <q-dialog v-model="reviewResultDialogOpen" maximized>
        <q-card>
          <q-card-section
            class="row items-center text-white"
            :class="reviewResult?.is_eligible_for_graduation ? 'bg-positive' : 'bg-warning'"
          >
            <q-icon
              :name="reviewResult?.is_eligible_for_graduation ? 'check_circle' : 'warning'"
              size="md"
              class="q-mr-md"
            />
            <div class="text-h6">
              {{ reviewResult?.is_eligible_for_graduation ? '審查通過' : '審查未通過' }}
            </div>
            <q-space />
            <q-btn flat dense round icon="close" v-close-popup />
          </q-card-section>

          <q-card-section v-if="reviewResult" class="q-pa-lg">
            <!-- 學生資訊 -->
            <div class="text-h6 q-mb-md">學生資訊</div>
            <q-list bordered separator class="q-mb-lg">
              <q-item>
                <q-item-section>
                  <q-item-label overline>學號</q-item-label>
                  <q-item-label>{{ reviewResult.student_info.id }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label overline>姓名</q-item-label>
                  <q-item-label>{{ reviewResult.student_info.name }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label overline>主修科系</q-item-label>
                  <q-item-label>{{ reviewResult.student_info.major }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>

            <!-- 審查結果摘要 -->
            <div class="text-h6 q-mb-md">審查摘要</div>
            <q-banner
              :class="
                reviewResult.is_eligible_for_graduation
                  ? 'bg-positive text-white'
                  : 'bg-warning text-white'
              "
              class="q-mb-lg"
            >
              <template v-slot:avatar>
                <q-icon
                  :name="reviewResult.is_eligible_for_graduation ? 'check_circle' : 'warning'"
                  size="lg"
                />
              </template>
              <div class="text-h6">
                {{ reviewResult.is_eligible_for_graduation ? '符合畢業資格' : '不符合畢業資格' }}
              </div>
              <div class="text-body2 q-mt-sm">
                獲得學分：{{ reviewResult.evaluation_results.earned_credits }} 學分
              </div>
            </q-banner>

            <!-- 詳細審查結果 -->
            <div class="text-h6 q-mb-md">詳細審查結果</div>
            <review-result-tree :result="reviewResult.evaluation_results" />
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import ReviewResultTree from 'components/ReviewResultTree.vue'

const $q = useQuasar()

// 狀態
const students = ref([])
const loading = ref(false)
const searchQuery = ref('')
const uploadDialogOpen = ref(false)
const detailDialogOpen = ref(false)
const selectedStudent = ref(null)
const excelFile = ref(null)
const majorInput = ref('')
const uploading = ref(false)
const uploadError = ref('')

// 審查相關狀態
const reviewDialogOpen = ref(false)
const reviewResultDialogOpen = ref(false)
const reviewStudent = ref(null)
const reviewMajor = ref('')
const reviewDoubleMajor = ref('')
const reviewMinors = ref([])
const reviewing = ref(false)
const reviewError = ref('')
const reviewResult = ref(null)

// 表格欄位定義
const columns = [
  {
    name: 'id',
    label: '學號',
    align: 'left',
    field: 'id',
    sortable: true,
  },
  {
    name: 'name',
    label: '姓名',
    align: 'left',
    field: 'name',
    sortable: true,
  },
  {
    name: 'major',
    label: '主修科系',
    align: 'left',
    field: 'major',
    sortable: true,
  },
  {
    name: 'actions',
    label: '操作',
    align: 'center',
    field: 'actions',
  },
]

const courseColumns = [
  {
    name: 'course_name',
    label: '課程名稱',
    align: 'left',
    field: 'course_name',
    sortable: true,
  },
  {
    name: 'course_codes',
    label: '課程代碼',
    align: 'left',
    field: 'course_codes',
    format: (val) => (val && val.length > 0 ? val.join(', ') : '-'),
  },
  {
    name: 'credit',
    label: '學分',
    align: 'center',
    field: 'credit',
    sortable: true,
  },
  {
    name: 'grade',
    label: '成績狀態',
    align: 'center',
    field: 'grade',
    sortable: true,
  },
  {
    name: 'year_taken',
    label: '修課年度',
    align: 'center',
    field: 'year_taken',
    sortable: true,
  },
  {
    name: 'semester_taken',
    label: '學期',
    align: 'center',
    field: 'semester_taken',
    sortable: true,
  },
]

// 計算屬性：過濾後的學生列表
const filteredStudents = computed(() => {
  if (!searchQuery.value) {
    return students.value
  }
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(
    (student) =>
      student.id.toLowerCase().includes(query) || student.name.toLowerCase().includes(query),
  )
})

// 載入學生列表
async function loadStudents() {
  loading.value = true
  try {
    const response = await api.get('/students/')
    if (response.data.success) {
      students.value = response.data.data
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '載入學生列表失敗：' + (error.response?.data?.detail || error.message),
      position: 'top',
    })
  } finally {
    loading.value = false
  }
}

// 查看學生詳細資料
async function viewStudentDetail(studentId) {
  try {
    const response = await api.get(`/students/${studentId}`)
    if (response.data.success) {
      selectedStudent.value = response.data.data
      detailDialogOpen.value = true
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '載入學生詳細資料失敗：' + (error.response?.data?.detail || error.message),
      position: 'top',
    })
  }
}

// 上傳 Excel
async function uploadExcel() {
  if (!excelFile.value || !majorInput.value) {
    return
  }

  uploading.value = true
  uploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('file', excelFile.value)
    formData.append('major', majorInput.value)

    const response = await api.post('/students/upload-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    if (response.data.success) {
      $q.notify({
        type: 'positive',
        message: response.data.message,
        position: 'top',
      })
      uploadDialogOpen.value = false
      excelFile.value = null
      majorInput.value = ''
      // 重新載入學生列表
      await loadStudents()
    }
  } catch (error) {
    uploadError.value = error.response?.data?.detail || error.message
    $q.notify({
      type: 'negative',
      message: '上傳失敗：' + uploadError.value,
      position: 'top',
    })
  } finally {
    uploading.value = false
  }
}

// 確認刪除
function confirmDelete(student) {
  $q.dialog({
    title: '確認刪除',
    message: `確定要刪除學生 ${student.name} (${student.id}) 的資料嗎？`,
    cancel: true,
    persistent: true,
  }).onOk(() => {
    deleteStudent(student.id)
  })
}

// 刪除學生
async function deleteStudent(studentId) {
  try {
    await api.delete(`/students/${studentId}`)
    $q.notify({
      type: 'positive',
      message: '學生資料已刪除',
      position: 'top',
    })
    await loadStudents()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '刪除失敗：' + (error.response?.data?.detail || error.message),
      position: 'top',
    })
  }
}

// 檔案選擇
function onFileSelected() {
  uploadError.value = ''
}

// 取得成績狀態
function getGradeStatus(grade) {
  if (grade === 999) return '修課中'
  if (grade === 555) return '抵免'
  if (grade >= 60) return `及格 (${grade})`
  if (grade >= 0) return `不及格 (${grade})`
  return '未知'
}

// 取得成績顏色
function getGradeColor(grade) {
  if (grade === 999) return 'blue'
  if (grade === 555) return 'purple'
  if (grade >= 60) return 'positive'
  if (grade >= 0) return 'negative'
  return 'grey'
}

// 開啟審查對話框
function openReviewDialog(student) {
  reviewStudent.value = student
  reviewMajor.value = student.major === 'AN' ? '' : student.major
  reviewDoubleMajor.value = ''
  // 不分系學生預設添加一個輔系欄位
  reviewMinors.value = student.major === 'AN' ? [''] : []
  reviewError.value = ''
  reviewDialogOpen.value = true
}

// 新增輔系
function addMinor() {
  reviewMinors.value.push('')
}

// 移除輔系
function removeMinor(index) {
  reviewMinors.value.splice(index, 1)
}

// 執行審查
async function performReview() {
  // 驗證：不分系學生必須至少有一個輔系
  if (reviewStudent.value.major === 'AN') {
    const validMinors = reviewMinors.value.filter((m) => m.trim())
    if (validMinors.length === 0) {
      reviewError.value = '不分系學生必須至少選擇一個輔系'
      return
    }
  }

  reviewing.value = true
  reviewError.value = ''

  try {
    // 構建查詢參數
    const params = new URLSearchParams()

    // 如果指定了主修（不分系學生可選，一般學生若不同於原科系）
    if (reviewMajor.value && reviewMajor.value !== reviewStudent.value.major) {
      params.append('major', reviewMajor.value)
    }

    // 雙主修
    if (reviewDoubleMajor.value) {
      params.append('double_major', reviewDoubleMajor.value)
    }

    // 輔系（過濾空值，每個輔系單獨添加）
    const minorList = reviewMinors.value.filter((m) => m && m.trim())
    minorList.forEach((m) => {
      params.append('minor', m.trim())
    })

    // 調試：打印參數
    console.log('Review params:', params.toString())
    console.log('Minor list:', minorList)

    const response = await api.post(`/review/${reviewStudent.value.id}?${params.toString()}`)

    if (response.data.success) {
      reviewResult.value = response.data.data
      reviewDialogOpen.value = false
      reviewResultDialogOpen.value = true

      $q.notify({
        type: 'positive',
        message: '審查完成',
        position: 'top',
      })
    }
  } catch (error) {
    reviewError.value = error.response?.data?.detail || error.message
    $q.notify({
      type: 'negative',
      message: '審查失敗：' + reviewError.value,
      position: 'top',
    })
  } finally {
    reviewing.value = false
  }
}

// 組件掛載時載入資料
onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>
