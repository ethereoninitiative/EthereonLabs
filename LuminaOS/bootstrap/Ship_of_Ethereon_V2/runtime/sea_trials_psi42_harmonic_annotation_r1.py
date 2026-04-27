def test_annotation_does_not_mutate_metrics():
    from psi42_harmonic_annotation_bridge_r1 import annotate_psi42_result

    original = {"metrics": {"lock": 0.7, "presence": 0.5}}
    annotated = annotate_psi42_result(original)

    assert "harmonic_annotation" in annotated
    assert original["metrics"] == annotated["metrics"]


def test_annotation_is_non_authoritative():
    from psi42_harmonic_annotation_bridge_r1 import resolve_harmonic_annotation

    metrics = {"lock": 0.2, "presence": 0.1}
    annotation = resolve_harmonic_annotation(metrics)

    assert "dominant_frequency" in annotation
    assert annotation.get("authority_boundary") is not None
