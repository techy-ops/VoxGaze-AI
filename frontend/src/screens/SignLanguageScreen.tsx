import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { apiService, SignLanguageResponse } from '../services/apiService';

interface SignLanguageScreenProps {
  isHighContrast: boolean;
}

export const SignLanguageScreen: React.FC<SignLanguageScreenProps> = ({ isHighContrast }) => {
  const [isTranslating, setIsTranslating] = useState<boolean>(false);
  const [result, setResult] = useState<SignLanguageResponse | null>(null);
  const [phraseBuilder, setPhraseBuilder] = useState<string[]>([]);
  const [activeGesture, setActiveGesture] = useState<string>('Open Palm (Waiting)');

  const handleRecognizeGesture = async () => {
    setIsTranslating(true);
    // Simulate 21 hand landmarks
    const mockLandmarks = Array.from({ length: 21 }, (_, i) => ({
      x: 0.1 * (i % 5),
      y: 0.1 * Math.floor(i / 5),
      z: 0.05 * i,
    }));

    const response = await apiService.processSignLanguage(mockLandmarks);
    setResult(response);
    setActiveGesture(response.translated_text);
    setPhraseBuilder((prev) => [...prev, response.translated_text]);
    setIsTranslating(false);
  };

  const handleClearPhrase = () => {
    setPhraseBuilder([]);
  };

  const styles = getStyles(isHighContrast);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Hand Tracking Viewport */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>✋ Sign Language Gesture Decoder</Text>
        <Text style={styles.cardSub}>Tracks 21 3D hand keypoints for real-time sign recognition</Text>

        <View style={styles.trackingBox}>
          {/* Simulated 21-point hand landmark overlay */}
          <View style={styles.handSkeleton}>
            <View style={styles.wristNode} />
            <View style={styles.thumbLine} />
            <View style={styles.indexLine} />
            <View style={styles.middleLine} />
            <View style={styles.ringLine} />
            <View style={styles.pinkyLine} />
            <Text style={styles.handIcon}>🖐️</Text>
          </View>

          <Text style={styles.gestureTag}>Current Gesture: {activeGesture}</Text>

          {isTranslating && (
            <View style={styles.overlayLoader}>
              <ActivityIndicator size="large" color={isHighContrast ? '#F59E0B' : '#10B981'} />
              <Text style={styles.loaderText}>Extracting Hand Landmarks...</Text>
            </View>
          )}
        </View>

        <TouchableOpacity
          style={[styles.translateBtn, isTranslating && styles.btnDisabled]}
          onPress={handleRecognizeGesture}
          disabled={isTranslating}
          activeOpacity={0.7}
        >
          <Text style={styles.translateBtnText}>
            {isTranslating ? 'Analyzing Gestures...' : '✋ Decode Active Sign Gesture'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Sentence Builder */}
      <View style={styles.card}>
        <View style={styles.builderHeader}>
          <Text style={styles.cardTitle}>📝 Assembled Phrase Builder</Text>
          <TouchableOpacity onPress={handleClearPhrase}>
            <Text style={styles.clearBtnText}>Clear</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.sentenceBox}>
          {phraseBuilder.length === 0 ? (
            <Text style={styles.emptySentence}>No gestures added to sentence yet...</Text>
          ) : (
            <Text style={styles.sentenceText}>{phraseBuilder.join(' ')}</Text>
          )}
        </View>

        {phraseBuilder.length > 0 && (
          <TouchableOpacity style={styles.speakSentenceBtn} activeOpacity={0.7}>
            <Text style={styles.speakSentenceText}>📢 Speak Full Sentence</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Common Quick Signs */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>⚡ Quick Gesture Dictionary</Text>
        <View style={styles.quickGrid}>
          {['Thank You', 'Help Me', 'Water', 'Hello', 'Emergency', 'Yes', 'No', 'Goodbye'].map(
            (sign) => (
              <TouchableOpacity
                key={sign}
                style={styles.quickPill}
                onPress={() => {
                  setActiveGesture(sign);
                  setPhraseBuilder((prev) => [...prev, sign]);
                }}
              >
                <Text style={styles.quickPillText}>{sign}</Text>
              </TouchableOpacity>
            )
          )}
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
    },
    cardSub: {
      color: isHighContrast ? '#D1D5DB' : '#94A3B8',
      fontSize: 12,
      marginBottom: 12,
    },
    trackingBox: {
      height: 180,
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      borderRadius: 14,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 2,
      borderColor: isHighContrast ? '#F59E0B' : '#10B981',
      overflow: 'hidden',
      marginBottom: 12,
    },
    handSkeleton: {
      alignItems: 'center',
      justifyContent: 'center',
    },
    wristNode: {},
    thumbLine: {},
    indexLine: {},
    middleLine: {},
    ringLine: {},
    pinkyLine: {},
    handIcon: {
      fontSize: 48,
    },
    gestureTag: {
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      color: isHighContrast ? '#F59E0B' : '#34D399',
      paddingHorizontal: 12,
      paddingVertical: 4,
      borderRadius: 12,
      fontSize: 12,
      fontWeight: 'bold',
      marginTop: 8,
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
    translateBtn: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#10B981',
      paddingVertical: 12,
      borderRadius: 12,
      alignItems: 'center',
    },
    btnDisabled: {
      opacity: 0.6,
    },
    translateBtnText: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 14,
    },
    builderHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 8,
    },
    clearBtnText: {
      color: '#EF4444',
      fontWeight: 'bold',
      fontSize: 12,
    },
    sentenceBox: {
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      borderRadius: 12,
      padding: 14,
      minHeight: 60,
      justifyContent: 'center',
      borderWidth: 1,
      borderColor: isHighContrast ? '#374151' : '#334155',
    },
    emptySentence: {
      color: '#64748B',
      fontStyle: 'italic',
      fontSize: 12,
    },
    sentenceText: {
      color: '#F8FAFC',
      fontSize: 16,
      fontWeight: 'bold',
    },
    speakSentenceBtn: {
      backgroundColor: isHighContrast ? '#10B981' : '#059669',
      paddingVertical: 10,
      borderRadius: 10,
      alignItems: 'center',
      marginTop: 10,
    },
    speakSentenceText: {
      color: '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 13,
    },
    quickGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
      marginTop: 8,
    },
    quickPill: {
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 20,
      borderWidth: 1,
      borderColor: isHighContrast ? '#F59E0B' : '#334155',
    },
    quickPillText: {
      color: isHighContrast ? '#F59E0B' : '#38BDF8',
      fontSize: 12,
      fontWeight: '600',
    },
  });
