import '../models/dashboard.dart';
import '../models/job.dart';
import 'api_client.dart';

/// Career API: dashboard, recommendations, agent advice, apply.
class CareerService {
  CareerService(this._api);
  final ApiClient _api;

  Future<Dashboard> dashboard() async {
    final data = await _api.get('/dashboard/') as Map<String, dynamic>;
    return Dashboard.fromJson(data);
  }

  Future<List<Job>> recommendations({
    int minScore = 40,
    double salaryMinLpa = 15.0,
  }) async {
    final data = await _api.get('/recommendations/jobs', query: {
      'min_score': minScore,
      'salary_min_lpa': salaryMinLpa,
    }) as Map<String, dynamic>;
    return (data['jobs'] as List? ?? [])
        .map((e) => Job.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Autonomous agent advice payload (scan, reason, plan, coach).
  Future<Map<String, dynamic>> advise({
    int minScore = 40,
    double salaryMinLpa = 15.0,
  }) async {
    return await _api.get('/agent/advise', query: {
      'min_score': minScore,
      'salary_min_lpa': salaryMinLpa,
    }) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> approveApply(String jobId) async {
    return await _api.post('/recommendations/approve',
        query: {'job_id': jobId}) as Map<String, dynamic>;
  }
}
