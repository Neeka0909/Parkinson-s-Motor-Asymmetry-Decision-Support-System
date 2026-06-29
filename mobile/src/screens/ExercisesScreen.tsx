import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onBack: () => void };

type Exercise = {
  key: string;
  title_en: string;
  title_si: string;
  instructions_en: string;
  instructions_si: string;
};

export default function ExercisesScreen({ onBack }: Props) {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getExercises()
      .then((d) => setExercises(d.exercises ?? []))
      .catch(() => Alert.alert('Error', 'Could not load exercises'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ActivityIndicator style={{ flex: 1 }} size="large" color="#1a5276" />;

  return (
    <ScreenContainer title={t('exercises')} subtitle={t('consultNeurologist')}>
      {exercises.map((ex) => (
        <View key={ex.key} style={styles.card}>
          <Text style={styles.title}>{ex.title_en}</Text>
          <Text style={styles.titleSi}>{ex.title_si}</Text>
          <Text style={styles.instructions}>{ex.instructions_en}</Text>
          <Text style={styles.instructionsSi}>{ex.instructions_si}</Text>
        </View>
      ))}
      <BigButton title="Back" onPress={onBack} variant="secondary" />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#fff', borderRadius: 14, padding: 16, marginBottom: 14 },
  title: { fontSize: 20, fontWeight: '800', color: '#1a5276' },
  titleSi: { fontSize: 18, color: '#2ecc71', marginBottom: 8 },
  instructions: { fontSize: 16, color: '#333', lineHeight: 24 },
  instructionsSi: { fontSize: 15, color: '#666', lineHeight: 22, marginTop: 8 },
});
