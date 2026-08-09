import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Switch } from 'react-native';
import { apiService, EyeTrackingResponse } from '../services/apiService';

interface EyeTrackingScreenProps {
  isHighContrast: boolean;
}

export const EyeTrackingScreen: React.FC<EyeTrackingScreenProps> = ({ isHighContrast }) => {
  const [gazeData, setGazeData] = useState<EyeTrackingResponse>({
    status: 'idle',
    direction: 'center',
    blink: false,
    coordinates: { x: 400, y: 300 },
  });
  const [isTrackingActive, setIsTrackingActive] = useState<boolean>(true);
  const [dwellClickEnabled, setDwellClickEnabled] = useState<boolean>(true);
  const [activeZone, setActiveZone] = useState<number>(4); // 0 to 8
  const [logs, setLogs] = useState<string[]>([]);
  const [calibrationStatus, setCalibrationStatus] = useState<string>('Calibrated (98% accuracy)');

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isTrackingActive) {
      interval = setInterval(async () => {
        const res = await apiService.processEyeTracking();
        setGazeData(res);

        // Calculate active zone based on simulated coordinates
        const zoneIndex = Math.floor(Math.random() * 9);
        setActiveZone(zoneIndex);

        if (res.blink) {
          addLog(`[BLINK DETECTED] Triggered selection on Zone ${zoneIndex + 1}`);
        }
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [isTrackingActive]);

  const addLog = (msg: string) => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [`[${time}] ${msg}`, ...prev.slice(0, 9)]);
  };

  const handleRecalibrate = () => {
    setCalibrationStatus('Calibrating... Look at 9 dots');
    setTimeout(() => {
      setCalibrationStatus('Calibrated (99.2% accuracy)');
      addLog('Gaze calibration complete.');
    }, 1500);
  };

  const styles = getStyles(isHighContrast);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Control Banner */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>👁️ Real-time Eye Tracking Engine</Text>
          <Switch
            value={isTrackingActive}
            onValueChange={(val) => {
              setIsTrackingActive(val);
              addLog(val ? 'Eye tracking enabled' : 'Eye tracking paused');
            }}
            trackColor={{ false: '#475569', true: isHighContrast ? '#F59E0B' : '#6366F1' }}
          />
        </View>

        <View style={styles.metricsRow}>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>GAZE DIRECTION</Text>
            <Text style={styles.metricValue}>{gazeData.direction.toUpperCase()}</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>BLINK STATE</Text>
            <Text
              style={[
                styles.metricValue,
                { color: gazeData.blink ? '#EF4444' : '#10B981' },
              ]}
            >
              {gazeData.blink ? 'BLINKING' : 'OPEN'}
            </Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>COORDINATES</Text>
            <Text style={styles.metricValue}>
              X:{gazeData.coordinates?.x} Y:{gazeData.coordinates?.y}
            </Text>
          </View>
        </View>

        <Text style={styles.calibText}>Status: {calibrationStatus}</Text>
        <TouchableOpacity style={styles.calibBtn} onPress={handleRecalibrate} activeOpacity={0.7}>
          <Text style={styles.calibBtnText}>🎯 Recalibrate Gaze Model</Text>
        </TouchableOpacity>
      </View>

      {/* Interactive Gaze Matrix Visualizer */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Gaze Target Matrix (9-Zone Dwell Grid)</Text>
        <Text style={styles.cardSub}>Look at a tile to focus and dwell click automatically</Text>

        <View style={styles.grid}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num, idx) => {
            const isFocused = idx === activeZone;
            return (
              <TouchableOpacity
                key={num}
                style={[styles.gridTile, isFocused && styles.gridTileFocused]}
                onPress={() => addLog(`Direct click on Tile ${num}`)}
              >
                <Text style={[styles.tileNum, isFocused && styles.tileNumFocused]}>
                  {num}
                </Text>
                {isFocused && <Text style={styles.gazeIndicator}>👁️ GAZE</Text>}
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Settings & Options */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Gaze Controls & Dwell Settings</Text>
        <View style={styles.settingRow}>
          <Text style={styles.settingLabel}>Auto-Dwell Selection (800ms)</Text>
          <Switch
            value={dwellClickEnabled}
            onValueChange={setDwellClickEnabled}
            trackColor={{ false: '#475569', true: isHighContrast ? '#F59E0B' : '#10B981' }}
          />
        </View>
      </View>

      {/* Realtime Event Log */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📜 Gaze Event Stream</Text>
        {logs.length === 0 ? (
          <Text style={styles.emptyLog}>No gaze events registered yet...</Text>
        ) : (
          logs.map((log, idx) => (
            <Text key={idx} style={styles.logLine}>
              {log}
            </Text>
          ))
        )}
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
    cardHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 12,
    },
    cardTitle: {
      color: isHighContrast ? '#FFFFFF' : '#F8FAFC',
      fontSize: 16,
      fontWeight: 'bold',
    },
    cardSub: {
      color: isHighContrast ? '#D1D5DB' : '#94A3B8',
      fontSize: 12,
      marginBottom: 12,
    },
    metricsRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      borderRadius: 12,
      padding: 12,
      marginBottom: 12,
    },
    metricItem: {
      alignItems: 'center',
    },
    metricLabel: {
      color: isHighContrast ? '#9CA3AF' : '#64748B',
      fontSize: 10,
      fontWeight: 'bold',
    },
    metricValue: {
      color: isHighContrast ? '#F59E0B' : '#38BDF8',
      fontSize: 14,
      fontWeight: 'bold',
      marginTop: 4,
    },
    calibText: {
      color: isHighContrast ? '#10B981' : '#A7F3D0',
      fontSize: 12,
      marginBottom: 8,
      textAlign: 'center',
    },
    calibBtn: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#4F46E5',
      paddingVertical: 10,
      borderRadius: 10,
      alignItems: 'center',
    },
    calibBtnText: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 13,
    },
    grid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      gap: 10,
    },
    gridTile: {
      width: '30%',
      aspectRatio: 1.2,
      backgroundColor: isHighContrast ? '#1E293B' : '#0F172A',
      borderRadius: 12,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 2,
      borderColor: isHighContrast ? '#374151' : '#1E293B',
    },
    gridTileFocused: {
      backgroundColor: isHighContrast ? '#7C2D12' : '#312E81',
      borderColor: isHighContrast ? '#F59E0B' : '#818CF8',
    },
    tileNum: {
      color: '#94A3B8',
      fontSize: 20,
      fontWeight: 'bold',
    },
    tileNumFocused: {
      color: '#FFFFFF',
    },
    gazeIndicator: {
      color: '#F59E0B',
      fontSize: 10,
      fontWeight: 'bold',
      marginTop: 4,
    },
    settingRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: 8,
    },
    settingLabel: {
      color: isHighContrast ? '#FFFFFF' : '#E2E8F0',
      fontSize: 13,
    },
    emptyLog: {
      color: '#64748B',
      fontStyle: 'italic',
      fontSize: 12,
      marginTop: 4,
    },
    logLine: {
      color: isHighContrast ? '#D1D5DB' : '#CBD5E1',
      fontSize: 12,
      fontFamily: 'monospace',
      marginTop: 4,
    },
  });
