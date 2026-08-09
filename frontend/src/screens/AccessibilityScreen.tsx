import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Switch, TextInput } from 'react-native';
import { apiService, AccessibilitySettings } from '../services/apiService';

interface AccessibilityScreenProps {
  isHighContrast: boolean;
  onToggleContrast: () => void;
  isBackendOnline: boolean;
  onCheckStatus: () => void;
}

export const AccessibilityScreen: React.FC<AccessibilityScreenProps> = ({
  isHighContrast,
  onToggleContrast,
  isBackendOnline,
  onCheckStatus,
}) => {
  const [fontSize, setFontSize] = useState<'normal' | 'large' | 'xlarge'>('large');
  const [speechRate, setSpeechRate] = useState<number>(1.0);
  const [gazeSensitivity, setGazeSensitivity] = useState<number>(0.8);
  const [emailInput, setEmailInput] = useState<string>('user@voxgaze.ai');
  const [passwordInput, setPasswordInput] = useState<string>('••••••••');
  const [authStatus, setAuthStatus] = useState<string>('Authenticated as user@voxgaze.ai');
  const [customHost, setCustomHost] = useState<string>('http://127.0.0.1:8000');
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string>('');

  const handleLogin = async () => {
    setAuthStatus('Authenticating with backend...');
    const result = await apiService.login(emailInput, passwordInput);
    if (result.success) {
      setAuthStatus(`Authenticated (JWT Token Active)`);
    } else {
      setAuthStatus(`Authentication Failed: ${result.error}`);
    }
  };

  const handleSaveSettings = async () => {
    const payload: AccessibilitySettings = {
      high_contrast: isHighContrast,
      font_size: fontSize,
      speech_rate: speechRate,
      gaze_sensitivity: gazeSensitivity,
    };
    await apiService.updateAccessibilitySettings(payload);
    setSavedSuccessMsg('Preferences saved to VoxGaze cloud profile!');
    setTimeout(() => setSavedSuccessMsg(''), 3000);
  };

  const handleApplyHost = () => {
    apiService.setBaseUrl(customHost);
    onCheckStatus();
  };

  const styles = getStyles(isHighContrast);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Visual & Accessibility Options */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🎨 Visual & Gaze Preferences</Text>

        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>High Contrast Dark Mode</Text>
          <Switch
            value={isHighContrast}
            onValueChange={onToggleContrast}
            trackColor={{ false: '#475569', true: isHighContrast ? '#F59E0B' : '#6366F1' }}
          />
        </View>

        <Text style={styles.groupLabel}>FONT SIZE SELECTION</Text>
        <View style={styles.pillGroup}>
          {(['normal', 'large', 'xlarge'] as const).map((size) => (
            <TouchableOpacity
              key={size}
              style={[styles.pillOption, fontSize === size && styles.pillOptionActive]}
              onPress={() => setFontSize(size)}
            >
              <Text style={[styles.pillOptionText, fontSize === size && styles.pillOptionTextActive]}>
                {size.toUpperCase()}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.groupLabel}>SPEECH SYNTHESIZER RATE: {speechRate.toFixed(1)}x</Text>
        <View style={styles.pillGroup}>
          {[0.8, 1.0, 1.2, 1.5].map((rate) => (
            <TouchableOpacity
              key={rate}
              style={[styles.pillOption, speechRate === rate && styles.pillOptionActive]}
              onPress={() => setSpeechRate(rate)}
            >
              <Text style={[styles.pillOptionText, speechRate === rate && styles.pillOptionTextActive]}>
                {rate}x
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.groupLabel}>GAZE SENSITIVITY LEVEL: {Math.round(gazeSensitivity * 100)}%</Text>
        <View style={styles.pillGroup}>
          {[0.5, 0.8, 1.0].map((sens) => (
            <TouchableOpacity
              key={sens}
              style={[styles.pillOption, gazeSensitivity === sens && styles.pillOptionActive]}
              onPress={() => setGazeSensitivity(sens)}
            >
              <Text style={[styles.pillOptionText, gazeSensitivity === sens && styles.pillOptionTextActive]}>
                {sens === 0.5 ? 'Low' : sens === 0.8 ? 'Medium' : 'High'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {savedSuccessMsg ? <Text style={styles.successMsg}>{savedSuccessMsg}</Text> : null}

        <TouchableOpacity style={styles.saveBtn} onPress={handleSaveSettings} activeOpacity={0.7}>
          <Text style={styles.saveBtnText}>💾 Save Preferences to Cloud</Text>
        </TouchableOpacity>
      </View>

      {/* User Account & Login */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>👤 VoxGaze User Account</Text>
        <Text style={styles.authStatusText}>Status: {authStatus}</Text>

        <TextInput
          style={styles.input}
          placeholder="Email Address"
          placeholderTextColor="#64748B"
          value={emailInput}
          onChangeText={setEmailInput}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#64748B"
          secureTextEntry
          value={passwordInput}
          onChangeText={setPasswordInput}
        />

        <TouchableOpacity style={styles.loginBtn} onPress={handleLogin} activeOpacity={0.7}>
          <Text style={styles.loginBtnText}>🔑 Authenticate Session</Text>
        </TouchableOpacity>
      </View>

      {/* Backend Endpoint Settings */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🌐 Backend Server Connection</Text>
        <Text style={styles.statusIndicatorText}>
          Server State: {isBackendOnline ? '🟢 Online (http://127.0.0.1:8000)' : '🟡 Local Fallback Mode'}
        </Text>

        <TextInput
          style={styles.input}
          placeholder="Backend Host URL"
          placeholderTextColor="#64748B"
          value={customHost}
          onChangeText={setCustomHost}
        />

        <View style={styles.btnRow}>
          <TouchableOpacity style={[styles.loginBtn, { flex: 1 }]} onPress={handleApplyHost}>
            <Text style={styles.loginBtnText}>🔄 Update Host & Reconnect</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.pingBtn, { flex: 1 }]} onPress={onCheckStatus}>
            <Text style={styles.pingBtnText}>⚡ Ping /health</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const getStyles = (isHighContrast: boolean) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isHighContrast ? '#050505' : '#090D16',
    },
    content: {
      padding: 16,
      gap: 16,
    },
    card: {
      backgroundColor: isHighContrast ? '#111111' : '#1E293B',
      borderRadius: 16,
      padding: 16,
      borderWidth: 1,
      borderColor: isHighContrast ? '#F59E0B' : '#334155',
    },
    cardTitle: {
      color: isHighContrast ? '#FFFFFF' : '#F8FAFC',
      fontSize: 16,
      fontWeight: 'bold',
      marginBottom: 12,
    },
    settingRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 12,
    },
    settingLabel: {
      color: isHighContrast ? '#FFFFFF' : '#E2E8F0',
      fontSize: 14,
    },
    groupLabel: {
      color: isHighContrast ? '#F59E0B' : '#94A3B8',
      fontSize: 11,
      fontWeight: 'bold',
      marginTop: 10,
      marginBottom: 6,
    },
    pillGroup: {
      flexDirection: 'row',
      gap: 8,
      marginBottom: 8,
    },
    pillOption: {
      flex: 1,
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      paddingVertical: 8,
      borderRadius: 8,
      alignItems: 'center',
      borderWidth: 1,
      borderColor: isHighContrast ? '#374151' : '#334155',
    },
    pillOptionActive: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#6366F1',
      borderColor: isHighContrast ? '#F59E0B' : '#818CF8',
    },
    pillOptionText: {
      color: isHighContrast ? '#9CA3AF' : '#94A3B8',
      fontSize: 12,
      fontWeight: 'bold',
    },
    pillOptionTextActive: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
    },
    saveBtn: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#4F46E5',
      paddingVertical: 12,
      borderRadius: 10,
      alignItems: 'center',
      marginTop: 12,
    },
    saveBtnText: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 13,
    },
    successMsg: {
      color: '#10B981',
      fontSize: 12,
      textAlign: 'center',
      marginVertical: 4,
      fontWeight: '600',
    },
    authStatusText: {
      color: isHighContrast ? '#10B981' : '#34D399',
      fontSize: 12,
      marginBottom: 10,
    },
    input: {
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      color: '#FFFFFF',
      borderRadius: 10,
      paddingHorizontal: 12,
      paddingVertical: 10,
      fontSize: 13,
      borderWidth: 1,
      borderColor: isHighContrast ? '#374151' : '#334155',
      marginBottom: 8,
    },
    loginBtn: {
      backgroundColor: isHighContrast ? '#1F2937' : '#059669',
      paddingVertical: 10,
      borderRadius: 10,
      alignItems: 'center',
      borderWidth: isHighContrast ? 1 : 0,
      borderColor: isHighContrast ? '#F59E0B' : 'transparent',
    },
    loginBtnText: {
      color: isHighContrast ? '#F59E0B' : '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 13,
    },
    statusIndicatorText: {
      color: isHighContrast ? '#E5E7EB' : '#CBD5E1',
      fontSize: 12,
      marginBottom: 10,
    },
    btnRow: {
      flexDirection: 'row',
      gap: 8,
      marginTop: 4,
    },
    pingBtn: {
      backgroundColor: isHighContrast ? '#374151' : '#334155',
      paddingVertical: 10,
      borderRadius: 10,
      alignItems: 'center',
    },
    pingBtnText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 13,
    },
  });
