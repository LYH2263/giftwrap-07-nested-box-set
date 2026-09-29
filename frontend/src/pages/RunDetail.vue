<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">{{ run.created_at }} · 折边系数 {{ run.overlap }}</p>
      <div class="result-board">
        <div class="figure">{{ run.result.paper_m2 }}<span>m² 合计</span></div>
        <p class="stat-line">盒表面积合计 {{ run.result.box_surface }} m²</p>
        <p class="stat-line" v-if="run.result.ribbon">丝带约 {{ run.result.ribbon.ribbon_m }} m</p>
        <table class="box-table">
          <thead>
            <tr><th>盒名</th><th>尺寸 (m)</th><th>盒表面积 (m²)</th><th>用纸 (m²)</th></tr>
          </thead>
          <tbody>
            <tr v-for="b in run.result.boxes" :key="b.box_id">
              <td>{{ b.name }}</td>
              <td class="meta">{{ b.length }}×{{ b.width }}×{{ b.height }}</td>
              <td class="meta">{{ b.box_surface }}</td>
              <td>{{ b.paper_m2 }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>
