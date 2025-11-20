<template>
  <div class="compose-layout">
    <el-row :gutter="24">
      <el-col :xs="24" :lg="14">
        <el-card shadow="hover" class="compose-card">
          <template #header>
            <div class="card-header">
              <div>
                <h3>AI-powered intelligent email composition</h3>
                <p>Add key information, and AI will automatically generate the complete email content.</p>
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
                <el-form-item label="Email Subject" prop="subject">
                  <el-input v-model="form.subject" placeholder="Please enter the email subject." />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="Tone" prop="tone">
                  <el-select v-model="form.tone" placeholder="选择语气">
                    <el-option label="Professional" value="professional" />
                    <el-option label="Formal" value="formal" />
                    <el-option label="Friendly" value="friendly" />
                    <el-option label="Casual" value="casual" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Content Overview" prop="brief_content">
              <el-input
                v-model="form.brief_content"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                placeholder="Describe the purpose of the email, key information, time, participants, etc."
              />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :xs="24">
                <el-form-item
                  label="Recipient's email address (separate multiple email addresses with commas)."
                  prop="to_emails_input"
                >
                  <el-input
                    v-model="form.to_emails_input"
                    placeholder="client@example.com, boss@company.com"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :xs="24" :sm="12">
                <el-form-item label="Purpose" prop="purpose">
                  <el-input v-model="form.purpose" placeholder="Specify the email target (optional)" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="Additional Background" prop="additional_context">
                  <el-input
                    v-model="form.additional_context"
                    placeholder="Additional background information (optional)"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :xs="24" :sm="8">
                <el-form-item label="Sender Name" prop="sender_name">
                  <el-input v-model="form.sender_name" placeholder="Alex Chen" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="Sender Position" prop="sender_position">
                  <el-input v-model="form.sender_position" placeholder="Product Manager" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item label="Sender's contact information" prop="sender_contact">
                  <el-input v-model="form.sender_contact" placeholder="alex@example.com" />
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
              <el-button @click="handleReset">Reset</el-button>
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
                  <h3>Generate Results</h3>
                  <p>View and adjust the automatically generated theme and body text.</p>
                </div>
                <el-button text type="primary" @click="copyResult">Copy content</el-button>
              </div>
            </template>

            <div class="result-body">
              <p class="result-label">Subject</p>
              <el-input
                v-model="result.subject"
                placeholder="Editable generated subject"
              />

              <p class="result-label">Content</p>
              <el-input
                v-model="result.content"
                type="textarea"
                :autosize="{ minRows: 6, maxRows: 12 }"
              />
            </div>
          </el-card>
        </transition>
        <el-empty v-else description="The generated results will be displayed here." class="result-placeholder" />
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
  to_emails_input: '', // 改为存储邮箱字符串
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
  to_emails_input: [{ required: true, message: 'Please enter at least one recipients email address.', trigger: 'blur' }],
  subject: [{ required: true, message: 'Please enter the email subject.', trigger: 'blur' }],
  brief_content: [
    { required: true, message: 'Please fill in a summary of the content.', trigger: 'blur' },
    {
      min: 5,
      message: 'Content summary (at least 5 characters)',
      trigger: 'blur'
    }
  ]
}

// 辅助函数：将输入的字符串解析为邮箱列表
const buildEmailPayload = () => {
  const emails = form.to_emails_input
    ? form.to_emails_input.split(',').map((e) => e.trim()).filter((e) => e)
    : []
  
  return {
    to_emails: emails // 后端直接接收字符串数组
  }
}

const handleCompose = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    result.value = null
    responseText.value = ''
    try {
      const { to_emails } = buildEmailPayload()

      // 构建 Payload：移除 recipient_id，使用 to_emails
      const payload = {
        to_emails,
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
        throw new Error(data?.message || 'Generation failed')
      }
      result.value = {
        subject: data.subject || form.subject,
        // 后端返回字段为 body，为了兼容性，建议同时尝试读取 body 和 content
        content: data.body || data.content || '' 
      }
      ElMessage.success('Email generated successfully')
    } catch (error) {
      const message = error?.message || 'Email generation failed'
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
  isSendReady.value ? 'Send email' : 'Generate email'
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
    ElMessage.warning('Please generate the email content first.')
    return
  }

  loading.value = true
  try {
    const { to_emails } = buildEmailPayload()
    
    // 构建 Payload：移除 recipient_id，使用 to_emails
    const payload = {
      to_emails,
      subject: result.value.subject || form.subject,
      body: result.value.content || ''
    }
    
    const { data } = await sendEmail(payload)
    responseText.value = JSON.stringify(data, null, 2)
    ElMessage.success('Email sent successfully')
  } catch (error) {
    const message = error?.message || 'Email failed to send'
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
      `Subject：${result.value.subject || ''}\n\n${result.value.content}`
    )
    ElMessage.success('Copy to clipboard')
  } catch {
    ElMessage.warning('Copying failed, please copy manually.')
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