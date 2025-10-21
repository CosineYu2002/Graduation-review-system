<template>
  <div class="rule-tree">
    <q-card flat bordered>
      <q-card-section>
        <div class="row items-center q-mb-sm">
          <q-icon
            :name="rule.rule_type === 'rule_set' ? 'account_tree' : 'list_alt'"
            :color="rule.rule_type === 'rule_set' ? 'primary' : 'positive'"
            size="sm"
            class="q-mr-sm"
          />
          <div class="text-h6">{{ rule.name }}</div>
          <q-space />
          <q-chip
            :color="rule.rule_type === 'rule_set' ? 'primary' : 'positive'"
            text-color="white"
            dense
          >
            {{ rule.rule_type === 'rule_set' ? 'RuleSet' : 'RuleAll' }}
          </q-chip>
        </div>

        <div v-if="rule.description" class="text-body2 text-grey-7 q-mb-sm">
          {{ rule.description }}
        </div>

        <!-- 要求資訊 -->
        <div v-if="rule.requirement" class="q-mt-md">
          <div class="text-subtitle2 q-mb-xs">📋 畢業要求</div>
          <div class="requirement-badges">
            <q-badge
              v-if="rule.requirement.credits !== undefined"
              color="blue"
              class="q-mr-sm q-mb-xs"
            >
              學分要求：{{ rule.requirement.credits }} 學分
            </q-badge>
            <q-badge
              v-if="rule.requirement.passed_courses !== undefined"
              color="green"
              class="q-mr-sm q-mb-xs"
            >
              課程數量：{{ rule.requirement.passed_courses }} 門
            </q-badge>
            <q-badge
              v-if="rule.requirement.min_credits !== undefined"
              color="orange"
              class="q-mr-sm q-mb-xs"
            >
              最低學分：{{ rule.requirement.min_credits }} 學分
            </q-badge>
            <q-badge
              v-if="rule.requirement.max_credits !== undefined"
              color="purple"
              class="q-mr-sm q-mb-xs"
            >
              最高學分：{{ rule.requirement.max_credits }} 學分
            </q-badge>
            <!-- 顯示其他 requirement 欄位 -->
            <template v-for="(value, key) in otherRequirements" :key="key">
              <q-badge color="grey" class="q-mr-sm q-mb-xs">
                {{ formatKey(key) }}：{{ value }}
              </q-badge>
            </template>
          </div>
        </div>

        <!-- RuleSet 專用：子規則邏輯 -->
        <div v-if="rule.rule_type === 'rule_set' && rule.sub_rule_logic" class="q-mt-sm">
          <q-badge color="info">
            邏輯：{{ rule.sub_rule_logic === 'AND' ? '且 (全部滿足)' : '或 (任一滿足)' }}
          </q-badge>
        </div>

        <!-- RuleAll 專用：課程條件 -->
        <div v-if="rule.rule_type === 'rule_all' && rule.course_criteria" class="q-mt-md">
          <div class="text-subtitle2 q-mb-xs">🔍 課程篩選條件</div>
          <div class="criteria-section bg-orange-1 rounded-borders q-pa-sm">
            <div v-for="(value, key) in rule.course_criteria" :key="key" class="criteria-item">
              <strong>{{ formatCriteriaKey(key) }}：</strong>
              <span>{{ formatCriteriaValue(value) }}</span>
            </div>
          </div>
        </div>

        <!-- RuleAll 專用：指定課程列表 -->
        <div
          v-if="rule.rule_type === 'rule_all' && rule.course_list && rule.course_list.length > 0"
          class="q-mt-md"
        >
          <q-expansion-item
            :label="`📚 指定課程列表 (${rule.course_list.length} 門)`"
            icon="list"
            default-opened
            header-class="bg-purple-1"
          >
            <q-card flat bordered>
              <q-card-section>
                <div class="course-chips">
                  <q-chip
                    v-for="(course, index) in rule.course_list"
                    :key="index"
                    color="purple-2"
                    text-color="purple-9"
                    size="sm"
                  >
                    {{ course }}
                  </q-chip>
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </div>

        <!-- RuleSet 專用：遞迴顯示子規則 -->
        <div
          v-if="rule.rule_type === 'rule_set' && rule.sub_rules && rule.sub_rules.length > 0"
          class="q-mt-md"
        >
          <div class="text-subtitle2 q-mb-sm">🌳 子規則 ({{ rule.sub_rules.length }} 項)</div>
          <div class="sub-rules-container">
            <RuleTree
              v-for="(subRule, index) in rule.sub_rules"
              :key="index"
              :rule="subRule"
              class="q-mb-sm"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rule: {
    type: Object,
    required: true,
  },
})

// 計算其他 requirement 欄位
const otherRequirements = computed(() => {
  if (!props.rule.requirement) return {}
  const knownKeys = ['credits', 'passed_courses', 'min_credits', 'max_credits']
  const result = {}
  Object.keys(props.rule.requirement).forEach((key) => {
    if (!knownKeys.includes(key)) {
      result[key] = props.rule.requirement[key]
    }
  })
  return result
})

// 格式化鍵名
function formatKey(key) {
  const keyMap = {
    min_grade: '最低成績',
    max_grade: '最高成績',
    year: '年級',
    semester: '學期',
  }
  return keyMap[key] || key
}

// 格式化課程條件鍵名
function formatCriteriaKey(key) {
  const keyMap = {
    department: '開課系所',
    course_type: '課程類型',
    level: '課程等級',
    grade: '年級',
    semester: '學期',
    min_credits: '最低學分',
    max_credits: '最高學分',
  }
  return keyMap[key] || key
}

// 格式化課程條件值
function formatCriteriaValue(value) {
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return value
}
</script>

<style scoped>
.rule-tree {
  width: 100%;
}

.requirement-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.criteria-section {
  border-radius: 8px;
}

.criteria-item {
  padding: 4px 0;
}

.criteria-item strong {
  color: #f57c00;
  margin-right: 8px;
}

.course-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sub-rules-container {
  padding-left: 16px;
  border-left: 3px solid #e0e0e0;
}

.rounded-borders {
  border-radius: 8px;
}
</style>
