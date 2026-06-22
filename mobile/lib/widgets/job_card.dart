import 'package:flutter/material.dart';

import '../models/job.dart';
import '../theme/app_theme.dart';

/// Compact match-score badge with tier color.
class ScoreBadge extends StatelessWidget {
  const ScoreBadge({super.key, required this.score, required this.tier});

  final int score;
  final String tier;

  @override
  Widget build(BuildContext context) {
    final color = AppTheme.tierColor(tier);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        '$score%',
        style: TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 13),
      ),
    );
  }
}

/// Tappable job summary card used in lists.
class JobCard extends StatelessWidget {
  const JobCard({super.key, required this.job, required this.onTap});

  final Job job;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(job.title,
                            style: theme.textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.w700)),
                        const SizedBox(height: 2),
                        Text('${job.company} · ${job.location}',
                            style: theme.textTheme.bodySmall),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  ScoreBadge(score: job.matchScore, tier: job.matchTier),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: [
                  _chip(context, job.salaryLabel, Icons.payments_outlined),
                  _chip(context, job.sourcePortal, Icons.public),
                  if (job.isAutoApply)
                    _chip(context, 'Auto-apply ready', Icons.bolt,
                        color: AppTheme.accent),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _chip(BuildContext context, String label, IconData icon,
      {Color? color}) {
    final c = color ?? Theme.of(context).colorScheme.outline;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: c),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12, color: c)),
      ],
    );
  }
}
