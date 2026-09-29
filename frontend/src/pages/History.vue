<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果，按次保留分盒面积与合计（写入快照，不随后改尺寸重算）。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">
          #{{ r.id }} · {{ r.result?.boxes?.length ?? 1 }} 盒
        </router-link>
        <span class="meta">
          {{ r.result?.paper_m2 ?? '—' }} m²
          <template v-if="r.result?.boxes?.length">
            · {{ r.result.boxes.map((b) => b.name).join('、') }}
          </template>
        </span>
      </li>
    </ul>
  </div>
</template>
