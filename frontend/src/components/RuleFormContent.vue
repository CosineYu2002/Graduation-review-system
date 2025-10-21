<template>
  <q-stepper v-model="step" vertical color="primary" animated>
    <!-- 步驟 1: 規則結構 -->
    <q-step :name="1" title="規則結構" icon="account_tree" :done="step > 1">
      <div class="q-gutter-md">
        <q-input
          v-model="localRule.name"
          label="規則名稱 *"
          outlined
          :rules="[(val) => !!val || '請輸入規則名稱']"
        >
          <template v-slot:prepend>
            <q-icon name="title" />
          </template>
        </q-input>

        <q-input v-model="localRule.description" label="規則描述" type="textarea" outlined rows="2">
          <template v-slot:prepend>
            <q-icon name="description" />
          </template>
        </q-input>

        <q-select
          v-model="localRule.rule_type"
          :options="ruleTypeOptions"
          option-value="value"
          option-label="label"
          emit-value
          map-options
          label="規則結構類型 *"
          outlined
          @update:model-value="onRuleTypeChange"
        >
          <template v-slot:prepend>
            <q-icon name="account_tree" />
          </template>
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section avatar>
                <q-icon :name="scope.opt.icon" :color="scope.opt.color" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ scope.opt.label }}</q-item-label>
                <q-item-label caption>{{ scope.opt.description }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>

        <q-input
          v-model.number="localRule.priority"
          type="number"
          label="優先級"
          outlined
          hint="數字越小優先級越高"
        >
          <template v-slot:prepend>
            <q-icon name="low_priority" />
          </template>
        </q-input>
      </div>

      <q-stepper-navigation>
        <q-btn @click="nextStep" color="primary" label="下一步" :disable="!canProceedStep1" />
      </q-stepper-navigation>
    </q-step>

    <!-- 步驟 2: 規則要求 -->
    <q-step :name="2" title="規則要求" icon="assignment" :done="step > 2">
      <div class="q-mb-md">
        <div class="text-subtitle2 q-mb-sm">📋 畢業要求設定</div>
        <q-card flat bordered>
          <q-card-section>
            <q-select
              v-model="requirementType"
              :options="requirementTypeOptions"
              option-value="value"
              option-label="label"
              emit-value
              map-options
              label="要求類型 *"
              outlined
              @update:model-value="onRequirementTypeChange"
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    <q-item-label>{{ scope.opt.label }}</q-item-label>
                    <q-item-label caption>{{ scope.opt.description }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

            <div v-if="requirementType" class="q-mt-md q-gutter-md">
              <!-- 最少學分數 -->
              <q-input
                v-if="requirementType === 'min_credits'"
                v-model.number="localRule.requirement.min_credits"
                type="number"
                label="最少學分數 *"
                outlined
                :rules="[(val) => val >= 0 || '學分數不能為負']"
              >
                <template v-slot:prepend>
                  <q-icon name="school" color="positive" />
                </template>
              </q-input>

              <!-- 最多學分數 -->
              <q-input
                v-if="requirementType === 'max_credits'"
                v-model.number="localRule.requirement.max_credits"
                type="number"
                label="最多學分數 *"
                outlined
                :rules="[(val) => val >= 0 || '學分數不能為負']"
              >
                <template v-slot:prepend>
                  <q-icon name="school" color="warning" />
                </template>
              </q-input>

              <!-- 學分區間 -->
              <template v-if="requirementType === 'credit_range'">
                <q-input
                  v-model.number="localRule.requirement.min_credits"
                  type="number"
                  label="最少學分數 *"
                  outlined
                  :rules="[(val) => val >= 0 || '學分數不能為負']"
                >
                  <template v-slot:prepend>
                    <q-icon name="school" color="positive" />
                  </template>
                </q-input>
                <q-input
                  v-model.number="localRule.requirement.max_credits"
                  type="number"
                  label="最多學分數 *"
                  outlined
                  :rules="[
                    (val) => val >= 0 || '學分數不能為負',
                    (val) =>
                      val >= (localRule.requirement.min_credits || 0) || '最多學分不能小於最少學分',
                  ]"
                >
                  <template v-slot:prepend>
                    <q-icon name="school" color="warning" />
                  </template>
                </q-input>
              </template>

              <!-- 最少課程數 -->
              <q-input
                v-if="requirementType === 'min_courses'"
                v-model.number="localRule.requirement.min_courses"
                type="number"
                label="最少課程數量 *"
                outlined
                :rules="[(val) => val >= 0 || '課程數量不能為負']"
              >
                <template v-slot:prepend>
                  <q-icon name="list" color="positive" />
                </template>
              </q-input>

              <!-- 最多課程數 -->
              <q-input
                v-if="requirementType === 'max_courses'"
                v-model.number="localRule.requirement.max_courses"
                type="number"
                label="最多課程數量 *"
                outlined
                :rules="[(val) => val >= 0 || '課程數量不能為負']"
              >
                <template v-slot:prepend>
                  <q-icon name="list" color="warning" />
                </template>
              </q-input>

              <!-- pass_or_none 選項 -->
              <q-checkbox
                v-model="localRule.requirement.pass_or_none"
                label="如果規則不符合，獲得學分數計算為0"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <q-stepper-navigation>
        <q-btn flat @click="step = 1" color="primary" label="上一步" class="q-mr-sm" />
        <q-btn @click="nextStep" color="primary" label="下一步" :disable="!canProceedStep2" />
      </q-stepper-navigation>
    </q-step>

    <!-- 步驟 3: 規則內容（根據類型不同） -->
    <q-step :name="3" title="規則內容" icon="edit" :done="step > 3">
      <!-- RuleSet: 子規則管理 -->
      <div v-if="localRule.rule_type === 'rule_set'" class="q-gutter-md">
        <q-select
          v-model="localRule.sub_rule_logic"
          :options="[
            { label: 'AND (全部滿足)', value: 'AND' },
            { label: 'OR (任一滿足)', value: 'OR' },
          ]"
          option-value="value"
          option-label="label"
          emit-value
          map-options
          label="子規則邏輯 *"
          outlined
        >
          <template v-slot:prepend>
            <q-icon name="call_split" />
          </template>
        </q-select>

        <SubRuleManager v-model="localRule.sub_rules" />
      </div>

      <!-- RuleAll: 課程篩選條件和課程列表 -->
      <div v-if="localRule.rule_type === 'rule_all'" class="q-gutter-md">
        <div class="text-subtitle2">🔍 課程篩選條件</div>
        <q-card flat bordered>
          <q-card-section>
            <div class="q-gutter-md">
              <q-input
                v-model="localRule.course_criteria.course_name_pattern"
                label="課程名稱模式（正則表達式）"
                outlined
                hint="例如：微積分.*"
              >
                <template v-slot:prepend>
                  <q-icon name="text_fields" />
                </template>
              </q-input>

              <q-input
                v-model="localRule.course_criteria.course_code_pattern"
                label="課程代碼模式（正則表達式）"
                outlined
                hint="例如：H5.*"
              >
                <template v-slot:prepend>
                  <q-icon name="tag" />
                </template>
              </q-input>

              <q-select
                v-model="localRule.course_criteria.department_codes"
                use-input
                use-chips
                multiple
                input-debounce="0"
                label="允許的系所代碼"
                outlined
                hint="可輸入多個系所代碼"
              >
                <template v-slot:prepend>
                  <q-icon name="domain" />
                </template>
              </q-select>

              <q-select
                v-model="localRule.course_criteria.course_types"
                use-chips
                multiple
                :options="[
                  { label: '必修', value: 1 },
                  { label: '選修', value: 2 },
                  { label: '通識', value: 3 },
                ]"
                option-value="value"
                option-label="label"
                emit-value
                map-options
                label="課程類型"
                outlined
              >
                <template v-slot:prepend>
                  <q-icon name="category" />
                </template>
              </q-select>

              <q-checkbox
                v-model="localRule.course_criteria.exclude_same_name"
                label="排除跟本系同名課程"
              />

              <q-checkbox
                v-model="localRule.course_criteria.allow_fail"
                label="允許未通過的課程計入"
              />

              <q-checkbox
                v-model="localRule.course_criteria.series_courses"
                label="必須修完完整課程系列"
              />
            </div>
          </q-card-section>
        </q-card>

        <div class="text-subtitle2 q-mt-md">📚 指定課程列表（選填）</div>
        <q-card flat bordered>
          <q-card-section>
            <q-select
              v-model="localRule.course_list"
              use-input
              use-chips
              multiple
              input-debounce="0"
              label="課程名稱列表"
              outlined
              hint="輸入課程名稱，按 Enter 新增"
              @new-value="addCourse"
            >
              <template v-slot:prepend>
                <q-icon name="list" />
              </template>
            </q-select>
          </q-card-section>
        </q-card>
      </div>

      <q-stepper-navigation>
        <q-btn flat @click="step = 2" color="primary" label="上一步" class="q-mr-sm" />
        <q-btn @click="emitUpdate" color="positive" label="完成" />
      </q-stepper-navigation>
    </q-step>
  </q-stepper>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import SubRuleManager from './SubRuleManager.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
  isSubRule: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const step = ref(1)
const requirementType = ref(props.modelValue?.requirement?.type || 'min_credits')
const localRule = ref(JSON.parse(JSON.stringify(props.modelValue)))

let isUpdating = false

// Watch for external changes only
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && !isUpdating) {
      const newValStr = JSON.stringify(newVal)
      const localStr = JSON.stringify(localRule.value)
      if (newValStr !== localStr) {
        localRule.value = JSON.parse(newValStr)
        if (newVal.requirement?.type) {
          requirementType.value = newVal.requirement.type
        }
      }
    }
  },
  { deep: true },
)

// Watch local changes and emit
watch(
  localRule,
  (newVal) => {
    isUpdating = true
    emit('update:modelValue', JSON.parse(JSON.stringify(newVal)))
    nextTick(() => {
      isUpdating = false
    })
  },
  { deep: true },
)

const ruleTypeOptions = [
  {
    label: 'RuleSet (規則集)',
    value: 'rule_set',
    icon: 'account_tree',
    color: 'primary',
    description: '包含多個子規則的規則集合，可設定 AND/OR 邏輯',
  },
  {
    label: 'RuleAll (課程列表)',
    value: 'rule_all',
    icon: 'list_alt',
    color: 'positive',
    description: '針對特定課程列表或課程條件的規則',
  },
]

const requirementTypeOptions = [
  { label: '最少學分數', value: 'min_credits', description: '至少需要修滿指定學分' },
  { label: '最多學分數', value: 'max_credits', description: '最多只能計入指定學分' },
  { label: '學分區間', value: 'credit_range', description: '學分數必須在指定區間內' },
  { label: '最少課程數', value: 'min_courses', description: '至少需要修滿指定數量的課程' },
  { label: '最多課程數', value: 'max_courses', description: '最多只能計入指定數量的課程' },
  { label: '全部課程', value: 'all', description: '需修完所有指定課程' },
  { label: '無限制', value: 'meaningless', description: '沒有特定要求' },
]

const canProceedStep1 = computed(() => {
  return localRule.value.name && localRule.value.rule_type
})

const canProceedStep2 = computed(() => {
  if (!requirementType.value) return false

  const req = localRule.value.requirement
  switch (requirementType.value) {
    case 'min_credits':
      return req.min_credits !== null && req.min_credits >= 0
    case 'max_credits':
      return req.max_credits !== null && req.max_credits >= 0
    case 'credit_range':
      return (
        req.min_credits !== null &&
        req.max_credits !== null &&
        req.min_credits >= 0 &&
        req.max_credits >= req.min_credits
      )
    case 'min_courses':
      return req.min_courses !== null && req.min_courses >= 0
    case 'max_courses':
      return req.max_courses !== null && req.max_courses >= 0
    case 'all':
    case 'meaningless':
    case 'prerequisite':
      return true
    default:
      return false
  }
})

function nextStep() {
  if (step.value < 3) {
    step.value++
  }
}

function onRuleTypeChange(newType) {
  // 根據規則類型初始化不同的預設值
  if (newType === 'rule_all') {
    if (!localRule.value.course_criteria) {
      localRule.value.course_criteria = {
        exclude_same_name: true,
        allow_fail: false,
        series_courses: false,
        allow_external_substitute_after_fail: false,
      }
    }
    // 清除 RuleSet 特有欄位
    delete localRule.value.sub_rules
    delete localRule.value.sub_rule_logic
  } else if (newType === 'rule_set') {
    localRule.value.sub_rule_logic = 'AND'
    if (!localRule.value.sub_rules) {
      localRule.value.sub_rules = []
    }
    // 清除 RuleAll 特有欄位
    delete localRule.value.course_criteria
    delete localRule.value.course_list
  }
}

function onRequirementTypeChange(newType) {
  // 清空所有要求值
  localRule.value.requirement = {
    type: newType,
    min_credits: null,
    max_credits: null,
    min_courses: null,
    max_courses: null,
    pass_or_none: false,
  }
}

function addCourse(val, done) {
  if (val.length > 0) {
    if (!localRule.value.course_list) {
      localRule.value.course_list = []
    }
    done(val, 'add-unique')
  }
}

function emitUpdate() {
  emit('update:modelValue', localRule.value)
}

function resetForm() {
  step.value = 1
  requirementType.value = 'min_credits'
  localRule.value = {
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
      exclude_same_name: true,
      allow_fail: false,
      series_courses: false,
    },
    course_list: null,
  }
}

defineExpose({
  resetForm,
})
</script>

<style scoped>
:deep(.q-stepper__step-inner) {
  padding: 24px;
}
</style>
