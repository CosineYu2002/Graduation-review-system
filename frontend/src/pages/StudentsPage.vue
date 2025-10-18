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
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

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
