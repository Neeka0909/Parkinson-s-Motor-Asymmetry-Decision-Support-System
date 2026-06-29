import React, { useState } from 'react';
import { Alert } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import DisclaimerBanner from '../components/DisclaimerBanner';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onBack: () => void };

export default function ReportScreen({ onBack }: Props) {
  const [loading, setLoading] = useState(false);
  const [reportId, setReportId] = useState<string | null>(null);

  const generate = async () => {
    setLoading(true);
    try {
      const result = await api.generateReport();
      setReportId(result.report_id);
      Alert.alert('Success', `Report generated: ${result.report_id}\nDownload via API: ${result.download_url}`);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Report generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenContainer title={t('report')} subtitle="For your neurologist">
      <DisclaimerBanner />
      <BigButton title={loading ? '...' : t('generateReport')} onPress={generate} />
      {reportId && <BigButton title={`Report ID: ${reportId}`} onPress={() => {}} variant="secondary" />}
      <BigButton title="Back" onPress={onBack} variant="secondary" />
    </ScreenContainer>
  );
}
