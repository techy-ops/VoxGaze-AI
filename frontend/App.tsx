import React, { useState, useEffect } from 'react';
import { StyleSheet, View, StatusBar } from 'react-native';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

import { Header } from './src/components/Header';
import { TabNavigation, TabKey } from './src/components/TabNavigation';
import { EyeTrackingScreen } from './src/screens/EyeTrackingScreen';
import { LipReadingScreen } from './src/screens/LipReadingScreen';
import { SignLanguageScreen } from './src/screens/SignLanguageScreen';
import { IntelligenceScreen } from './src/screens/IntelligenceScreen';
import { EmergencyScreen } from './src/screens/EmergencyScreen';
import { AccessibilityScreen } from './src/screens/AccessibilityScreen';
import { apiService } from './src/services/apiService';

function App() {
  return (
    <SafeAreaProvider>
      <MainContainer />
    </SafeAreaProvider>
  );
}

function MainContainer() {
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = useState<TabKey>('eye');
  const [isHighContrast, setIsHighContrast] = useState<boolean>(true);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);

  const checkBackendStatus = async () => {
    const status = await apiService.checkHealth();
    setIsBackendOnline(status.isOnline);
  };

  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const getTabTitle = (tab: TabKey): string => {
    switch (tab) {
      case 'eye':
        return 'Gaze Control & Dwell Matrix';
      case 'lip':
        return 'Silent Speech & Lip Reading';
      case 'sign':
        return 'ASL Hand Gesture Decoder';
      case 'ai':
        return 'Multimodal Intelligence AI';
      case 'emergency':
        return 'Emergency SOS Dispatch';
      case 'settings':
        return 'Accessibility Preferences';
      default:
        return 'Accessibility Platform';
    }
  };

  return (
    <View
      style={[
        styles.root,
        {
          paddingTop: insets.top,
          paddingBottom: insets.bottom,
          backgroundColor: isHighContrast ? '#000000' : '#0F172A',
        },
      ]}
    >
      <StatusBar
        barStyle={isHighContrast ? 'light-content' : 'light-content'}
        backgroundColor={isHighContrast ? '#000000' : '#0F172A'}
      />

      <Header
        title={getTabTitle(activeTab)}
        isBackendOnline={isBackendOnline}
        isHighContrast={isHighContrast}
        onToggleContrast={() => setIsHighContrast((prev) => !prev)}
        onCheckStatus={checkBackendStatus}
      />

      <View style={styles.contentArea}>
        {activeTab === 'eye' && <EyeTrackingScreen isHighContrast={isHighContrast} />}
        {activeTab === 'lip' && <LipReadingScreen isHighContrast={isHighContrast} />}
        {activeTab === 'sign' && <SignLanguageScreen isHighContrast={isHighContrast} />}
        {activeTab === 'ai' && <IntelligenceScreen isHighContrast={isHighContrast} />}
        {activeTab === 'emergency' && <EmergencyScreen isHighContrast={isHighContrast} />}
        {activeTab === 'settings' && (
          <AccessibilityScreen
            isHighContrast={isHighContrast}
            onToggleContrast={() => setIsHighContrast((prev) => !prev)}
            isBackendOnline={isBackendOnline}
            onCheckStatus={checkBackendStatus}
          />
        )}
      </View>

      <TabNavigation
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isHighContrast={isHighContrast}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  contentArea: {
    flex: 1,
  },
});

export default App;
