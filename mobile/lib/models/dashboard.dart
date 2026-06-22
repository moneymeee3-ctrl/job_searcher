import 'job.dart';

/// Dashboard metrics, mirrors the API's `metrics` object.
class DashboardMetrics {
  final int profileScore;
  final int totalApplications;
  final int submitted;
  final int interviews;
  final int offers;
  final double conversionRate;
  final double interviewRate;
  final double offerRate;
  final double avgMatchScore;

  const DashboardMetrics({
    required this.profileScore,
    required this.totalApplications,
    required this.submitted,
    required this.interviews,
    required this.offers,
    required this.conversionRate,
    required this.interviewRate,
    required this.offerRate,
    required this.avgMatchScore,
  });

  static double _toDouble(dynamic v) => (v is num) ? v.toDouble() : 0.0;
  static int _toInt(dynamic v) => (v is num) ? v.toInt() : 0;

  factory DashboardMetrics.fromJson(Map<String, dynamic> json) {
    return DashboardMetrics(
      profileScore: _toInt(json['profile_score']),
      totalApplications: _toInt(json['total_applications']),
      submitted: _toInt(json['submitted']),
      interviews: _toInt(json['interviews']),
      offers: _toInt(json['offers']),
      conversionRate: _toDouble(json['conversion_rate']),
      interviewRate: _toDouble(json['interview_rate']),
      offerRate: _toDouble(json['offer_rate']),
      avgMatchScore: _toDouble(json['avg_match_score']),
    );
  }
}

/// A recent application summary row.
class RecentApplication {
  final String job;
  final String company;
  final int score;
  final String status;
  final String outcome;

  const RecentApplication({
    required this.job,
    required this.company,
    required this.score,
    required this.status,
    required this.outcome,
  });

  factory RecentApplication.fromJson(Map<String, dynamic> json) {
    return RecentApplication(
      job: json['job'] as String? ?? '',
      company: json['company'] as String? ?? '',
      score: json['score'] as int? ?? 0,
      status: json['status'] as String? ?? '',
      outcome: json['outcome'] as String? ?? '',
    );
  }
}

/// Full dashboard payload.
class Dashboard {
  final DashboardMetrics metrics;
  final int totalQualified;
  final int autoApplyReady;
  final int strongMatches;
  final List<Job> topJobs;
  final List<RecentApplication> recentApplications;

  const Dashboard({
    required this.metrics,
    required this.totalQualified,
    required this.autoApplyReady,
    required this.strongMatches,
    required this.topJobs,
    required this.recentApplications,
  });

  factory Dashboard.fromJson(Map<String, dynamic> json) {
    final recSummary = json['recommendations_summary'] as Map<String, dynamic>? ?? {};
    final top = (recSummary['top_5'] as List? ?? [])
        .map((e) => Job.fromJson(e as Map<String, dynamic>))
        .toList();
    final recent = (json['recent_applications'] as List? ?? [])
        .map((e) => RecentApplication.fromJson(e as Map<String, dynamic>))
        .toList();
    return Dashboard(
      metrics: DashboardMetrics.fromJson(
          json['metrics'] as Map<String, dynamic>? ?? {}),
      totalQualified: recSummary['total_qualified'] as int? ?? 0,
      autoApplyReady: recSummary['auto_apply_ready'] as int? ?? 0,
      strongMatches: recSummary['strong_matches'] as int? ?? 0,
      topJobs: top,
      recentApplications: recent,
    );
  }
}
