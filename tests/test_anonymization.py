import pandas as pd
from app.services.analysis_service import SimpleAnalysisService


def test_anonymization_applied_flag_and_sensitive_columns():
    df = pd.DataFrame({
        'email': ['user1@example.com', 'user2@example.com'],
        'phone': ['+33123456789', '+33987654321'],
        'age': [30, 42],
        'name': ['Alice', 'Bob']
    })

    service = SimpleAnalysisService()
    result = service.analyze_single_file(df=df, question='Analyse', anonymize_data=True)

    privacy = result.get('privacy_report', {})
    assert privacy.get('anonymization_applied') is True
    assert 'email' in privacy.get('sensitive_columns_detected', [])
    assert 'phone' in privacy.get('sensitive_columns_detected', [])
    assert 'name' in privacy.get('sensitive_columns_detected', [])


def test_anonymization_not_applied_flag():
    df = pd.DataFrame({
        'email': ['user1@example.com'],
        'score': [0.8]
    })

    service = SimpleAnalysisService()
    result = service.analyze_single_file(df=df, question='Analyse', anonymize_data=False)

    privacy = result.get('privacy_report', {})
    assert privacy.get('anonymization_applied') is False
    # sensitive_columns_detected should be empty when anonymization is off per current implementation
    assert privacy.get('sensitive_columns_detected') == []


def test_data_is_anonymized_in_output_when_enabled():
    df = pd.DataFrame({
        'email': ['user1@example.com', 'user2@example.com'],
        'user_id': ['u1', 'u2'],
        'value': [1, 2]
    })

    service = SimpleAnalysisService()
    result = service.analyze_single_file(df=df, question='Analyse', anonymize_data=True)

    # Ensure charts and insights generation do not leak raw sensitive values
    # We verify that columns reported in data_summary are present, but values are anonymized for object columns
    data_summary = result.get('data_summary', {})
    columns = data_summary.get('columns', {})
    assert 'email' in columns
    assert 'user_id' in columns

    # The service anonymizes object columns by replacing them with a constant token
    # We ensure ai_analysis exists and does not contain raw emails
    ai_analysis = result.get('ai_analysis', '') or ''
    assert 'user1@example.com' not in ai_analysis
    assert 'user2@example.com' not in ai_analysis




