// API Configuration for VoxGaze AI Mobile Client
import { Platform } from 'react-native';

// Default backend host (Android emulator uses 10.0.2.2, iOS/Web/Desktop uses localhost)
const DEFAULT_HOST = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://127.0.0.1:8000';

export const API_CONFIG = {
  BASE_URL: DEFAULT_HOST,
  TIMEOUT: 10000,
  ENDPOINTS: {
    HEALTH: '/health',
    AUTH_REGISTER: '/auth/register',
    AUTH_LOGIN: '/auth/login',
    AUTH_PROFILE: '/auth/profile',
    EYE_TRACKING_PROCESS: '/eye-tracking/process',
    EYE_TRACKING_CALIBRATE: '/eye-tracking/calibrate',
    LIP_READING_PROCESS: '/lip-reading/process',
    SIGN_LANGUAGE_PROCESS: '/sign-language/process',
    INTELLIGENCE_PROCESS: '/intelligence/process',
    INTELLIGENCE_PROFILE: '/intelligence/profile',
    GPT_CHAT: '/gpt/chat',
    GPT_SUMMARIZE: '/gpt/summarize',
    EMERGENCY_ALERT: '/emergency/alert',
    EMERGENCY_CONTACTS: '/emergency/contacts',
    ACCESSIBILITY_SETTINGS: '/accessibility/settings',
  },
};
