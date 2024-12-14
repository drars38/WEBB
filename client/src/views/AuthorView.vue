<script setup>
import axios from 'axios';
import {ref, onBeforeMount} from 'vue';
import {Modal} from 'bootstrap';
import useUserStore from "@/stores/UserStore.js";
import {storeToRefs} from "pinia";
const userStore = useUserStore();
const { isAuth,
    otpRequired,
    otpVerified } = storeToRefs(userStore);
let modalInstance = null; // Глобальная переменная для модального окна
const authors = ref([]);
const authorToAdd = ref({bio: '', picture: null});
const authorToEdit = ref({bio: '', picture: null});
const authorPictureUrl = ref();  // URL изображения для предпросмотра
const modelEditRef = ref();
const editAuthorPictureUrl = ref();  // URL изображения для предпросмотра при редактировании
// Новая переменная для хранения статистики
const authorStats = ref({
  count: 0,
  avg: 0,
  max: 0,
  min: 0,
});
async function fetchAuthors() {
  const r = await axios.get('/api/authors/');
  authors.value = r.data;
}

async function onAuthorAdd() {
  const formData = new FormData();
  formData.append('bio', authorToAdd.value.bio);
  if (authorToAdd.value.picture) {
    formData.append('picture', authorToAdd.value.picture);
  }

  await axios.post("/api/authors/", formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchAuthors();
  resetAuthorForm();
}

function resetAuthorForm() {
  authorToAdd.value = {bio: '', picture: null};
  authorPictureUrl.value = null;
}

function onAuthorPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    authorToAdd.value.picture = file;
    authorPictureUrl.value = URL.createObjectURL(file); // Предпросмотр изображения
  }
}

async function onRemoveClick(author) {
  await axios.delete(`/api/authors/${author.id}/`);
  await fetchAuthors();
}

async function onAuthorEditClick(author) {
  authorToEdit.value = {...author};
  editAuthorPictureUrl.value = author.picture; // Загружаем текущее изображение
  modalInstance = new Modal(modelEditRef.value);
  modalInstance.show();
}

function closeModal() {
  if (modalInstance) {
    modalInstance.hide();
  }
}

async function onUpdateAuthor() {
  const formData = new FormData();
  formData.append('bio', authorToEdit.value.bio);
  if (authorToEdit.value.picture) {
    formData.append('picture', authorToEdit.value.picture);
  }

  await axios.put(`/api/authors/${authorToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  closeModal();
  await fetchAuthors();
}

function onEditAuthorPictureChange(event) {
  const file = event.target.files[0];
  if (file) {
    authorToEdit.value.picture = file;
    editAuthorPictureUrl.value = URL.createObjectURL(file); // Предпросмотр изображения при редактировании
  }
}

onBeforeMount(async () => {
  await fetchAuthors();
  await fetchAuthorsStats();
});

async function fetchAuthorsStats() {
  try {
    const response = await axios.get('/api/authors/stats/');
    authorStats.value = response.data;
  } catch (error) {
    console.error("Ошибка при получении статистики постов:", error);
  }
}

</script>

<template>
  <div class="p-2" v-if="!otpRequired">
    <form @submit.prevent="onAuthorAdd">
      <div class="row">
        <div class="col">
          <div class="form-floating mb-2">
            <input type="text" class="form-control" v-model="authorToAdd.bio" required/>
            <label for="floatingInput">БИО автора</label>
          </div>
          <div class="mb-2">
            <input class="form-control" type="file" @change="onAuthorPictureChange">
            <img :src="authorPictureUrl" v-if="authorPictureUrl" style="max-height: 60px"
                 alt="Предпросмотр изображения"/>
          </div>
        </div>

        <div class="col-auto">
          <button class="btn btn-primary">Добавить</button>
        </div>
      </div>
    </form>
  </div>
  <h3>Статистика авторов</h3>
  <p><strong>Всего авторов:</strong> {{ authorStats.count }}</p>
  <p><strong>Средний ID:</strong> {{ authorStats.avg }}</p>
  <p><strong>Максимальный ID:</strong> {{ authorStats.max }}</p>
  <p><strong>Минимальный ID:</strong> {{ authorStats.min }}</p>
  <div>
    <div v-for="author in authors" class="post-item" :key="author.id">
      <b>{{ author.bio }}</b>
      <div v-if="author.picture">
        <img :src="author.picture" style="max-height: 60px" alt="Изображение автора"/>
      </div>
      <button v-if="!otpRequired" class="btn btn-success" @click="onAuthorEditClick(author)">
        <i class="bi bi-pen-fill"></i>
      </button>
      <button v-if="!otpRequired" class="btn btn-danger" @click="onRemoveClick(author)">
        <i class="bi bi-x"></i>
      </button>
    </div>
  </div>

  <!-- Модальное окно для редактирования автора -->
  <div ref="modelEditRef" class="modal fade" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактирование автора</h5>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close" @click="closeModal">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-floating mb-2">
            <input type="text" class="form-control" v-model="authorToEdit.bio" required/>
            <label for="floatingInput">БИО автора</label>
          </div>
          <div class="mb-2">
            <input class="form-control" type="file" @change="onEditAuthorPictureChange">
            <img :src="editAuthorPictureUrl" v-if="editAuthorPictureUrl" style="max-height: 60px"
                 alt="Предпросмотр изображения"/>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-dismiss="modal" @click="closeModal">Закрыть</button>
          <button type="button" class="btn btn-primary" @click="onUpdateAuthor">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid salmon;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-content: center;
  align-items: center;
  gap: 16px;
}
</style>
