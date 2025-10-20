<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>畢業審查系統</q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> 功能選單 </q-item-label>

        <q-item v-for="page in pages" :key="page.name" clickable v-ripple :to="page.route" exact>
          <q-item-section avatar>
            <q-icon :name="page.icon" />
          </q-item-section>

          <q-item-section>
            <q-item-label>{{ page.title }}</q-item-label>
            <q-item-label caption>{{ page.caption }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'

const pages = [
  {
    name: 'students',
    title: '學生資料',
    caption: '管理學生資訊與課程記錄',
    icon: 'school',
    route: '/students',
  },
  {
    name: 'rules',
    title: '規則資料',
    caption: '查看與管理畢業規則',
    icon: 'rule',
    route: '/rules',
  },
  {
    name: 'results',
    title: '審查結果',
    caption: '查看審查結果與詳細報告',
    icon: 'assessment',
    route: '/results',
  },
]

const leftDrawerOpen = ref(false)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>
