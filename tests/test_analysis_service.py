import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import os

# Mock OpenAI API key for tests
os.environ['OPENAI_API_KEY'] = 'test-key'

from app.services.analysis_service import AnalysisService
from app.utils.data_processor import DataProcessor

class TestAnalysisService:
    @pytest.fixture
    def analysis_service(self):
        return AnalysisService()

    @pytest.fixture
    def sample_csv_data(self):
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'sales': [100, 150, 200],
            'category': ['A', 'B', 'A']
        })

    @patch('app.services.analysis_service.OpenAIService')
    @patch('app.services.analysis_service.AnonymizationService')
    @patch('app.services.analysis_service.VisualizationService')
    def test_analyze_single_file_success(self, mock_viz, mock_anon, mock_openai, analysis_service, sample_csv_data):
        # Mock setup
        mock_openai_instance = Mock()
        mock_openai_instance.analyze_data.return_value = {
            'insights': [{'type': 'trend', 'description': 'Sales increasing'}],
            'anomalies': [],
            'recommendations': [{'priority': 'high', 'action': 'Monitor trends'}]
        }
        mock_openai.return_value = mock_openai_instance

        mock_anon_instance = Mock()
        mock_anon_instance.anonymize_dataframe.return_value = (sample_csv_data, {'anonymized_columns': []})
        mock_anon.return_value = mock_anon_instance

        mock_viz_instance = Mock()
        mock_viz_instance.generate_charts.return_value = [{'type': 'line', 'data': {}}]
        mock_viz.return_value = mock_viz_instance

        # Test
        result = analysis_service.analyze_single_file(
            sample_csv_data,
            "Quelles sont les tendances dans ces données ?",
            analysis_type="trends",
            include_charts=True,
            anonymize_data=True
        )

        # Assertions
        assert result is not None
        assert 'key_insights' in result
        assert 'anomalies' in result
        assert 'recommendations' in result
        assert 'charts' in result
        assert 'privacy_report' in result

    @patch('app.services.analysis_service.OpenAIService')
    def test_analyze_single_file_no_charts(self, mock_openai, analysis_service, sample_csv_data):
        # Mock setup
        mock_openai_instance = Mock()
        mock_openai_instance.analyze_data.return_value = {
            'insights': [{'type': 'trend', 'description': 'Sales increasing'}],
            'anomalies': [],
            'recommendations': []
        }
        mock_openai.return_value = mock_openai_instance

        # Test
        result = analysis_service.analyze_single_file(
            sample_csv_data,
            "Quelles sont les tendances dans ces données ?",
            include_charts=False
        )

        # Assertions
        assert result is not None
        assert 'charts' in result
        assert len(result['charts']) == 0

    def test_analyze_single_file_invalid_data(self, analysis_service):
        # Test with invalid data
        with pytest.raises(ValueError):
            analysis_service.analyze_single_file(
                None,
                "Test question"
            )

class TestDataProcessor:
    @pytest.fixture
    def data_processor(self):
        return DataProcessor()

    @pytest.fixture
    def sample_csv_data(self):
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03', None],
            'sales': [100, 150, 200, 250],
            'category': ['A', 'B', 'A', 'B'],
            'price': [10.5, 15.2, 12.8, 18.1]
        })

    def test_load_csv_data(self, data_processor, sample_csv_data):
        # Test CSV loading
        csv_string = sample_csv_data.to_csv(index=False)
        result = data_processor.load_csv_data(csv_string)
        
        assert result is not None
        assert len(result) == 4
        assert 'date' in result.columns
        assert 'sales' in result.columns

    def test_clean_data(self, data_processor, sample_csv_data):
        # Test data cleaning
        cleaned_data = data_processor.clean_data(sample_csv_data)
        
        assert cleaned_data is not None
        assert len(cleaned_data) == 3  # One row with None should be removed
        assert cleaned_data['date'].isna().sum() == 0

    def test_generate_summary(self, data_processor, sample_csv_data):
        # Test summary generation
        summary = data_processor.generate_summary(sample_csv_data)
        
        assert summary is not None
        assert 'total_rows' in summary
        assert 'total_columns' in summary
        assert 'column_types' in summary
        assert summary['total_rows'] == 4
        assert summary['total_columns'] == 4

    def test_detect_anomalies(self, data_processor, sample_csv_data):
        # Test anomaly detection
        anomalies = data_processor.detect_anomalies(sample_csv_data, 'sales')
        
        assert anomalies is not None
        assert isinstance(anomalies, list) 