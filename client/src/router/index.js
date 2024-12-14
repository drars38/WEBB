import { createRouter, createWebHistory } from 'vue-router'
import AuthorView from "@/views/AuthorView.vue";
import PostsView from "@/views/PostsView.vue";
import LoginPage from "@/views/LoginPage.vue";
import TagsPage from "@/views/TagsPage.vue";
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/posts',
      name: 'PostsView',
      component: PostsView
    },
    {
      path: '/authors',
      name: 'AuthorView',
      component: AuthorView
    },
      {
      path: '/login',
      name: 'LoginPage',
      component: LoginPage
    },
      {
      path: '/tags',
      name: 'tags',
      component: TagsPage
    },
  ]
})

export default router
