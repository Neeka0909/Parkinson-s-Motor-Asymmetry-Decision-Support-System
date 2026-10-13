import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import ReportCard from '../components/ReportCard';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onBack: () => void };

export default function ProgressScreen({ onBack }: Props) {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.getProgress()
      .then(setData)
      .catch(() => Alert.alert('Error', 'Could not load progress'))
      .finally(() => setLoading(false));
  }, []);

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      const result = await api.analyze();
      setAnalysis(result);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const downloadPdf = async () => {
    setDownloading(true);
    try {
      const created = await api.generateReport();
      await api.downloadReport(created.report_id);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Could not download the report');
    } finally {
      setDownloading(false);
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
      <BigButton title={analyzing ? 'Analyzing...' : t('analyze')} onPress={runAnalysis} />
      {analysis && (
        <>
          <ReportCard
            report={{
              risk_profile: String(analysis.risk_profile ?? ''),
              confidence: Number(analysis.confidence ?? 0),
              recommendation: String(analysis.recommendation ?? ''),
              feature_summary: (analysis.feature_summary ?? {}) as Record<string, number>,
              total_sessions: Number(data?.total_sessions ?? 0),
            }}
          />
          <BigButton
            title={downloading ? 'Preparing PDF...' : 'Download PDF'}
            onPress={downloadPdf}
            variant="secondary"
          />
        </>
      )}
      <BigButton title="Back" onPress={onBack} variant="secondary" />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  stat: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between' },
  statLabel: { fontSize: 18, color: '#555' },
  statValue: { fontSize: 22, fontWeight: '800', color: '#1a5276' },
});
