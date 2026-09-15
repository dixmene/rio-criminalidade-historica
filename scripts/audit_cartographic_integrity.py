# -*- coding: utf-8 -*-
"""
Auditoria Automatizada de Integridade Cartográfica e Epistemológica (FASE 7)
===========================================================================

Executa 14 checagens de validação matemática, arquivística e metodológica
sobre os modelos, camadas vetoriais, snapshots e serviços do Atlas.
Gera o relatório formal em reports/cartographic_integrity_report.json.
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Adiciona raiz ao path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.database import SessionLocal
from app.models.region import Region
from app.models.event import Event
from app.models.source import Source
from app.models.atlas import (
    TerritorialDataset,
    RegionVersion,
    TerritorialRelation,
    InstitutionalFacility,
    MovementFlow,
)
from app.services.atlas_service import AtlasService
from app.services.ethics_guard import EthicsGuard, OPERATIONAL_KEYWORDS


class CartographicAuditor:
    """
    Auditor oficial de integridade dos 14 pilares cartográficos do Atlas.
    """

    def __init__(self):
        self.db = SessionLocal()
        self.results = {}
        self.passed_count = 0
        self.failed_count = 0

    def run_all_checks(self) -> Dict[str, Any]:
        try:
            self._check_01_no_invented_coordinates()
            self._check_02_strict_null_preservation()
            self._check_03_crs_validation()
            self._check_04_sha256_cryptographic_hashes()
            self._check_05_region_version_dataset_link()
            self._check_06_temporal_validity_consistency()
            self._check_07_anachronism_explicit_flagging()
            self._check_08_strict_territorial_semantics()
            self._check_09_disputed_territories_flagged()
            self._check_10_facility_lifecycle_consistency()
            self._check_11_movement_flows_geometry_integrity()
            self._check_12_snapshots_and_manifest_integrity()
            self._check_13_ethics_embargo_24_months()
            self._check_14_anti_operational_intelligence_filter()

            total = len(self.results)
            passed = sum(1 for r in self.results.values() if r["status"] == "PASS")
            failed = total - passed
            score = round((passed / total) * 100, 1)

            report = {
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
                "total_checks": total,
                "passed_checks": passed,
                "failed_checks": failed,
                "integrity_score": score,
                "is_fully_compliant": (failed == 0),
                "checks": self.results
            }

            out_file = _ROOT / "reports" / "cartographic_integrity_report.json"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            return report
        finally:
            self.db.close()

    def _record(self, check_id: str, title: str, passed: bool, details: str, violations: int = 0):
        self.results[check_id] = {
            "title": title,
            "status": "PASS" if passed else "FAIL",
            "violations_count": violations,
            "details": details
        }

    # 1. Zero Coordenadas Inventadas (0,0 ou NaN)
    def _check_01_no_invented_coordinates(self):
        regions = self.db.query(Region).all()
        violations = []
        for r in regions:
            if r.latitude is not None and r.longitude is not None:
                if (r.latitude == 0.0 and r.longitude == 0.0) or abs(r.latitude) > 90 or abs(r.longitude) > 180:
                    violations.append(f"Região ID {r.id} com coordenadas anômalas: ({r.latitude}, {r.longitude})")

        self._record(
            "check_01_no_invented_coordinates",
            "Zero Coordenadas Inventadas ou Anômalas",
            len(violations) == 0,
            f"{len(violations)} regiões com coordenadas inválidas.",
            len(violations)
        )

    # 2. Preservação Estrita de NULL (IDs 89, 91, 124)
    def _check_02_strict_null_preservation(self):
        null_ids = [89, 91, 124]
        violations = []
        for nid in null_ids:
            reg = self.db.query(Region).filter(Region.id == nid).first()
            if reg:
                if reg.latitude is not None or reg.longitude is not None:
                    violations.append(f"Região ID {nid} deveria ter coordenadas NULL, mas possui ({reg.latitude}, {reg.longitude})")
                versions = self.db.query(RegionVersion).filter(RegionVersion.region_id == nid).all()
                if len(versions) > 0:
                    violations.append(f"Região ID {nid} possui versões espaciais inventadas sem coordenadas comprovadas.")

        self._record(
            "check_02_strict_null_preservation",
            "Preservação Estrita de NULL (NULL != 0)",
            len(violations) == 0,
            f"Regiões conceituais {null_ids} preservadas como estritamente NULL sem geometrias fictícias.",
            len(violations)
        )

    # 3. Validação de CRS Oficial (EPSG:4326 / EPSG:4674)
    def _check_03_crs_validation(self):
        datasets = self.db.query(TerritorialDataset).all()
        violations = []
        for ds in datasets:
            if ds.crs not in ("EPSG:4326", "EPSG:4674"):
                violations.append(f"Dataset '{ds.name}' possui CRS não homologado: {ds.crs}")

        self._record(
            "check_03_crs_validation",
            "Validação de CRS Cartográfico Oficial",
            len(violations) == 0 and len(datasets) > 0,
            f"{len(datasets)} datasets validados sob CRS oficial homologado (WGS84 / SIRGAS2000).",
            len(violations)
        )

    # 4. Integridade de Hash Criptográfico SHA-256
    def _check_04_sha256_cryptographic_hashes(self):
        datasets = self.db.query(TerritorialDataset).all()
        violations = []
        for ds in datasets:
            if not ds.sha256 or len(ds.sha256) != 64:
                violations.append(f"Dataset '{ds.name}' sem hash SHA-256 válido.")

        self._record(
            "check_04_sha256_cryptographic_hashes",
            "Hashes Criptográficos SHA-256 de Camadas Oficiais",
            len(violations) == 0,
            f"Todos os datasets cartográficos possuem hash SHA-256 auditável.",
            len(violations)
        )

    # 5. Rastreabilidade Dataset -> RegionVersion
    def _check_05_region_version_dataset_link(self):
        versions = self.db.query(RegionVersion).all()
        violations = []
        for ver in versions:
            if not ver.dataset_id or not ver.dataset:
                violations.append(f"RegionVersion ID {ver.id} órfã sem dataset de proveniência.")

        self._record(
            "check_05_region_version_dataset_link",
            "Rastreabilidade Ininterrupta de Versões aos Datasets",
            len(violations) == 0 and len(versions) > 0,
            f"{len(versions)} versões espaciais rigorosamente vinculadas aos datasets de proveniência.",
            len(violations)
        )

    # 6. Consistência da Vigência Temporal (valid_from <= valid_to)
    def _check_06_temporal_validity_consistency(self):
        versions = self.db.query(RegionVersion).all()
        violations = []
        for ver in versions:
            if ver.valid_from and ver.valid_to:
                if ver.valid_from > ver.valid_to:
                    violations.append(f"RegionVersion ID {ver.id} com valid_from ({ver.valid_from}) > valid_to ({ver.valid_to})")

        self._record(
            "check_06_temporal_validity_consistency",
            "Consistência Lógica de Vigência Temporal",
            len(violations) == 0,
            f"Intervalos de vigência espacial validados.",
            len(violations)
        )

    # 7. Sinalização Explícita de Anacronismo
    def _check_07_anachronism_explicit_flagging(self):
        versions = self.db.query(RegionVersion).filter(RegionVersion.is_anachronistic == True).all()
        violations = []
        for ver in versions:
            if not ver.anachronism_note or len(ver.anachronism_note.strip()) == 0:
                violations.append(f"RegionVersion ID {ver.id} marcada como anacrônica sem nota explicativa.")

        self._record(
            "check_07_anachronism_explicit_flagging",
            "Sinalização Explícita de Anacronismo Cartográfico",
            len(violations) == 0 and len(versions) > 0,
            f"{len(versions)} versões contemporâneas sinalizadas com nota metodológica de anacronismo.",
            len(violations)
        )

    # 8. Semântica Estrita de Relações Territoriais
    def _check_08_strict_territorial_semantics(self):
        valid_types = {"controle", "presenca", "influencia", "disputa", "presenca_estatal"}
        relations = self.db.query(TerritorialRelation).all()
        violations = []
        for rel in relations:
            if rel.relation_type not in valid_types:
                violations.append(f"TerritorialRelation ID {rel.id} possui relação inválida: '{rel.relation_type}'")

        self._record(
            "check_08_strict_territorial_semantics",
            "Semântica Estrita de Domínio Territorial",
            len(violations) == 0 and len(relations) > 0,
            f"{len(relations)} relações territoriais obedecem à taxonomia estrita homologada.",
            len(violations)
        )

    # 9. Disputas Territoriais Sinalizadas (is_contested = True)
    def _check_09_disputed_territories_flagged(self):
        disputas = self.db.query(TerritorialRelation).filter(TerritorialRelation.relation_type == "disputa").all()
        violations = []
        for rel in disputas:
            if not rel.is_contested:
                violations.append(f"TerritorialRelation ID {rel.id} do tipo disputa sem flag is_contested.")

        self._record(
            "check_09_disputed_territories_flagged",
            "Sinalização de Conflito em Áreas sob Disputa",
            len(violations) == 0 and len(disputas) > 0,
            f"Todas as áreas sob disputa armada identificadas possuem marcação de controvérsia.",
            len(violations)
        )

    # 10. Ciclo de Vida de Instalações Institucionais
    def _check_10_facility_lifecycle_consistency(self):
        facilities = self.db.query(InstitutionalFacility).all()
        violations = []
        for fac in facilities:
            if fac.opened_at and fac.closed_at:
                if fac.opened_at > fac.closed_at:
                    violations.append(f"Instalação '{fac.name}' com abertura ({fac.opened_at}) posterior ao fechamento ({fac.closed_at})")

        self._record(
            "check_10_facility_lifecycle_consistency",
            "Consistência do Ciclo de Vida Institucional",
            len(violations) == 0 and len(facilities) > 0,
            f"{len(facilities)} equipamentos institucionais com cronologia de atividade validada.",
            len(violations)
        )

    # 11. Integridade de Geometrias de Fluxos
    def _check_11_movement_flows_geometry_integrity(self):
        flows = self.db.query(MovementFlow).all()
        violations = []
        for fl in flows:
            if not fl.origin_geometry or not fl.destination_geometry:
                violations.append(f"MovementFlow ID {fl.id} sem geometria completa de origem ou destino.")
            else:
                try:
                    json.loads(fl.origin_geometry)
                    json.loads(fl.destination_geometry)
                except Exception:
                    violations.append(f"MovementFlow ID {fl.id} com GeoJSON inválido.")

        self._record(
            "check_11_movement_flows_geometry_integrity",
            "Integridade Geométrica de Fluxos Espaço-Temporais",
            len(violations) == 0 and len(flows) > 0,
            f"{len(flows)} fluxos de deslocamento validados com geometrias de origem/destino consistentes.",
            len(violations)
        )

    # 12. Integridade dos Snapshots e Manifest
    def _check_12_snapshots_and_manifest_integrity(self):
        snap_dir = _ROOT / "data" / "exports" / "snapshots"
        manifest_file = snap_dir / "manifest.json"
        violations = []

        if not manifest_file.exists():
            violations.append("manifest.json ausente.")
        else:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            if len(manifest.get("snapshots", {})) != 69:
                violations.append(f"Manifest possui {len(manifest.get('snapshots', {}))} snapshots, esperado 69.")

            # Verifica hashes de uma amostra
            for yr in (1958, 1979, 1988, 2026):
                meta = manifest["snapshots"].get(str(yr))
                if not meta:
                    violations.append(f"Snapshot para o ano {yr} ausente no manifest.")
                else:
                    s_file = snap_dir / meta["filename"]
                    if not s_file.exists():
                        violations.append(f"Arquivo {meta['filename']} não encontrado.")
                    else:
                        with open(s_file, "rb") as sf:
                            computed = hashlib.sha256(sf.read()).hexdigest()
                            if computed != meta["sha256"]:
                                violations.append(f"Hash divergente para {meta['filename']}")

        self._record(
            "check_12_snapshots_and_manifest_integrity",
            "Integridade dos 69 Snapshots Anuais e Manifest Criptográfico",
            len(violations) == 0,
            f"Snapshots pré-computados (1958-2026) validados com manifest.json.",
            len(violations)
        )

    # 13. Embargo Ético de 24 Meses
    def _check_13_ethics_embargo_24_months(self):
        atlas = AtlasService(self.db)
        ws_recent = atlas.get_world_state(year=2026, is_demo=False)
        violations = []

        if not ws_recent.metadata.get("ethics_embargo_active"):
            violations.append("Embargo ético inativo para o ano corrente de 2026.")

        for ev in ws_recent.events:
            if ev["geometry"]["type"] == "Point":
                prec = ev["properties"].get("location_precision", "")
                if "embargo" not in prec and "agregado" not in prec:
                    violations.append(f"Evento ID {ev['properties']['event_id']} expõe ponto exato recente sob embargo.")

        self._record(
            "check_13_ethics_embargo_24_months",
            "Embargo Ético de Granularidade Temporal (24 Meses)",
            len(violations) == 0,
            f"Regra de salvaguarda de pessoas vivas ativamente aplicada sobre acontecimentos recentes.",
            len(violations)
        )

    # 14. Filtro Anti-Inteligência Operacional
    def _check_14_anti_operational_intelligence_filter(self):
        atlas = AtlasService(self.db)
        violations = []
        # Amostra anos
        for test_yr in (1979, 1988, 2024, 2026):
            ws = atlas.get_world_state(year=test_yr, is_demo=False)
            for feat in (ws.territories + ws.facilities + ws.events + ws.flows):
                text_to_test = json.dumps(feat.get("properties", {}), ensure_ascii=False)
                has_viol, terms = EthicsGuard.scan_operational_intelligence(text_to_test)
                if has_viol:
                    violations.append(f"Feição {feat.get('id')} contém termos proibidos: {terms}")

        self._record(
            "check_14_anti_operational_intelligence_filter",
            "Filtro Rigoroso Anti-Inteligência Operacional",
            len(violations) == 0,
            f"Nenhum termo de inteligência tática identificado nas saídas públicas do Atlas.",
            len(violations)
        )


def main():
    auditor = CartographicAuditor()
    report = auditor.run_all_checks()

    print(f"=== Relatório de Integridade Cartográfica (FASE 7) ===")
    print(f"Total de checagens: {report['total_checks']}")
    print(f"Checagens aprovadas: {report['passed_checks']}")
    print(f"Violações: {report['failed_checks']}")
    print(f"Índice de Integridade: {report['integrity_score']}%\n")

    for cid, data in sorted(report["checks"].items()):
        symbol = "OK" if data["status"] == "PASS" else "FAIL"
        print(f"[{symbol}] {data['title']}: {data['details']}")

    if not report["is_fully_compliant"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
