import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { apiService, LipReadingResponse } from '../services/apiService';

interface LipReadingScreenProps {
  isHighContrast: boolean;
}

export const LipReadingScreen: React.FC<LipReadingScreenProps> = ({ isHighContrast }) => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [result, setResult] = useState<LipReadingResponse | null>(null);
  const [history, setHistory] = useState<LipReadingResponse[]>([]);
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);

  const handleCaptureLipStream = async () => {
    setIsProcessing(true);
    const response = await apiService.processLipReading();
    setResult(response);
    setHistory((prev) => [response, ...prev]);
    setIsProcessing(false);
  };

  const handleSpeakTTS = (text: string) => {
    setIsPlayingAudio(true);
    setTimeout(() => {
      setIsPlayingAudio(false);
    }, 2000);
  };

  const styles = getStyles(isHighContrast);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Video Viewport Simulated Feed */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>👄 Silent Speech & Lip Reading AI</Text>
        <Text style={styles.cardSub}>Place your lips within camera view to decode non-verbal speech</Text>

        <View style={styles.cameraBox}>
          <View style={styles.lipTargetFrame}>
            <Text style={styles.lipIcon}>💋</Text>
            <Text style={styles.cameraGuideText}>Keep lips centered</Text>
          </View>

          {isProcessing && (
            <View style={styles.overlayLoader}>
              <ActivityIndicator size="large" color={isHighContrast ? '#F59E0B' : '#6366F1'} />
              <Text style={styles.loaderText}>Analyzing lip phonemes...</Text>
            </View>
          )}
        </View>

        <TouchableOpacity
          style={[styles.captureBtn, isProcessing && styles.btnDisabled]}
          onPress={handleCaptureLipStream}
          disabled={isProcessing}
          activeOpacity={0.7}
        >
          <Text style={styles.captureBtnText}>
            {isProcessing ? 'Decoding Stream...' : '🎙️ Capture & Decode Lip Movement'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Output Transcript */}
      {result && (
        <View style={styles.card}>
          <View style={styles.resultHeader}>
            <Text style={styles.resultLabel}>DECODED SPEECH TRANSCRIPT</Text>
            <Text style={styles.confidencePill}>
              Confidence: {Math.round(result.confidence * 100)}%
            </Text>
          </View>

          <View style={styles.transcriptBox}>
            <Text style={styles.transcriptText}>"{result.transcript}"</Text>
          </View>

          <TouchableOpacity
            style={styles.ttsBtn}
            onPress={() => handleSpeakTTS(result.transcript)}
            activeOpacity={0.7}
          >
            <Text style={styles.ttsBtnText}>
              {isPlayingAudio ? '🔊 Speaking...' : '🔊 Read Aloud (Text-to-Speech)'}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Recognized Speech History */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📋 Recognized Lip Sequences</Text>
        {history.length === 0 ? (
          <Text style={styles.emptyText}>No decoded lip phrases yet. Tap capture above!</Text>
        ) : (
          history.map((item, idx) => (
            <View key={idx} style={styles.historyRow}>
              <Text style={styles.historyText}>"{item.transcript}"</Text>
              <TouchableOpacity
                style={styles.miniTtsBtn}
                onPress={() => handleSpeakTTS(item.transcript)}
              >
                <Text style={styles.miniTtsText}>🔊</Text>
              </TouchableOpacity>
            </View>
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
    cameraBox: {
      height: 180,
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      borderRadius: 14,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 2,
      borderColor: isHighContrast ? '#374151' : '#334155',
      borderStyle: 'dashed',
      overflow: 'hidden',
      marginBottom: 12,
    },
    lipTargetFrame: {
      alignItems: 'center',
      padding: 12,
      borderRadius: 50,
      borderWidth: 2,
      borderColor: isHighContrast ? '#F59E0B' : '#6366F1',
    },
    lipIcon: {
      fontSize: 36,
    },
    cameraGuideText: {
      color: '#94A3B8',
      fontSize: 11,
      marginTop: 4,
    },
    overlayLoader: {
      ...StyleSheet.absoluteFillObject,
      backgroundColor: 'rgba(15, 23, 42, 0.85)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    loaderText: {
      color: '#F8FAFC',
      fontSize: 13,
      fontWeight: '600',
      marginTop: 8,
    },
    captureBtn: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#6366F1',
      paddingVertical: 12,
      borderRadius: 12,
      alignItems: 'center',
    },
    btnDisabled: {
      opacity: 0.6,
    },
    captureBtnText: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 14,
    },
    resultHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 8,
    },
    resultLabel: {
      color: isHighContrast ? '#F59E0B' : '#38BDF8',
      fontSize: 11,
      fontWeight: 'bold',
    },
    confidencePill: {
      backgroundColor: '#10B981',
      color: '#000000',
      paddingHorizontal: 8,
      paddingVertical: 2,
      borderRadius: 10,
      fontSize: 10,
      fontWeight: 'bold',
    },
    transcriptBox: {
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      borderRadius: 12,
      padding: 16,
      marginVertical: 8,
      borderLeftWidth: 4,
      borderLeftColor: isHighContrast ? '#F59E0B' : '#10B981',
    },
    transcriptText: {
      color: '#FFFFFF',
      fontSize: 18,
      fontWeight: 'bold',
    },
    ttsBtn: {
      backgroundColor: isHighContrast ? '#10B981' : '#059669',
      paddingVertical: 10,
      borderRadius: 10,
      alignItems: 'center',
      marginTop: 6,
    },
    ttsBtnText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 13,
    },
    emptyText: {
      color: '#64748B',
      fontStyle: 'italic',
      fontSize: 12,
      marginTop: 4,
    },
    historyRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      padding: 10,
      borderRadius: 8,
      marginTop: 6,
    },
    historyText: {
      color: isHighContrast ? '#FFFFFF' : '#E2E8F0',
      fontSize: 13,
      flex: 1,
    },
    miniTtsBtn: {
      padding: 6,
    },
    miniTtsText: {
      fontSize: 16,
    },
  });
