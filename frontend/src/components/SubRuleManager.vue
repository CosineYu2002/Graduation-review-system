<template>
  <div>
    <div class="text-subtitle2 q-mb-md">📚 子規則管理</div>

    <!-- 子規則列表 -->
    <q-list bordered separator v-if="modelValue && modelValue.length > 0">
      <q-item v-for="(subRule, index) in modelValue" :key="index">
        <q-item-section avatar>
          <q-icon
            :name="subRule.rule_type === 'rule_set' ? 'account_tree' : 'list_alt'"
            :color="subRule.rule_type === 'rule_set' ? 'primary' : 'positive'"
          />
        </q-item-section>

        <q-item-section>
          <q-item-label>{{ subRule.name }}</q-item-label>
          <q-item-label caption>
            {{ subRule.rule_type === 'rule_set' ? 'RuleSet' : 'RuleAll' }}
            <span v-if="subRule.description"> - {{ subRule.description }}</span>
          </q-item-label>
          <q-item-label caption class="q-mt-xs">
            <q-badge v-if="subRule.requirement.type" color="grey-7" text-color="white" size="sm">
              {{ getRequirementTypeLabel(subRule.requirement.type) }}
            </q-badge>
            <q-badge
              v-if="subRule.requirement.min_credits"
              color="positive"
              text-color="white"
              size="sm"
              class="q-ml-xs"
            >
              ≥{{ subRule.requirement.min_credits }}學分
            </q-badge>
            <q-badge
              v-if="subRule.requirement.max_credits"
              color="warning"
              text-color="white"
              size="sm"
              class="q-ml-xs"
            >
              ≤{{ subRule.requirement.max_credits }}學分
            </q-badge>
            <q-badge
              v-if="subRule.rule_type === 'rule_set' && subRule.sub_rules"
              color="blue-grey"
              text-color="white"
              size="sm"
              class="q-ml-xs"
            >
              {{ subRule.sub_rules.length }} 個子規則
            </q-badge>
          </q-item-label>
        </q-item-section>

        <q-item-section side>
          <div class="q-gutter-xs">
            <q-btn flat dense round color="primary" icon="edit" @click="editSubRule(index)">
              <q-tooltip>編輯</q-tooltip>
            </q-btn>
            <q-btn flat dense round color="negative" icon="delete" @click="deleteSubRule(index)">
              <q-tooltip>刪除</q-tooltip>
            </q-btn>
          </div>
        </q-item-section>
      </q-item>
    </q-list>

    <div v-else class="text-center q-pa-md bg-grey-2 rounded-borders">
      <q-icon name="inbox" size="3em" color="grey-5" />
      <div class="text-grey-7 q-mt-sm">尚無子規則</div>
    </div>

    <!-- 新增子規則按鈕 -->
    <div class="q-mt-md">
      <q-btn color="primary" icon="add" label="新增子規則" @click="openSubRuleDialog" outline />
    </div>

    <!-- 子規則編輯對話框 -->
    <q-dialog v-model="subRuleDialogOpen" persistent maximized>
      <q-card>
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editingIndex !== null ? '編輯' : '新增' }}子規則</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="closeSubRuleDialog" />
        </q-card-section>

        <q-separator />

        <q-card-section style="max-height: calc(100vh - 120px); overflow-y: auto">
          <RuleFormContent
            v-if="currentSubRule"
            ref="subRuleFormRef"
            v-model="currentSubRule"
            :is-sub-rule="true"
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn flat label="取消" @click="closeSubRuleDialog" />
          <q-btn color="primary" label="確認" @click="saveSubRule" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import RuleFormContent from './RuleFormContent.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const $q = useQuasar()

const subRuleDialogOpen = ref(false)
const editingIndex = ref(null)
const currentSubRule = ref({
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
})
const subRuleFormRef = ref(null)

const requirementTypeLabels = {
  min_credits: '最少學分數',
  max_credits: '最多學分數',
  credit_range: '學分區間',
  min_courses: '最少課程數',
  max_courses: '最多課程數',
  all: '全部課程',
  meaningless: '無限制',
  prerequisite: '先修',
}

function getRequirementTypeLabel(type) {
  return requirementTypeLabels[type] || type
}

function openSubRuleDialog() {
  editingIndex.value = null
  currentSubRule.value = {
    name: '',
    description: '',
    rule_type: 'rule_set',
    priority: 0,
    requirement: {
      type: 'min_credits',
      min_credits: null,
      max_credits: null,
      min_courses: null,
      max_courses: null,
      pass_or_none: false,
    },
    sub_rules: [],
    sub_rule_logic: 'AND',
    course_criteria: {
      course_name_pattern: null,
      course_code_pattern: null,
      department_codes: null,
      exclude_department_codes: null,
      course_types: null,
      categories: null,
      tags: null,
      whitelist_courses: null,
      blacklist_courses: null,
      exclude_same_name: true,
      allow_fail: false,
      series_courses: false,
      allow_external_substitute_after_fail: false,
    },
    course_list: null,
  }
  subRuleDialogOpen.value = true
}

function editSubRule(index) {
  editingIndex.value = index
  // Deep clone to avoid modifying original
  currentSubRule.value = JSON.parse(JSON.stringify(props.modelValue[index]))
  subRuleDialogOpen.value = true
}

function deleteSubRule(index) {
  $q.dialog({
    title: '確認刪除',
    message: '確定要刪除此子規則嗎？',
    cancel: true,
    persistent: true,
  }).onOk(() => {
    const newSubRules = [...props.modelValue]
    newSubRules.splice(index, 1)
    emit('update:modelValue', newSubRules)
  })
}

function saveSubRule() {
  // Validate
  if (!currentSubRule.value.name) {
    $q.notify({
      type: 'warning',
      message: '請輸入規則名稱',
    })
    return
  }

  // Clean up null values
  const cleanedRule = cleanupRule(currentSubRule.value)

  const newSubRules = [...props.modelValue]
  if (editingIndex.value !== null) {
    newSubRules[editingIndex.value] = cleanedRule
  } else {
    newSubRules.push(cleanedRule)
  }

  emit('update:modelValue', newSubRules)
  closeSubRuleDialog()
}

function closeSubRuleDialog() {
  subRuleDialogOpen.value = false
  editingIndex.value = null
  currentSubRule.value = null
}

function cleanupRule(rule) {
  const cleaned = JSON.parse(JSON.stringify(rule))

  // Clean course_criteria
  if (cleaned.course_criteria) {
    Object.keys(cleaned.course_criteria).forEach((key) => {
      if (cleaned.course_criteria[key] === null || cleaned.course_criteria[key] === undefined) {
        delete cleaned.course_criteria[key]
      }
    })
  }

  // Clean requirement
  if (cleaned.requirement) {
    Object.keys(cleaned.requirement).forEach((key) => {
      if (cleaned.requirement[key] === null || cleaned.requirement[key] === undefined) {
        delete cleaned.requirement[key]
      }
    })
  }

  // Remove unnecessary fields based on rule_type
  if (cleaned.rule_type === 'rule_set') {
    delete cleaned.course_criteria
    delete cleaned.course_list
  } else if (cleaned.rule_type === 'rule_all') {
    delete cleaned.sub_rules
    delete cleaned.sub_rule_logic
  }

  return cleaned
}
</script>

<style scoped>
.rounded-borders {
  border-radius: 8px;
}
</style>
