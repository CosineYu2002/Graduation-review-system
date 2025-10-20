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
      <q-dialog v-model="createDialogOpen" persistent>
        <q-card style="min-width: 600px; max-width: 800px">
          <q-card-section class="row items-center">
            <div class="text-h6">新增規則</div>
            <q-space />
            <q-btn icon="close" flat round dense @click="closeCreateDialog" />
          </q-card-section>

          <q-separator />

          <q-card-section class="q-pt-md" style="max-height: 60vh; overflow-y: auto">
            <q-form @submit="submitCreateRule" class="q-gutter-md">
              <!-- 系所選擇 -->
              <q-select
                v-model="newRule.department_code"
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

              <!-- 入學年度 -->
              <q-input
                v-model.number="newRule.admission_year"
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

              <!-- 規則類型 -->
              <q-select
                v-model="newRule.rule_type"
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

              <!-- 規則名稱 -->
              <q-input
                v-model="newRule.rule_content.name"
                label="規則名稱 *"
                outlined
                :rules="[(val) => !!val || '請輸入規則名稱']"
              >
                <template v-slot:prepend>
                  <q-icon name="title" />
                </template>
              </q-input>

              <!-- 規則描述 -->
              <q-input
                v-model="newRule.rule_content.description"
                label="規則描述"
                type="textarea"
                outlined
                rows="3"
              >
                <template v-slot:prepend>
                  <q-icon name="description" />
                </template>
              </q-input>

              <!-- 規則類型 (RuleSet/RuleAll) -->
              <q-select
                v-model="newRule.rule_content.rule_type"
                :options="[
                  { label: 'RuleSet (規則集)', value: 'rule_set' },
                  { label: 'RuleAll (全部課程)', value: 'rule_all' },
                ]"
                option-value="value"
                option-label="label"
                emit-value
                map-options
                label="規則結構類型 *"
                outlined
              >
                <template v-slot:prepend>
                  <q-icon name="account_tree" />
                </template>
              </q-select>

              <!-- 優先級 -->
              <q-input
                v-model.number="newRule.rule_content.priority"
                type="number"
                label="優先級"
                outlined
                hint="數字越小優先級越高"
              >
                <template v-slot:prepend>
                  <q-icon name="low_priority" />
                </template>
              </q-input>

              <!-- 規則 JSON 內容 -->
              <div class="q-mt-md">
                <div class="text-subtitle2 q-mb-sm">規則內容 (JSON格式)</div>
                <q-input
                  v-model="ruleJsonInput"
                  type="textarea"
                  outlined
                  rows="10"
                  placeholder='請輸入完整的規則 JSON，例如：
{
  "requirement": {
    "credits": 128,
    "passed_courses": 0
  },
  "sub_rules": [],
  "sub_rule_logic": "AND"
}'
                  :rules="[validateJson]"
                  @update:model-value="parseRuleJson"
                />
                <div class="text-caption text-grey q-mt-xs">
                  * 請參考現有規則檔案格式，需包含 requirement 等必要欄位
                </div>
              </div>
            </q-form>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <q-btn flat label="取消" @click="closeCreateDialog" />
            <q-btn color="primary" label="新增" @click="submitCreateRule" :loading="submitting" />
          </q-card-actions>
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

          <q-card-section style="max-height: 80vh; overflow-y: auto">
            <div v-if="selectedRule">
              <!-- 基本資訊 -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle1 text-weight-bold q-mb-md">基本資訊</div>
                  <div class="row q-col-gutter-md">
                    <div class="col-6">
                      <div class="text-caption text-grey">系所代碼</div>
                      <div class="text-body1">{{ selectedRule.basic_info.department_code }}</div>
                    </div>
                    <div class="col-6">
                      <div class="text-caption text-grey">系所名稱</div>
                      <div class="text-body1">{{ selectedRule.basic_info.department_name }}</div>
                    </div>
                    <div class="col-6">
                      <div class="text-caption text-grey">入學年度</div>
                      <div class="text-body1">{{ selectedRule.basic_info.admission_year }}</div>
                    </div>
                    <div class="col-6">
                      <div class="text-caption text-grey">所屬學院</div>
                      <div class="text-body1">{{ selectedRule.basic_info.college }}</div>
                    </div>
                    <div class="col-6">
                      <div class="text-caption text-grey">規則類型</div>
                      <div class="text-body1">
                        <q-badge :color="getRuleTypeBadgeColor(selectedRule.basic_info.rule_type)">
                          {{ getRuleTypeLabel(selectedRule.basic_info.rule_type) }}
                        </q-badge>
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- 規則內容 -->
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-subtitle1 text-weight-bold q-mb-md">規則內容</div>

                  <!-- 規則基本資訊 -->
                  <div class="rule-info-section q-mb-lg">
                    <div class="row q-col-gutter-md">
                      <div class="col-12 col-md-6">
                        <div class="info-item">
                          <q-icon name="title" color="primary" size="20px" class="q-mr-sm" />
                          <div>
                            <div class="text-caption text-grey">規則名稱</div>
                            <div class="text-body1">{{ selectedRule.rule_content.name }}</div>
                          </div>
                        </div>
                      </div>
                      <div class="col-12 col-md-6">
                        <div class="info-item">
                          <q-icon name="category" color="primary" size="20px" class="q-mr-sm" />
                          <div>
                            <div class="text-caption text-grey">規則類型</div>
                            <div class="text-body1">
                              <q-badge
                                :color="
                                  selectedRule.rule_content.rule_type === 'rule_set'
                                    ? 'blue'
                                    : 'green'
                                "
                              >
                                {{
                                  selectedRule.rule_content.rule_type === 'rule_set'
                                    ? 'RuleSet (規則集)'
                                    : 'RuleAll (全部課程)'
                                }}
                              </q-badge>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="col-12" v-if="selectedRule.rule_content.description">
                        <div class="info-item">
                          <q-icon name="description" color="primary" size="20px" class="q-mr-sm" />
                          <div>
                            <div class="text-caption text-grey">規則描述</div>
                            <div class="text-body1">
                              {{ selectedRule.rule_content.description }}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="col-12 col-md-6">
                        <div class="info-item">
                          <q-icon name="low_priority" color="primary" size="20px" class="q-mr-sm" />
                          <div>
                            <div class="text-caption text-grey">優先級</div>
                            <div class="text-body1">
                              {{ selectedRule.rule_content.priority || 0 }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 畢業要求 -->
                  <div class="rule-section q-mb-lg">
                    <div class="section-title">
                      <q-icon
                        name="assignment_turned_in"
                        color="positive"
                        size="24px"
                        class="q-mr-sm"
                      />
                      <span class="text-h6">畢業要求</span>
                    </div>
                    <q-card flat bordered class="q-mt-md bg-green-1">
                      <q-card-section>
                        <div class="row q-col-gutter-md">
                          <div
                            class="col-6 col-md-3"
                            v-if="selectedRule.rule_content.requirement.credits !== undefined"
                          >
                            <div class="requirement-item">
                              <div class="text-h4 text-positive">
                                {{ selectedRule.rule_content.requirement.credits }}
                              </div>
                              <div class="text-caption text-grey-7">學分要求</div>
                            </div>
                          </div>
                          <div
                            class="col-6 col-md-3"
                            v-if="
                              selectedRule.rule_content.requirement.passed_courses !== undefined
                            "
                          >
                            <div class="requirement-item">
                              <div class="text-h4 text-positive">
                                {{ selectedRule.rule_content.requirement.passed_courses }}
                              </div>
                              <div class="text-caption text-grey-7">通過課程數</div>
                            </div>
                          </div>
                          <div
                            class="col-6 col-md-3"
                            v-if="selectedRule.rule_content.requirement.min_credits !== undefined"
                          >
                            <div class="requirement-item">
                              <div class="text-h4 text-positive">
                                {{ selectedRule.rule_content.requirement.min_credits }}
                              </div>
                              <div class="text-caption text-grey-7">最低學分</div>
                            </div>
                          </div>
                          <div
                            class="col-6 col-md-3"
                            v-if="selectedRule.rule_content.requirement.max_credits !== undefined"
                          >
                            <div class="requirement-item">
                              <div class="text-h4 text-positive">
                                {{ selectedRule.rule_content.requirement.max_credits }}
                              </div>
                              <div class="text-caption text-grey-7">最高學分</div>
                            </div>
                          </div>
                        </div>
                        <!-- 顯示其他 requirement 欄位 -->
                        <div
                          v-if="hasOtherRequirements(selectedRule.rule_content.requirement)"
                          class="q-mt-md"
                        >
                          <q-separator class="q-mb-md" />
                          <div class="text-subtitle2 q-mb-sm">其他要求</div>
                          <div
                            v-for="(value, key) in getOtherRequirements(
                              selectedRule.rule_content.requirement,
                            )"
                            :key="key"
                            class="q-mb-xs"
                          >
                            <span class="text-weight-bold">{{ key }}:</span> {{ value }}
                          </div>
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>

                  <!-- RuleSet 專用：子規則 -->
                  <div
                    v-if="
                      selectedRule.rule_content.rule_type === 'rule_set' &&
                      selectedRule.rule_content.sub_rules?.length
                    "
                    class="rule-section q-mb-lg"
                  >
                    <div class="section-title">
                      <q-icon name="account_tree" color="primary" size="24px" class="q-mr-sm" />
                      <span class="text-h6">子規則</span>
                      <q-chip
                        v-if="selectedRule.rule_content.sub_rule_logic"
                        color="primary"
                        text-color="white"
                        size="sm"
                        class="q-ml-md"
                      >
                        邏輯: {{ selectedRule.rule_content.sub_rule_logic }}
                      </q-chip>
                    </div>

                    <div class="q-mt-md">
                      <q-expansion-item
                        v-for="(subRule, index) in selectedRule.rule_content.sub_rules"
                        :key="index"
                        :label="`子規則 ${index + 1}: ${subRule.name || '未命名規則'}`"
                        :caption="subRule.description || ''"
                        icon="rule"
                        header-class="bg-blue-1"
                        expand-icon-class="text-primary"
                        class="q-mb-sm rule-expansion"
                      >
                        <q-card flat bordered>
                          <q-card-section>
                            <render-rule :rule="subRule" :level="1" />
                          </q-card-section>
                        </q-card>
                      </q-expansion-item>
                    </div>
                  </div>

                  <!-- RuleAll 專用：課程條件和課程列表 -->
                  <div v-if="selectedRule.rule_content.rule_type === 'rule_all'">
                    <!-- 課程條件 -->
                    <div
                      v-if="selectedRule.rule_content.course_criteria"
                      class="rule-section q-mb-lg"
                    >
                      <div class="section-title">
                        <q-icon name="filter_alt" color="orange" size="24px" class="q-mr-sm" />
                        <span class="text-h6">課程篩選條件</span>
                      </div>
                      <q-card flat bordered class="q-mt-md bg-orange-1">
                        <q-card-section>
                          <div class="row q-col-gutter-sm">
                            <div
                              v-for="(value, key) in selectedRule.rule_content.course_criteria"
                              :key="key"
                              class="col-12 col-md-6"
                            >
                              <div class="criteria-item">
                                <q-icon
                                  name="check_circle"
                                  color="orange"
                                  size="18px"
                                  class="q-mr-xs"
                                />
                                <span class="text-weight-bold">{{ formatCriteriaKey(key) }}:</span>
                                <span class="q-ml-xs">{{ formatCriteriaValue(value) }}</span>
                              </div>
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>

                    <!-- 課程列表 -->
                    <div v-if="selectedRule.rule_content.course_list?.length" class="rule-section">
                      <div class="section-title">
                        <q-icon name="list_alt" color="purple" size="24px" class="q-mr-sm" />
                        <span class="text-h6">指定課程列表</span>
                        <q-chip color="purple" text-color="white" size="sm" class="q-ml-md">
                          共 {{ selectedRule.rule_content.course_list.length }} 門課程
                        </q-chip>
                      </div>
                      <q-card flat bordered class="q-mt-md">
                        <q-card-section>
                          <div class="course-list">
                            <q-chip
                              v-for="(course, index) in selectedRule.rule_content.course_list"
                              :key="index"
                              color="purple-2"
                              text-color="purple-10"
                              class="q-ma-xs"
                            >
                              {{ course }}
                            </q-chip>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>

                  <!-- 原始 JSON (摺疊) -->
                  <div class="q-mt-lg">
                    <q-expansion-item label="查看原始 JSON" icon="code" header-class="bg-grey-2">
                      <q-card flat bordered>
                        <q-card-section>
                          <pre class="rule-json-display">{{
                            formatRuleContent(selectedRule.rule_content)
                          }}</pre>
                        </q-card-section>
                      </q-card>
                    </q-expansion-item>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, h, defineComponent } from 'vue'
import { api } from 'boot/axios'
import { useQuasar, QIcon, QBadge, QCard, QCardSection, QExpansionItem, QChip } from 'quasar'

const $q = useQuasar()

// 遞迴渲染子規則的組件定義
const RenderRule = defineComponent({
  name: 'RenderRule',
  props: {
    rule: {
      type: Object,
      required: true,
    },
    level: {
      type: Number,
      default: 0,
    },
  },
  setup(props) {
    return () =>
      h(
        'div',
        { class: 'sub-rule-content' },
        [
          // 規則基本信息
          h('div', { class: 'row q-col-gutter-sm q-mb-md' }, [
            h('div', { class: 'col-12' }, [
              h('div', { class: 'text-subtitle2 text-weight-bold' }, [
                h(QIcon, {
                  name: props.rule.rule_type === 'rule_set' ? 'account_tree' : 'list',
                  size: '18px',
                  class: 'q-mr-xs',
                }),
                props.rule.name,
              ]),
              props.rule.description
                ? h('div', { class: 'text-caption text-grey-7 q-ml-md' }, props.rule.description)
                : null,
            ]),
            h('div', { class: 'col-6' }, [
              h('div', { class: 'text-caption text-grey' }, '規則類型'),
              h(
                QBadge,
                {
                  color: props.rule.rule_type === 'rule_set' ? 'blue' : 'green',
                  size: 'sm',
                },
                () => (props.rule.rule_type === 'rule_set' ? 'RuleSet' : 'RuleAll'),
              ),
            ]),
            props.rule.priority !== undefined
              ? h('div', { class: 'col-6' }, [
                  h('div', { class: 'text-caption text-grey' }, '優先級'),
                  h('div', { class: 'text-body2' }, props.rule.priority),
                ])
              : null,
          ]),

          // 要求
          props.rule.requirement
            ? h('div', { class: 'q-mb-md' }, [
                h('div', { class: 'text-caption text-grey q-mb-xs' }, '畢業要求'),
                h(QCard, { flat: true, bordered: true, class: 'bg-blue-grey-1' }, () =>
                  h(QCardSection, { class: 'q-pa-sm' }, () =>
                    h(
                      'div',
                      { class: 'row q-col-gutter-xs' },
                      [
                        props.rule.requirement.credits !== undefined
                          ? h('div', { class: 'col-auto' }, [
                              h(
                                QBadge,
                                { color: 'positive', outline: true },
                                () => `學分: ${props.rule.requirement.credits}`,
                              ),
                            ])
                          : null,
                        props.rule.requirement.passed_courses !== undefined
                          ? h('div', { class: 'col-auto' }, [
                              h(
                                QBadge,
                                { color: 'positive', outline: true },
                                () => `課程數: ${props.rule.requirement.passed_courses}`,
                              ),
                            ])
                          : null,
                        props.rule.requirement.min_credits !== undefined
                          ? h('div', { class: 'col-auto' }, [
                              h(
                                QBadge,
                                { color: 'info', outline: true },
                                () => `最低學分: ${props.rule.requirement.min_credits}`,
                              ),
                            ])
                          : null,
                      ].filter(Boolean),
                    ),
                  ),
                ),
              ])
            : null,

          // RuleSet: 子規則
          props.rule.rule_type === 'rule_set' && props.rule.sub_rules?.length
            ? h('div', { class: 'q-mb-md' }, [
                h('div', { class: 'text-caption text-grey q-mb-xs' }, [
                  '子規則',
                  props.rule.sub_rule_logic
                    ? h(
                        QBadge,
                        { color: 'primary', size: 'xs', class: 'q-ml-xs' },
                        () => props.rule.sub_rule_logic,
                      )
                    : null,
                ]),
                ...props.rule.sub_rules.map((subRule, idx) =>
                  h(
                    QExpansionItem,
                    {
                      key: idx,
                      label: subRule.name || `子規則 ${idx + 1}`,
                      dense: true,
                      headerClass: `bg-blue-${Math.min(props.level + 2, 3)}`,
                      class: 'q-mb-xs',
                    },
                    () =>
                      h(QCard, { flat: true, bordered: true }, () =>
                        h(QCardSection, { class: 'q-pa-sm' }, () =>
                          h(RenderRule, { rule: subRule, level: props.level + 1 }),
                        ),
                      ),
                  ),
                ),
              ])
            : null,

          // RuleAll: 課程條件
          props.rule.rule_type === 'rule_all' && props.rule.course_criteria
            ? h('div', { class: 'q-mb-md' }, [
                h('div', { class: 'text-caption text-grey q-mb-xs' }, '課程篩選條件'),
                h(QCard, { flat: true, bordered: true, class: 'bg-orange-1' }, () =>
                  h(QCardSection, { class: 'q-pa-sm' }, () =>
                    h(
                      'div',
                      { class: 'text-caption' },
                      Object.entries(props.rule.course_criteria).map(([key, value]) =>
                        h('div', { key }, [
                          h(QIcon, { name: 'check_circle', size: '14px', color: 'orange' }),
                          h('span', { class: 'text-weight-bold q-ml-xs' }, `${key}:`),
                          h(
                            'span',
                            { class: 'q-ml-xs' },
                            typeof value === 'object' ? JSON.stringify(value) : value,
                          ),
                        ]),
                      ),
                    ),
                  ),
                ),
              ])
            : null,

          // RuleAll: 課程列表
          props.rule.rule_type === 'rule_all' && props.rule.course_list?.length
            ? h('div', { class: 'q-mb-md' }, [
                h(
                  'div',
                  { class: 'text-caption text-grey q-mb-xs' },
                  `指定課程 (${props.rule.course_list.length})`,
                ),
                h(QCard, { flat: true, bordered: true }, () =>
                  h(QCardSection, { class: 'q-pa-sm' }, () =>
                    props.rule.course_list.map((course, idx) =>
                      h(
                        QChip,
                        {
                          key: idx,
                          size: 'sm',
                          color: 'purple-2',
                          textColor: 'purple-10',
                          class: 'q-ma-xs',
                        },
                        () => course,
                      ),
                    ),
                  ),
                ),
              ])
            : null,
        ].filter(Boolean),
      )
  },
})

// 資料狀態
const loading = ref(false)
const submitting = ref(false)
const rules = ref([])
const departments = ref({})
const searchQuery = ref('')

// 對話框狀態
const createDialogOpen = ref(false)
const detailDialogOpen = ref(false)
const selectedRule = ref(null)

// 新增規則表單
const newRule = ref({
  department_code: '',
  admission_year: null,
  rule_type: 'major',
  rule_content: {
    name: '',
    description: '',
    rule_type: 'rule_set',
    priority: 0,
    requirement: {},
    sub_rules: [],
    sub_rule_logic: 'AND',
  },
})

const ruleJsonInput = ref('')

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

// 格式化規則內容
function formatRuleContent(content) {
  return JSON.stringify(content, null, 2)
}

// 打開新增對話框
function openCreateDialog() {
  resetForm()
  createDialogOpen.value = true
}

// 關閉新增對話框
function closeCreateDialog() {
  createDialogOpen.value = false
  resetForm()
}

// 重置表單
function resetForm() {
  newRule.value = {
    department_code: '',
    admission_year: null,
    rule_type: 'major',
    rule_content: {
      name: '',
      description: '',
      rule_type: 'rule_set',
      priority: 0,
      requirement: {},
      sub_rules: [],
      sub_rule_logic: 'AND',
    },
  }
  ruleJsonInput.value = ''
}

// 驗證 JSON 格式
function validateJson(value) {
  if (!value) return '請輸入規則內容'
  try {
    JSON.parse(value)
    return true
  } catch (e) {
    return 'JSON 格式錯誤：' + e.message
  }
}

// 解析 JSON 輸入
function parseRuleJson() {
  try {
    if (ruleJsonInput.value) {
      const parsed = JSON.parse(ruleJsonInput.value)
      // 合併到 rule_content
      Object.assign(newRule.value.rule_content, parsed)
    }
  } catch {
    // JSON 格式錯誤時不做處理，讓驗證函數顯示錯誤
  }
}

// 提交新增規則
async function submitCreateRule() {
  // 驗證必填欄位
  if (!newRule.value.department_code || !newRule.value.admission_year) {
    $q.notify({
      type: 'warning',
      message: '請填寫所有必填欄位',
    })
    return
  }

  // 驗證 JSON 內容
  if (validateJson(ruleJsonInput.value) !== true) {
    $q.notify({
      type: 'warning',
      message: '規則內容 JSON 格式錯誤',
    })
    return
  }

  submitting.value = true
  try {
    // 確保 rule_content 包含最新的 JSON 內容
    if (ruleJsonInput.value) {
      const parsed = JSON.parse(ruleJsonInput.value)
      Object.assign(newRule.value.rule_content, parsed)
    }

    const response = await api.post('/rules/', newRule.value)

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

// 輔助函數：判斷是否有其他 requirement 欄位
function hasOtherRequirements(requirement) {
  if (!requirement) return false
  const knownKeys = ['credits', 'passed_courses', 'min_credits', 'max_credits']
  return Object.keys(requirement).some((key) => !knownKeys.includes(key))
}

// 輔助函數：取得其他 requirement 欄位
function getOtherRequirements(requirement) {
  if (!requirement) return {}
  const knownKeys = ['credits', 'passed_courses', 'min_credits', 'max_credits']
  const result = {}
  Object.keys(requirement).forEach((key) => {
    if (!knownKeys.includes(key)) {
      result[key] = requirement[key]
    }
  })
  return result
}

// 輔助函數：格式化課程條件鍵名
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

// 輔助函數：格式化課程條件值
function formatCriteriaValue(value) {
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return value
}

// 初始化
onMounted(() => {
  loadRules()
  loadDepartments()
})
</script>

<style scoped>
.rule-json-display {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 16px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}

.rule-info-section {
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.rule-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 16px;
}

.requirement-item {
  text-align: center;
  padding: 12px;
}

.criteria-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.course-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.rule-expansion {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.rule-expansion :deep(.q-item) {
  min-height: 56px;
}

.sub-rule-content {
  padding: 8px;
}

.sub-rule-content .text-subtitle2 {
  color: #1976d2;
}
</style>
