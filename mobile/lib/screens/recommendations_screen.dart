import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/career_provider.dart';
import '../widgets/job_card.dart';
import 'job_detail_screen.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  double _minScore = 40;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() =>
      context.read<CareerProvider>().loadRecommendations(minScore: _minScore.round());

  @override
  Widget build(BuildContext context) {
    final career = context.watch<CareerProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Matched jobs')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                const Text('Min score'),
                Expanded(
                  child: Slider(
                    value: _minScore,
                    min: 0,
                    max: 100,
                    divisions: 20,
                    label: '${_minScore.round()}%',
                    onChanged: (v) => setState(() => _minScore = v),
                    onChangeEnd: (_) => _load(),
                  ),
                ),
                Text('${_minScore.round()}%'),
              ],
            ),
          ),
          Expanded(child: _list(context, career)),
        ],
      ),
    );
  }

  Widget _list(BuildContext context, CareerProvider career) {
    if (career.loading && career.jobs.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }
    if (career.error != null && career.jobs.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(career.error!),
            const SizedBox(height: 12),
            OutlinedButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }
    if (career.jobs.isEmpty) {
      return const Center(child: Text('No matches at this threshold.'));
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: career.jobs.length,
        itemBuilder: (_, i) {
          final job = career.jobs[i];
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: JobCard(
              job: job,
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => JobDetailScreen(job: job)),
              ),
            ),
          );
        },
      ),
    );
  }
}
