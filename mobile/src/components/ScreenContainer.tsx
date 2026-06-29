import React from 'react';
import { StyleSheet, Text, View, ViewStyle } from 'react-native';

type Props = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  style?: ViewStyle;
};

export default function ScreenContainer({ title, subtitle, children, style }: Props) {
  return (
    <View style={[styles.container, style]}>
      <Text style={styles.title}>{title}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f6fa', padding: 24, paddingTop: 56 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a5276', marginBottom: 4 },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 20 },
});
