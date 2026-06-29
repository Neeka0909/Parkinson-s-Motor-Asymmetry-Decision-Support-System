import React, { useState } from 'react';
import { Alert, StyleSheet, Text, TextInput, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import DisclaimerBanner from '../components/DisclaimerBanner';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onLogin: () => void; onGoRegister: () => void };

export default function LoginScreen({ onLogin, onGoRegister }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      await api.login(email, password);
      onLogin();
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenContainer title={t('appName')} subtitle={t('tagline')}>
      <DisclaimerBanner />
      <TextInput style={styles.input} placeholder={t('email')} value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
      <TextInput style={styles.input} placeholder={t('password')} value={password} onChangeText={setPassword} secureTextEntry />
      <BigButton title={loading ? '...' : t('login')} onPress={handleLogin} />
      <BigButton title={t('register')} onPress={onGoRegister} variant="secondary" />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  input: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    fontSize: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#ddd',
    minHeight: 56,
  },
});
