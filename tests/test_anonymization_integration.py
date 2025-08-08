import os
from datetime import datetime
import hashlib
import pandas as pd
import pytest
from app.services.analysis_service import SimpleAnalysisService


@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY absente: test d'intégration ignoré")
def test_integration_openai_anonymization_no_leak(tmp_path):
    # Petit dataset avec colonnes sensibles
    df = pd.DataFrame({
        'email': ['alice@example.com', 'bob@example.com'],
        'phone': ['+33111111111', '+33222222222'],
        'score': [0.9, 0.7]
    })

    service = SimpleAnalysisService()
    # Utiliser un modèle économique si possible
    service.settings["model"] = "gpt-4.1-mini"

    result = service.analyze_single_file(df=df, question='Analyse test intégration', anonymize_data=True)

    # Vérifications clés
    assert result.get('ai_analysis'), "ai_analysis doit être non vide"
    ai_text = result['ai_analysis']
    assert 'alice@example.com' not in ai_text
    assert 'bob@example.com' not in ai_text

    privacy = result.get('privacy_report', {})
    assert privacy.get('anonymization_applied') is True

    # Écrire une preuve claire et exploitable dans les logs (pour livrables)
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    out = os.path.join(logs_dir, 'anonymization_integration_test.log')
    sha = hashlib.sha256(ai_text.encode('utf-8')).hexdigest()[:12]
    sensitive_cols = privacy.get('sensitive_columns_detected', [])
    model_used = service.settings.get('model')
    with open(out, 'a', encoding='utf-8') as f:
        f.write(
            (
                "\n=== Anonymization Integration Test ===\n"
                f"timestamp: {datetime.utcnow().isoformat()}Z\n"
                f"model: {model_used}\n"
                f"anonymization_applied: {privacy.get('anonymization_applied')}\n"
                f"sensitive_columns_detected_count: {len(sensitive_cols)}\n"
                f"sensitive_columns_detected: {', '.join(sensitive_cols) if sensitive_cols else '-'}\n"
                f"ai_analysis_length: {len(ai_text)}\n"
                f"ai_analysis_sha256_12: {sha}\n"
                "result: PASS\n"
            )
        )


