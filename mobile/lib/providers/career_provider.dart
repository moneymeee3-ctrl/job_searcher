import 'package:flutter/foundation.dart';

import '../models/dashboard.dart';
import '../models/job.dart';
import '../services/api_client.dart';
import '../services/career_service.dart';

/// Loads and holds dashboard + recommendation data.
class CareerProvider extends ChangeNotifier {
  CareerProvider(this._career);
  final CareerService _career;

  bool _loading = false;
  String? _error;
  Dashboard? _dashboard;
  List<Job> _jobs = const [];

  bool get loading => _loading;
  String? get error => _error;
  Dashboard? get dashboard => _dashboard;
  List<Job> get jobs => _jobs;

  Future<void> loadDashboard() async {
    await _guard(() async => _dashboard = await _career.dashboard());
  }

  Future<void> loadRecommendations({
    int minScore = 40,
    double salaryMinLpa = 15.0,
  }) async {
    await _guard(() async => _jobs = await _career.recommendations(
          minScore: minScore,
          salaryMinLpa: salaryMinLpa,
        ));
  }

  Future<Map<String, dynamic>?> approve(String jobId) async {
    try {
      return await _career.approveApply(jobId);
    } on ApiException catch (e) {
      _error = e.message;
      notifyListeners();
      return null;
    }
  }

  Future<void> _guard(Future<void> Function() action) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await action();
    } on ApiException catch (e) {
      _error = e.message;
    } catch (_) {
      _error = 'Could not reach the server.';
    }
    _loading = false;
    notifyListeners();
  }
}
