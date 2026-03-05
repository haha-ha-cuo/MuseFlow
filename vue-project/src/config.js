// API Base URL Configuration
// 如果环境变量中定义了 VITE_API_BASE_URL，则使用它
// 否则默认为 '/api' (通过 Vite 代理转发)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'