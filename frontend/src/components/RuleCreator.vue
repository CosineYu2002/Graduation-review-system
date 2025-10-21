<template>
  <div>
    <!-- 基本資訊 -->
    <div class="q-mb-lg">
      <div class="text-h6 q-mb-md">📋 基本資訊</div>
      <q-card flat bordered>
        <q-card-section>
          <div class="q-gutter-md">
            <q-select
              v-model="formData.department_code"
              :options="departmentOptions"
              option-value="code"
              option-label="label"
              emit-value
              map-options
              label="系所 *"
              outlined
              :rules="[(val) => !!val || '請選擇系所']"
            >
              <template v-slot:prepend>
                <q-icon name="school" />
              </template>
            </q-select>

            <q-input
              v-model.number="formData.admission_year"
              type="number"
              label="入學年度 *"
              outlined
              :rules="[
                (val) => !!val || '請輸入入學年度',
                (val) => (val >= 90 && val <= 150) || '請輸入有效的學年度（90-150）',
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="calendar_today" />
              </template>
            </q-input>

            <q-select
              v-model="formData.rule_type"
              :options="[
                { label: '主修規則', value: 'major' },
                { label: '輔系規則', value: 'minor' },
                { label: '雙主修規則', value: 'double_major' },
              ]"
              option-value="value"
              option-label="label"
              emit-value
              map-options
              label="規則類型 *"
              outlined
            >
              <template v-slot:prepend>
                <q-icon name="category" />
              </template>
            </q-select>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- 規則內容表單 -->
    <div class="q-mb-lg">
      <div class="text-h6 q-mb-md">📐 規則內容</div>
      <RuleFormContent v-model="formData.rule_content" />
    </div>

    <!-- 提交按鈕 -->
    <div class="q-mt-lg text-right">
      <q-btn flat label="取消" @click="$emit('cancel')" class="q-mr-sm" />
      <q-btn
        color="positive"
        label="提交規則"
        @click="submitRule"
        :loading="submitting"
        :disable="!canSubmit"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import RuleFormContent from './RuleFormContent.vue'

const props = defineProps({
  departmentOptions: {
    type: Array,
    required: true,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
  initialData: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['submit', 'cancel'])

const formData = ref(
  props.initialData || {
    department_code: '',
    admission_year: null,
    rule_type: 'major',
    rule_content: {
      name: '',
      description: '',
      rule_type: 'rule_set',
      priority: 0,
      requirement: {
        type: 'min_credits',
        pass_or_none: false,
      },
      sub_rules: [],
      sub_rule_logic: 'AND',
    },
  },
)

const canSubmit = computed(() => {
  return (
    formData.value.department_code &&
    formData.value.admission_year &&
    formData.value.rule_content.name
  )
})

function submitRule() {
  // 清理空值
  const cleanedData = cleanupRuleData(formData.value)
  emit('submit', cleanedData)
}

function cleanupRuleData(data) {
  const cleaned = JSON.parse(JSON.stringify(data))

  // 清理 course_criteria 中的 null 值
  if (cleaned.rule_content.course_criteria) {
    Object.keys(cleaned.rule_content.course_criteria).forEach((key) => {
      if (
        cleaned.rule_content.course_criteria[key] === null ||
        cleaned.rule_content.course_criteria[key] === undefined
      ) {
        delete cleaned.rule_content.course_criteria[key]
      }
    })
  }

  // 清理 requirement 中的 null 值
  if (cleaned.rule_content.requirement) {
    Object.keys(cleaned.rule_content.requirement).forEach((key) => {
      if (
        cleaned.rule_content.requirement[key] === null ||
        cleaned.rule_content.requirement[key] === undefined
      ) {
        delete cleaned.rule_content.requirement[key]
      }
    })
  }

  // 如果是 RuleSet，移除不需要的欄位
  if (cleaned.rule_content.rule_type === 'rule_set') {
    delete cleaned.rule_content.course_criteria
    delete cleaned.rule_content.course_list
  }

  // 如果是 RuleAll，移除不需要的欄位
  if (cleaned.rule_content.rule_type === 'rule_all') {
    delete cleaned.rule_content.sub_rules
    delete cleaned.rule_content.sub_rule_logic
  }

  return cleaned
}

function resetForm() {
  formData.value = {
    department_code: '',
    admission_year: null,
    rule_type: 'major',
    rule_content: {
      name: '',
      description: '',
      rule_type: 'rule_set',
      priority: 0,
      requirement: {
        type: 'min_credits',
        pass_or_none: false,
      },
      sub_rules: [],
      sub_rule_logic: 'AND',
    },
  }
}

defineExpose({
  resetForm,
})
</script>

<style scoped>
.rounded-borders {
  border-radius: 8px;
}
</style>
