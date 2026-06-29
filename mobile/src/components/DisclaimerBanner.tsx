import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { t, Language } from '../i18n';

type Props = { lang?: Language };

export default function DisclaimerBanner({ lang = 'mixed' }: Props) {
  return (
    <View style={styles.banner}>
      <Text style={styles.text}>{t('disclaimer', lang)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#fdecea',
    borderLeftWidth: 4,
    borderLeftColor: '#e74c3c',
    padding: 14,
    borderRadius: 8,
    marginBottom: 16,
  },
  text: { color: '#922b21', fontSize: 14, lineHeight: 20 },
});
