import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface HeaderProps {
  title: string;
  isBackendOnline: boolean;
  isHighContrast: boolean;
  onToggleContrast: () => void;
  onCheckStatus: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  isBackendOnline,
  isHighContrast,
  onToggleContrast,
  onCheckStatus,
}) => {
  const styles = getStyles(isHighContrast);

  return (
    <View style={styles.headerContainer}>
      <View style={styles.titleRow}>
        <View style={styles.logoBadge}>
          <Text style={styles.logoBadgeText}>VG</Text>
        </View>
        <View style={styles.titleGroup}>
          <Text style={styles.brandTitle}>VoxGaze AI</Text>
          <Text style={styles.subtitle}>{title}</Text>
        </View>
      </View>

      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.statusPill} onPress={onCheckStatus} activeOpacity={0.7}>
          <View
            style={[
              styles.statusDot,
              { backgroundColor: isBackendOnline ? '#10B981' : '#EF4444' },
            ]}
          />
          <Text style={styles.statusText}>
            {isBackendOnline ? 'API Connected' : 'Local Mode'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.contrastBtn} onPress={onToggleContrast} activeOpacity={0.7}>
          <Text style={styles.contrastBtnText}>
            {isHighContrast ? '☀️ Normal' : '🌙 Contrast'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const getStyles = (isHighContrast: boolean) =>
  StyleSheet.create({
    headerContainer: {
      backgroundColor: isHighContrast ? '#000000' : '#0F172A',
      paddingHorizontal: 18,
      paddingTop: 16,
      paddingBottom: 14,
      borderBottomWidth: isHighContrast ? 2 : 1,
      borderBottomColor: isHighContrast ? '#F59E0B' : '#1E293B',
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    titleRow: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    logoBadge: {
      width: 38,
      height: 38,
      borderRadius: 10,
      backgroundColor: isHighContrast ? '#F59E0B' : '#6366F1',
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: 12,
    },
    logoBadgeText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 16,
    },
    titleGroup: {},
    brandTitle: {
      color: isHighContrast ? '#FFFFFF' : '#F8FAFC',
      fontSize: 18,
      fontWeight: 'bold',
      letterSpacing: 0.5,
    },
    subtitle: {
      color: isHighContrast ? '#F59E0B' : '#94A3B8',
      fontSize: 12,
      fontWeight: '600',
    },
    actionRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
    },
    statusPill: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: isHighContrast ? '#111827' : '#1E293B',
      paddingHorizontal: 10,
      paddingVertical: 6,
      borderRadius: 20,
      borderWidth: 1,
      borderColor: isHighContrast ? '#374151' : '#334155',
    },
    statusDot: {
      width: 8,
      height: 8,
      borderRadius: 4,
      marginRight: 6,
    },
    statusText: {
      color: isHighContrast ? '#F3F4F6' : '#CBD5E1',
      fontSize: 11,
      fontWeight: '600',
    },
    contrastBtn: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#312E81',
      paddingHorizontal: 10,
      paddingVertical: 6,
      borderRadius: 20,
    },
    contrastBtnText: {
      color: isHighContrast ? '#000000' : '#E0E7FF',
      fontSize: 11,
      fontWeight: 'bold',
    },
  });
