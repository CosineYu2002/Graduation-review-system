const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'students', component: () => import('pages/StudentsPage.vue') },
      { path: 'rules', component: () => import('pages/RulesPage.vue') },
      { path: 'results', component: () => import('pages/ResultsPage.vue') },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
