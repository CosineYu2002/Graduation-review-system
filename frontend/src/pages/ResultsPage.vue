<template>
  <q-page padding>
    <div class="q-pa-md">
      <div class="row items-center q-mb-md">
        <div class="text-h4 q-mr-md">審查結果管理</div>
        <q-space />
        <q-btn
          color="negative"
          icon="delete_sweep"
          label="刪除所有結果"
          @click="confirmDeleteAll"
          :disable="results.length === 0"
        />
      </div>

      <!-- 結果列表 -->
      <q-table
        :rows="results"
        :columns="columns"
        row-key="file_name"
        :loading="loading"
        :pagination="pagination"
        flat
        bordered
      >
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn
              flat
              dense
              round
              icon="visibility"
              color="primary"
              @click="viewResult(props.row)"
            >
              <q-tooltip>查看詳細</q-tooltip>
            </q-btn>
            <q-btn
              flat
              dense
              round
              icon="delete"
              color="negative"
              @click="confirmDelete(props.row)"
            >
              <q-tooltip>刪除</q-tooltip>
            </q-btn>
          </q-td>
        </template>

        <template v-slot:loading>
          <q-inner-loading showing color="primary" />
        </template>
      </q-table>
    </div>

    <!-- 結果詳細查看對話框 -->
    <q-dialog v-model="showResultDialog" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">審查結果詳細</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section v-if="selectedResult">
          <!-- 學生基本資訊 -->
          <div class="q-mb-md">
            <q-banner class="bg-grey-2 rounded-borders">
              <template v-slot:avatar>
                <q-icon name="person" color="primary" />
              </template>
              <div class="row q-gutter-md">
                <div><strong>姓名：</strong>{{ selectedResult.name }}</div>
                <div><strong>學號：</strong>{{ selectedResult.id }}</div>
                <div><strong>科系：</strong>{{ selectedResult.major }}</div>
                <div><strong>入學年度：</strong>{{ selectedResult.admission_year }}</div>
              </div>
            </q-banner>
          </div>

          <!-- 審查結果樹狀圖 -->
          <div v-if="selectedResult.main">
            <ReviewResultTree :result="selectedResult.main" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- 刪除確認對話框 -->
    <q-dialog v-model="showDeleteDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">確認刪除</div>
        </q-card-section>

        <q-card-section>
          {{ deleteMessage }}
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn flat label="確認刪除" color="negative" @click="executeDelete" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import ReviewResultTree from 'components/ReviewResultTree.vue'

const $q = useQuasar()

// 資料狀態
const results = ref([])
const loading = ref(false)
const selectedResult = ref(null)
const showResultDialog = ref(false)
const showDeleteDialog = ref(false)
const deleteMessage = ref('')
const deleteAction = ref(null)

// 分頁設定
const pagination = ref({
  rowsPerPage: 10,
})

// 表格欄位定義
const columns = [
  {
    name: 'file_name',
    label: '檔案名稱',
    field: 'file_name',
    align: 'left',
    sortable: true,
  },
  {
    name: 'student_id',
    label: '學號',
    field: 'student_id',
    align: 'left',
    sortable: true,
  },
  {
    name: 'student_name',
    label: '姓名',
    field: 'student_name',
    align: 'left',
    sortable: true,
  },
  {
    name: 'actions',
    label: '操作',
    field: 'actions',
    align: 'center',
  },
]

// 載入所有結果
const loadResults = async () => {
  loading.value = true
  try {
    const response = await api.get('/results/')
    if (response.data.success) {
      results.value = response.data.data
      $q.notify({
        type: 'positive',
        message: response.data.message,
      })
    }
  } catch (error) {
    console.error('載入結果失敗:', error)
    $q.notify({
      type: 'negative',
      message: '載入結果失敗: ' + (error.response?.data?.detail || error.message),
    })
  } finally {
    loading.value = false
  }
}

// 查看結果詳細
const viewResult = async (result) => {
  try {
    const response = await api.get(`/results/file/${result.file_name}`)
    if (response.data.success) {
      selectedResult.value = response.data.data
      showResultDialog.value = true
    }
  } catch (error) {
    console.error('載入結果詳細失敗:', error)
    $q.notify({
      type: 'negative',
      message: '載入結果詳細失敗: ' + (error.response?.data?.detail || error.message),
    })
  }
}

// 確認刪除單一結果
const confirmDelete = (result) => {
  deleteMessage.value = `確定要刪除 ${result.student_name} (${result.student_id}) 的審查結果嗎？\n檔案：${result.file_name}`
  deleteAction.value = async () => {
    try {
      const response = await api.delete(`/results/file/${result.file_name}`)
      if (response.data.success) {
        $q.notify({
          type: 'positive',
          message: response.data.message,
        })
        await loadResults()
      }
    } catch (error) {
      console.error('刪除失敗:', error)
      $q.notify({
        type: 'negative',
        message: '刪除失敗: ' + (error.response?.data?.detail || error.message),
      })
    }
  }
  showDeleteDialog.value = true
}

// 確認刪除所有結果
const confirmDeleteAll = () => {
  deleteMessage.value = `⚠️ 警告：此操作將刪除所有 ${results.value.length} 筆審查記錄，無法復原！\n\n確定要繼續嗎？`
  deleteAction.value = async () => {
    try {
      const response = await api.delete('/results/')
      if (response.data.success) {
        $q.notify({
          type: 'positive',
          message: response.data.message,
        })
        await loadResults()
      }
    } catch (error) {
      console.error('刪除所有結果失敗:', error)
      $q.notify({
        type: 'negative',
        message: '刪除失敗: ' + (error.response?.data?.detail || error.message),
      })
    }
  }
  showDeleteDialog.value = true
}

// 執行刪除操作
const executeDelete = () => {
  if (deleteAction.value) {
    deleteAction.value()
  }
}

// 組件掛載時載入資料
onMounted(() => {
  loadResults()
})
</script>

<style scoped>
.rounded-borders {
  border-radius: 8px;
}
</style>
