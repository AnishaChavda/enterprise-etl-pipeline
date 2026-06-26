import os
import json
import time
import logging
from datetime import datetime
from sqlalchemy import func
from loading.connection import get_db_session
from loading.models import ETLRun, AuditLog

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PipelineMetrics:
    def __init__(self):
        self.start_times = {}
        self.api_latencies = {}

    def start_timing(self, stage_name):
        self.start_times[stage_name] = time.time()

    def stop_timing(self, stage_name):
        if stage_name in self.start_times:
            duration = time.time() - self.start_times[stage_name]
            logging.info(f"Stage '{stage_name}' executed in {duration:.2f} seconds.")
            return duration
        return 0.0

    def record_api_latency(self, api_name, latency):
        if api_name not in self.api_latencies:
            self.api_latencies[api_name] = []
        self.api_latencies[api_name].append(latency)
        logging.info(f"API '{api_name}' latency recorded: {latency:.2f}s.")

    def get_aggregate_metrics(self):
        """
        Query PostgreSQL database to generate high-level pipeline health reports.
        """
        report = {}
        with get_db_session() as session:
            # 1. Pipeline health summary
            total_runs = session.query(func.count(ETLRun.id)).scalar() or 0
            success_runs = session.query(func.count(ETLRun.id)).filter(ETLRun.status == "SUCCESS").scalar() or 0
            failed_runs = session.query(func.count(ETLRun.id)).filter(ETLRun.status == "FAILED").scalar() or 0
            
            success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0.0
            
            # 2. Avg duration of runs
            avg_duration_sec = 0.0
            runs = session.query(ETLRun).filter(ETLRun.ended_at.isnot(None)).all()
            if runs:
                durations = [(r.ended_at - r.started_at).total_seconds() for r in runs]
                avg_duration_sec = sum(durations) / len(durations)

            # 3. Warehouse statistics
            total_records_processed = session.query(func.sum(ETLRun.records_processed)).scalar() or 0
            
            # 4. Data freshness: last successful sync time
            last_success = session.query(ETLRun).filter(ETLRun.status == "SUCCESS").order_by(ETLRun.ended_at.desc()).first()
            last_sync_time = last_success.ended_at.isoformat() if last_success else "Never"

            report = {
                "total_runs": total_runs,
                "success_runs": success_runs,
                "failed_runs": failed_runs,
                "success_rate": f"{success_rate:.2f}%",
                "avg_duration_seconds": f"{avg_duration_sec:.2f}s",
                "total_records_processed": int(total_records_processed),
                "last_successful_sync": last_sync_time
            }
            
        return report

    def generate_dashboard_report(self):
        """
        Writes a dashboard summary to logs/pipeline_dashboard.json and outputs to console.
        """
        try:
            metrics = self.get_aggregate_metrics()
            os.makedirs("logs", exist_ok=True)
            filepath = "logs/pipeline_dashboard.json"
            with open(filepath, "w") as f:
                json.dump(metrics, f, indent=4)
            
            print("\n" + "="*40)
            print("      ETL PIPELINE HEALTH DASHBOARD     ")
            print("="*40)
            print(f"Total Job Executions      : {metrics['total_runs']}")
            print(f"Success/Failure           : {metrics['success_runs']} / {metrics['failed_runs']}")
            print(f"Pipeline Success Rate     : {metrics['success_rate']}")
            print(f"Average Duration          : {metrics['avg_duration_seconds']}")
            print(f"Total Records Synchronized: {metrics['total_records_processed']}")
            print(f"Warehouse Freshness (L.S.): {metrics['last_successful_sync']}")
            print("="*40 + "\n")
            return metrics
        except Exception as e:
            logging.error(f"Failed to generate dashboard report: {e}")
            return {}

if __name__ == "__main__":
    pm = PipelineMetrics()
    pm.generate_dashboard_report()
