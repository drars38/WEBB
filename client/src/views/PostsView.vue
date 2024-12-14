<script setup>
import axios from 'axios';
import {ref, onBeforeMount, watch} from 'vue';
import { Modal } from 'bootstrap';
import { storeToRefs } from "pinia";
import useUserStore from "@/stores/UserStore.js";
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { Document, Packer, Paragraph, TextRun } from 'docx';



const userStore = useUserStore();
const { isAuth,
    otpRequired,
    otpVerified } = storeToRefs(userStore);

let modalInstance = null;
const posts = ref([]);
const tags = ref([]);
const categorys = ref([]);
const comments = ref([]);
const authors = ref([]);
const postToAdd = ref({ tags: [] });
const postPicture = ref();
const postPictureUrl = ref();
const postEditPicture = ref();
const postEditPictureUrl = ref();
const postToEdit = ref({ tags: [] });
const commentToAdd = ref({ author: '', content: '' });
const modelEditRef = ref();
const commentModalRef = ref();
// Filters for category, tags, and author
const categoryFilter = ref('');
const tagsFilter = ref('');
const authorFilter = ref('');
// Новая переменная для хранения статистики
const postStats = ref({
  count: 0,
  avg: 0,
  max: 0,
  min: 0,
});
// Function to fetch posts with filters
async function fetchPostsWithFilters() {
  const queryParams = new URLSearchParams();

  if (categoryFilter.value) queryParams.append('category', categoryFilter.value);
  if (authorFilter.value) queryParams.append('author', authorFilter.value);
  if (tagsFilter.value.length > 0) queryParams.append('tags', tagsFilter.value.join(','));

  try {
    const response = await axios.get(`/api/posts/?${queryParams.toString()}`);
    const postsData = response.data;

    // Fetch comments for the posts
    const commentsResponse = await axios.get('/api/comments/');
    const allComments = commentsResponse.data;

    // Associate comments with posts
    posts.value = postsData.map(post => {
      const postComments = allComments.filter(comment => comment.post === post.id);
      return { ...post, comments: postComments };
    });
  } catch (error) {
    console.error('Error fetching posts with filters:', error);
  }
}
async function fetchPosts() {
  const postsResponse = await axios.get('/api/posts/'); // Получение постов
  const postsData = postsResponse.data;

  // Запрашиваем комментарии для всех постов
  const commentsResponse = await axios.get('/api/comments/');
  const allComments = commentsResponse.data;

  // Привязываем комментарии к постам
  posts.value = postsData.map(post => {
    const postComments = allComments.filter(comment => comment.post === post.id); // Только комментарии для текущего поста
    return { ...post, comments: postComments }; // Добавляем комментарии к каждому посту
  });
}



async function fetchAuthors() {
  const r = await axios.get('/api/authors/');
  authors.value = r.data;
}

async function fetchTags() {
  const r = await axios.get('/api/tags/');
  tags.value = r.data;
}

async function fetchCategorys() {
  const r = await axios.get('/api/categorys/');
  categorys.value = r.data;
}

async function fetchCommentsForPost(postId) {
  const r = await axios.get(`/api/comments/?post=${postId}/`);
  comments.value = r.data;
}

async function onPostAdd() {
  const formData = new FormData();
  formData.append('picture', postPicture.value.files[0]);

  const tagsArray = Array.isArray(postToAdd.value.tags) ? postToAdd.value.tags.slice() : [];
  tagsArray.forEach(tag => {
    formData.append('tags', tag);
  });

  formData.set('author', postToAdd.value.author);
  formData.set('category', postToAdd.value.category);
  formData.set('title', postToAdd.value.title);
  formData.set('content', postToAdd.value.content);

  await axios.post('/api/posts/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  await fetchPosts();
}

async function onPostEditClick(post) {
  postToEdit.value = { ...post };
  postEditPictureUrl.value = post.picture;
  modalInstance = new Modal(modelEditRef.value);
  modalInstance.show();
}

function closeModal() {
  if (modalInstance) {
    modalInstance.hide();
  }
}

async function onUpdatePost() {
  const formData = new FormData();
  if (postEditPicture.value && postEditPicture.value.files.length > 0) {
    formData.append('picture', postEditPicture.value.files[0]);
  }

  formData.set('author', postToEdit.value.author);
  formData.set('category', postToEdit.value.category);
  formData.set('title', postToEdit.value.title);
  formData.set('content', postToEdit.value.content);

  const tagsArray = Array.isArray(postToEdit.value.tags) ? postToEdit.value.tags.slice() : [];
  tagsArray.forEach(tag => {
    formData.append('tags', tag);
  });

  await axios.put(`/api/posts/${postToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  closeModal();
  await fetchPosts();
}

async function onRemoveClick(post) {
  await axios.delete('/api/posts/${post.id}/');
  await fetchPosts();
}

async function onCommentPost(post) {
  await fetchCommentsForPost(post.id);
  postToEdit.value = post;
  modalInstance = new Modal(commentModalRef.value);
  modalInstance.show();
}

async function onAddComment(post) {
  await axios.post('/api/comments/', {
    post: post.id,
    content: commentToAdd.value.content,
    author: commentToAdd.value.author,
  });
  commentToAdd.value.content = '';
  commentToAdd.value.author = '';
  await fetchCommentsForPost(post.id);
  modalInstance.hide();
  await fetchPosts();
}

onBeforeMount(async () => {
  await fetchPostsWithFilters();
  await fetchAuthors();
  await fetchTags();
  await fetchCategorys();
  await fetchPostStats();
});
// Watch for changes in filters and refetch posts accordingly
watch([categoryFilter, tagsFilter, authorFilter], () => {
  fetchPostsWithFilters();
});

function getAuthorBioById(author_id) {
  const author = authors.value.find(author => author.id === author_id);
  return author ? author.bio : '';
}

async function postAddPictureChange() {
  postPictureUrl.value = URL.createObjectURL(postPicture.value.files[0]);
}

async function postEditPictureChange() {
  postEditPictureUrl.value = URL.createObjectURL(postEditPicture.value.files[0]);
}

// Функция для получения статистики постов
async function fetchPostStats() {
  try {
    const response = await axios.get('/api/posts/stats/');
    postStats.value = response.data;
  } catch (error) {
    console.error("Ошибка при получении статистики постов:", error);
  }
}



// Функция для экспорта в Excel
function exportToExcel() {
  const transformedData = posts.value.map(post => {
    const { id, title, content, author} = post;
    if (post.comments && post.comments.length > 0) {
      return post.comments.map(comment => ({
        PostID: id,
        Title: title,
        Content: content,
        Author: author,
        CommentID: comment.id,
        CommentContent: comment.content,
      }));
    } else {
      return [{
        PostID: id,
        Title: title,
        Content: content,
        Author: author,
        CommentID: null,
        CommentContent: null,
      }];
    }
  }).flat();


  const worksheet = XLSX.utils.json_to_sheet(transformedData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Posts');

  // Сохраняем файл
  try {
    XLSX.writeFile(workbook, 'posts_with_authors_and_comments.xlsx');
  } catch (error) {
    console.error('Error exporting Excel file:', error);
  }
}


// Функция для экспорта в Word
async function exportToWord() {
  const doc = new Document({
    sections: [
      {
        properties: {},
        children: posts.value.map(post => {
          const categoryName = categorys.value.find(cat => cat.id === post.category)?.name || 'Неизвестно';
          const tagNames = post.tags.map(tagId => {
            const tag = tags.value.find(t => t.id === tagId);
            return tag ? tag.name : 'Неизвестно';
          }).join(', ');

          const paragraphs = [
            new Paragraph({
              children: [
                new TextRun({ text: `Post: ${post.title}`, bold: true }),
                new TextRun({ text: `\nAuthor: ${post.author}`, break: 1 }),
                new TextRun({ text: `Content: ${post.content}`, break: 1 }),
                new TextRun({ text: `Category: ${categoryName}`, break: 1 }),
                new TextRun({ text: `Tags: ${tagNames}`, break: 1 }),
              ],
            }),
          ];

          if (post.comments && post.comments.length > 0) {
            post.comments.forEach(comment => {
              paragraphs.push(
                new Paragraph({
                  children: [
                    new TextRun({ text: `Comment: ${comment.content} author: ${comment.author}`, italic: true }),
                  ],
                })
              );
            });
          }

          return paragraphs;
        }).flat(),
      },
    ],
  });

  const buffer = await Packer.toBlob(doc);
  saveAs(buffer, 'posts.docx');
}

</script>

<template>
  <div>
  <div class="p-4" v-if="otpVerified">


    <form @submit.prevent="onPostAdd">
      <div class="row">
        <div class="col">
          <div class="form-floating">
            <input type="text" class="form-control" v-model="postToAdd.title" required />
            <label for="floatingInput">Название</label>
          </div>
          <div class="form-floating">
            <input type="text" class="form-control" v-model="postToAdd.content" required />
            <label for="floatingInput">Ваш текст</label>
          </div>
          <input class="form-control" type="file" ref="postPicture" @change="postAddPictureChange" />
          <img :src="postPictureUrl" style="max-height: 60px" alt="картинка">
        </div>

        <div class="form-group">
          <label>Тэги</label>
          <div class="form-check" v-for="tag in tags" :key="tag.id">
            <input class="form-check-input" type="checkbox" :value="tag.id" v-model="postToAdd.tags" />
            <label class="form-check-label">{{ tag.name }}</label>
          </div>
        </div>

        <div class="col-auto">
          <div class="form-floating">
            <select name="" id="" class="form-select" v-model="postToAdd.category">
              <option :value="category.id" v-for="category in categorys" :key="category.id">{{ category.name }}</option>
            </select>
            <label for="floatingInput">Категория</label>
          </div>
        </div>

        <div class="col-auto">
          <div class="form-floating">
            <select name="author" id="authorSelect" class="form-select" v-model="postToAdd.author" required>
              <option :value="author.id" v-for="author in authors" :key="author.id">{{ author.bio }}</option>
            </select>
            <label for="floatingInput">Автор</label>
          </div>
        </div>

        <div  class="col-auto">
          <button class="btn btn-primary">Добавить</button>
        </div>

      </div>
    </form>
    <div class="export-buttons p-4">
      <button class="btn btn-success" @click="exportToExcel">Скачать в Excel</button>
      <button class="btn btn-primary" @click=" exportToWord">Скачать в Word</button>
      </div>
    <div class="filters">
      <!-- Category filter -->
      <div class="form-group">
        <label for="categoryFilter">Категория</label>
        <select id="categoryFilter" class="form-select" v-model="categoryFilter">
          <option value="">Все категории</option>
          <option v-for="category in categorys" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>

      <!-- Tags filter -->
      <div class="form-group">
        <label for="tagFilter">Тэги</label>
        <select id="tagFilter" class="form-select" v-model="tagsFilter" >
          <option value="">Все тэги</option>
          <option v-for="tag in tags" :key="tag.id" :value="tag.id">
            {{ tag.name }}
          </option>
        </select>
      </div>

      <!-- Author filter -->
      <div class="form-group">
        <label for="authorFilter">Автор</label>
        <select id="authorFilter" class="form-select" v-model="authorFilter">
          <option value="">Все авторы</option>
          <option v-for="author in authors" :key="author.id" :value="author.id">
            {{ author.bio }}
          </option>
        </select>
      </div>
    </div>

  </div>

  <div class="stats-section">
  <h3>Статистика постов</h3>
  <p><strong>Всего постов:</strong> {{ postStats.count }}</p>
  <p><strong>Средний ID:</strong> {{ postStats.avg }}</p>
  <p><strong>Максимальный ID:</strong> {{ postStats.max }}</p>
  <p><strong>Минимальный ID:</strong> {{ postStats.min }}</p>
</div>


  <!-- Список постов -->
  <div>
      <div v-for="post in posts" class="post-item" :key="post.id">
        <!-- Название поста и содержание -->
        <div class="post-content">
          <b>{{ post.title }}</b>
          <p>{{ post.content }}</p>
          <div v-show="post.picture">
            <img :src="post.picture" style="max-height: 60px" alt="картинка">
          </div>
        </div>

        <!-- Кнопки управления -->
        <div class="btn-group">
          <button v-if="otpVerified" class="btn btn-info" @click="onCommentPost(post)">
            <i class="bi bi-chat"></i>
          </button>
          <button v-if="otpVerified" class="btn btn-success" @click="onPostEditClick(post)">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button v-if="otpVerified" class="btn btn-danger" @click="onRemoveClick(post)">
            <i class="bi bi-x"></i>
          </button>

        </div>

        <!-- Секция комментариев для поста -->
        <div class="comments-section col-12">
          <div v-if="post.comments && post.comments.length > 0">
            <div v-for="comment in post.comments" :key="comment.id" class="comment-item">
              <p><strong>{{ getAuthorBioById(comment.author) }}</strong>: {{ comment.content }}</p>
            </div>
          </div>
          <div v-else>
            <p>Комментариев нет</p>
          </div>
        </div>
      </div>
    </div>


  <!-- Модальное окно для добавления комментария -->
  <div ref="commentModalRef" class="modal fade" id="commentModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Добавить комментарий</h5>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close" @click="closeModal">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-floating">
            <textarea class="form-control" v-model="commentToAdd.content" placeholder="Ваш комментарий" required></textarea>
            <label for="floatingTextarea">Комментарий</label>
          </div>

         <!-- Список авторов в модальном окне для комментария -->
<div class="form-floating mt-2">
  <select name="author" id="authorSelectComment" class="form-select" v-model="commentToAdd.author">
    <option :value="author.id" v-for="author in authors" :key="author.id">{{ author.bio }}</option>
  </select>
  <label for="floatingInput">Автор</label>
</div>

        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Закрыть</button>
          <button type="button" class="btn btn-primary" @click="onAddComment(postToEdit)">Добавить</button>
        </div>
      </div>
    </div>
  </div>


   <!-- Модальное окно для редактирования поста -->
  <div ref="modelEditRef" class="modal fade" id="editPostModal" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать пост</h5>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close" @click="closeModal">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-floating">
            <input type="text" class="form-control" v-model="postToEdit.title" required />
            <label for="floatingInput">Название</label>
          </div>
          <div class="form-floating">
            <input type="text" class="form-control" v-model="postToEdit.content" required />
            <label for="floatingInput">Ваш текст</label>
          </div>

          <!-- Чекбоксы для редактирования поста -->
      <div class="form-group">
        <label>Тэги</label>
        <div class="form-check" v-for="tag in tags" :key="tag.id">
          <input
            class="form-check-input"
            type="checkbox"
            :value="tag.id"
            v-model="postToEdit.tags"
          >
        <label class="form-check-label">{{ tag.name }}</label>
        </div>
      </div>


          <div class="form-floating mt-2">
            <select name="" id="" class="form-select" v-model="postToEdit.category">
              <option :value="category.id" v-for="category in categorys" :key="category.id">{{ category.name }}</option>
            </select>
            <label for="floatingInput">Категория</label>
          </div>

          <div class="form-floating mt-2">
            <select name="author" id="authorSelect" class="form-select" v-model="postToEdit.author">
              <option :value="author.id" v-for="author in authors" :key="author.id">{{ author.bio }}</option>
            </select>
            <label for="floatingInput">Автор</label>
          </div>
          <div class="form-floating mt-2">
          <input class="form-control" type="file" ref="postEditPicture" @change="postEditPictureChange">
          <img :src="postEditPictureUrl" style="max-height: 60px" alt="картинка">
        </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Закрыть</button>
          <button type="button" class="btn btn-primary" @click="onUpdatePost">Обновить</button>
        </div>


      </div>
    </div>
  </div>
  </div>
</template>

<style lang="scss" scoped>
.content {
  flex-grow: 1;
  padding: 20px;
  overflow: hidden;
}

.post-item {
  padding: 1rem;
  margin: 1rem 0;
  border: 1px solid salmon;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 15px; /* Добавляем промежуток между элементами */
  width: 100%; /* Добавляем, чтобы пост занимал всю доступную ширину */
}

.post-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-group {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.comments-section {
  margin-top: 15px;
  padding-left: 20px;
  border-top: 1px solid #ccc;
  width: 100%; /* Секция комментариев растягивается на всю ширину */
}

.comment-item {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.export-buttons {
  display: flex;
  gap: 1rem;
}

.export-buttons button {
  margin-left: 5px;
}

.stats-section {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.stats-section p {
  margin: 5px 0;
}
</style>

