import React, { useState } from 'react';
import { Alert, StyleSheet, TextInput } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import DisclaimerBanner from '../components/DisclaimerBanner';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onRegistered: () => void; onBack: () => void };

export default function RegisterScreen({ onRegistered, onBack }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState('65');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    setLoading(true);
    try {
      await api.register({
        email,
        password,
        full_name: fullName,
        age: parseInt(age, 10),
        handedness: 'right',
        language_pref: 'mixed',
      });
      onRegistered();
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenContainer title={t('register')} subtitle={t('tagline')}>
      <DisclaimerBanner />
      <TextInput style={styles.input} placeholder={t('fullName')} value={fullName} onChangeText={setFullName} />
      <TextInput style={styles.input} placeholder={t('email')} value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
      <TextInput style={styles.input} placeholder={t('password')} value={password} onChangeText={setPassword} secureTextEntry />
      <TextInput style={styles.input} placeholder={t('age')} value={age} onChangeText={setAge} keyboardType="number-pad" />
      <BigButton title={loading ? '...' : t('register')} onPress={handleRegister} />
      <BigButton title="Back" onPress={onBack} variant="secondary" />
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
