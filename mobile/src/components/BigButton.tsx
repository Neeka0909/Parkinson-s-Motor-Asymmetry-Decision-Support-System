import React from 'react';
import { Pressable, StyleSheet, Text, ViewStyle } from 'react-native';

type Props = {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  style?: ViewStyle;
};

export default function BigButton({ title, onPress, variant = 'primary', style }: Props) {
  return (
    <Pressable
      style={[styles.btn, styles[variant], style]}
      onPress={onPress}
    >
      <Text style={styles.text}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    paddingVertical: 18,
    paddingHorizontal: 24,
    borderRadius: 14,
    alignItems: 'center',
    marginVertical: 8,
    minHeight: 60,
    justifyContent: 'center',
  },
  primary: { backgroundColor: '#1a5276' },
  secondary: { backgroundColor: '#2ecc71' },
  danger: { backgroundColor: '#e74c3c' },
  text: { color: '#fff', fontSize: 20, fontWeight: '700' },
});
