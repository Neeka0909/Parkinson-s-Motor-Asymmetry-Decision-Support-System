import React from 'react';
import { ScrollView, StyleSheet, Text, ViewStyle } from 'react-native';

type Props = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  style?: ViewStyle;
};

export default function ScreenContainer({ title, subtitle, children, style }: Props) {
  return (
    <ScrollView
      style={[styles.container, style]}
      contentContainerStyle={styles.content}
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.title}>{title}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {children}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f6fa' },
  content: { padding: 24, paddingTop: 56, paddingBottom: 40 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a5276', marginBottom: 4 },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 20 },
});
