<template>
  <div class="review-result-tree">
    <q-card flat bordered>
      <q-card-section>
        <div class="row items-center q-mb-sm">
          <q-icon
            :name="result.is_valid ? 'check_circle' : 'cancel'"
            :color="result.is_valid ? 'positive' : 'negative'"
            size="sm"
            class="q-mr-sm"
          />
          <div class="text-h6">{{ result.name }}</div>
          <q-space />
          <q-chip :color="result.is_valid ? 'positive' : 'negative'" text-color="white" dense>
            {{ result.is_valid ? '通過' : '未通過' }}
          </q-chip>
        </div>

        <div v-if="result.description" class="text-body2 text-grey-7 q-mb-sm">
          {{ result.description }}
        </div>

        <div class="text-body2">
          <q-badge color="primary" class="q-mr-sm">
            獲得學分：{{ result.earned_credits }} 學分
          </q-badge>
          <q-badge v-if="result.result_type === 'rule_set'" color="info">
            邏輯：{{ result.sub_rule_logic === 'AND' ? '且 (全部滿足)' : '或 (任一滿足)' }}
          </q-badge>
        </div>

        <!-- RuleAll 類型：顯示課程列表 -->
        <div
          v-if="
            result.result_type === 'rule_all' &&
            result.finished_course_list &&
            result.finished_course_list.length > 0
          "
          class="q-mt-md"
        >
          <q-expansion-item
            :label="`認證課程 (${result.finished_course_list.length} 門)`"
            icon="school"
            default-opened
          >
            <q-table
              :rows="result.finished_course_list"
              :columns="courseColumns"
              row-key="course_name"
              flat
              dense
              :pagination="{ rowsPerPage: 10 }"
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
          </q-expansion-item>
        </div>

        <!-- RuleSet 類型：遞歸顯示子規則 -->
        <div
          v-if="
            result.result_type === 'rule_set' && result.sub_results && result.sub_results.length > 0
          "
          class="q-mt-md"
        >
          <div class="text-subtitle2 q-mb-sm">子規則</div>
          <div
            v-for="(subResult, index) in result.sub_results"
            :key="index"
            class="q-ml-md q-mb-sm"
          >
            <review-result-tree :result="subResult" />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  result: {
    type: Object,
    required: true,
  },
})

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
    format: (val) => (val && val.length > 0 ? val[0] : '-'),
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
    label: '年度',
    align: 'center',
    field: 'year_taken',
    format: (val) => `${val}`,
  },
  {
    name: 'semester_taken',
    label: '學期',
    align: 'center',
    field: 'semester_taken',
  },
]

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
</script>

<style scoped>
.review-result-tree {
  margin-bottom: 8px;
}
</style>
