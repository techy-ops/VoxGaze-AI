import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, ActivityIndicator } from 'react-native';
import { apiService } from '../services/apiService';

interface IntelligenceScreenProps {
  isHighContrast: boolean;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}

export const IntelligenceScreen: React.FC<IntelligenceScreenProps> = ({ isHighContrast }) => {
  const [inputText, setInputText] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'bot',
      text: 'Hello! I am VoxGaze Intelligence AI. How can I assist your navigation, gaze shortcuts, or communication today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const handleSendMessage = async (textToSend?: string) => {
    const prompt = textToSend || inputText;
    if (!prompt.trim()) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: 'user',
      text: prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setIsTyping(true);

    const res = await apiService.askGPT(prompt, 'VoxGaze Multimodal Mobile Context');

    const botMsg: ChatMessage = {
      id: String(Date.now() + 1),
      sender: 'bot',
      text: res.response,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, botMsg]);
    setIsTyping(false);
  };

  const styles = getStyles(isHighContrast);

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Multimodal Intelligence Fusion Bar */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🧠 Multimodal Intent Fusion Engine</Text>
          <Text style={styles.cardSub}>Combines Gaze Dwell + Lip Phonemes + Hand Sign Signals</Text>

          <View style={styles.fusionGrid}>
            <View style={styles.fusionPill}>
              <Text style={styles.fusionIcon}>👁️</Text>
              <Text style={styles.fusionLabel}>Gaze: Target Z-2</Text>
            </View>
            <View style={styles.fusionPill}>
              <Text style={styles.fusionIcon}>💋</Text>
              <Text style={styles.fusionLabel}>Lips: Ready</Text>
            </View>
            <View style={styles.fusionPill}>
              <Text style={styles.fusionIcon}>✋</Text>
              <Text style={styles.fusionLabel}>Sign: Palm Open</Text>
            </View>
          </View>
        </View>

        {/* Chat History Container */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🤖 AI Smart Accessibility Assistant</Text>
          <View style={styles.chatBox}>
            {messages.map((msg) => (
              <View
                key={msg.id}
                style={[
                  styles.msgBubble,
                  msg.sender === 'user' ? styles.userBubble : styles.botBubble,
                ]}
              >
                <Text
                  style={[
                    styles.msgText,
                    msg.sender === 'user' ? styles.userMsgText : styles.botMsgText,
                  ]}
                >
                  {msg.text}
                </Text>
                <Text style={styles.msgTime}>{msg.timestamp}</Text>
              </View>
            ))}

            {isTyping && (
              <View style={[styles.msgBubble, styles.botBubble, { flexDirection: 'row', gap: 6 }]}>
                <ActivityIndicator size="small" color={isHighContrast ? '#F59E0B' : '#6366F1'} />
                <Text style={styles.botMsgText}>Thinking...</Text>
              </View>
            )}
          </View>
        </View>

        {/* Quick Gaze & Voice Shortcuts */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>⚡ Quick Accessibility Prompts</Text>
          <View style={styles.quickPromptContainer}>
            {[
              'Summarize screen options',
              'Open gaze calibration',
              'Set high contrast theme',
              'Send location to contacts',
            ].map((promptText) => (
              <TouchableOpacity
                key={promptText}
                style={styles.promptBtn}
                onPress={() => handleSendMessage(promptText)}
              >
                <Text style={styles.promptBtnText}>{promptText}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Input Bar */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          placeholder="Ask AI assistant or type prompt..."
          placeholderTextColor="#64748B"
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={() => handleSendMessage()}
        />
        <TouchableOpacity
          style={styles.sendBtn}
          onPress={() => handleSendMessage()}
          activeOpacity={0.7}
        >
          <Text style={styles.sendBtnText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const getStyles = (isHighContrast: boolean) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isHighContrast ? '#050505' : '#090D16',
    },
    scrollContent: {
      padding: 16,
      gap: 16,
      paddingBottom: 20,
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
      marginBottom: 4,
    },
    cardSub: {
      color: isHighContrast ? '#D1D5DB' : '#94A3B8',
      fontSize: 12,
      marginBottom: 12,
    },
    fusionGrid: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      gap: 8,
    },
    fusionPill: {
      flex: 1,
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      paddingVertical: 10,
      paddingHorizontal: 8,
      borderRadius: 12,
      alignItems: 'center',
      borderWidth: 1,
      borderColor: isHighContrast ? '#F59E0B' : '#334155',
    },
    fusionIcon: {
      fontSize: 20,
    },
    fusionLabel: {
      color: isHighContrast ? '#F59E0B' : '#38BDF8',
      fontSize: 10,
      fontWeight: 'bold',
      marginTop: 4,
    },
    chatBox: {
      gap: 10,
      marginTop: 8,
    },
    msgBubble: {
      padding: 12,
      borderRadius: 14,
      maxWidth: '85%',
    },
    userBubble: {
      alignSelf: 'flex-end',
      backgroundColor: isHighContrast ? '#F59E0B' : '#6366F1',
    },
    botBubble: {
      alignSelf: 'flex-start',
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      borderWidth: 1,
      borderColor: isHighContrast ? '#374151' : '#334155',
    },
    msgText: {
      fontSize: 13,
      lineHeight: 18,
    },
    userMsgText: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: '600',
    },
    botMsgText: {
      color: isHighContrast ? '#FFFFFF' : '#E2E8F0',
    },
    msgTime: {
      fontSize: 9,
      color: isHighContrast ? '#4B5563' : '#64748B',
      alignSelf: 'flex-end',
      marginTop: 4,
    },
    quickPromptContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
      marginTop: 8,
    },
    promptBtn: {
      backgroundColor: isHighContrast ? '#1F2937' : '#0F172A',
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderRadius: 20,
      borderWidth: 1,
      borderColor: isHighContrast ? '#F59E0B' : '#6366F1',
    },
    promptBtnText: {
      color: isHighContrast ? '#F59E0B' : '#A5B4FC',
      fontSize: 12,
      fontWeight: '600',
    },
    inputContainer: {
      flexDirection: 'row',
      padding: 12,
      backgroundColor: isHighContrast ? '#000000' : '#0F172A',
      borderTopWidth: isHighContrast ? 2 : 1,
      borderTopColor: isHighContrast ? '#F59E0B' : '#1E293B',
      gap: 8,
    },
    textInput: {
      flex: 1,
      backgroundColor: isHighContrast ? '#111111' : '#1E293B',
      color: '#FFFFFF',
      borderRadius: 12,
      paddingHorizontal: 14,
      paddingVertical: 10,
      fontSize: 14,
      borderWidth: 1,
      borderColor: isHighContrast ? '#374151' : '#334155',
    },
    sendBtn: {
      backgroundColor: isHighContrast ? '#F59E0B' : '#6366F1',
      paddingHorizontal: 18,
      justifyContent: 'center',
      borderRadius: 12,
    },
    sendBtnText: {
      color: isHighContrast ? '#000000' : '#FFFFFF',
      fontWeight: 'bold',
      fontSize: 14,
    },
  });
