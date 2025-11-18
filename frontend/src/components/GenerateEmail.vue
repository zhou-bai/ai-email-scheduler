<template>
  <div class="compose-layout">
    <el-row :gutter="24">
      <el-col :xs="24" :lg="14">
        <el-card shadow="hover" class="compose-card">
          <template #header>
            <div class="card-header">
              <div>
                <h3>AI 智能写邮件</h3>
                <p>补充关键信息，AI 将自动生成完整邮件内容。</p>
              </div>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            class="compose-form"
          >
            <el-row :gutter="16">
              <el-col :xs="24" :sm="16">
                <el-form-item label="邮件主题" prop="subject">
                  <el-input v-model="form.subject" placeholder="请输入邮件主题" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="语气风格" prop="tone">
                  <el-select v-model="form.tone" placeholder="选择语气">
                    <el-option label="专业" value="professional" />
                    <el-option label="正式" value="formal" />
                    <el-option label="友好" value="friendly" />
                    <el-option label="轻松" value="casual" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="内容概述" prop="brief_content">
              <el-input
                v-model="form.brief_content"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                placeholder="描述邮件目的、关键信息、时间、参与者等"
              />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :xs="24" :sm="12">
                <el-form-item label="单个收件人 ID" prop="recipient_id">
                  <el-input
                    v-model="form.recipient_id"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item
                  label="收件人 ID 列表（以逗号分隔）"
                  prop="recipient_ids_input"
                >
                  <el-input
                    v-model="form.recipient_ids_input"
                    placeholder="例如：1,2,3"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :xs="24" :sm="12">
                <el-form-item label="邮件目的" prop="purpose">
                  <el-input v-model="form.purpose" placeholder="说明邮件目标（可选）" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="补充背景" prop="additional_context">
                  <el-input
                    v-model="form.additional_context"
                    placeholder="补充背景信息（可选）"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :xs="24" :sm="8">
                <el-form-item label="发件人姓名" prop="sender_name">
                  <el-input v-model="form.sender_name" placeholder="例如：Alex Chen" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="发件人身份" prop="sender_position">
                  <el-input v-model="form.sender_position" placeholder="例如：产品经理" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="发件人联系方式" prop="sender_contact">
                  <el-input v-model="form.sender_contact" placeholder="例如：alex@example.com" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="actions">
              <el-button
                type="primary"
                :loading="loading"
                @click="handlePrimaryAction"
              >
                {{ primaryButtonText }}
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <transition v-if="result" name="fade">
          <el-card class="result-card" shadow="never">
            <template #header>
              <div class="result-header">
                <div>
                  <h3>生成结果</h3>
                  <p>查看并调整自动生成的主题与正文。</p>
                </div>
                <el-button text type="primary" @click="copyResult">复制内容</el-button>
              </div>
            </template>

            <div class="result-body">
              <p class="result-label">主题</p>
              <el-input
                v-model="result.subject"
                placeholder="可编辑生成的主题"
              />

              <p class="result-label">正文</p>
              <el-input
                v-model="result.content"
                type="textarea"
                :autosize="{ minRows: 6, maxRows: 12 }"
              />
            </div>
          </el-card>
        </transition>
        <el-empty v-else description="生成结果将显示在此处" class="result-placeholder" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateEmail, sendEmail } from '../api/genEmail.js'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)
const responseText = ref('')

const form = reactive({
  recipient_id: 0,
  recipient_ids_input: '',
  subject: '',
  brief_content: '',
  tone: 'professional',
  purpose: '',
  additional_context: '',
  sender_name: '',
  sender_position: '',
  sender_contact: ''
})

const rules = {
  subject: [{ required: true, message: '请输入邮件主题', trigger: 'blur' }],
  brief_content: [
    { required: true, message: '请填写内容概述', trigger: 'blur' },
    {
      min: 5,
      message: '内容概述至少 5 个字符',
      trigger: 'blur'
    }
  ]
}

const buildRecipientInfo = () => {
  const parseRecipientIds = (value) =>
    value
      .split(',')
      .map((id) => Number(id.trim()))
      .filter((id) => !Number.isNaN(id))

  const primaryRecipientId = Number(form.recipient_id)
  const parsedRecipientIds = form.recipient_ids_input
    ? parseRecipientIds(form.recipient_ids_input)
    : []
  const fallbackRecipientId = Number.isNaN(primaryRecipientId)
    ? 0
    : primaryRecipientId
  const recipientIds =
    parsedRecipientIds.length > 0 ? parsedRecipientIds : [fallbackRecipientId]

  return {
    recipient_id: fallbackRecipientId,
    recipient_ids: recipientIds
  }
}

const handleCompose = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    result.value = null
    responseText.value = ''
    try {
      const { recipient_id, recipient_ids } = buildRecipientInfo()

      const payload = {
        recipient_id,
        recipient_ids,
        subject: form.subject,
        brief_content: form.brief_content,
        tone: form.tone,
        purpose: form.purpose || undefined,
        additional_context: form.additional_context || undefined,
        sender_name: form.sender_name || undefined,
        sender_position: form.sender_position || undefined,
        sender_contact: form.sender_contact || undefined
      }
      const { data } = await generateEmail(payload)
      responseText.value = JSON.stringify(data, null, 2)
      if (!data?.success) {
        throw new Error(data?.message || '生成失败')
      }
      result.value = {
        subject: data.subject || form.subject,
        content: data.content || ''
      }
      ElMessage.success('邮件生成成功')
    } catch (error) {
      const message = error?.message || '生成邮件失败'
      responseText.value = message
      ElMessage.error(message)
    } finally {
      loading.value = false
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  result.value = null
  responseText.value = ''
}

const isSendReady = computed(() => {
  if (!result.value) return false
  const hasSubject = !!result.value.subject?.trim()
  const hasContent = !!result.value.content?.trim()
  return hasSubject || hasContent
})

const primaryButtonText = computed(() =>
  isSendReady.value ? '发送邮件' : '生成邮件'
)

const handlePrimaryAction = () => {
  if (isSendReady.value) {
    handleSend()
  } else {
    handleCompose()
  }
}

const handleSend = async () => {
  if (!isSendReady.value) {
    ElMessage.warning('请先生成邮件内容')
    return
  }

  loading.value = true
  try {
    const { recipient_id, recipient_ids } = buildRecipientInfo()
    const payload = {
      recipient_id,
      recipient_ids,
      subject: result.value.subject || form.subject,
      body: result.value.content || '',
      body_html: result.value.content || ''
    }
    const { data } = await sendEmail(payload)
    responseText.value = JSON.stringify(data, null, 2)
    ElMessage.success('邮件发送成功')
  } catch (error) {
    const message = error?.message || '发送邮件失败'
    responseText.value = message
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const copyResult = async () => {
  if (!result.value?.content) return
  try {
    await navigator.clipboard.writeText(
      `主题：${result.value.subject || ''}\n\n${result.value.content}`
    )
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.compose-layout {
  width: 100%;
}

.compose-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compose-form {
  margin-top: 8px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.result-card {
  border: 1px dashed var(--el-color-primary-light-5);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-label {
  font-weight: 600;
  margin: 0;
  color: #606266;
}

.result-subject {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.result-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--el-color-info-light-5);
  border-radius: 8px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>