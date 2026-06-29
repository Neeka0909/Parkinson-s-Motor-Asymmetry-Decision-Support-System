import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onBack: () => void };

export default function ProgressScreen({ onBack }: Props) {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProgress()
      .then(setData)
      .catch(() => Alert.alert('Error', 'Could not load progress'))
      .finally(() => setLoading(false));
  }, []);

  const runAnalysis = async () => {
    try {
      const result = await api.analyze();
      setAnalysis(result);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Analysis failed');
    }
  };

  if (loading) return <ActivityIndicator style={{ flex: 1 }} size="large" color="#1a5276" />;

  return (
    <ScreenContainer title={t('progress')} subtitle={t('consultNeurologist')}>
      <View style={styles.stat}>
        <Text style={styles.statLabel}>{t('totalSessions')}</Text>
        <Text style={styles.statValue}>{String(data?.total_sessions ?? 0)}</Text>
      </View>
      <View style={styles.stat}>
        <Text style={styles.statLabel}>{t('streak')}</Text>
        <Text style={styles.statValue}>{String(data?.streak_days ?? 0)}</Text>
      </View>
      {data?.avg_reaction_time_ms != null && (
        <View style={styles.stat}>
          <Text style={styles.statLabel}>Avg Reaction Time</Text>
          <Text style={styles.statValue}>{String(data.avg_reaction_time_ms)} ms</Text>
        </View>
      )}
      {data?.avg_flight_time_ms != null && (
        <View style={styles.stat}>
          <Text style={styles.statLabel}>Avg Flight Time</Text>
          <Text style={styles.statValue}>{String(data.avg_flight_time_ms)} ms</Text>
        </View>
      )}
      <BigButton title={t('analyze')} onPress={runAnalysis} />
      {analysis && (
        <View style={styles.analysisBox}>
          <Text style={styles.analysisTitle}>{t('riskProfile')}: {String(analysis.risk_profile).toUpperCase()}</Text>
          <Text style={styles.analysisText}>Confidence: {(Number(analysis.confidence) * 100).toFixed(0)}%</Text>
          <Text style={styles.analysisText}>{String(analysis.recommendation)}</Text>
        </View>
      )}
      <BigButton title="Back" onPress={onBack} variant="secondary" />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  stat: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between' },
  statLabel: { fontSize: 18, color: '#555' },
  statValue: { fontSize: 22, fontWeight: '800', color: '#1a5276' },
  analysisBox: { backgroundColor: '#eaf2f8', borderRadius: 12, padding: 16, marginVertical: 12 },
  analysisTitle: { fontSize: 20, fontWeight: '800', color: '#1a5276', marginBottom: 8 },
  analysisText: { fontSize: 16, color: '#333', lineHeight: 24 },
});
