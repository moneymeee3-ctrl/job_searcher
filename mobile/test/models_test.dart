import 'package:embedhunt/models/dashboard.dart';
import 'package:embedhunt/models/job.dart';
import 'package:embedhunt/models/user.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Job.fromJson', () {
    test('parses the API job shape', () {
      final job = Job.fromJson({
        'rank': 1,
        'job_id': 'abc',
        'title': 'Embedded Engineer',
        'company': 'NVIDIA',
        'company_tier': 'tier1',
        'location': 'Bangalore',
        'source_portal': 'greenhouse',
        'apply_url': 'https://example.com',
        'salary_min_lpa': 30,
        'salary_max_lpa': 45.5,
        'meets_salary': true,
        'match_score': 88,
        'match_tier': 'auto_apply',
        'is_auto_apply': true,
        'matched_skills': ['c', 'rtos'],
        'missing_skills': ['can'],
        'explanation': 'Strong overlap.',
        'recommendation': 'Apply now.',
      });

      expect(job.title, 'Embedded Engineer');
      expect(job.matchScore, 88);
      expect(job.isAutoApply, isTrue);
      expect(job.matchedSkills, ['c', 'rtos']);
      expect(job.salaryLabel, '30–46 LPA');
    });

    test('tolerates missing/null fields', () {
      final job = Job.fromJson({});
      expect(job.title, '');
      expect(job.matchedSkills, isEmpty);
      expect(job.salaryLabel, 'Not disclosed');
    });
  });

  group('Dashboard.fromJson', () {
    test('parses metrics and nested summaries', () {
      final dash = Dashboard.fromJson({
        'metrics': {
          'profile_score': 72,
          'total_applications': 5,
          'interviews': 2,
          'offers': 1,
          'avg_match_score': 81.4,
        },
        'recommendations_summary': {
          'total_qualified': 10,
          'auto_apply_ready': 3,
          'strong_matches': 4,
          'top_5': [
            {'title': 'A', 'match_score': 90, 'match_tier': 'strong'}
          ],
        },
        'recent_applications': [
          {'job': 'X', 'company': 'Y', 'score': 80, 'status': 'submitted'}
        ],
      });

      expect(dash.metrics.profileScore, 72);
      expect(dash.totalQualified, 10);
      expect(dash.topJobs.single.title, 'A');
      expect(dash.recentApplications.single.company, 'Y');
    });
  });

  group('User.fromJson', () {
    test('parses first/last/full name', () {
      final user = User.fromJson({
        'id': '1',
        'email': 'a@b.com',
        'username': 'ab',
        'first_name': 'Ada',
        'last_name': 'Lovelace',
        'full_name': 'Ada Lovelace',
        'role': 'candidate',
        'is_verified': true,
        'is_premium': false,
      });
      expect(user.firstName, 'Ada');
      expect(user.fullName, 'Ada Lovelace');
      expect(user.isVerified, isTrue);
    });
  });
}
