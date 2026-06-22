import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/dashboard.dart';
import '../providers/auth_provider.dart';
import '../providers/career_provider.dart';
import '../theme/app_theme.dart';
import 'login_screen.dart';
import 'recommendations_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback(
        (_) => context.read<CareerProvider>().loadDashboard());
  }

  Future<void> _logout() async {
    await context.read<AuthProvider>().logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final career = context.watch<CareerProvider>();
    final user = context.watch<AuthProvider>().user;
    final dash = career.dashboard;

    return Scaffold(
      appBar: AppBar(
        title: Text('Hi, ${user?.firstName ?? 'there'}'),
        actions: [
          IconButton(
              onPressed: _logout, icon: const Icon(Icons.logout), tooltip: 'Log out'),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => const RecommendationsScreen()),
        ),
        icon: const Icon(Icons.work_outline),
        label: const Text('Find jobs'),
      ),
      body: RefreshIndicator(
        onRefresh: () => career.loadDashboard(),
        child: _body(context, career, dash),
      ),
    );
  }

  Widget _body(BuildContext context, CareerProvider career, Dashboard? dash) {
    if (career.loading && dash == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (career.error != null && dash == null) {
      return _error(context, career.error!, () => career.loadDashboard());
    }
    if (dash == null) {
      return const Center(child: Text('No data yet.'));
    }
    final m = dash.metrics;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _sectionTitle(context, 'Your snapshot'),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.6,
          children: [
            _metric('Profile score', '${m.profileScore}', Icons.person_outline),
            _metric('Applications', '${m.totalApplications}', Icons.send_outlined),
            _metric('Interviews', '${m.interviews}', Icons.event_available),
            _metric('Offers', '${m.offers}', Icons.celebration_outlined),
          ],
        ),
        const SizedBox(height: 24),
        _sectionTitle(context, 'Pipeline'),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _row('Qualified matches', '${dash.totalQualified}'),
                _row('Strong matches', '${dash.strongMatches}'),
                _row('Auto-apply ready', '${dash.autoApplyReady}'),
                _row('Avg match score',
                    '${m.avgMatchScore.toStringAsFixed(0)}%'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),
        if (dash.recentApplications.isNotEmpty) ...[
          _sectionTitle(context, 'Recent applications'),
          const SizedBox(height: 12),
          ...dash.recentApplications.map((a) => Card(
                child: ListTile(
                  title: Text(a.job),
                  subtitle: Text(a.company),
                  trailing: Text('${a.score}%',
                      style: const TextStyle(fontWeight: FontWeight.w700)),
                ),
              )),
        ],
        const SizedBox(height: 80),
      ],
    );
  }

  Widget _sectionTitle(BuildContext context, String text) => Text(text,
      style: Theme.of(context)
          .textTheme
          .titleMedium
          ?.copyWith(fontWeight: FontWeight.w800));

  Widget _metric(String label, String value, IconData icon) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: AppTheme.primary),
              const Spacer(),
              Text(value,
                  style: const TextStyle(
                      fontSize: 24, fontWeight: FontWeight.w800)),
              Text(label,
                  style: const TextStyle(
                      color: AppTheme.textMuted, fontSize: 12)),
            ],
          ),
        ),
      );

  Widget _row(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(color: AppTheme.textMuted)),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w700)),
          ],
        ),
      );

  Widget _error(BuildContext context, String message, VoidCallback retry) =>
      ListView(
        children: [
          const SizedBox(height: 120),
          const Icon(Icons.cloud_off, size: 48, color: AppTheme.textMuted),
          const SizedBox(height: 12),
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          Center(
            child: OutlinedButton(onPressed: retry, child: const Text('Retry')),
          ),
        ],
      );
}
