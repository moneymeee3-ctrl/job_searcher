import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/job.dart';
import '../providers/career_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/job_card.dart';

class JobDetailScreen extends StatelessWidget {
  const JobDetailScreen({super.key, required this.job});

  final Job job;

  Future<void> _apply(BuildContext context) async {
    final career = context.read<CareerProvider>();
    final messenger = ScaffoldMessenger.of(context);
    final result = await career.approve(job.jobId);
    if (result != null) {
      messenger.showSnackBar(
        const SnackBar(content: Text('Application approved.')),
      );
    } else {
      messenger.showSnackBar(
        SnackBar(content: Text(career.error ?? 'Could not apply.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Job details')),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton.icon(
            onPressed: () => _apply(context),
            icon: const Icon(Icons.send),
            label: Text(job.isAutoApply ? 'Approve auto-apply' : 'Apply'),
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(job.title,
                        style: theme.textTheme.headlineSmall
                            ?.copyWith(fontWeight: FontWeight.w800)),
                    const SizedBox(height: 4),
                    Text('${job.company} · ${job.location}',
                        style: theme.textTheme.bodyMedium
                            ?.copyWith(color: AppTheme.textMuted)),
                  ],
                ),
              ),
              ScoreBadge(score: job.matchScore, tier: job.matchTier),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _pill(job.salaryLabel, Icons.payments_outlined),
              _pill(job.sourcePortal, Icons.public),
              _pill(job.companyTier, Icons.apartment),
              if (job.meetsSalary)
                _pill('Meets salary', Icons.check_circle_outline,
                    color: AppTheme.accent),
            ],
          ),
          const SizedBox(height: 24),
          if (job.explanation.isNotEmpty) ...[
            _heading(context, 'Why this matches'),
            Text(job.explanation),
            const SizedBox(height: 20),
          ],
          if (job.recommendation.isNotEmpty) ...[
            _heading(context, 'Recommendation'),
            Text(job.recommendation),
            const SizedBox(height: 20),
          ],
          if (job.matchedSkills.isNotEmpty) ...[
            _heading(context, 'Matched skills'),
            _chips(job.matchedSkills, AppTheme.accent),
            const SizedBox(height: 20),
          ],
          if (job.missingSkills.isNotEmpty) ...[
            _heading(context, 'Skill gaps'),
            _chips(job.missingSkills, AppTheme.warning),
            const SizedBox(height: 20),
          ],
          const SizedBox(height: 60),
        ],
      ),
    );
  }

  Widget _heading(BuildContext context, String text) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(text,
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(fontWeight: FontWeight.w800)),
      );

  Widget _pill(String label, IconData icon, {Color color = AppTheme.textMuted}) =>
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.10),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 6),
            Text(label, style: TextStyle(color: color, fontSize: 13)),
          ],
        ),
      );

  Widget _chips(List<String> items, Color color) => Wrap(
        spacing: 8,
        runSpacing: 8,
        children: items
            .map((s) => Chip(
                  label: Text(s),
                  backgroundColor: color.withValues(alpha: 0.12),
                  side: BorderSide(color: color.withValues(alpha: 0.3)),
                  labelStyle: TextStyle(color: color),
                ))
            .toList(),
      );
}
