import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { apiService, EmergencyResponse } from '../services/apiService';

interface EmergencyScreenProps {
  isHighContrast: boolean;
}

export const EmergencyScreen: React.FC<EmergencyScreenProps> = ({ isHighContrast }) => {
  const [countdown, setCountdown] = useState<number | null>(null);
  const [alertStatus, setAlertStatus] = useState<EmergencyResponse | null>(null);
  const [isAlertActive, setIsAlertActive] = useState<boolean>(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (countdown !== null && countdown > 0) {
      timer = setTimeout(() => {
        setCountdown((prev) => (prev !== null ? prev - 1 : null));
      }, 1000);
    } else if (countdown === 0) {
      triggerEmergencyAlert();
      setCountdown(null);
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const startSosCountdown = () => {
    setCountdown(3);
  };

  const cancelSos = () => {
    setCountdown(null);
  };

  const triggerEmergencyAlert = async () => {
    setIsAlertActive(true);
    const res = await apiService.triggerEmergency('usr_voxgaze_1001');
    setAlertStatus(res);
  };

  const resetAlert = () => {
    setIsAlertActive(false);
    setAlertStatus(null);
  };

  const styles = getStyles(isHighContrast);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* High Visibility Emergency SOS Card */}
      <View style={[styles.card, styles.emergencyCard]}>
        <Text style={styles.emergencyTitle}>🚨 EMERGENCY ASSISTANCE HUB</Text>
        <Text style={styles.emergencySub}>
          Gaze hold or tap below to send immediate distress alert with your location
        </Text>

        {countdown !== null ? (
          <View style={styles.countdownBox}>
            <Text style={styles.countdownNumber}>{countdown}</Text>
            <Text style={styles.countdownLabel}>DISPATCHING EMERGENCY ALERT IN...</Text>
            <TouchableOpacity style={styles.cancelBtn} onPress={cancelSos} activeOpacity={0.7}>
              <Text style={styles.cancelBtnText}>❌ CANCEL SOS ALERT</Text>
            </TouchableOpacity>
          </View>
        ) : isAlertActive ? (
          <View style={styles.activeAlertBox}>
            <Text style={styles.alertHeader}>🚨 EMERGENCY DISPATCH ACTIVE!</Text>
            <Text style={styles.alertDetails}>Alert ID: {alertStatus?.alert_id}</Text>
            <Text style={styles.alertDetails}>{alertStatus?.message}</Text>

            <TouchableOpacity style={styles.resetBtn} onPress={resetAlert} activeOpacity={0.7}>
              <Text style={styles.resetBtnText}>✅ Mark Safe / Dismiss Alert</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity style={styles.sosButton} onPress={startSosCountdown} activeOpacity={0.8}>
            <Text style={styles.sosButtonIcon}>🆘</Text>

            <Text style={styles.sosButtonText}>HOLD GAZE OR TAP FOR SOS</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* GPS Location Broadcaster */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📍 Live GPS Broadcast</Text>
        <View style={styles.locationRow}>
          <Text style={styles.locLabel}>LATITUDE / LONGITUDE:</Text>
          <Text style={styles.locValue}>37.7749° N, 122.4194° W</Text>
        </View>
        <View style={styles.locationRow}>
          <Text style={styles.locLabel}>ACCURACY:</Text>
          <Text style={styles.locValue}>High Precision (± 3 meters)</Text>
        </View>
      </View>

      {/* Primary Emergency Contacts */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📞 Designated Emergency Contacts</Text>
        {[
          { name: 'Family Contact (Sarah)', phone: '+1 (555) 019-2831', status: 'Notified on SOS' },
          { name: 'Caregiver (Dr. Alex)', phone: '+1 (555) 014-9920', status: 'Notified on SOS' },
          { name: 'Local Emergency Dispatch', phone: '911', status: 'Automatic Call' },
        ].map((contact, idx) => (
          <View key={idx} style={styles.contactRow}>
            <View>
              <Text style={styles.contactName}>{contact.name}</Text>
              <Text style={styles.contactPhone}>{contact.phone}</Text>
            </View>
            <Text style={styles.contactStatus}>{contact.status}</Text>
          </View>
        ))}
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
    emergencyCard: {
      backgroundColor: isHighContrast ? '#7F1D1D' : '#450A0A',
      borderColor: '#EF4444',
      borderWidth: 2,
      alignItems: 'center',
    },
    emergencyTitle: {
      color: '#FFFFFF',
      fontSize: 18,
      fontWeight: 'bold',
      textAlign: 'center',
    },
    emergencySub: {
      color: '#FECACA',
      fontSize: 12,
      textAlign: 'center',
      marginTop: 4,
      marginBottom: 16,
    },
    sosButton: {
      width: '100%',
      backgroundColor: '#DC2626',
      borderRadius: 20,
      paddingVertical: 24,
      alignItems: 'center',
      justifyContent: 'center',
      borderWidth: 3,
      borderColor: '#F87171',
      shadowColor: '#EF4444',
      shadowOpacity: 0.8,
      shadowRadius: 10,
    },
    sosButtonIcon: {
      fontSize: 48,
      marginBottom: 6,
    },
    sosButtonText: {
      color: '#FFFFFF',
      fontSize: 16,
      fontWeight: '900',
      letterSpacing: 1,
    },
    countdownBox: {
      alignItems: 'center',
      paddingVertical: 12,
      width: '100%',
    },
    countdownNumber: {
      color: '#F59E0B',
      fontSize: 64,
      fontWeight: 'bold',
    },
    countdownLabel: {
      color: '#FFFFFF',
      fontSize: 12,
      fontWeight: 'bold',
      marginBottom: 12,
    },
    cancelBtn: {
      backgroundColor: '#374151',
      paddingHorizontal: 20,
      paddingVertical: 10,
      borderRadius: 10,
    },
    cancelBtnText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
    },
    activeAlertBox: {
      backgroundColor: '#991B1B',
      width: '100%',
      borderRadius: 12,
      padding: 16,
      alignItems: 'center',
    },
    alertHeader: {
      color: '#FFFFFF',
      fontSize: 16,
      fontWeight: 'bold',
      marginBottom: 8,
    },
    alertDetails: {
      color: '#FEE2E2',
      fontSize: 13,
      textAlign: 'center',
      marginTop: 2,
    },
    resetBtn: {
      backgroundColor: '#10B981',
      paddingHorizontal: 16,
      paddingVertical: 10,
      borderRadius: 10,
      marginTop: 14,
    },
    resetBtnText: {
      color: '#000000',
      fontWeight: 'bold',
    },
    cardTitle: {
      color: isHighContrast ? '#FFFFFF' : '#F8FAFC',
      fontSize: 16,
      fontWeight: 'bold',
      marginBottom: 10,
    },
    locationRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginVertical: 4,
    },
    locLabel: {
      color: isHighContrast ? '#9CA3AF' : '#94A3B8',
      fontSize: 12,
      fontWeight: '600',
    },
    locValue: {
      color: isHighContrast ? '#F59E0B' : '#38BDF8',
      fontSize: 12,
      fontWeight: 'bold',
    },
    contactRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      padding: 12,
      borderRadius: 10,
      marginTop: 8,
    },
    contactName: {
      color: isHighContrast ? '#FFFFFF' : '#F8FAFC',
      fontSize: 13,
      fontWeight: 'bold',
    },
    contactPhone: {
      color: isHighContrast ? '#9CA3AF' : '#94A3B8',
      fontSize: 11,
    },
    contactStatus: {
      color: isHighContrast ? '#F59E0B' : '#34D399',
      fontSize: 11,
      fontWeight: 'bold',
    },
  });
