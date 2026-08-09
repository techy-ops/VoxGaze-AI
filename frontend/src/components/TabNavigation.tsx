import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export type TabKey = 'eye' | 'lip' | 'sign' | 'ai' | 'emergency' | 'settings';

interface TabNavigationProps {
  activeTab: TabKey;
  onSelectTab: (tab: TabKey) => void;
  isHighContrast: boolean;
}

interface TabConfig {
  key: TabKey;
  label: string;
  icon: string;
}

const TABS: TabConfig[] = [
  { key: 'eye', label: 'Eye Gaze', icon: '👁️' },
  { key: 'lip', label: 'Lip Read', icon: '👄' },
  { key: 'sign', label: 'Sign Lang', icon: '✋' },
  { key: 'ai', label: 'AI Assist', icon: '🤖' },
  { key: 'emergency', label: 'SOS', icon: '🚨' },
  { key: 'settings', label: 'Settings', icon: '⚙️' },
];

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onSelectTab,
  isHighContrast,
}) => {
  const styles = getStyles(isHighContrast);

  return (
    <View style={styles.container}>
      {TABS.map((tab) => {
        const isActive = activeTab === tab.key;
        return (
          <TouchableOpacity
            key={tab.key}
            style={[styles.tabButton, isActive && styles.activeTabButton]}
            onPress={() => onSelectTab(tab.key)}
            activeOpacity={0.7}
          >
            <Text style={styles.tabIcon}>{tab.icon}</Text>
            <Text style={[styles.tabLabel, isActive && styles.activeTabLabel]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const getStyles = (isHighContrast: boolean) =>
  StyleSheet.create({
    container: {
      flexDirection: 'row',
      backgroundColor: isHighContrast ? '#000000' : '#0F172A',
      borderTopWidth: isHighContrast ? 2 : 1,
      borderTopColor: isHighContrast ? '#F59E0B' : '#1E293B',
      paddingVertical: 8,
      paddingHorizontal: 4,
      justifyContent: 'space-around',
    },
    tabButton: {
      alignItems: 'center',
      paddingVertical: 6,
      paddingHorizontal: 8,
      borderRadius: 12,
    },
    activeTabButton: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#6366F1',
    },
    tabIcon: {
      fontSize: 18,
      marginBottom: 2,
    },
    tabLabel: {
      fontSize: 10,
      fontWeight: '600',
      color: isHighContrast ? '#9CA3AF' : '#94A3B8',
    },
    activeTabLabel: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: 'bold',
    },
  });
